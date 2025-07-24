import os
import json
from datetime import datetime, timezone

PROFILE_DIR = "data/memory"

os.makedirs(PROFILE_DIR, exist_ok=True)

def _profile_path(user_id):
    return os.path.join(PROFILE_DIR, f"{user_id}.json")

def load_user_profile(user_id):
    path = _profile_path(user_id)
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    else:
        return {
            "user_id": user_id,
            "blurb": "",
            "headline": "",
            "goal": "",
            "known_skills": [],
            "missing_skills": [],
            "preferences": {
                "format": [],
                "style": [],
                "avoid_styles": []
            },
            "feedback_log": []
        }

def update_user_profile(user_id, profile):
    path = _profile_path(user_id)
    with open(path, 'w') as f:
        json.dump(profile, f, indent=2)

def log_feedback(user_id, course_id, feedback_type, reason):
    profile = load_user_profile(user_id)
    entry = {
        "course_id": course_id,
        "feedback_type": feedback_type,
        "reason": reason,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    profile.setdefault("feedback_log", []).append(entry)
    update_user_profile(user_id, profile)

def update_preferences(user_id, new_prefs):
    profile = load_user_profile(user_id)
    prefs = profile.setdefault("preferences", {})

    for key, values in new_prefs.items():
        if key in prefs:
            current = set(prefs.get(key, []))
            updated = current.union(set(values))
            prefs[key] = list(updated)

    update_user_profile(user_id, profile)
