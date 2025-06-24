from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.tools import Tool
from coachable_course_agent.esco_matcher import match_to_esco

from dotenv import load_dotenv
import os
import json

load_dotenv()

llm = ChatGroq(model="llama3-70b-8192", temperature=0.3, api_key=os.getenv("GROQ_API_KEY"))

linkedin_prompt = PromptTemplate.from_template("""
You are an assistant that extracts career information from LinkedIn profiles.

Given the text below, return a JSON object with:
- "headline": a short career summary
- "skills": a list of professional skills (max 10)
- "goal": an inferred learning or career goal if available

LinkedIn profile:
\"\"\"
{profile_text}
\"\"\"
""")

profile_chain = LLMChain(prompt=linkedin_prompt, llm=llm)

def extract_profile_info(profile_text: str) -> dict:
    try:
        output = profile_chain.run(profile_text)
        result = json.loads(output)
        return result
    except Exception as e:
        print(f"Parsing error: {e}")
        return {
            "headline": "",
            "skills": [],
            "goal": ""
        }


profile_extract_tool = Tool.from_function(
    name="ExtractProfileFromText",
    func=extract_profile_info,
    description="Given a free-form LinkedIn profile text, extracts a short career headline, a list of up to 10 professional skills, and an inferred learning or career goal. Input should be raw profile text."
)


def match_esco_wrapper(input_str: str) -> str:
    try:
        input_dict = json.loads(input_str)
        skills = input_dict.get("skills", [])
        if not isinstance(skills, list):
            return "Error: 'skills' must be a list of strings."

        top_matches = match_to_esco(skills, esco_vectorstore)

        results = [
            {
                "label": doc.metadata["label"],
                "uri": doc.metadata["uri"],
                "description": doc.page_content
            }
            for doc in top_matches
        ]
        return json.dumps(results, indent=2)

    except json.JSONDecodeError:
        return "Error: Could not parse input JSON."


def get_skill_tool(vectorstore):
    return Tool(
        name="MatchSkillsToESCO",
        func=lambda q: match_esco_wrapper(q, vectorstore),
        description="Matches a comma-separated list of skill names to ESCO concepts. Input format: 'skill1, skill2, ...'. Returns matched skills with ESCO URIs."
    )
