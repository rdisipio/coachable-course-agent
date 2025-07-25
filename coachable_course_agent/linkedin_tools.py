from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.tools import Tool
from langchain_core.tools import tool

from coachable_course_agent.esco_matcher import match_to_esco
from coachable_course_agent.utils import extract_json_block

from dotenv import load_dotenv
from functools import partial

import os
import json

load_dotenv()


def build_profile_from_bio(user_id, blurb):
    """
    Build a user profile from a LinkedIn-style bio and user ID.
    Returns the generated profile text and the loaded profile data (dict).
    """
    # Step 0: Load ChromaDB skill vectorstore
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma(
        persist_directory="data/esco_chroma",
        embedding_function=embedding_model
    )
    # Step 1: Format prompt
    prompt = f"My user ID is {user_id}. Here is my bio: {blurb}"
    # Step 2: Create and run the agent (define tools inline to avoid circular import)
    from coachable_course_agent.tools_profile import profile_extract_tool, get_skill_tool, get_save_profile_tool, get_infer_skills_tool
    from langchain.memory.buffer import ConversationBufferMemory
    from langchain_groq import ChatGroq
    from langchain.agents import initialize_agent, AgentType
    llm = ChatGroq(
        model="llama3-70b-8192",
        temperature=0.7,
        api_key=os.getenv("GROQ_API_KEY")
    )
    tools = [profile_extract_tool, get_skill_tool(vectorstore), get_infer_skills_tool(vectorstore), get_save_profile_tool(user_id)]
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        verbose=False,
        memory=memory,
        handle_parsing_errors=True
    )
    result = agent.invoke({"input": prompt})
    result_text = result["output"]
    # Step 3: Load the generated profile data
    with open(f"data/memory/{user_id}.json", "r") as f:
        data = json.load(f)
    return result_text, data



def match_esco_wrapper(input_text: str, vectorstore) -> str:
    try:
        # Parse the string into a list of skills
        skills = [s.strip() for s in input_text.split(",") if s.strip()]
    except Exception as e:
        return f"Error: Failed to match ESCO skills - {str(e)}"

    top_matches = match_to_esco(skills, vectorstore)

    results = [
        {
            "preferredLabel": doc["preferredLabel"],
            "conceptUri": doc["conceptUri"],
            "description": doc['description']
        }
        for doc in top_matches
    ]
    return json.dumps(results, indent=2)


def get_skill_tool(vectorstore):
    return Tool(
        name="MatchSkillsToESCO",
        func=lambda q: match_esco_wrapper(q, vectorstore),
        description=(
            "Matches a comma-separated list of skill names to ESCO concepts. "
            "Input format: 'skill1, skill2, ...'. Returns matched ESCO skills."
            "For each skill, returns a JSON object with 'preferredLabel', 'conceptUri', and 'description' (if available). "
            "Make sure not to have any duplicates in the output list."
            "An example input is: 'Python'. "
            "An example output is: "
            "["
            "   {{"
            "       'preferredLabel': 'Python (programming language)', "
            "       'conceptUri': 'https://uri.esco.ec.europa.eu/concept/123456', "
            "       'description': 'A high-level programming language used for general-purpose programming.'"
            "   }}"
            "]"
            "If no skills are matched, return an empty list."
            "If the input is empty, return an empty list."
            "If the skill preferredLabel is N/A, remove it from the output list."
            "If the input is not a valid comma-separated list, return an error message."
        )
    )


def save_profile_from_str(json_str: str, user_id: str ):
    try:
        from coachable_course_agent.memory_store import load_user_profile, update_user_profile
        data = json.loads(json_str)
        user_profile = load_user_profile(user_id)

        # Add or update missing_skills
        if "missing_skills" in data:
            user_profile["missing_skills"] = data["missing_skills"]
        
        update_user_profile(user_id, {
            "goal": data.get("goal", ""),
            "known_skills": data.get("skills", []),
            "missing_skills": data.get("missing_skills", []),
            "preferences": {
                "format": [],
                "style": [],
                "avoid_styles": []
            },
            "feedback_log": [],
            "user_id": user_id,
            "blurb": data.get("blurb", ""),
            "headline": data.get("headline", "")
        })
        return f"User profile for '{user_id}' saved successfully."
    except json.JSONDecodeError:
        return "Invalid JSON format. Please return a valid JSON object."

def get_save_profile_tool(user_id):
    return Tool.from_function(
        name="SaveUserProfile",
        func=partial(save_profile_from_str, user_id=user_id),
        description="Saves the extracted user profile. Input must be a JSON string with 'headline', 'goal', and 'skills'."
    )


def infer_missing_skills(profile: dict, vectorstore, top_k=5):
    skills = profile.get("skills", [])
    query_parts = [profile.get("headline", "")]
    query_parts += [s["preferredLabel"] for s in skills]
    query_parts += [profile.get("goal", "")]
    query_text = " ".join(query_parts).strip()

    if not query_text:
        return []

    results = vectorstore.similarity_search(query_text, k=top_k)
    inferred = []
    for doc in results:
        inferred.append({
            "preferredLabel": doc.metadata.get("preferredLabel", "N/A"),
            "conceptUri": doc.metadata.get("conceptUri", "N/A"),
            "description": doc.page_content
        })
    return inferred


def get_infer_skills_tool(vectorstore):
    def infer_skills_from_json(json_str: str):
        try:
            profile = extract_json_block(json_str)
            results = infer_missing_skills(profile, vectorstore)
            return json.dumps(results, indent=2)
        except Exception as e:
            return f"Error during skill inference: {e}"

    return Tool(
        name="InferMissingSkillsFromProfile",
        func=infer_skills_from_json,
        description=(
            "Given a career headline, known skills, and a goal, infer additional ESCO skills "
            "the user might be missing. Use this when the skill list is incomplete or sparse. "
            "Do not include skills already in the profile. "
            "Input: a JSON string containing 'headline', 'skills' (ESCO-matched), and 'goal'."
            "Output: a JSON array of inferred ESCO skills, each with 'preferredLabel', 'conceptUri', and 'description'. "
            "The output will be appended to the user profile under 'missing_skills'."
        )
    )
