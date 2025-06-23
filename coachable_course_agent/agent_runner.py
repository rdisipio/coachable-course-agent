from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType
from langchain_groq import ChatGroq
from langchain.chains import LLMChain
from dotenv import load_dotenv
import os

from coachable_course_agent.vector_store import query_similar_courses
from coachable_course_agent.memory_store import load_user_profile
from coachable_course_agent.recommendation_prompt import base_prompt

load_dotenv()

# Initialize LLM
llm = ChatGroq(model="llama3-70b-8192", temperature=0.7, api_key=os.getenv("GROQ_API_KEY"))

# Define tool: query vector store
def vector_search_tool(profile: dict):
    from coachable_course_agent.vector_store import initialize_chroma
    chroma = initialize_chroma()
    return query_similar_courses(chroma, profile, top_n=10)


# Add tools
tools = [
    Tool(
        name="VectorSearchCourses",
        func=vector_search_tool,
        description="Searches courses similar to user profile using vector embeddings"
    )
]

# Initialize the agent
def create_course_agent():
    return initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )
