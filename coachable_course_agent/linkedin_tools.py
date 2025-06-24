from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.tools import Tool
from langchain_core.tools import tool

from coachable_course_agent.esco_matcher import match_to_esco
from coachable_course_agent.feedback_processor import update_user_profile

from dotenv import load_dotenv
from functools import partial

import os
import json
import re

load_dotenv()

llm = ChatGroq(model="llama3-70b-8192", temperature=0.3, api_key=os.getenv("GROQ_API_KEY"))

linkedin_prompt = PromptTemplate.from_template("""
You are an assistant that extracts career information from LinkedIn profiles.

Given the text below, return a JSON object with:
- "headline": a short career summary
- "skills": a list of professional skills (max 10)
- "goal": an inferred learning or career goal if available

Return your answer as a JSON object like this:
{{
  "headline": "...",
  "skills": ["...", "..."],
  "goal": "..."
}}

LinkedIn profile:
\"\"\"
{profile_text}
\"\"\"
""")

profile_chain = LLMChain(prompt=linkedin_prompt, llm=llm)

def extract_profile_info(profile_text: str) -> dict:
    response = profile_chain.invoke({"profile_text": profile_text})
    output = response["text"]
    try:
        json_str = re.search(r'\{[\s\S]*\}', output).group()
        #print("LLM raw output:", response["text"])  # Debug
        return json.loads(json_str)
    except Exception as e:
        print("Error in profile extraction:", e)
        return {
            "headline": "Unknown",
            "skills": [],
            "goal": "Unknown"
        }


profile_extract_tool = Tool.from_function(
    name="ExtractProfileFromText",
    func=extract_profile_info,
    description="Given a free-form LinkedIn profile text, extracts a short career headline, a list of up to 10 professional skills, and an inferred learning or career goal. Input should be raw profile text."
)


def match_esco_wrapper(input_text: str, vectorstore) -> str:
    print("\n[DEBUG] Raw input received by match_esco_wrapper:", repr(input_text))

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
            "Input format: 'skill1, skill2, ...'. Returns matched skills with ESCO URIs."
        )
    )


def save_profile_from_str(json_str: str, user_id: str ):
    try:
        data = json.loads(json_str)
        update_user_profile(user_id, {
            "goal": data.get("goal", ""),
            "known_skills": data.get("skills", []),
            "missing_skills": [],  # Start empty; could be inferred later
            "preferences": {
                "format": [],
                "style": [],
                "avoid_styles": []
            },
            "feedback_log": [],
            "user_id": user_id
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


