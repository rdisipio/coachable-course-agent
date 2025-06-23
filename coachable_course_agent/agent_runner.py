from langchain.agents import Tool
from langchain.agents import initialize_agent, AgentType, AgentExecutor, AgentOutputParser
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain.agents import create_react_agent
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

from coachable_course_agent.vector_store import query_similar_courses
from coachable_course_agent.recommendation_prompt import base_prompt

load_dotenv()

# Initialize LLM
llm = ChatGroq(
    model="llama3-70b-8192", 
    temperature=0.7, 
    api_key=os.getenv("GROQ_API_KEY")
)

# Define tool: query vector store
def vector_search_tool(input: dict):
    chroma = input["chroma"]
    profile = input["profile"]
    courses = query_similar_courses(chroma, profile, top_n=10)

    formatted = "\n".join([
        f"- {c['title']} ({c['provider']}) | Level: {c.get('level', 'N/A')} | Duration: {c.get('duration_hours', '?')}h | Skills: {c.get('skills', '')} | ID: {c.get('id')}"
        for c in courses
    ])
    return f"Here are the top courses based on the user's profile and preferences:\n{formatted}"


# Add tools
tools = [
    Tool(
        name="VectorSearchCourses",
        func=vector_search_tool,
        description="Searches courses similar to user profile using vector embeddings"
    )
]

# Create agent with custom prompt
def create_course_agent():
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Use the available tools to retrieve relevant courses."),
        MessagesPlaceholder("agent_scratchpad")
    ])

    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

    return AgentExecutor(agent=agent, tools=tools, verbose=True)
    