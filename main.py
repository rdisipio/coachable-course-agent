from agents.recommender_agent import get_recommendations
from utils.load_data import load_courses, load_esco_skills
from utils.memory_store import load_user_profile, update_user_profile
from utils.feedback_processor import process_feedback
from utils.vector_store import initialize_chroma, add_courses_to_chroma, query_similar_courses

# Load course catalog and ESCO skills
courses = load_courses("data/course_catalog_esco.json")
esco_skills = load_esco_skills("data/esco/skills_en.csv")

# Initialize ChromaDB and populate course embeddings
chroma_collection = initialize_chroma()
add_courses_to_chroma(chroma_collection, courses)

# Load or initialize user profile
user_id = "julia"
user_profile = load_user_profile(user_id)

# Query top-N similar courses based on user's missing skills and preferences
similar_courses = query_similar_courses(chroma_collection, user_profile, top_n=10)

# Get refined recommendations from the agent
recommended_courses = get_recommendations(user_profile, similar_courses, esco_skills)

# Show recommendations and get feedback (stub)
for course in recommended_courses:
    print(f"Suggested: {course['title']} ({course['provider']})")
    print("Why: ", course["justification"])
    feedback = input("Feedback? (approve / adjust / reject / suggest): ")
    reason = input("Reason (optional): ")
    process_feedback(user_id, course["id"], feedback, reason)

# Save updated profile
update_user_profile(user_id, user_profile)

print("\nThanks for helping improve the recommendations!")
