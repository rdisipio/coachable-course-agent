import json
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_groq import ChatGroq
from langchain.output_parsers import JsonOutputKeyToolsParser

from dotenv import load_dotenv
import os

from coachable_course_agent.recommendation_prompt import base_prompt

load_dotenv()

def create_justifier_chain():
    llm = ChatGroq(model="llama3-70b-8192", temperature=0.3, api_key=os.getenv("GROQ_API_KEY"))
    prompt = PromptTemplate.from_template(base_prompt)
    return LLMChain(prompt=prompt, llm=llm)


def justify_recommendations(user_profile, courses):
    course_block = "\n".join([
        f"- {c['title']} ({c['provider']}) | Level: {c.get('level', 'N/A')} | Format: {c.get('format', 'N/A')} | Skills: {c['skills']} | Duration: {c.get('duration_hours', 'N/A')} hours."
        for c in courses
    ])

    user_known_skills = user_profile.get("known_skills", []) # list of ESCO skills such as {"preferredLabel": "Python", "conceptUri": "http://example.com/skill/python"}
    user_missing_skills = user_profile.get("missing_skills", []) # list of ESCO skills such as {"preferredLabel": "Data Analysis", "conceptUri": "http://example.com/skill/data-analysis"}
    user_preferences = user_profile.get("preferences", {})
    
    
    chain = create_justifier_chain()
    response = chain.run({
        "goal": user_profile["goal"],
        "known_skills": [skill["preferredLabel"] for skill in user_known_skills if skill.get("preferredLabel") != "N/A"],
        "missing_skills": [user["preferredLabel"] for user in user_missing_skills if user.get("preferredLabel") != "N/A"],
        "format": ", ".join(user_preferences["format"]),
        "style": ", ".join(user_preferences["style"]),
        "avoid_styles": ", ".join(user_preferences.get("avoid_styles", [])),
        "feedback_log": json.dumps(user_profile.get("feedback_log", [])[-3:], indent=2),
        "course_block": course_block,
    })
    
    # Attempt to parse as JSON
    try:
        recommendations = json.loads(response)
        if isinstance(recommendations, list) and all("course_id" in r for r in recommendations):
            return recommendations
        else:
            raise ValueError("Parsed output is not a list of valid recommendations.")
    except Exception as e:
        print("⚠️ Could not parse LLM response as valid JSON.")
        print("Raw output:\n", response)
        raise e
