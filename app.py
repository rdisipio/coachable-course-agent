# ===========================================================
#   Coachable Course Agent — Design Manifesto
#
#   • From clever demo ➜ to principled foundation
#   • Align what’s technically possible with what’s humanly meaningful
#   • Build with Google People+AI guidelines as a compass
#   • Leave space for UX voices to shape the experience
# ===========================================================


import os
import json
import subprocess
import tarfile
import gradio as gr
from datetime import datetime
from huggingface_hub import hf_hub_download

MEMORY_DIR = "data/memory"
COURSES_PATH = "data/course_catalog_esco.json"
GOALS = "Support cross-functional collaboration, and accelerate internal mobility."

from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# ---------- Download and Extract Prebuilt ChromaDB ----------
def fetch_and_extract(repo_id, filename, target_dir):
    if not os.path.exists(target_dir):
        print(f"Fetching {filename} from {repo_id}...")
        path = hf_hub_download(repo_id=repo_id, filename=filename, repo_type="dataset")
        with tarfile.open(path, "r:gz") as tar:
            tar.extractall(path="data/")

fetch_and_extract("rdisipio/esco-skills", "esco_chroma.tar.gz", "data/esco_chroma")
fetch_and_extract("rdisipio/esco-skills", "courses_chroma.tar.gz", "data/courses_chroma")

courses_collection = Chroma(
    persist_directory="data/courses_chroma",
    embedding_function=embedding_model
)

esco_collection = Chroma(
    persist_directory="data/esco_chroma",
    embedding_function=embedding_model
)

# ---------- Output Management System ----------
class GradioOutputManager:
    """Manages Gradio outputs by name instead of index to prevent order-related bugs."""
    
    def __init__(self, output_names):
        """Initialize with a list of output component names in the expected order."""
        self.output_names = output_names
        self.output_map = {name: idx for idx, name in enumerate(output_names)}
        self._values = [None] * len(output_names)
    
    def set(self, name, value):
        """Set a value for a named output."""
        if name not in self.output_map:
            raise ValueError(f"Unknown output name: {name}. Available: {list(self.output_map.keys())}")
        self._values[self.output_map[name]] = value
        return self
    
    def set_multiple(self, **kwargs):
        """Set multiple outputs at once."""
        for name, value in kwargs.items():
            self.set(name, value)
        return self
    
    def get_tuple(self):
        """Return the values as a tuple in the correct order."""
        return tuple(self._values)
    
    def reset(self):
        """Reset all values to None."""
        self._values = [None] * len(self.output_names)
        return self

# Define output schemas for different functions
FEEDBACK_OUTPUTS = [
    "recommendations",      # 0
    "keep_btn",            # 1
    "adjust_btn",          # 2
    "reject_btn",          # 3
    "rec_index_state",     # 4
    "feedback_log_state",  # 5
    "chatbox",             # 6
    "agent_memory",        # 7
    "chat_input",          # 8
    "send_btn",            # 9
    "new_recs_btn",        # 10
    "memory_display"       # 11
]

SEE_RECOMMENDATIONS_OUTPUTS = [
    "profile_section",      # 0
    "recommend_section",    # 1
    "recommendations",      # 2
    "agent_memory",         # 3
    "profile_status",       # 4
    "user_id_state",        # 5
    "profile_json",         # 6
    "footer_status",        # 7
    "app_mode",             # 8
    "see_recommendations_btn", # 9
    "recs_state",           # 10
    "rec_index_state",      # 11
    "feedback_log_state",   # 12
    "keep_btn",             # 13
    "adjust_btn",           # 14
    "reject_btn",           # 15
    "chatbox",              # 16
    "new_recs_btn",         # 17
    "expectation_accordion", # 18
    "memory_editor_accordion", # 19
    "memory_display",       # 20
    "goal_input"            # 21
]

PROFILE_BUILD_OUTPUTS = [
    "profile_section",      # 0
    "recommend_section",    # 1
    "recommendations",      # 2
    "agent_memory",         # 3
    "profile_status",       # 4
    "user_id_state",        # 5
    "profile_json",         # 6
    "footer_status",        # 7
    "app_mode",             # 8
    "see_recommendations_btn", # 9
    "build_btn"             # 10
]

# ---------- Helper Functions ----------
def user_profile_exists(user_id):
    return os.path.exists(f"{MEMORY_DIR}/{user_id}.json")

def build_profile(user_id, blurb):
    result = subprocess.run(
        ["python3", "./scripts/build_profile_from_linkedin.py", user_id, blurb],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        return True, f"\u2705 Profile created for **{user_id}**."
    else:
        return False, f"❌ Error:\n```\n{result.stderr}\n```"

def load_memory(user_id):
    with open(f"{MEMORY_DIR}/{user_id}.json", "r") as f:
        return json.load(f)

def load_courses():
    with open(COURSES_PATH, "r") as f:
        return json.load(f)


def get_platform_display_name(source_platform):
    """Get a user-friendly platform name"""
    platform_names = {
        'coursera': 'Coursera',
        'udemy': 'Udemy',
        'udacity': 'Udacity',
        'futurelearn': 'FutureLearn',
        'khan': 'Khan Academy'
    }
    return platform_names.get(source_platform.lower(), source_platform.title())

def render_course_card(course, explanation=None):
    # Handle skills as string or list
    skills = course.get("skills", "")
    if isinstance(skills, str):
        skills_str = skills
    elif isinstance(skills, list):
        if skills and isinstance(skills[0], dict):
            skills_str = ", ".join(skill.get("name", "") for skill in skills)
        else:
            skills_str = ", ".join(str(skill) for skill in skills)
    else:
        skills_str = ""
    
    # Get fit score and format it
    confidence = course.get('confidence_score', 0)
    fit_score_text = f"**Fit Score:** {confidence:.2f}"
    confidence_bar = "🟩" * int(confidence * 10) + "⬜" * (10 - int(confidence * 10))
    fit_tooltip = "Score reflects how closely the course matches your skills/goals profile. Feedback shapes the next batch, not the current one."
    
    # Format duration with better fallback
    duration_hours = course.get('duration_hours', 0)
    try:
        duration_num = float(duration_hours) if duration_hours else 0
        if duration_num > 0:
            duration_text = f"{duration_num:g} hrs"  # :g removes trailing zeros
        else:
            duration_text = "Unknown"
    except (ValueError, TypeError):
        duration_text = "Unknown"
    
    # Build the card with proper order: Details → Fit Score → Why (with explanation + teaches)
    title = course.get('title') or course.get('course_title') or course.get('name') or 'Untitled Course'
    
    # Get platform and provider info
    source_platform = course.get('source_platform', '')
    provider = course.get('provider', '')
    
    # Format platform name
    platform_name = get_platform_display_name(source_platform) if source_platform else ''
    
    # Always show both platform and provider if available
    if platform_name and provider:
        # Show both platform and provider
        if provider.lower() == platform_name.lower():
            # If provider is same as platform, just show platform
            provider_line = f"**Platform**: {platform_name}"
        else:
            # Show both platform and provider
            provider_line = f"**Platform**: {platform_name} | **Provider**: {provider}"
    elif platform_name:
        provider_line = f"**Platform**: {platform_name}"
    elif provider:
        provider_line = f"**Provider**: {provider}"
    else:
        provider_line = ""
    
    card = f"""### [{title}]({course.get('url', '')})
{provider_line}  
**Duration**: {duration_text}  
**Level**: {course.get('level', '')} | **Format**: {course.get('format', '')}  

{fit_score_text} {confidence_bar}  
*{fit_tooltip}*"""
    
    # Add Why section with explanation followed by skills
    if explanation and explanation.strip():
        why_explanation = explanation
    else:
        # Provide a basic explanation based on fit score
        if confidence > 0.7:
            why_explanation = "This course aligns well with your goals and skill gaps."
        elif confidence > 0.4:
            why_explanation = "This course partially matches your profile and learning objectives."
        else:
            why_explanation = "This course may help fill some of your identified skill gaps."
    
    card += f"\n\n**Why:**\n> {why_explanation}"
    
    # Add teaches information after the explanation
    if skills_str:
        card += f"\n\n**Skills:** {skills_str}"
    
    # Add missing skills context if available
    missing_skills = course.get('query_missing_skills', [])
    if missing_skills and len(missing_skills) > 0:
        # Convert list to string if needed
        if isinstance(missing_skills, list):
            missing_skills_str = ", ".join(str(skill) for skill in missing_skills[:3])
        else:
            missing_skills_str = str(missing_skills)
        
        if missing_skills_str:
            card += f"\n\n**Addresses your gaps:** {missing_skills_str}"
    
    return card

def format_agent_memory_panel(mem):
    """Format user memory for display in the left agent memory panel"""
    known = "\n".join(f"- {s['preferredLabel']}" for s in mem["known_skills"])
    missing = "\n".join(f"- {s['preferredLabel']}" for s in mem["missing_skills"])
    
    # Enhanced feedback display with classifications
    feedback_log = mem.get("feedback_log", [])
    if feedback_log:
        feedback_lines = []
        for f in reversed(feedback_log[-5:]):  # Show last 5 entries, most recent first
            course_title = f.get('course_title', '')
            course_id = f.get('course_id', '?')
            feedback_type = f.get('feedback_type', '?')
            reason = f.get('reason', '')
            
            # Handle old feedback entries where course_title might be None or missing
            if course_title and course_title.strip() and course_title != '?' and str(course_title) != 'None':
                # We have a real course title, use it
                display_name = course_title.strip()
            else:
                # For old entries with missing/bad titles, use a generic name
                display_name = "Course (legacy entry)"
            
            # Add classification emoji if available
            classification_emoji = ""
            if "classification" in f:
                category = f["classification"].get("category", "")
                emoji_map = {
                    "friction": "🚫",
                    "credibility": "🔍", 
                    "better_way": "🔄",
                    "negative_impact": "❌",
                    "positive": "✅",
                    "other": "❓"
                }
                classification_emoji = emoji_map.get(category, "")
            
            # Truncate course titles after 20 characters
            if len(display_name) > 20:
                display_name = display_name[:20] + "..."
            
            # Format the feedback entry with icons instead of text
            feedback_type_icons = {
                "keep": "✅",      # green tick mark for accept
                "approve": "✅",   # green tick mark for approve (legacy)
                "accept": "✅",    # green tick mark for accept
                "adjust": "🔄",    # two swirling arrows for adjust  
                "reject": "🛑"     # stop sign for reject
            }
            feedback_icon = feedback_type_icons.get(feedback_type.lower().strip(), feedback_type.upper() if feedback_type.strip() else "❓")
            
            classification_note = ""
            if "classification" in f:
                category = f["classification"].get("category", "")
                if category and category != feedback_type:
                    classification_note = f" ({category})"
            
            feedback_lines.append(f"- {classification_emoji} **{display_name}**: {feedback_icon}{classification_note} — {reason[:50]}{'...' if len(reason) > 50 else ''}")
        
        feedback = "\n".join(feedback_lines)
        if len(feedback_log) > 5:
            feedback += f"\n... and {len(feedback_log) - 5} more entries"
    else:
        feedback = "No feedback recorded yet"
    
    company_goal = mem.get('company_goal', '')
    company_goal_md = f"\n\n### 📈 Company Goal\n{company_goal}" if company_goal else ""
    
    return f"""### 🌟 User's Goal
{mem['goal']}{company_goal_md}

### ✅ Known Skills
{known}

### 🚧 Missing Skills
{missing}

### 💬 Feedback Log
*REJECT courses won't appear again*  
{feedback}
"""

def chat_response(message, history):
    response = f"Echo: {message}"  # replace with actual logic
    history.append((message, response))
    return history, history


# ----------------- UI: Step 1 - Profile Creation -----------------
from coachable_course_agent.linkedin_tools import build_profile_from_bio
from coachable_course_agent.memory_store import load_user_profile
from coachable_course_agent.vector_store import query_similar_courses

from coachable_course_agent.justifier_chain import justify_recommendations
from coachable_course_agent.feedback_processor import process_feedback
from coachable_course_agent.memory_store import (
    format_memory_editor_display,
    update_goal_dialog,
    save_updated_goal,
    remove_skill,
    remove_known_skill,
    remove_learning_goal,
    add_skill,
    clear_feedback_log
)
with gr.Blocks(title="Coachable Course Agent") as demo:
    # Generate session-based user ID that persists during the session
    session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_user_id = f"user_{session_timestamp}"
    
    user_id_state = gr.State()
    app_mode = gr.State(value="profile")  # 'profile' or 'recommend'
    recs_state = gr.State(value=[])  # List of recommendations with explanations
    rec_index_state = gr.State(value=0)  # Current index in recommendations
    feedback_log_state = gr.State(value=[])  # List of feedbacks

    with gr.Accordion("My skills & goals", open=False, visible=False) as memory_editor_accordion:
        gr.Markdown("### 🧠 Manage Your Profile Memory")
        memory_display = gr.Markdown("No profile loaded.", elem_id="memory_display")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("**Remove Skill:**")
                remove_skill_input = gr.Textbox(
                    label="Skill to Remove", 
                    placeholder="Exact match only (for now)...",
                    lines=2
                )
                with gr.Row():
                    remove_known_btn = gr.Button("Remove from Known Skills")
                    remove_learning_btn = gr.Button("Remove from Learning Goals")
                remove_skill_status = gr.Markdown()
            
            with gr.Column():
                gr.Markdown("**Add Skill:**")
                add_skill_input = gr.Textbox(
                    label="Skill to Add", 
                    placeholder="Enter a new skill you have...",
                    lines=2
                )
                with gr.Row():
                    add_known_btn = gr.Button("Add as Known Skill")
                    add_missing_btn = gr.Button("Add as Learning Goal")
                add_skill_status = gr.Markdown()
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("**Update Goal:**")
                goal_input = gr.Textbox(
                    label="Career Goal", 
                    placeholder="Enter your new career goal...",
                    lines=2
                )
                update_goal_btn = gr.Button("Update Goal")
                goal_status = gr.Markdown()
            
            with gr.Column():
                gr.Markdown("**Clear Data:**")
                clear_feedback_btn = gr.Button("Clear Feedback Log")
                feedback_status = gr.Markdown()

    with gr.Column(visible=True) as profile_section:
        gr.Markdown("## 📝 Create Your Profile")
        
        # Display course catalog size
        try:
            course_count = courses_collection._collection.count()
            gr.Markdown(f"📚 **Course Catalog:** {course_count:,} courses available across diverse domains including Computer Science & AI, Business & Management, Engineering, Sciences, Environmental Studies, Health & Social Sciences, Humanities & Arts, and Design & Architecture.")
        except:
            gr.Markdown("📚 **Course Catalog:** Comprehensive collection of courses across diverse academic and professional domains.")
        
        gr.Markdown("💡 **New here?** Click below for a quick overview of how this agent works and what to expect.")
        with gr.Accordion("📋 Instructions & What to Expect", open=False) as expectation_accordion:
            # Load instructions from separate file
            try:
                with open("instructions.md", "r") as f:
                    instructions_content = f.read()
                gr.Markdown(instructions_content)
            except FileNotFoundError:
                gr.Markdown("Instructions file not found.")
        
        blurb_input = gr.Textbox(lines=5, label="LinkedIn-style Blurb", placeholder="Tell us about your background, current role, and career goals...")
        gr.Markdown("💡 *Processing typically takes 2-3 seconds while we analyze your profile and match ESCO skills.*")
        build_btn = gr.Button("Build Profile and Continue")
        profile_status = gr.Markdown()
        profile_json = gr.JSON(visible=False)
        see_recommendations_btn = gr.Button("See Recommendations", visible=False)

    with gr.Row(visible=False) as recommend_section:
        # Left: Agent memory
        with gr.Column(scale=1):
            gr.Markdown("## 🧠 Agent Memory")
            agent_memory = gr.Markdown("(Agent memory will appear here)", elem_id="agent_memory")
        # Center: Course Recommendations (main focus)
        with gr.Column(scale=1):
            gr.Markdown("## 🎯 Course Recommendations")
            recommendations = gr.Markdown("(Recommendations will appear here)")
            keep_btn = gr.Button("✅ Keep", visible=False)
            adjust_btn = gr.Button("✏️ Adjust", visible=False)
            reject_btn = gr.Button("🗙 Reject", visible=False)
            new_recs_btn = gr.Button("Get New Recommendations", visible=False)
        # Right: Chat
        with gr.Column(scale=1):
            gr.Markdown("## 💬 Your Feedback")
            chatbox = gr.Chatbot(type='messages', elem_id="chatbox")
            chat_input = gr.Textbox(label="Type your message", interactive=False, placeholder="Chat will be enabled when feedback explanation is needed...")
            send_btn = gr.Button("Send", interactive=False)

    with gr.Row() as footer:
        footer_status = gr.Markdown("👋 Ready")

    
    def on_see_recommendations_click(uid):
        outputs = GradioOutputManager(SEE_RECOMMENDATIONS_OUTPUTS)
        
        # Check if user profile exists, if not, redirect to profile creation
        if not uid or not user_profile_exists(uid):
            return outputs.set_multiple(
                profile_section=gr.update(visible=True),
                recommend_section=gr.update(visible=False),
                recommendations="",
                agent_memory="",
                profile_status="❌ **Profile not found.** Please create a new profile below.",
                user_id_state=None,
                profile_json=gr.update(visible=False),
                footer_status="❌ Profile not found. Please create a new profile.",
                app_mode="profile",
                see_recommendations_btn=gr.update(visible=False),
                recs_state=[],
                rec_index_state=0,
                feedback_log_state=[],
                keep_btn=gr.update(visible=False),
                adjust_btn=gr.update(visible=False),
                reject_btn=gr.update(visible=False),
                chatbox=[],
                new_recs_btn=gr.update(visible=False),
                expectation_accordion=gr.update(open=False),
                memory_editor_accordion=gr.update(visible=False),
                memory_display="No profile loaded.",
                goal_input=""
            ).get_tuple()
        
        # Load user profile and compute recommendations
        user_profile = load_user_profile(uid)
        # Print user profile skills
        user_skills = user_profile.get("known_skills", [])
        print("User profile skills:", [s.get("preferredLabel", s.get("name", "")) for s in user_skills])

        # Print number of stored courses
        try:
            n_courses = courses_collection._collection.count()
            print(f"Number of stored courses in Chroma: {n_courses}")
        except Exception as e:
            print(f"Could not count courses: {e}")

        # Get top N courses
        retrieved_courses = query_similar_courses(courses_collection, user_profile, top_n=5)
        print("retrieved_courses:", retrieved_courses)

        # Justify and refine recommendations
        explanations = justify_recommendations(user_profile, retrieved_courses)
        print("recommendations_list:", explanations)

        # Merge explanations into course dicts
        recommendations_list = []
        for i, course in enumerate(retrieved_courses):
            course_copy = dict(course)  # shallow copy
            if isinstance(explanations, list) and i < len(explanations):
                exp = explanations[i]
                # Prefer 'justification' if present, else 'explanation', else str(exp)
                if isinstance(exp, dict):
                    if 'justification' in exp:
                        course_copy['explanation'] = exp['justification']
                    elif 'explanation' in exp:
                        course_copy['explanation'] = exp['explanation']
                    else:
                        course_copy['explanation'] = str(exp)
                else:
                    course_copy['explanation'] = str(exp)
            else:
                # No explanation available, provide a fallback
                course_copy['explanation'] = "This course matches your profile based on skill alignment and learning goals."
            recommendations_list.append(course_copy)

        # Start at the first course
        if not recommendations_list:
            cards_md = "No recommendations found."
            approve_vis = adjust_vis = reject_vis = False
            chat_history = []
        else:
            course = recommendations_list[0]
            explanation = course.get("explanation", "")
            card = render_course_card(course, explanation)
            cards_md = card
            approve_vis = adjust_vis = reject_vis = True
            # Compose agent's prompt for chat
            chat_msg = f"Suggested: {course.get('title','?')}\nWhy:  \n{explanation}\nFeedback? (keep / adjust / reject)"
            chat_history = [{"role": "assistant", "content": chat_msg}]

        return outputs.set_multiple(
            profile_section=gr.update(visible=False),
            recommend_section=gr.update(visible=True),
            recommendations=gr.update(value=cards_md, visible=True),
            agent_memory=format_agent_memory_panel(user_profile),
            profile_status="",
            user_id_state=uid,
            profile_json=gr.update(visible=False),
            footer_status="👀 You are now viewing recommendations.",
            app_mode="recommend",
            see_recommendations_btn=gr.update(visible=False),
            recs_state=recommendations_list,
            rec_index_state=0,
            feedback_log_state=[],
            keep_btn=gr.update(visible=True),
            adjust_btn=gr.update(visible=True),
            reject_btn=gr.update(visible=True),
            chatbox=chat_history,
            new_recs_btn=gr.update(visible=False),
            expectation_accordion=gr.update(open=False),
            memory_editor_accordion=gr.update(visible=True),
            memory_display=format_memory_editor_display(uid),
            goal_input=update_goal_dialog(uid)
        ).get_tuple()


    # Bind the 'See Recommendations' button to the handler (must be inside Blocks context)
    see_recommendations_btn.click(
        on_see_recommendations_click,
        inputs=[user_id_state],
        outputs=[
            profile_section,      # hide
            recommend_section,    # show
            recommendations,      # update recommendations
            agent_memory,         # update agent memory
            profile_status,       # hide profile status
            user_id_state,        # keep user id
            profile_json,         # hide profile json
            footer_status,        # update footer
            app_mode,             # update app mode
            see_recommendations_btn, # hide see recommendations button
            recs_state,           # store recommendations
            rec_index_state,      # store current index
            feedback_log_state,   # store feedback log
            keep_btn, adjust_btn, reject_btn,
            chatbox,              # update chatbox
            new_recs_btn,         # update new_recs_btn (pad for output count)
            expectation_accordion, # collapse the accordion
            memory_editor_accordion, # show memory editor
            memory_display,       # load memory display
            goal_input           # load current goal for editing
        ]
    )

    def feedback_action(feedback_type, recs, idx, feedback_log, user_id_state, agent_memory, chatbox):
        outputs = GradioOutputManager(FEEDBACK_OUTPUTS)
        
        # Get current course
        if idx >= len(recs):
            chatbox = chatbox + [{"role": "assistant", "content": "All feedback collected. Thank you!"}]
            # Update agent memory after feedback loop is finished
            updated_profile = load_user_profile(user_id_state) if user_id_state else {}
            updated_memory = format_agent_memory_panel(updated_profile) if updated_profile else ""
            updated_memory_editor = format_memory_editor_display(user_id_state) if user_id_state else "No profile loaded."
            
            return outputs.set_multiple(
                recommendations=gr.update(value="All feedback collected. Thank you!", visible=True),
                keep_btn=gr.update(visible=False),
                adjust_btn=gr.update(visible=False),
                reject_btn=gr.update(visible=False),
                rec_index_state=idx,
                feedback_log_state=feedback_log,
                chatbox=chatbox,
                agent_memory=updated_memory,
                chat_input=gr.update(interactive=False, value="", placeholder="Chat will be enabled when feedback explanation is needed..."),
                send_btn=gr.update(visible=False, interactive=False),
                new_recs_btn=gr.update(visible=True),
                memory_display=updated_memory_editor
            ).get_tuple()
        
        course = recs[idx]
        course_id = course.get("id", "?")
        title = course.get("title") or course.get("course_title") or course.get("name") or "?"
        explanation = course.get("explanation", "")
        feedback_map = {
            "keep": "good fit",
            "adjust": "close, needs refinement", 
            "reject": "not suitable"
        }
        feedback_label = feedback_map.get(feedback_type, feedback_type)
        user_feedback_msg = f"Feedback: {feedback_type} ({feedback_label})"
        chatbox = chatbox + [
            {"role": "user", "content": user_feedback_msg}
        ]
        
        # If feedback requires a reason, prompt for it
        if feedback_type in ["adjust", "reject"]:
            if feedback_type == "adjust":
                prompt = "Any specific adjustments needed? (optional)"
            else:  # reject
                prompt = "Why isn't this course a good fit? (optional)"
            chatbox = chatbox + [{"role": "assistant", "content": prompt}]
            
            return outputs.set_multiple(
                recommendations=gr.update(),  # no change
                keep_btn=gr.update(visible=False),
                adjust_btn=gr.update(visible=False),
                reject_btn=gr.update(visible=False),
                rec_index_state=idx,
                feedback_log_state=feedback_log,
                chatbox=chatbox,
                agent_memory=agent_memory,  # no change
                chat_input=gr.update(interactive=True, placeholder="Please explain your feedback..."),
                send_btn=gr.update(visible=True, interactive=True),
                new_recs_btn=gr.update(visible=False),
                memory_display=gr.update()  # no change
            ).get_tuple()
        
        # Otherwise, process feedback and move to next course
        # Use the same title extraction logic as the course card
        actual_title = course.get('title') or course.get('course_title') or course.get('name') or 'Untitled Course'
        feedback_entry = {
            "course_id": course_id,
            "course_title": actual_title,
            "feedback_type": feedback_type,
            "reason": feedback_label
        }
        feedback_log = feedback_log + [feedback_entry]
        # Persist feedback to disk
        if user_id_state:
            process_feedback(user_id_state, course_id, feedback_type, feedback_label, actual_title)
        next_idx = idx + 1
        chatbox = chatbox + [{"role": "assistant", "content": f"Thanks for your feedback on '{title}' ({feedback_label})."}]
        if next_idx < len(recs):
            next_course = recs[next_idx]
            explanation = next_course.get('explanation', '')
            next_card = render_course_card(next_course, explanation)
            chat_msg = f"Suggested: {next_course.get('title','?')}\nWhy:  \n{explanation}\nFeedback? (keep / adjust / reject)"
            chatbox = chatbox + [{"role": "assistant", "content": chat_msg}]
            
            return outputs.set_multiple(
                recommendations=gr.update(value=next_card, visible=True),
                keep_btn=gr.update(visible=True),
                adjust_btn=gr.update(visible=True),
                reject_btn=gr.update(visible=True),
                rec_index_state=next_idx,
                feedback_log_state=feedback_log,
                chatbox=chatbox,
                agent_memory=format_agent_memory_panel(load_user_profile(user_id_state)) if user_id_state else "",
                chat_input=gr.update(interactive=False, value="", placeholder="Chat will be enabled when feedback explanation is needed..."),
                send_btn=gr.update(visible=False, interactive=False),
                new_recs_btn=gr.update(visible=False),
                memory_display=format_memory_editor_display(user_id_state) if user_id_state else "No profile loaded."
            ).get_tuple()
        else:
            # Update agent memory after feedback loop is finished
            updated_profile = load_user_profile(user_id_state) if user_id_state else {}
            updated_memory = format_agent_memory_panel(updated_profile) if updated_profile else ""
            
            return outputs.set_multiple(
                recommendations=gr.update(value="All feedback collected. Thank you!", visible=True),
                keep_btn=gr.update(visible=False),
                adjust_btn=gr.update(visible=False),
                reject_btn=gr.update(visible=False),
                rec_index_state=next_idx,
                feedback_log_state=feedback_log,
                chatbox=chatbox,
                agent_memory=updated_memory,
                chat_input=gr.update(interactive=False, value="", placeholder="Chat will be enabled when feedback explanation is needed..."),
                send_btn=gr.update(visible=False, interactive=False),
                new_recs_btn=gr.update(visible=True),
                memory_display=format_memory_editor_display(user_id_state) if user_id_state else "No profile loaded."
            ).get_tuple()

    def reason_action(reason, recs, idx, feedback_log, user_id_state, agent_memory, chatbox):
        outputs = GradioOutputManager(FEEDBACK_OUTPUTS)
        
        # Get current course
        if idx >= len(recs):
            # Update agent memory after feedback loop is finished
            updated_profile = load_user_profile(user_id_state) if user_id_state else {}
            updated_memory = format_agent_memory_panel(updated_profile) if updated_profile else ""
            
            return outputs.set_multiple(
                recommendations=gr.update(),
                keep_btn=gr.update(visible=False),
                adjust_btn=gr.update(visible=False),
                reject_btn=gr.update(visible=False),
                rec_index_state=idx,
                feedback_log_state=feedback_log,
                chatbox=chatbox,
                agent_memory=updated_memory,
                chat_input=gr.update(interactive=False, value="", placeholder="Chat will be enabled when feedback explanation is needed..."),
                send_btn=gr.update(visible=False, interactive=False),
                new_recs_btn=gr.update(visible=True),
                memory_display=format_memory_editor_display(user_id_state) if user_id_state else "No profile loaded."
            ).get_tuple()
        
        course = recs[idx]
        course_id = course.get("id", "?")
        title = course.get("title") or course.get("course_title") or course.get("name") or "?"
        
        # Find the last feedback entry for this course and update it with the reason and correct feedback_type
        if feedback_log and feedback_log[-1]["course_id"] == course_id and feedback_log[-1]["feedback_type"]:
            feedback_type = feedback_log[-1]["feedback_type"]
        else:
            # fallback: this shouldn't happen, but default to reject for safety
            feedback_type = "reject"
            print(f"Warning: Could not determine feedback type for course {course_id}, defaulting to 'reject'")
        
        # Use the same title extraction logic as the course card
        actual_title = course.get('title') or course.get('course_title') or course.get('name') or 'Untitled Course'
        feedback_entry = {
            "course_id": course_id,
            "course_title": actual_title,
            "feedback_type": feedback_type,
            "reason": reason if reason else feedback_type
        }
        feedback_log = feedback_log[:-1] + [feedback_entry] if feedback_log else [feedback_entry]
        
        # Persist feedback to disk
        if user_id_state:
            process_feedback(user_id_state, course_id, feedback_type, reason if reason else feedback_type, actual_title)
        
        chatbox = chatbox + [
            {"role": "user", "content": reason},
            {"role": "assistant", "content": f"Thanks for your feedback on '{title}' ({feedback_type})."}
        ]
        next_idx = idx + 1
        
        if next_idx < len(recs):
            next_course = recs[next_idx]
            explanation = next_course.get('explanation', '')
            next_card = render_course_card(next_course, explanation)
            chat_msg = f"Suggested: {next_course.get('title','?')}\nWhy:  \n{explanation}\nFeedback? (keep / adjust / reject)"
            chatbox = chatbox + [{"role": "assistant", "content": chat_msg}]
            
            return outputs.set_multiple(
                recommendations=gr.update(value=next_card, visible=True),
                keep_btn=gr.update(visible=True),
                adjust_btn=gr.update(visible=True),
                reject_btn=gr.update(visible=True),
                rec_index_state=next_idx,
                feedback_log_state=feedback_log,
                chatbox=chatbox,
                agent_memory=format_agent_memory_panel(load_user_profile(user_id_state)) if user_id_state else "",
                chat_input=gr.update(interactive=False, value="", placeholder="Chat will be enabled when feedback explanation is needed..."),
                send_btn=gr.update(visible=False, interactive=False),
                new_recs_btn=gr.update(visible=False),
                memory_display=format_memory_editor_display(user_id_state) if user_id_state else "No profile loaded."
            ).get_tuple()
        else:
            # Update agent memory after feedback loop is finished
            updated_profile = load_user_profile(user_id_state) if user_id_state else {}
            updated_memory = format_agent_memory_panel(updated_profile) if updated_profile else ""
            
            return outputs.set_multiple(
                recommendations=gr.update(value="All feedback collected. Thank you!", visible=True),
                keep_btn=gr.update(visible=False),
                adjust_btn=gr.update(visible=False),
                reject_btn=gr.update(visible=False),
                rec_index_state=next_idx,
                feedback_log_state=feedback_log,
                chatbox=chatbox,
                agent_memory=updated_memory,
                chat_input=gr.update(interactive=False, value="", placeholder="Chat will be enabled when feedback explanation is needed..."),
                send_btn=gr.update(visible=False, interactive=False),
                new_recs_btn=gr.update(visible=True),
                memory_display=format_memory_editor_display(user_id_state) if user_id_state else "No profile loaded."
            ).get_tuple()

    for btn, ftype in zip([keep_btn, adjust_btn, reject_btn], ["keep", "adjust", "reject"]):
        btn.click(
            feedback_action,
            inputs=[gr.State(ftype), recs_state, rec_index_state, feedback_log_state, user_id_state, agent_memory, chatbox],
            outputs=[
                recommendations,      # update recommendations
                keep_btn,             # update keep_btn
                adjust_btn,           # update adjust_btn
                reject_btn,           # update reject_btn
                rec_index_state,      # update rec_index_state
                feedback_log_state,   # update feedback_log_state
                chatbox,              # update chatbox
                agent_memory,         # update agent_memory (left column)
                chat_input,           # update chat_input (text box)
                send_btn,             # update send_btn
                new_recs_btn,         # update new_recs_btn (show/hide)
                memory_display        # update memory editor display
            ]
        )

    # Bind send_btn to reason_action for collecting reason
    send_btn.click(
        reason_action,
        inputs=[chat_input, recs_state, rec_index_state, feedback_log_state, user_id_state, agent_memory, chatbox],
        outputs=[
            recommendations,      # update recommendations
            keep_btn,             # update keep_btn
            adjust_btn,           # update adjust_btn
            reject_btn,           # update reject_btn
            rec_index_state,      # update rec_index_state
            feedback_log_state,   # update feedback_log_state
            chatbox,              # update chatbox
            agent_memory,         # update agent_memory (left column)
            chat_input,           # update chat_input (text box)
            send_btn,             # update send_btn
            new_recs_btn,         # update new_recs_btn (show/hide)
            memory_display        # update memory editor display
        ]
    )
    def on_new_recs_click(user_id_state):
        # Reload user profile and get new recommendations
        result = on_see_recommendations_click(user_id_state)
        # Keep the accordion collapsed when getting new recommendations
        return result

    new_recs_btn.click(
        on_new_recs_click,
        inputs=[user_id_state],
        outputs=[
            profile_section,      # hide
            recommend_section,    # show
            recommendations,      # update recommendations
            agent_memory,         # update agent memory
            profile_status,       # hide profile status
            user_id_state,        # keep user id
            profile_json,         # hide profile json
            footer_status,        # update footer
            app_mode,             # update app mode
            see_recommendations_btn, # hide see recommendations button
            recs_state,           # store recommendations
            rec_index_state,      # store current index
            feedback_log_state,   # store feedback log
            keep_btn, adjust_btn, reject_btn,
            chatbox,
            new_recs_btn,
            expectation_accordion # keep accordion collapsed
        ]
    )


    def on_profile_submit(blurb):
        outputs = GradioOutputManager(PROFILE_BUILD_OUTPUTS)
        
        # Use the session-based user ID
        uid = session_user_id
        
        # Add a note about session-based profiles
        print(f"Creating profile with ID: {uid}")
        
        # Show immediate processing feedback
        processing_msg = "🔄 **Processing your profile...** This may take a few seconds while we analyze your background and match skills."
        
        try:
            result_text, data = build_profile_from_bio(uid, blurb)
            # Add company goal to the user profile dict and persist it
            company_goal = GOALS
            if isinstance(data, dict):
                data["company_goal"] = company_goal
                # Save updated profile with company goal
                with open(f"{MEMORY_DIR}/{uid}.json", "w") as f:
                    json.dump(data, f, indent=2)
            
            # Create a clean, user-friendly success message
            headline = data.get("headline", "N/A") if isinstance(data, dict) else "N/A"
            skills_count = len(data.get("known_skills", [])) if isinstance(data, dict) else 0
            missing_skills_count = len(data.get("missing_skills", [])) if isinstance(data, dict) else 0
            
            msg = f"✅ **Profile created successfully!**\n\n"
            msg += f"**Headline:** {headline}\n"
            msg += f"**Skills identified:** {skills_count} skills\n"
            if missing_skills_count > 0:
                msg += f"**Growth opportunities:** {missing_skills_count} additional skills suggested\n"
            msg += f"\n💡 Click 'See Recommendations' to proceed - you'll be able to customize your profile there."
            
            # Show the 'See Recommendations' button after profile creation
            return outputs.set_multiple(
                profile_section=gr.update(visible=True),
                recommend_section=gr.update(visible=False),
                recommendations="",
                agent_memory="",
                profile_status=msg,
                user_id_state=uid,
                profile_json=gr.update(value=data, visible=False),
                footer_status="✌️ Profile created.",
                app_mode="profile",
                see_recommendations_btn=gr.update(visible=True),
                build_btn=gr.update(interactive=False, value="Profile Created ✓")
            ).get_tuple()
            
        except Exception as e:
            return outputs.set_multiple(
                profile_section=gr.update(visible=True),
                recommend_section=gr.update(visible=False),
                recommendations="",
                agent_memory="",
                profile_status=f"❌ Error: {e}",
                user_id_state=None,
                profile_json=gr.update(visible=False),
                footer_status=f"❌ Error: {e}",
                app_mode="profile",
                see_recommendations_btn=gr.update(visible=False),
                build_btn=gr.update(interactive=True, value="Build Profile and Continue")
            ).get_tuple()



    build_btn.click(
        on_profile_submit,
        inputs=[blurb_input],
        outputs=[
            profile_section,      # show/hide
            recommend_section,    # show/hide
            recommendations,      # update recommendations
            agent_memory,         # update agent memory
            profile_status,       # update profile status
            user_id_state,        # update user id
            profile_json,         # update profile json
            footer_status,        # update footer
            app_mode,             # update app mode
            see_recommendations_btn, # show/hide see recommendations button
            build_btn             # disable after success
        ]
    )

    # Memory Editor Event Handlers
    def update_goal_and_update_all(user_id, new_goal):
        """Update goal, recompute missing skills, and return updates for both memory displays"""
        status = save_updated_goal(user_id, new_goal, esco_collection)
        memory_editor_display = format_memory_editor_display(user_id) if user_id else "No profile loaded."
        updated_profile = load_user_profile(user_id) if user_id else {}
        agent_memory_display = format_agent_memory_panel(updated_profile) if updated_profile else ""
        return status, memory_editor_display, agent_memory_display

    update_goal_btn.click(
        update_goal_and_update_all,
        inputs=[user_id_state, goal_input],
        outputs=[goal_status, memory_display, agent_memory]
    )
    
    def remove_known_skill_and_update_all(user_id, skill_to_remove):
        """Remove skill from known skills and return updates for both memory displays"""
        status, memory_editor_display, cleared_input = remove_known_skill(user_id, skill_to_remove)
        updated_profile = load_user_profile(user_id) if user_id else {}
        agent_memory_display = format_agent_memory_panel(updated_profile) if updated_profile else ""
        return status, memory_editor_display, cleared_input, agent_memory_display

    remove_known_btn.click(
        remove_known_skill_and_update_all,
        inputs=[user_id_state, remove_skill_input],
        outputs=[remove_skill_status, memory_display, remove_skill_input, agent_memory]
    )
    
    def remove_learning_goal_and_update_all(user_id, skill_to_remove):
        """Remove skill from learning goals and return updates for both memory displays"""
        status, memory_editor_display, cleared_input = remove_learning_goal(user_id, skill_to_remove)
        updated_profile = load_user_profile(user_id) if user_id else {}
        agent_memory_display = format_agent_memory_panel(updated_profile) if updated_profile else ""
        return status, memory_editor_display, cleared_input, agent_memory_display

    remove_learning_btn.click(
        remove_learning_goal_and_update_all,
        inputs=[user_id_state, remove_skill_input],
        outputs=[remove_skill_status, memory_display, remove_skill_input, agent_memory]
    )
    
    def add_known_skill_and_update_all(user_id, skill_name):
        """Add skill as known and return updates for both memory displays"""
        status, memory_editor_display, cleared_input = add_skill(user_id, skill_name, "known", esco_collection)
        updated_profile = load_user_profile(user_id) if user_id else {}
        agent_memory_display = format_agent_memory_panel(updated_profile) if updated_profile else ""
        return status, memory_editor_display, cleared_input, agent_memory_display

    add_known_btn.click(
        add_known_skill_and_update_all,
        inputs=[user_id_state, add_skill_input],
        outputs=[add_skill_status, memory_display, add_skill_input, agent_memory]
    )
    
    def add_missing_skill_and_update_all(user_id, skill_name):
        """Add skill as learning goal and return updates for both memory displays"""
        status, memory_editor_display, cleared_input = add_skill(user_id, skill_name, "missing", esco_collection)
        updated_profile = load_user_profile(user_id) if user_id else {}
        agent_memory_display = format_agent_memory_panel(updated_profile) if updated_profile else ""
        return status, memory_editor_display, cleared_input, agent_memory_display

    add_missing_btn.click(
        add_missing_skill_and_update_all,
        inputs=[user_id_state, add_skill_input],
        outputs=[add_skill_status, memory_display, add_skill_input, agent_memory]
    )
    
    def clear_feedback_and_update_all(user_id):
        """Clear feedback and return updates for both memory displays"""
        status, memory_editor_display = clear_feedback_log(user_id)
        updated_profile = load_user_profile(user_id) if user_id else {}
        agent_memory_display = format_agent_memory_panel(updated_profile) if updated_profile else ""
        return status, memory_editor_display, agent_memory_display

    clear_feedback_btn.click(
        clear_feedback_and_update_all,
        inputs=[user_id_state],
        outputs=[feedback_status, memory_display, agent_memory]
    )

if __name__ == "__main__":
    demo.launch()


