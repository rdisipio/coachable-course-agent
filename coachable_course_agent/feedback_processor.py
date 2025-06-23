from .memory_store import load_user_profile, update_user_profile
from datetime import datetime, timezone

def process_feedback(user_id, course_id, feedback_type, reason):
    profile = load_user_profile(user_id)
    entry = {
        "course_id": course_id,
        "feedback_type": feedback_type,
        "reason": reason,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    profile.setdefault("feedback_log", []).append(entry)
    update_user_profile(user_id, profile)
