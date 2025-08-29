import chromadb
from transformers import pipeline
from .utils import calculate_confidence_scores

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
    Returns courses with similarity scores for confidence display.
    Filters out previously rejected courses.
    """
    missing_skills = user_profile.get("missing_skills", [])
    missing_skills_str = [skill["preferredLabel"] for skill in missing_skills if skill.get("preferredLabel") != "N/A"]
    user_preferences_str = ', '.join(user_profile['preferences']['style'])

    user_goal_str = user_profile.get("goal", "")
    company_goal_str = user_profile.get("company_goal", "")
    query_text = f"{user_goal_str} {company_goal_str} {missing_skills_str} {user_preferences_str}"

    # Get rejected course IDs from feedback history
    feedback_log = user_profile.get("feedback_log", [])
    rejected_course_ids = set()
    for feedback in feedback_log:
        if feedback.get("feedback_type") == "reject":
            rejected_course_ids.add(feedback.get("course_id"))
    
    print(f"Filtering out {len(rejected_course_ids)} previously rejected courses: {rejected_course_ids}")

    # LangChain Chroma API: returns list of (Document, score) tuples
    # Get more results initially to account for filtering
    initial_k = min(top_n * 3, 50)  # Get 3x more to account for filtering
    results = vectorstore.similarity_search_with_score(query_text, k=initial_k)

    # Filter out rejected courses
    filtered_results = []
    for doc, score in results:
        course_id = doc.metadata.get("id")
        if course_id not in rejected_course_ids:
            filtered_results.append((doc, score))
        else:
            print(f"Filtered out rejected course: {doc.metadata.get('title', course_id)}")
    
    # Trim to requested number
    filtered_results = filtered_results[:top_n]

    # Extract scores and calculate confidence scores
    scores = [score for _, score in filtered_results]
    confidence_scores = calculate_confidence_scores(scores)

    # Extract metadata and add confidence scores
    courses = []
    for i, (doc, score) in enumerate(filtered_results):
        course = dict(doc.metadata)
        course['confidence_score'] = confidence_scores[i]
        
        # Store query components for "because" chips
        course['query_goal'] = user_goal_str
        course['query_missing_skills'] = missing_skills_str[:3]  # Top 3 missing skills
        course['query_preferences'] = user_preferences_str
        courses.append(course)
    
    return courses
