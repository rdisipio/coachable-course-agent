from langchain.agents import Tool
from langchain.agents import initialize_agent, AgentType
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
import json

from coachable_course_agent.vector_store import query_similar_courses
from coachable_course_agent.recommendation_prompt import base_prompt
from coachable_course_agent.linkedin_tools import profile_extract_tool, match_skills_tool

load_dotenv()

# Initialize LLM
llm = ChatGroq(
    model="llama3-70b-8192", 
    temperature=0.7, 
    api_key=os.getenv("GROQ_API_KEY")
)

# Define tool: query vector store
def vector_search_tool(input_str: str):
    input = json.loads(input_str)
    chroma = input["chroma"]
    profile = input["profile"]
    courses = query_similar_courses(chroma, profile, top_n=10)

    formatted = "\n".join([
        f"- {c['title']} ({c['provider']}) | Level: {c.get('level', 'N/A')} | Duration: {c.get('duration_hours', '?')}h | Skills: {c.get('skills', '')} | ID: {c.get('id')}"
        for c in courses
    ])
    return f"Here are the top courses based on the user's profile and preferences:\n{formatted}"



def create_course_agent():
    return initialize_agent(
        tools=[
            Tool(
                name="VectorSearchCourses",
                func=vector_search_tool,
                description="Searches courses similar to user profile using vector embeddings"
            )
        ],
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True
    )


def create_linkedin_profile_agent():
    return initialize_agent(
        tools=[profile_extract_tool, match_skills_tool],
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True
    )