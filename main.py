import json

from coachable_course_agent.load_data import load_courses, load_esco_skills
from coachable_course_agent.memory_store import load_user_profile, update_user_profile
from coachable_course_agent.feedback_processor import process_feedback
from coachable_course_agent.vector_store import initialize_chroma, add_courses_to_chroma, query_similar_courses
from coachable_course_agent.agent_runner import create_course_agent
from coachable_course_agent.justifier_chain import justify_recommendations

# Load course catalog and ESCO skills
courses = load_courses("data/course_catalog_esco.json")
esco_skills = load_esco_skills("data/esco/skills_en.csv")

# Initialize ChromaDB and populate course embeddings
chroma_collection = initialize_chroma()
add_courses_to_chroma(chroma_collection, courses)

# Load or initialize user profile
user_id = "julia"
user_profile = load_user_profile(user_id)

# Step 1: Retrieve top N courses from vector store based on user profile
retrieved_courses = query_similar_courses(chroma_collection, user_profile, top_n=10)

# Step 2: Use the LLM to justify and refine top 3 recommendations
recommendations = justify_recommendations(user_profile, retrieved_courses)

# Collect feedback on each course
for rec in recommendations:
    print(f"\nSuggested: {rec['title']}")
    print("Why: ", rec["justification"])
    feedback = input("Feedback? (approve / adjust / reject / suggest): ")
    reason = input("Reason (optional): ")
    process_feedback(user_id, rec["course_id"], feedback, reason)

print("\nThanks for helping improve the recommendations!")
