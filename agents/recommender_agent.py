from langchain.prompts import PromptTemplate
from langchain.llms import Groq
from langchain.chains import LLMChain
import random
import json

from prompts.recommendation_prompt import base_prompt

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

    llm = Groq(model="mixtral-8x7b-32768", temperature=0.7)
    chain = LLMChain(prompt=PromptTemplate.from_template("{input}"), llm=llm)

    response = chain.run(input=prompt_input)

    # For this prototype, we attach the LLM output as justification to the sampled courses
    for i, c in enumerate(sampled_courses[:top_n]):
        c["justification"] = f"Recommended by agent: {response}"
    return sampled_courses[:top_n]
