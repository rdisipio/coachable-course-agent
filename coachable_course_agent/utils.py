import json
import re

def extract_json_block(text: str) -> dict:
    try:
        # Try raw parse
        return json.loads(text)
    except json.JSONDecodeError:
        # Fallback: extract JSON array or object from LLM text
        match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        raise

def calculate_confidence_scores(scores):
    """
    Convert distance scores to normalized confidence scores (0-1 range).
    Lower distance scores indicate better matches, so we invert and normalize.
    
    Args:
        scores: List of distance scores from similarity search
        
    Returns:
        List of confidence scores where 1.0 = best match, 0.1+ = worst match
    """
    if not scores:
        return []
    
    min_score = min(scores)
    max_score = max(scores)
    score_range = max_score - min_score if max_score > min_score else 1
    
    confidence_scores = []
    for score in scores:
        # Normalize score to 0-1 range where 1 is best match
        # For distance metrics, lower scores are better, so we invert
        if score_range > 0:
            normalized_score = 1 - ((score - min_score) / score_range)
        else:
            normalized_score = 1.0  # All scores are the same
        
        # Ensure confidence is between 0.1 and 1.0 for better UX
        confidence_score = max(0.1, min(1.0, normalized_score))
        confidence_scores.append(confidence_score)
    
    return confidence_scores
