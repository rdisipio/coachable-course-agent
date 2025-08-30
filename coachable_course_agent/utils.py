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

def clean_provider_name(provider):
    """Clean provider name by removing duplicate letters and formatting properly"""
    if not provider:
        return ""
    
    # Fix the double letter issue at the beginning: if first two letters are same uppercase, remove first
    # e.g., "UUniversity" → "University", "IIBM" → "IBM", "OO.P." → "O.P."
    cleaned = re.sub(r'^([A-Z])\1', r'\1', provider)
    
    # Fix the double letter issue (e.g., "D Duke University" → "Duke University")
    # Pattern: single letter, space, then same letter followed by word
    cleaned = re.sub(r'^([A-Z])\s+\1([A-Z][a-z])', r'\2', cleaned)
    
    # Additional cleanup patterns
    cleaned = re.sub(r'^([A-Z])\s+([A-Z])', r'\2', cleaned)  # "D Duke" → "Duke"
    
    # Remove duplicate words (e.g., "Arizona State University Arizona State" → "Arizona State University")
    words = cleaned.split()
    if len(words) > 3:  # Only check for duplicates in longer names
        # Check if the name is duplicated
        mid = len(words) // 2
        first_half = ' '.join(words[:mid])
        second_half = ' '.join(words[mid:])
        if first_half == second_half:
            cleaned = first_half
        else:
            # Check for trailing duplicates (e.g., "University Name University Name")
            # Look for repeating patterns at the end
            for i in range(1, min(4, len(words))):  # Check up to 3-word repetitions
                if len(words) >= i * 2:
                    suffix = words[-i:]
                    prefix = words[-(i*2):-i]
                    if suffix == prefix:
                        cleaned = ' '.join(words[:-i])
                        break
    
    # Clean up specific patterns that often appear
    # Remove course-specific suffixes that got mixed into provider names
    course_suffixes = [
        r'\s+(Introduction To|Skills|Fundamentals|Certificate|Course|Program).*$',
        r'\s+(And|The|Of|For|In|With|To|From)$',  # Trailing prepositions
        r'\s+[A-Z]$'  # Single trailing letters
    ]
    
    for pattern in course_suffixes:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    return cleaned.strip()

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
