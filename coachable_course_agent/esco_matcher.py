from coachable_course_agent.vector_store import get_embedding

def match_to_esco(query, vectorstore, top_k=10):
    results = vectorstore.similarity_search(query, k=top_k)
    if not results:
        return "No similar skills found."
    return "\n".join([f"{r.metadata['label']}: {r.page_content}" for r in results])
