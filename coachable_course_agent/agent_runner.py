from langchain.agents import Tool
from langchain.agents import create_react_agent, initialize_agent, AgentType
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

from coachable_course_agent.vector_store import query_similar_courses

load_dotenv()

# Initialize LLM
llm = ChatGroq(
    model="llama3-70b-8192", 
    temperature=0.7, 
    api_key=os.getenv("GROQ_API_KEY")
)

# Define tool: query vector store
def vector_search_tool(profile: dict):
    from coachable_course_agent.vector_store import initialize_chroma
    chroma = initialize_chroma()
    results = query_similar_courses(chroma, profile, top_n=10)
    return "\n".join([
        f"- {c['title']} | {c.get('duration_hours', '?')}h | Skills: {c['skills']} | ID: {c['id']}"
        for c in results
    ])


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

