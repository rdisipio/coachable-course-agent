from coachable_course_agent.vector_store import get_embedding

def match_to_esco(skills: list[str], vectorstore, top_k=10):
    matches = []
    for skill in skills:
        # Perform semantic search for each skill string
        try:
            results = vectorstore.similarity_search(skill, k=top_k)
        except Exception as e:
            print(f"[ERROR] Skill '{skill}' failed search: {e}")
            continue

        if results:
            top_result = results[0]
            matches.append({
                "raw_skill": skill,
                "preferredLabel": top_result.metadata.get("preferredLabel", "N/A"),
                "conceptUri": top_result.metadata.get("conceptUri", "N/A"),
                "description": top_result.metadata.get('page_content', "N/A")
            })
        else:
            matches.append({
                "raw_skill": skill,
                "preferredLabel": None,
                "conceptUri": None,
                "description": None
            })

    return [m for m in matches if m["preferredLabel"] != "N/A"]

