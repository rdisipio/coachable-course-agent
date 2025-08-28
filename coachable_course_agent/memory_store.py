
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
                "better_way": "🔄 Better Way (too broad/theoretical)",
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

def add_skill(user_id, skill_name, skill_type="known", esco_vectorstore=None):
    """Add a skill to user's profile using ESCO matching
    
    Args:
        user_id: User identifier
        skill_name: Name of the skill to add
        skill_type: "known" for known_skills or "missing" for missing_skills
        esco_vectorstore: ESCO Chroma collection for semantic matching
    """
    memory = load_user_profile(user_id)
    
    if not memory:
        return "No user profile found", format_memory_editor_display(user_id), ""
    
    if not skill_name or not skill_name.strip():
        return "Please enter a skill name", format_memory_editor_display(user_id), ""
    
    skill_name = skill_name.strip()
    
    # Find the most similar ESCO skill
    if esco_vectorstore:
        try:
            results = esco_vectorstore.similarity_search(skill_name, k=1)
            if results:
                top_result = results[0]
                skill_obj = {
                    "preferredLabel": top_result.metadata.get("preferredLabel", skill_name),
                    "conceptUri": top_result.metadata.get("conceptUri", f"custom:{skill_name.lower().replace(' ', '_')}"),
                    "description": top_result.metadata.get("description", "ESCO-matched skill")
                }
                matched_label = skill_obj["preferredLabel"]
            else:
                # Fallback if no ESCO match found
                skill_obj = {
                    "preferredLabel": skill_name,
                    "conceptUri": f"custom:{skill_name.lower().replace(' ', '_')}",
                    "description": "User-added skill (no ESCO match)"
                }
                matched_label = skill_name
        except Exception as e:
            print(f"ESCO matching failed for '{skill_name}': {e}")
            # Fallback if ESCO search fails
            skill_obj = {
                "preferredLabel": skill_name,
                "conceptUri": f"custom:{skill_name.lower().replace(' ', '_')}",
                "description": "User-added skill (ESCO search failed)"
            }
            matched_label = skill_name
    else:
        # Fallback if no ESCO vectorstore provided
        skill_obj = {
            "preferredLabel": skill_name,
            "conceptUri": f"custom:{skill_name.lower().replace(' ', '_')}",
            "description": "User-added skill"
        }
        matched_label = skill_name
    
    # Determine target list
    target_list = "known_skills" if skill_type == "known" else "missing_skills"
    skills_list = memory.get(target_list, [])
    
    # Check if skill already exists (by ESCO URI or label)
    existing_skill = None
    for skill in skills_list:
        if (skill.get("conceptUri") == skill_obj["conceptUri"] or 
            skill.get("preferredLabel", "").lower() == matched_label.lower()):
            existing_skill = skill
            break
    
    if existing_skill:
        return f"Skill '{matched_label}' already exists in {target_list.replace('_', ' ')}", format_memory_editor_display(user_id), ""
    
    # Check if it exists in the other list
    other_list = "missing_skills" if skill_type == "known" else "known_skills"
    other_skills = memory.get(other_list, [])
    
    for skill in other_skills:
        if (skill.get("conceptUri") == skill_obj["conceptUri"] or 
            skill.get("preferredLabel", "").lower() == matched_label.lower()):
            return f"Skill '{matched_label}' already exists in {other_list.replace('_', ' ')}. Remove it there first if you want to move it.", format_memory_editor_display(user_id), ""
    
    # Add the skill
    skills_list.append(skill_obj)
    memory[target_list] = skills_list
    update_user_profile(user_id, memory)
    
    list_name = "known skills" if skill_type == "known" else "learning goals"
    
    # Show whether it was ESCO-matched or custom
    if matched_label != skill_name:
        return f"Added '{matched_label}' (ESCO match for '{skill_name}') to {list_name}", format_memory_editor_display(user_id), ""
    else:
        return f"Added '{matched_label}' to {list_name}", format_memory_editor_display(user_id), ""
