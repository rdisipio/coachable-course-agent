import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from coachable_course_agent.memory_store import load_user_profile
from coachable_course_agent.feedback_processor import process_feedback
from coachable_course_agent.vector_store import query_similar_courses
from coachable_course_agent.justifier_chain import justify_recommendations

from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
courses_collection = Chroma(
        persist_directory="data/courses_chroma",
        embedding_function=embedding_model
    )

# Load or initialize user profile
user_id = input("🆔 What is your user ID? ").strip()
user_profile = load_user_profile(user_id)

# Step 1: Retrieve top N courses from vector store based on user profile
retrieved_courses = query_similar_courses(courses_collection, user_profile, top_n=10)

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
