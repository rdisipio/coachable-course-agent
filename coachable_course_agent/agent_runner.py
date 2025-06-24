from langchain.agents import Tool
from langchain.agents import initialize_agent, AgentType
from langchain_groq import ChatGroq
from langchain.memory.buffer import ConversationBufferMemory
from dotenv import load_dotenv
import os
import json

from coachable_course_agent.vector_store import query_similar_courses
from coachable_course_agent.recommendation_prompt import base_prompt
from coachable_course_agent.linkedin_tools import profile_extract_tool, get_skill_tool, get_save_profile_tool, get_infer_skills_tool
from coachable_course_agent.memory_store import update_user_profile

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


def create_profile_building_agent(vectorstore, user_id):
    llm = ChatGroq(
        model="llama3-70b-8192", 
        temperature=0.7, 
        api_key=os.getenv("GROQ_API_KEY")
    )
    tools = [profile_extract_tool, get_skill_tool(vectorstore), get_save_profile_tool(user_id), get_infer_skills_tool(vectorstore)]
    
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    return initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        verbose=True,
        memory=memory,
        handle_parsing_errors=True
    )