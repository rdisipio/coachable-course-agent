
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


# Memory Editor UI Functions
# =========================

def format_memory_editor_display(user_id):
    """Load and display user memory in a readable format for the memory editor"""
    if not user_id:
        return "No user profile loaded."
    
    profile = load_user_profile(user_id)
    
    goal = profile.get("goal", "No goal set")
    skills = profile.get("known_skills", [])
    feedback_log = profile.get("feedback_log", [])
    feedback_count = len(feedback_log)
    
    # Format skills list
    if skills:
        formatted_skills = []
        for skill in skills:
            if isinstance(skill, dict):
                skill_name = skill.get('preferredLabel', skill.get('name', str(skill)))
            else:
                skill_name = str(skill)
            formatted_skills.append(f"• {skill_name}")
        skills_text = "\n".join(formatted_skills)
    else:
        skills_text = "No skills recorded"
    
    # Analyze feedback classifications if available
    feedback_insights = ""
    if feedback_count > 0:
        # Count classifications
        classifications = {}
        for entry in feedback_log:
            if "classification" in entry:
                category = entry["classification"].get("category", "unclassified")
                classifications[category] = classifications.get(category, 0) + 1
        
        if classifications:
            feedback_insights = "\n\n**📊 Feedback Patterns:**\n"
            category_labels = {
                "friction": "🚫 Friction (time/relevance issues)",
                "credibility": "� Credibility (provider/certification concerns)", 
                "better_way": "🎯 Better Way (too broad/theoretical)",
                "negative_impact": "❌ Negative Impact (misaligned goals)",
                "positive": "✅ Positive feedback",
                "other": "❓ Other/Unclassified"
            }
            
            for category, count in sorted(classifications.items(), key=lambda x: x[1], reverse=True):
                if count > 0:
                    label = category_labels.get(category, f"📝 {category.title()}")
                    feedback_insights += f"{label}: {count}\n"
    
    memory_display = f"""### Current Memory Profile

**🎯 Goal:**
{goal}

**🔧 Known Skills ({len(skills)}):**
{skills_text}

**📝 Feedback Log:**
{feedback_count} feedback entries recorded{feedback_insights}
    """
    
    return memory_display


def update_goal_dialog(user_id):
    """Return current goal for editing"""
    if not user_id:
        return ""
    
    profile = load_user_profile(user_id)
    return profile.get("goal", "")


def save_updated_goal(user_id, new_goal):
    """Save the updated goal to user's memory"""
    if not new_goal or not new_goal.strip():
        return "Please enter a goal before saving"
    
    memory = load_user_profile(user_id)
    memory["goal"] = new_goal.strip()
    update_user_profile(user_id, memory)
    
    return f"Goal updated successfully!"


def remove_skill(user_id, skill_to_remove):
    """Remove a skill from user's memory"""
    if not skill_to_remove or not skill_to_remove.strip():
        return "Please enter a skill to remove", format_memory_editor_display(user_id), ""
    
    memory = load_user_profile(user_id)
    
    if not memory or "known_skills" not in memory:
        return "No skills found to remove", format_memory_editor_display(user_id), ""
    
    skills = memory["known_skills"]
    original_count = len(skills)
    
    # Remove skills that match (case-insensitive)
    skill_to_remove_lower = skill_to_remove.strip().lower()
    updated_skills = []
    
    for skill in skills:
        if isinstance(skill, dict):
            # Check preferredLabel for match
            skill_name = skill.get('preferredLabel', skill.get('name', str(skill)))
        else:
            skill_name = str(skill)
        
        if skill_name.lower() != skill_to_remove_lower:
            updated_skills.append(skill)
    
    removed_count = original_count - len(updated_skills)
    
    if removed_count > 0:
        memory["known_skills"] = updated_skills
        update_user_profile(user_id, memory)
        return f"Removed {removed_count} skill(s) matching '{skill_to_remove}'", format_memory_editor_display(user_id), ""
    else:
        return f"No skill found matching '{skill_to_remove}'", format_memory_editor_display(user_id), ""


def clear_feedback_log(user_id):
    """Clear user's feedback log"""
    memory = load_user_profile(user_id)
    
    if not memory:
        return "No user profile found", format_memory_editor_display(user_id)
    
    feedback_count = len(memory.get("feedback_log", []))
    memory["feedback_log"] = []
    update_user_profile(user_id, memory)
    
    return f"Cleared {feedback_count} feedback entries", format_memory_editor_display(user_id)
