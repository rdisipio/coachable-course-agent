from coachable_course_agent.vector_store import get_embedding

def match_to_esco(skills: list[str], vectorstore, top_k=10):
    matches = []
    
    # Define mappings for modern terms that don't exist in ESCO
    modern_term_mappings = {
        'llm': 'machine learning',
        'large language model': 'machine learning',
        'large language models': 'machine learning',
        'transformer': 'machine learning',
        'gpt': 'machine learning',
        'bert': 'machine learning',
        'responsible ai': 'principles of artificial intelligence',
        'ethical ai': 'principles of artificial intelligence',
        'ai ethics': 'principles of artificial intelligence',
        'mlops': 'machine learning',
        'devops': 'software engineering',
        'kubernetes': 'software engineering',
        'docker': 'software engineering',
        'react': 'software engineering',
        'node.js': 'software engineering',
        'nodejs': 'software engineering',
        'ux design': 'user experience design',
        'ui design': 'user interface design',
        'user experience': 'user experience design',
        'user interface': 'user interface design',
    }
    
    for skill in skills:
        skill_lower = skill.lower().strip()
        
        # Check if this is a modern term we should map
        mapped_skill = modern_term_mappings.get(skill_lower)
        if mapped_skill:
            search_term = mapped_skill
            print(f"[INFO] Mapping '{skill}' to '{mapped_skill}' for ESCO search")
        else:
            search_term = skill
        
        # Perform semantic search for each skill string
        try:
            results = vectorstore.similarity_search(search_term, k=top_k)
        except Exception as e:
            print(f"[ERROR] Skill '{skill}' failed search: {e}")
            continue


        import random
        if results:
            # Get top 3 results (if available)
            top_results = results[:3] if len(results) >= 3 else results
            # Try to get scores if available
            scores = []
            for r in top_results:
                score = None
                if hasattr(r, 'score'):
                    score = r.score
                elif isinstance(r, tuple) and len(r) == 2:
                    score = r[1]
                    r = r[0]
                scores.append(score)
            # If scores are available and valid, use threshold logic
            threshold = 0.15
            if scores and scores[0] is not None and scores[1] is not None:
                # Scores are usually distance, so lower is better
                diff = scores[1] - scores[0]
                if diff > threshold:
                    chosen = top_results[0]
                else:
                    chosen = random.choice(top_results)
            else:
                chosen = random.choice(top_results)
            # If tuple, get doc
            if isinstance(chosen, tuple):
                chosen = chosen[0]
            matches.append({
                "raw_skill": skill,
                "preferredLabel": chosen.metadata.get("preferredLabel", "N/A"),
                "conceptUri": chosen.metadata.get("conceptUri", "N/A"),
                "description": chosen.metadata.get('page_content', "N/A")
            })
        # If no matches found, skip

    return [m for m in matches if m["preferredLabel"] != "N/A"]

