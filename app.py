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
from huggingface_hub import hf_hub_download

MEMORY_DIR = "data/memory"
COURSES_PATH = "data/course_catalog_esco.json"
GOALS = "Support cross-functional collaboration and accelerate internal mobility."

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
    
    # Generate "because" chips
    because_chips = generate_because_chips(course)
    because_text = " • ".join(because_chips)
    
    # Get confidence score and format it
    confidence = course.get('confidence_score', 0)
    confidence_text = f"**Confidence:** {confidence:.2f}"
    confidence_bar = "🟩" * int(confidence * 10) + "⬜" * (10 - int(confidence * 10))
    
    # Build the card with proper order: Details → Confidence → Why → Because
    card = f"""### [{course.get('title', '')}]({course.get('url', '')})
**Provider**: {course.get('provider', '')}  
**Duration**: {course.get('duration_hours', '?')} hrs  
**Level**: {course.get('level', '')} | **Format**: {course.get('format', '')}  
**Skills**: {skills_str}

{confidence_text} {confidence_bar}"""
    
    # Add Why section if explanation is provided
    if explanation and explanation.strip():
        card += f"\n\n**Why:**\n> {explanation}"
    else:
        # Provide a basic explanation based on confidence
        if confidence > 0.7:
            fallback = "This course aligns well with your goals and skill gaps."
        elif confidence > 0.4:
            fallback = "This course partially matches your profile and learning objectives."
        else:
            fallback = "This course may help fill some of your identified skill gaps."
        card += f"\n\n**Why:**\n> {fallback}"
    
    # Add Because section
    card += f"\n\n**Because:** {because_text}"
    
    return card

def generate_because_chips(course):
    """Generate at least 2 'because' chips showing why this course was recommended."""
    chips = []
    
    # 1. Goal-based chip (first priority)
    if course.get('query_goal'):
        goal_words = course.get('query_goal', '').split()[:3]  # First 3 words of goal
        if goal_words:
            chips.append(f"goal: {' '.join(goal_words)}")
    
    # 2. Course-specific skills chips (teaches - second priority)
    course_skills = course.get('skills', '')
    if isinstance(course_skills, str):
        skill_list = [s.strip() for s in course_skills.split(',')][:2]
        for skill in skill_list:
            if skill:
                chips.append(f"teaches: {skill}")
    
    # 3. Missing skills chips (third priority)
    missing_skills = course.get('query_missing_skills', [])
    for skill in missing_skills[:2]:
        if skill:
            chips.append(f"missing: {skill}")
    
    # 4. Preferences chip (fallback)
    preferences = course.get('query_preferences', '')
    if preferences:
        pref_words = preferences.split()[:2]  # First 2 preference words
        if pref_words:
            chips.append(f"style: {' '.join(pref_words)}")
    
    # Ensure we have at least 2 chips
    if len(chips) < 2:
        chips.append(f"level: {course.get('level', 'suitable')}")
        chips.append(f"format: {course.get('format', 'available')}")
    
    return chips[:4]  # Max 4 chips to avoid clutter

def format_agent_memory_panel(mem):
    """Format user memory for display in the left agent memory panel"""
    known = "\n".join(f"- {s['preferredLabel']}" for s in mem["known_skills"])
    missing = "\n".join(f"- {s['preferredLabel']}" for s in mem["missing_skills"])
    feedback = "\n".join(
        f"- {f.get('course_id','?')}: {f.get('feedback_type','?')} — {f.get('reason','')}"
        for f in mem.get("feedback_log", [])
    )
    company_goal = mem.get('company_goal', '')
    company_goal_md = f"\n\n### 📈 Company Goal\n{company_goal}" if company_goal else ""
    return f"""### 🌟 User's Goal
{mem['goal']}{company_goal_md}

### ✅ Known Skills
{known}

### 🚧 Missing Skills
{missing}

### 💬 Feedback Log
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
    clear_feedback_log
)
with gr.Blocks(title="Coachable Course Agent") as demo:
    user_id_state = gr.State()
    app_mode = gr.State(value="profile")  # 'profile' or 'recommend'
    recs_state = gr.State(value=[])  # List of recommendations with explanations
    rec_index_state = gr.State(value=0)  # Current index in recommendations
    feedback_log_state = gr.State(value=[])  # List of feedbacks

    with gr.Accordion("Before we start...", open=True) as expectation_accordion:
        gr.Markdown("""
### 🤖 What this agent does
- Matches your **skills and goals** to ESCO skills.
- Retrieves and ranks relevant courses.
- Explains *why* each course fits you.
- Lets you give feedback to improve suggestions.
- Provides a **Memory Editor** so you can view and modify your profile data.

### 🚫 What this agent doesn't do
- Guarantee prices, certification status, or course dates.
- Replace human career guidance. Never ever!

### 🔒 About your data
- Your profile is saved **locally in this app**, not in a central database.
- A Large Language Model (LLM) is called to generate explanations.
- You can view, edit, or delete your profile and feedback anytime using the Memory Editor.
        """)

    with gr.Accordion("Memory Editor", open=False, visible=False) as memory_editor_accordion:
        gr.Markdown("### 🧠 Manage Your Profile Memory")
        memory_display = gr.Markdown("No profile loaded.", elem_id="memory_display")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("**Update Goal:**")
                goal_input = gr.Textbox(
                    label="Career Goal", 
                    placeholder="Enter your new career goal...",
                    lines=2
                )
                update_goal_btn = gr.Button("Update Goal", variant="primary")
                goal_status = gr.Markdown()
            
            with gr.Column():
                gr.Markdown("**Remove Skill:**")
                skill_input = gr.Textbox(
                    label="Skill to Remove", 
                    placeholder="Type skill name (partial match works)...",
                    lines=1
                )
                remove_skill_btn = gr.Button("Remove Skill", variant="secondary")
                skill_status = gr.Markdown()
        
        with gr.Row():
            clear_feedback_btn = gr.Button("Clear Feedback Log", variant="stop")
            feedback_status = gr.Markdown()

    with gr.Column(visible=True) as profile_section:
        gr.Markdown("## 🔐 Create Your Profile")
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
            approve_btn = gr.Button("Approve", visible=False)
            adjust_btn = gr.Button("Adjust", visible=False)
            reject_btn = gr.Button("Reject", visible=False)
            suggest_btn = gr.Button("Suggest", visible=False)
            new_recs_btn = gr.Button("Get New Recommendations", visible=False)
        # Right: Chat
        with gr.Column(scale=1):
            gr.Markdown("## 💬 Chat with the Agent")
            chatbox = gr.Chatbot(type='messages', elem_id="chatbox")
            chat_input = gr.Textbox(label="Type your message", interactive=False, placeholder="Chat will be enabled when feedback explanation is needed...")
            send_btn = gr.Button("Send", interactive=False)

    with gr.Row() as footer:
        footer_status = gr.Markdown("👋 Ready")

    
    def on_see_recommendations_click(uid):
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
            approve_vis = adjust_vis = reject_vis = suggest_vis = False
            chat_history = []
        else:
            course = recommendations_list[0]
            explanation = course.get("explanation", "")
            card = render_course_card(course, explanation)
            cards_md = card
            approve_vis = adjust_vis = reject_vis = suggest_vis = True
            # Compose agent's prompt for chat
            chat_msg = f"Suggested: {course.get('title','?')}\nWhy:  \n{explanation}\nFeedback? (approve / adjust / reject / suggest)"
            chat_history = [{"role": "assistant", "content": chat_msg}]

        return (
            gr.update(visible=False),  # profile_section
            gr.update(visible=True),   # recommend_section
            gr.update(value=cards_md, visible=True),  # recommendations
            format_agent_memory_panel(user_profile), # agent_memory (show memory)
            "",                       # profile_status (hide)
            uid,                      # user_id_state (keep)
            gr.update(visible=False),  # profile_json (hide)
            "👀 You are now viewing recommendations.",  # footer_status
            "recommend",              # app_mode
            gr.update(visible=False),   # see_recommendations_btn (hide it)
            recommendations_list,      # recs_state
            0,                        # rec_index_state
            [],                       # feedback_log_state
            gr.update(visible=True),
            gr.update(visible=True),
            gr.update(visible=True),
            gr.update(visible=True),
            chat_history,             # chatbox
            gr.update(visible=False),  # hide new_recs_btn until feedback loop is finished
            gr.update(open=False),     # collapse the expectation accordion
            gr.update(visible=True),   # show memory editor accordion
            format_memory_editor_display(uid),     # load memory display
            update_goal_dialog(uid)    # load current goal for editing
        )


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
            approve_btn, adjust_btn, reject_btn, suggest_btn,
            chatbox,              # update chatbox
            new_recs_btn,         # update new_recs_btn (pad for output count)
            expectation_accordion, # collapse the accordion
            memory_editor_accordion, # show memory editor
            memory_display,       # load memory display
            goal_input           # load current goal for editing
        ]
    )

    def feedback_action(feedback_type, recs, idx, feedback_log, user_id_state, agent_memory, chatbox):
        # Get current course
        if idx >= len(recs):
            chatbox = chatbox + [{"role": "assistant", "content": "All feedback collected. Thank you!"}]
            # Update agent memory after feedback loop is finished
            updated_profile = load_user_profile(user_id_state) if user_id_state else {}
            updated_memory = format_agent_memory_panel(updated_profile) if updated_profile else ""
            updated_memory_editor = format_memory_editor_display(user_id_state) if user_id_state else "No profile loaded."
            return (
                gr.update(value="All feedback collected. Thank you!", visible=True),
                gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False),
                idx, feedback_log, chatbox, updated_memory, 
                gr.update(interactive=False, value="", placeholder="Chat will be enabled when feedback explanation is needed..."), # disable chat_input
                gr.update(visible=False, interactive=False),  # disable send_btn
                gr.update(visible=True),  # Show new_recs_btn
                updated_memory_editor  # update memory editor display
            )
        course = recs[idx]
        course_id = course.get("id", "?")
        title = course.get("title", "?")
        explanation = course.get("explanation", "")
        feedback_map = {
            "approve": "great fit",
            "adjust": "close, but not quite",
            "reject": "nope",
            "suggest": "you propose a better match"
        }
        feedback_label = feedback_map.get(feedback_type, feedback_type)
        user_feedback_msg = f"Feedback: {feedback_type} ({feedback_label})"
        chatbox = chatbox + [
            {"role": "user", "content": user_feedback_msg}
        ]
        # If feedback requires a reason, prompt for it
        if feedback_type in ["adjust", "reject", "suggest"]:
            chatbox = chatbox + [{"role": "assistant", "content": "Please provide a reason for your feedback."}]
            return (
                gr.update(),  # recommendations (no change)
                gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False),
                idx, feedback_log, chatbox, agent_memory, 
                gr.update(interactive=True, placeholder="Please explain your feedback..."), # enable chat_input
                gr.update(visible=True, interactive=True),  # enable send_btn
                gr.update(visible=False), gr.update()  # pad outputs to match count - no memory display update needed here
            )
        # Otherwise, process feedback and move to next course
        feedback_entry = {
            "course_id": course_id,
            "feedback_type": feedback_type,
            "reason": feedback_label
        }
        feedback_log = feedback_log + [feedback_entry]
        # Persist feedback to disk
        if user_id_state:
            process_feedback(user_id_state, course_id, feedback_type, feedback_label)
        next_idx = idx + 1
        chatbox = chatbox + [{"role": "assistant", "content": f"Thanks for your feedback on '{title}' ({feedback_label})."}]
        if next_idx < len(recs):
            next_course = recs[next_idx]
            explanation = next_course.get('explanation', '')
            next_card = render_course_card(next_course, explanation)
            chat_msg = f"Suggested: {next_course.get('title','?')}\nWhy:  \n{explanation}\nFeedback? (approve / adjust / reject / suggest)"
            chatbox = chatbox + [{"role": "assistant", "content": chat_msg}]
            return (
                gr.update(value=next_card, visible=True),
                gr.update(visible=True), gr.update(visible=True), gr.update(visible=True), gr.update(visible=True),
                next_idx, feedback_log, chatbox, agent_memory, 
                gr.update(interactive=False, value="", placeholder="Chat will be enabled when feedback explanation is needed..."), # disable chat_input
                gr.update(visible=False, interactive=False),  # disable send_btn
                gr.update(visible=False), format_memory_editor_display(user_id_state) if user_id_state else "No profile loaded."  # update memory editor
            )
        else:
            # Update agent memory after feedback loop is finished
            updated_profile = load_user_profile(user_id_state) if user_id_state else {}
            updated_memory = format_agent_memory_panel(updated_profile) if updated_profile else ""
            return (
                gr.update(value="All feedback collected. Thank you!", visible=True),
                gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False),
                next_idx, feedback_log, chatbox, updated_memory, 
                gr.update(interactive=False, value="", placeholder="Chat will be enabled when feedback explanation is needed..."), # disable chat_input
                gr.update(visible=False, interactive=False),  # disable send_btn
                gr.update(visible=True), format_memory_editor_display(user_id_state) if user_id_state else "No profile loaded."  # update memory editor
            )

    def reason_action(reason, recs, idx, feedback_log, user_id_state, agent_memory, chatbox):
        # Get current course
        if idx >= len(recs):
            # Update agent memory after feedback loop is finished
            updated_profile = load_user_profile(user_id_state) if user_id_state else {}
            updated_memory = format_agent_memory_panel(updated_profile) if updated_profile else ""
            return (
                gr.update(), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False),
                idx, feedback_log, chatbox, updated_memory, 
                gr.update(interactive=False, value="", placeholder="Chat will be enabled when feedback explanation is needed..."), # disable chat_input
                gr.update(visible=False, interactive=False),  # disable send_btn
                gr.update(visible=True), format_memory_editor_display(user_id_state) if user_id_state else "No profile loaded."  # update memory editor
            )
        course = recs[idx]
        course_id = course.get("id", "?")
        title = course.get("title", "?")
        # Find the last feedback entry for this course and update it with the reason and correct feedback_type
        if feedback_log and feedback_log[-1]["course_id"] == course_id and feedback_log[-1]["feedback_type"]:
            feedback_type = feedback_log[-1]["feedback_type"]
        else:
            # fallback: try to infer from previous state or default to 'adjust'
            feedback_type = "adjust"
        feedback_entry = {
            "course_id": course_id,
            "feedback_type": feedback_type,
            "reason": reason if reason else feedback_type
        }
        feedback_log = feedback_log[:-1] + [feedback_entry] if feedback_log else [feedback_entry]
        # Persist feedback to disk
        if user_id_state:
            process_feedback(user_id_state, course_id, feedback_type, reason if reason else feedback_type)
        chatbox = chatbox + [
            {"role": "user", "content": reason},
            {"role": "assistant", "content": f"Thanks for your feedback on '{title}' ({feedback_type})."}
        ]
        next_idx = idx + 1
        if next_idx < len(recs):
            next_course = recs[next_idx]
            explanation = next_course.get('explanation', '')
            next_card = render_course_card(next_course, explanation)
            chat_msg = f"Suggested: {next_course.get('title','?')}\nWhy:  \n{explanation}\nFeedback? (approve / adjust / reject / suggest)"
            chatbox = chatbox + [{"role": "assistant", "content": chat_msg}]
            return (
                gr.update(value=next_card, visible=True),
                gr.update(visible=True), gr.update(visible=True), gr.update(visible=True), gr.update(visible=True),
                next_idx, feedback_log, chatbox, agent_memory, 
                gr.update(interactive=False, value="", placeholder="Chat will be enabled when feedback explanation is needed..."), # disable chat_input
                gr.update(visible=False, interactive=False),  # disable send_btn
                gr.update(visible=False), format_memory_editor_display(user_id_state) if user_id_state else "No profile loaded."  # update memory editor
            )
        else:
            # Update agent memory after feedback loop is finished
            updated_profile = load_user_profile(user_id_state) if user_id_state else {}
            updated_memory = format_agent_memory_panel(updated_profile) if updated_profile else ""
            return (
                gr.update(value="All feedback collected. Thank you!", visible=True),
                gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False),
                next_idx, feedback_log, chatbox, updated_memory, 
                gr.update(interactive=False, value="", placeholder="Chat will be enabled when feedback explanation is needed..."), # disable chat_input
                gr.update(visible=False, interactive=False),  # disable send_btn
                gr.update(visible=True), format_memory_editor_display(user_id_state) if user_id_state else "No profile loaded."  # update memory editor
            )

    for btn, ftype in zip([approve_btn, adjust_btn, reject_btn, suggest_btn], ["approve", "adjust", "reject", "suggest"]):
        btn.click(
            feedback_action,
            inputs=[gr.State(ftype), recs_state, rec_index_state, feedback_log_state, user_id_state, agent_memory, chatbox],
            outputs=[
                recommendations,      # update recommendations
                approve_btn,          # update approve_btn
                adjust_btn,           # update adjust_btn
                reject_btn,           # update reject_btn
                suggest_btn,          # update suggest_btn
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
            approve_btn,          # update approve_btn
            adjust_btn,           # update adjust_btn
            reject_btn,           # update reject_btn
            suggest_btn,          # update suggest_btn
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
            approve_btn, adjust_btn, reject_btn, suggest_btn,
            chatbox,
            new_recs_btn,
            expectation_accordion # keep accordion collapsed
        ]
    )


    def on_profile_submit(blurb):
        # Use a default user ID since sessions are isolated in HF Spaces
        uid = "default_user"
        
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
            msg = f"✅ Profile created successfully.\n\n**Summary:** {result_text}"
            # Show the 'See Recommendations' button after profile creation
            return (
                gr.update(visible=True),   # profile_section
                gr.update(visible=False),  # recommend_section
                "",                       # recommendations (not used here)
                "",                       # agent_memory (not used here)
                msg,                       # profile_status (success message)
                uid,                       # user_id_state
                gr.update(value=data, visible=False),  # profile_json (hide after creation)
                "✌️ Profile created.",       # footer_status
                "profile",                # app_mode
                gr.update(visible=True)    # see_recommendations_btn (show it)
            )
        except Exception as e:
            return (
                gr.update(visible=True),   # profile_section
                gr.update(visible=False),  # recommend_section
                "",                       # recommendations
                "",                       # agent_memory
                f"❌ Error: {e}",          # profile_status
                None,                      # user_id_state
                gr.update(visible=False),  # profile_json
                f"❌ Error: {e}",          # footer_status
                "profile",                # app_mode
                gr.update(visible=False)   # see_recommendations_btn (hide it)
            )



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
            see_recommendations_btn # show/hide see recommendations button
        ]
    )

    # Memory Editor Event Handlers
    update_goal_btn.click(
        save_updated_goal,
        inputs=[user_id_state, goal_input],
        outputs=[goal_status, memory_display]
    )
    
    # Also update agent memory when goal is updated
    update_goal_btn.click(
        lambda uid, goal: format_agent_memory_panel(load_user_profile(uid)),
        inputs=[user_id_state, goal_input],
        outputs=[agent_memory]
    )
    
    remove_skill_btn.click(
        remove_skill,
        inputs=[user_id_state, skill_input],
        outputs=[skill_status, memory_display, skill_input]
    )
    
    # Also update agent memory when skill is removed
    remove_skill_btn.click(
        lambda uid, skill: format_agent_memory_panel(load_user_profile(uid)),
        inputs=[user_id_state, skill_input],
        outputs=[agent_memory]
    )
    
    clear_feedback_btn.click(
        clear_feedback_log,
        inputs=[user_id_state],
        outputs=[feedback_status, memory_display]
    )
    
    # Also update agent memory when feedback is cleared
    clear_feedback_btn.click(
        lambda uid: format_agent_memory_panel(load_user_profile(uid)),
        inputs=[user_id_state],
        outputs=[agent_memory]
    )

demo.launch()


