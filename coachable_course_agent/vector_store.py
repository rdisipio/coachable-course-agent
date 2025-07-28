import chromadb
from transformers import pipeline

# Create HuggingFace sentence embedding pipeline
embedding_pipeline = pipeline("feature-extraction", model="sentence-transformers/all-MiniLM-L6-v2", tokenizer="sentence-transformers/all-MiniLM-L6-v2")

def get_embedding(text):
    # Extract and average embeddings
    output = embedding_pipeline(text, truncation=True, padding=True, return_tensors="pt")
    return [float(x) for x in output[0][0]]  # mean-pooled first token

def initialize_chroma():
    client = chromadb.Client()
    collection = client.get_or_create_collection(name="courses")
    return collection

def add_courses_to_chroma(collection, courses):
    for course in courses:
        text = f"{course['title']} {', '.join([s['name'] for s in course['skills']])}"
        embedding = get_embedding(text)
        metadata = {
            "id": course["id"],
            "title": course["title"],
            "provider": course["provider"],
            "skills": ", ".join([s["name"] for s in course["skills"]]),
            "duration_hours": course.get("duration_hours", 0),
            "level": course.get("level", "Unknown"),
            "format": course.get("format", "Unknown"),
            "url": course.get("url", "")
        }
        collection.add(
            documents=[text],
            embeddings=[embedding],
            ids=[course["id"]],
            metadatas=[metadata]
        )

def query_similar_courses(vectorstore, user_profile, top_n=10):
    """
    Query the vector store for courses similar to the user's profile.
    Uses the user's goal, missing skills, and preferences to create a query embedding.
    Missing skills is a list of dictionary items with 'preferredLabel' and 'conceptUri'.
    """
    missing_skills = user_profile.get("missing_skills", [])
    missing_skills_str = [skill["preferredLabel"] for skill in missing_skills if skill.get("preferredLabel") != "N/A"]
    user_preferences_str = ', '.join(user_profile['preferences']['style'])

    user_goal_str = user_profile.get("goal", "")
    company_goal_str = user_profile.get("company_goal", "")
    query_text = f"{user_goal_str} {company_goal_str} {missing_skills_str} {user_preferences_str}"

    # LangChain Chroma API: returns list of Documents
    results = vectorstore.similarity_search(query_text, k=top_n)

    # Extract metadata from Documents
    courses = [doc.metadata for doc in results]
    
    return courses
