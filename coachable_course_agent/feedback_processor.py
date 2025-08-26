from .memory_store import load_user_profile, update_user_profile
from .feedback_classifier import classify_feedback
from datetime import datetime, timezone

def process_feedback(user_id, course_id, feedback_type, reason):
    profile = load_user_profile(user_id)
    
    # Classify the feedback
    classification = classify_feedback(reason, feedback_type)
    
    entry = {
        "course_id": course_id,
        "feedback_type": feedback_type,
        "reason": reason,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "classification": classification
    }
    profile.setdefault("feedback_log", []).append(entry)
    update_user_profile(user_id, profile)
