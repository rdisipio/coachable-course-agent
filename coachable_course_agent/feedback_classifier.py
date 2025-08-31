"""
Feedback Classification Module
Classifies user feedback into specific categories using LLM for better accuracy
"""

import json
from typing import Dict, Optional
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()


def _fallback_keyword_classification(feedback_text: str, feedback_type: str) -> Dict[str, str]:
    """Fallback keyword-based classification when LLM is unavailable"""
    if feedback_type == "approve":
        return {
            "category": "positive",
            "subcategory": "approved", 
            "confidence": "high",
            "reasoning": "User approved the recommendation"
        }
    
    if not feedback_text or feedback_text.strip() == "":
        return {
            "category": "unknown",
            "subcategory": "no_reason",
            "confidence": "low", 
            "reasoning": "No feedback text provided"
        }
    
    # Convert to lowercase for analysis
    text = feedback_text.lower().strip()
    
    # Define keyword patterns for each category
    friction_keywords = [
        "too long", "time consuming", "takes too much time", "too many hours",
        "don't have time", "too intensive", "not relevant", "irrelevant", 
        "doesn't match", "off topic", "not what i need", "waste of time",
        "too difficult", "too advanced", "too basic", "wrong level",
        "not interested", "no interest", "don't want"
    ]
    
    credibility_keywords = [
        "certification", "not certified", "not accredited", "provider", 
        "don't trust", "unreliable", "unknown provider", "questionable",
        "credentials", "diploma", "certificate", "accreditation",
        "not recognized", "bureaucratic", "paperwork"
    ]
    
    better_way_keywords = [
        "too broad", "too general", "not specific", "not practical",
        "too theoretical", "not hands-on", "need more specific", "vague",
        "too abstract", "prefer different approach", "better way",
        "different method", "more focused", "more targeted"
    ]
    
    negative_impact_keywords = [
        "doesn't align", "not aligned", "wrong direction", "off track",
        "doesn't cover", "missing skills", "wrong skills", "not helpful",
        "contradicts goals", "opposite direction", "doesn't fit goals",
        "not what i want to learn", "different path"
    ]
    
    # Score each category based on keyword matches
    scores = {
        "friction": _calculate_keyword_score(text, friction_keywords),
        "credibility": _calculate_keyword_score(text, credibility_keywords), 
        "better_way": _calculate_keyword_score(text, better_way_keywords),
        "negative_impact": _calculate_keyword_score(text, negative_impact_keywords)
    }
    
    # Find the category with highest score
    max_score = max(scores.values())
    
    if max_score == 0:
        return {
            "category": "other",
            "subcategory": "unclassified",
            "confidence": "low",
            "reasoning": "Could not classify based on available keywords"
        }
    
    # Get the category with highest score
    top_category = max(scores, key=scores.get)
    
    # Determine confidence based on score
    confidence = "high" if max_score >= 2 else "medium" if max_score >= 1 else "low"
    
    # Create detailed response
    category_descriptions = {
        "friction": "Course perceived as not relevant or too time-consuming",
        "credibility": "Concerns about provider credibility or certification value", 
        "better_way": "Course too broad, theoretical, or not practical enough",
        "negative_impact": "Course doesn't align with goals or cover needed skills"
    }
    
    return {
        "category": top_category,
        "subcategory": feedback_type,
        "confidence": confidence,
        "reasoning": category_descriptions[top_category],
        "keyword_scores": scores,
        "original_feedback": feedback_text
    }


def classify_feedback(feedback_text: str, feedback_type: str) -> Dict[str, str]:
    """
    Classify user feedback using LLM for better accuracy and context understanding.
    Falls back to keyword-based classification if LLM is unavailable.
    
    Args:
        feedback_text: The user's written feedback/reason
        feedback_type: The feedback type (approve, adjust, reject, suggest)
    
    Returns:
        Dict with classification results including category and confidence
    """
    # Handle obvious positive feedback first
    if feedback_type == "approve":
        return {
            "category": "positive",
            "subcategory": "approved", 
            "confidence": "high",
            "reasoning": "User approved the recommendation",
            "method": "rule_based"
        }
    
    # Handle empty feedback
    if not feedback_text or feedback_text.strip() == "":
        return {
            "category": "unknown",
            "subcategory": "no_reason",
            "confidence": "low", 
            "reasoning": "No feedback text provided",
            "method": "rule_based"
        }
    
    try:
        # Try LLM classification first
        return _llm_classify_feedback(feedback_text, feedback_type)
    except Exception as e:
        print(f"LLM classification failed, falling back to keywords: {e}")
        # Fall back to keyword-based classification
        result = _fallback_keyword_classification(feedback_text, feedback_type)
        result["method"] = "keyword_fallback"
        return result


def _llm_classify_feedback(feedback_text: str, feedback_type: str) -> Dict[str, str]:
    """Use LLM to classify feedback with better context understanding"""
    
    # Initialize LLM
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1, api_key=os.getenv("GROQ_API_KEY"))
    
    # Create classification prompt
    prompt_template = """
You are an expert at analyzing user feedback about online course recommendations. 
Classify the following feedback into one of these categories:

**Categories:**
- **friction**: User finds the course not relevant, too time-consuming, too difficult/easy, or generally not interested
- **credibility**: User has concerns about the course provider, certification value, accreditation, or trustworthiness
- **better_way**: User wants something more specific, practical, hands-on, or has a preferred learning approach
- **negative_impact**: User believes the course doesn't align with their goals or would not help their career
- **positive**: User likes the recommendation (even if providing minor adjustments)
- **other**: Doesn't clearly fit the above categories

**User Feedback:**
Feedback Type: {feedback_type}
User's Reason: "{feedback_text}"

Analyze the feedback and respond with ONLY a valid JSON object in this exact format:
{{
    "category": "one of the categories above",
    "confidence": "high|medium|low",
    "reasoning": "brief explanation of why this category was chosen",
    "key_phrases": ["list", "of", "key", "phrases", "that", "influenced", "classification"]
}}
"""
    
    prompt = PromptTemplate.from_template(prompt_template)
    formatted_prompt = prompt.format(feedback_text=feedback_text, feedback_type=feedback_type)
    
    # Get LLM response
    response = llm.invoke(formatted_prompt)
    
    # Parse JSON response
    try:
        result = json.loads(response.content.strip())
        
        # Add metadata
        result["subcategory"] = feedback_type
        result["original_feedback"] = feedback_text
        result["method"] = "llm"
        
        # Validate required fields
        required_fields = ["category", "confidence", "reasoning"]
        if all(field in result for field in required_fields):
            return result
        else:
            raise ValueError("Missing required fields in LLM response")
            
    except (json.JSONDecodeError, ValueError) as e:
        raise Exception(f"Failed to parse LLM response: {e}")


def _calculate_keyword_score(text: str, keywords: list) -> int:
    """Calculate score based on keyword matches in text"""
    score = 0
    for keyword in keywords:
        if keyword in text:
            score += 1
            # Give extra weight to exact phrase matches
            if keyword.count(" ") > 0:  # Multi-word phrases get bonus
                score += 0.5
    return score


def get_feedback_insights(user_id: str, feedback_log: list) -> Dict:
    """
    Analyze all feedback for a user and provide insights
    
    Args:
        user_id: User identifier
        feedback_log: List of feedback entries
    
    Returns:
        Dict with feedback patterns and insights
    """
    if not feedback_log:
        return {"total_feedback": 0, "insights": "No feedback available"}
    
    categories = {"friction": 0, "credibility": 0, "better_way": 0, "negative_impact": 0, "positive": 0, "other": 0}
    detailed_feedback = []
    
    for entry in feedback_log:
        feedback_text = entry.get("reason", "")
        feedback_type = entry.get("feedback_type", "")
        
        classification = classify_feedback(feedback_text, feedback_type)
        categories[classification["category"]] += 1
        detailed_feedback.append(classification)
    
    total = len(feedback_log)
    
    # Generate insights
    insights = []
    if categories["friction"] > total * 0.3:
        insights.append("User often finds courses too time-consuming or irrelevant")
    if categories["credibility"] > total * 0.3:
        insights.append("User has concerns about course providers and certification value")
    if categories["better_way"] > total * 0.3:
        insights.append("User prefers more specific and practical courses")
    if categories["negative_impact"] > total * 0.3:
        insights.append("User feedback suggests courses don't align well with their goals")
    
    return {
        "total_feedback": total,
        "category_breakdown": categories,
        "insights": insights if insights else ["No clear patterns detected yet"],
        "detailed_classifications": detailed_feedback
    }
