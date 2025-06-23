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
        collection.add(
            documents=[text],
            embeddings=[embedding],
            ids=[course["id"]],
            metadatas=[course]
        )

def query_similar_courses(collection, user_profile, top_n=10):
    query_text = f"{user_profile['goal']} {', '.join(user_profile['missing_skills'])} {', '.join(user_profile['preferences']['style'])}"
    query_embedding = get_embedding(query_text)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_n
    )
    return [hit for hit in results["metadatas"][0]]
