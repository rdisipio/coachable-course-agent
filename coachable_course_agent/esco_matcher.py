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
    }
    
    for skill in skills:
        skill_lower = skill.lower().strip()
        
        # Check if this is a modern term we should map
        mapped_skill = modern_term_mappings.get(skill_lower)
        if mapped_skill:
            # Search for the mapped term instead
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

        if results:
            # Look for exact or close matches first
            best_match = None
            search_lower = search_term.lower()
            
            for result in results:
                label = result.metadata.get("preferredLabel", "").lower()
                
                # Check for exact match
                if label == search_lower:
                    best_match = result
                    break
                
                # Check if the search term is contained in the label or vice versa
                if search_lower in label or label in search_lower:
                    # Prefer shorter labels for better specificity
                    if best_match is None or len(label) < len(best_match.metadata.get("preferredLabel", "")):
                        best_match = result
            
            # If no close match found, use semantic similarity but filter out poor matches
            if best_match is None:
                top_result = results[0]
                label = top_result.metadata.get("preferredLabel", "").lower()
                
                # Skip clearly unrelated matches
                bad_patterns = ['liaise', 'distribution', 'channel', 'assume responsibility']
                if not any(bad_word in label for bad_word in bad_patterns):
                    best_match = top_result
            
            if best_match:
                matches.append({
                    "raw_skill": skill,
                    "preferredLabel": best_match.metadata.get("preferredLabel", "N/A"),
                    "conceptUri": best_match.metadata.get("conceptUri", "N/A"),
                    "description": best_match.metadata.get('page_content', "N/A")
                })
        else:
            matches.append({
                "raw_skill": skill,
                "preferredLabel": None,
                "conceptUri": None,
                "description": None
            })

    return [m for m in matches if m["preferredLabel"] != "N/A"]

