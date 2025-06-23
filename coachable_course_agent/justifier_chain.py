import json
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.chat_models import ChatGroq
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
    justifier_chain = create_justifier_chain()

    course_block = "\n".join([
        f"- {c['title']} ({c['provider']}) | Level: {c.get('level', 'N/A')} | Format: {c.get('format', 'N/A')} | Skills: {', '.join(c['skills'])}"
        for c in courses
    ])

    # Format prompt input
    instructions = base_prompt.format(
        goal=user_profile["goal"],
        known_skills=", ".join(user_profile["known_skills"]),
        missing_skills=", ".join(user_profile["missing_skills"]),
        format=", ".join(user_profile["preferences"]["format"]),
        style=", ".join(user_profile["preferences"]["style"]),
        avoid_styles=", ".join(user_profile["preferences"].get("avoid_styles", [])),
        feedback_log=json.dumps(user_profile.get("feedback_log", [])[-3:], indent=2),
        course_block=course_block
    )
    response = justifier_chain.run(input=instructions)
    
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
