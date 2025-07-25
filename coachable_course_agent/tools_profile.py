import os
import json
import re

from langchain.tools import Tool
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from coachable_course_agent.linkedin_tools import get_infer_skills_tool, get_skill_tool, get_save_profile_tool

llm = ChatGroq(model="llama3-70b-8192", temperature=0.3, api_key=os.getenv("GROQ_API_KEY"))


linkedin_prompt = PromptTemplate.from_template("""
You are an assistant that extracts career information from LinkedIn profiles.

Given the text below, return a JSON object with:

- "headline": a short career summary
- "skills": a list of professional skills (max 10)
- "goal": an inferred learning or career goal if available
- "blurb": a short personal blurb or summary based on the profile text (max 100 words).
                                               
Return your answer as a JSON object like this:
{{
  "headline": "...",
  "skills": ["...", "..."],
  "goal": "...",
  "blurb": "..."
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
            "headline": "",
            "skills": [],
            "goal": "",
            "blurb": ""
        }


profile_extract_tool = Tool.from_function(
    name="ExtractProfileFromText",
    func=extract_profile_info,
    description=(
        "Given a free-form LinkedIn profile text (referred as blurb in the following), extract a short career headline, "
        "a list of up to 10 professional skills, and an inferred learning or career goal. Also return the blurb if available. " 
        "Input should be raw profile text."
        "After extracting skills, always match them to ESCO concepts and save only the matched preferredLabel and conceptUri into the user profile."
        )
    )


def get_skill_tool(vectorstore):
    from coachable_course_agent.linkedin_tools import get_skill_tool as _get_skill_tool
    return _get_skill_tool(vectorstore)

def get_save_profile_tool(user_id):
    from coachable_course_agent.linkedin_tools import get_save_profile_tool as _get_save_profile_tool
    return _get_save_profile_tool(user_id)

def get_infer_skills_tool(vectorstore):
    from coachable_course_agent.linkedin_tools import get_infer_skills_tool as _get_infer_skills_tool
    return _get_infer_skills_tool(vectorstore)
