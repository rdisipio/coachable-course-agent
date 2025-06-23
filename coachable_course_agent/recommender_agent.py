from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_groq import ChatGroq
import random
import json

from coachable_course_agent.recommendation_prompt import base_prompt

from dotenv import load_dotenv
import os
load_dotenv()


def get_recommendations(user_profile, courses, esco_skills, top_n=3):
    # Sample 5-7 courses to feed into the LLM (in a real version, use vector search)
    sampled_courses = random.sample(courses, k=min(7, len(courses)))

    course_block = "\n".join([
        f"- {c['title']} ({c['provider']}) | {c['duration_hours']}h | Skills: {', '.join([s['name'] for s in c['skills']])}"
        for c in sampled_courses
    ])

    prompt_input = base_prompt.format(
        goal=user_profile["goal"],
        known_skills=", ".join(user_profile["known_skills"]),
        missing_skills=", ".join(user_profile["missing_skills"]),
        format=", ".join(user_profile["preferences"]["format"]),
        style=", ".join(user_profile["preferences"]["style"]),
        avoid_styles=", ".join(user_profile["preferences"].get("avoid_styles", [])),
        feedback_log=json.dumps(user_profile.get("feedback_log", [])[-3:], indent=2),
        course_block=course_block
    )

    # Use a LLaMA-based model hosted via Groq
    llm = ChatGroq(model_name="llama3-70b-8192", temperature=0.2) # 0-> deterministic output, 1-> more creative
    chain = LLMChain(prompt=PromptTemplate.from_template("{input}"), llm=llm)

    response = chain.run(input=prompt_input)

    # For this prototype, we attach the LLM output as justification to the sampled courses
    for i, c in enumerate(sampled_courses[:top_n]):
        c["justification"] = f"Recommended by agent: {response}"
    return sampled_courses[:top_n]
