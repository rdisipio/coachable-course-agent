import json

from coachable_course_agent.load_data import load_courses, load_esco_skills
from coachable_course_agent.memory_store import load_user_profile, update_user_profile
from coachable_course_agent.feedback_processor import process_feedback
from coachable_course_agent.vector_store import initialize_chroma, add_courses_to_chroma, query_similar_courses
from coachable_course_agent.agent_runner import create_course_agent
from coachable_course_agent.recommendation_prompt import base_prompt

# Load course catalog and ESCO skills
courses = load_courses("data/course_catalog_esco.json")
esco_skills = load_esco_skills("data/esco/skills_en.csv")

# Initialize ChromaDB and populate course embeddings
chroma_collection = initialize_chroma()
add_courses_to_chroma(chroma_collection, courses)

# Load or initialize user profile
user_id = "julia"
user_profile = load_user_profile(user_id)

# Create the LangChain agent
agent = create_course_agent()

# Run the agent to get recommendation response
instructions = base_prompt.format(
    goal=user_profile["goal"],
    known_skills=", ".join(user_profile["known_skills"]),
    missing_skills=", ".join(user_profile["missing_skills"]),
    format=", ".join(user_profile["preferences"]["format"]),
    style=", ".join(user_profile["preferences"]["style"]),
    avoid_styles=", ".join(user_profile["preferences"].get("avoid_styles", [])),
    feedback_log=json.dumps(user_profile.get("feedback_log", [])[-3:], indent=2)
)

input_payload = {
    "goal": user_profile["goal"],
    "known_skills": ", ".join(user_profile["known_skills"]),
    "missing_skills": ", ".join(user_profile["missing_skills"]),
    "format": ", ".join(user_profile["preferences"]["format"]),
    "style": ", ".join(user_profile["preferences"]["style"]),
    "avoid_styles": ", ".join(user_profile["preferences"].get("avoid_styles", [])),
    "feedback_log": json.dumps(user_profile.get("feedback_log", [])[-3:], indent=2),
    "instruction": instructions,
}

response = agent.run(input_payload)

# Parse response (assume it's valid JSON for now)
recommendations = json.loads(response)

# Collect feedback on each course
for rec in recommendations:
    print(f"\nSuggested: {rec['title']}")
    print("Why: ", rec["justification"])
    feedback = input("Feedback? (approve / adjust / reject / suggest): ")
    reason = input("Reason (optional): ")
    process_feedback(user_id, rec["course_id"], feedback, reason)

print("\nThanks for helping improve the recommendations!")
