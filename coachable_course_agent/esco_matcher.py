from coachable_course_agent.vector_store import get_embedding
import chromadb

def get_esco_chroma_collection():
    client = chromadb.Client()
    return client.get_or_create_collection(name="esco_skills")

def match_to_esco_semantic(skills: list[str], top_k: int = 1) -> list[dict]:
    collection = get_esco_chroma_collection()
    results = []

    for skill in skills:
        emb = get_embedding(skill)
        query_result = collection.query(query_embeddings=[emb], n_results=top_k)

        hits = query_result['metadatas'][0]
        documents = query_result['documents'][0]

        if hits:
            results.append({
                "input": skill,
                "matched_name": hits[0].get("preferredLabel", documents[0]),
                "uri": hits[0].get("conceptUri", None),
                "score": query_result["distances"][0][0]
            })
        else:
            results.append({
                "input": skill,
                "matched_name": None,
                "uri": None,
                "score": None
            })

    return results