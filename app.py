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


def render_course_card(course):
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
    return f"""### [{course.get('title', '')}]({course.get('url', '')})
**Provider**: {course.get('provider', '')}  
**Duration**: {course.get('duration_hours', '?')} hrs  
**Level**: {course.get('level', '')} | **Format**: {course.get('format', '')}  
**Skills**: {skills_str}
"""

def format_memory(mem):
    known = "\n".join(f"- {s['preferredLabel']}" for s in mem["known_skills"])
    missing = "\n".join(f"- {s['preferredLabel']}" for s in mem["missing_skills"])
    feedback = "\n".join(
        f"- {f['course_id']}: {f['feedback_type']} — {f['reason']}"
        for f in mem["feedback_log"] if f['feedback_type']
    )
    return f"""### 🌟 Goal
{mem['goal']}

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



with gr.Blocks(title="Coachable Course Agent") as demo:
    user_id_state = gr.State()
    app_mode = gr.State(value="profile")  # 'profile' or 'recommend'
    recs_state = gr.State(value=[])  # List of recommendations with explanations
    rec_index_state = gr.State(value=0)  # Current index in recommendations
    feedback_log_state = gr.State(value=[])  # List of feedbacks

    with gr.Column(visible=True) as profile_section:
        gr.Markdown("## 🔐 Create Your Profile")
        uid_input = gr.Textbox(label="User ID", placeholder="e.g. user_1")
        blurb_input = gr.Textbox(lines=5, label="LinkedIn-style Blurb")
        build_btn = gr.Button("Build Profile and Continue")
        profile_status = gr.Markdown()
        profile_json = gr.JSON(visible=False)
        see_recommendations_btn = gr.Button("See Recommendations", visible=False)

    with gr.Row(visible=False) as recommend_section:
        # Left: Agent memory
        with gr.Column(scale=1):
            gr.Markdown("## 🧠 Agent Memory")
            agent_memory = gr.Markdown("(Agent memory will appear here)", elem_id="agent_memory")
        # Middle: Chat
        with gr.Column(scale=1):
            gr.Markdown("## 💬 Chat with the Agent")
            chatbox = gr.Chatbot(type='messages', elem_id="chatbox")
            chat_input = gr.Textbox(label="Type your message")
            send_btn = gr.Button("Send")
        # Right: Recommendations
        with gr.Column(scale=1):
            gr.Markdown("## 🎯 Course Recommendations")
            recommendations = gr.Markdown("(Recommendations will appear here)")
            approve_btn = gr.Button("Approve", visible=False)
            adjust_btn = gr.Button("Adjust", visible=False)
            reject_btn = gr.Button("Reject", visible=False)
            suggest_btn = gr.Button("Suggest", visible=False)

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
            recommendations_list.append(course_copy)

        # Start at the first course
        if not recommendations_list:
            cards_md = "No recommendations found."
            approve_vis = adjust_vis = reject_vis = suggest_vis = False
            chat_history = []
        else:
            course = recommendations_list[0]
            explanation = course.get("explanation", "")
            card = render_course_card(course)
            if explanation:
                card += f"\n**Why:**\n> {explanation}\n"
            cards_md = card
            approve_vis = adjust_vis = reject_vis = suggest_vis = True
            # Compose agent's prompt for chat
            chat_msg = f"Suggested: {course.get('title','?')}\nWhy:  \n{explanation}\nFeedback? (approve / adjust / reject / suggest)"
            chat_history = [{"role": "assistant", "content": chat_msg}]

        return (
            gr.update(visible=False),  # profile_section
            gr.update(visible=True),   # recommend_section
            gr.update(value=cards_md, visible=True),  # recommendations
            format_memory(user_profile), # agent_memory (show memory)
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
            chat_history              # chatbox
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
            chatbox               # update chatbox
        ]
    )

    def feedback_action(feedback_type, recs, idx, feedback_log, user_id_state, agent_memory, chatbox):
        # Get current course
        if idx >= len(recs):
            chatbox = chatbox + [{"role": "assistant", "content": "All feedback collected. Thank you!"}]
            # Update agent memory after feedback loop is finished
            updated_profile = load_user_profile(user_id_state) if user_id_state else {}
            updated_memory = format_memory(updated_profile) if updated_profile else ""
            return (
                gr.update(value="All feedback collected. Thank you!", visible=True),
                gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False),
                idx, feedback_log, chatbox, "", updated_memory, gr.update(visible=False)  # agent_memory, chat_input, send_btn
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
                idx, feedback_log, chatbox, "", gr.update(visible=True)  # chat_input, send_btn enabled
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
            next_card = render_course_card(next_course)
            explanation = next_course.get('explanation', '')
            if explanation:
                next_card += f"\n**Why:**\n> {explanation}\n"
            chat_msg = f"Suggested: {next_course.get('title','?')}\nWhy:  \n{explanation}\nFeedback? (approve / adjust / reject / suggest)"
            chatbox = chatbox + [{"role": "assistant", "content": chat_msg}]
            return (
                gr.update(value=next_card, visible=True),
                gr.update(visible=True), gr.update(visible=True), gr.update(visible=True), gr.update(visible=True),
                next_idx, feedback_log, chatbox, "", gr.update(visible=False)
            )
        else:
            # Update agent memory after feedback loop is finished
            updated_profile = load_user_profile(user_id_state) if user_id_state else {}
            updated_memory = format_memory(updated_profile) if updated_profile else ""
            return (
                gr.update(value="All feedback collected. Thank you!", visible=True),
                gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False),
                next_idx, feedback_log, chatbox, "", updated_memory, gr.update(visible=False)
            )

    def reason_action(reason, recs, idx, feedback_log, user_id_state, agent_memory, chatbox):
        # Get current course
        if idx >= len(recs):
            # Update agent memory after feedback loop is finished
            updated_profile = load_user_profile(user_id_state) if user_id_state else {}
            updated_memory = format_memory(updated_profile) if updated_profile else ""
            return (
                gr.update(), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False),
                idx, feedback_log, chatbox, "", updated_memory, gr.update(visible=False)
            )
        course = recs[idx]
        course_id = course.get("id", "?")
        title = course.get("title", "?")
        feedback_type = feedback_log[-1]["feedback_type"] if feedback_log else ""
        # Update last feedback entry with reason
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
            next_card = render_course_card(next_course)
            explanation = next_course.get('explanation', '')
            if explanation:
                next_card += f"\n**Why:**\n> {explanation}\n"
            chat_msg = f"Suggested: {next_course.get('title','?')}\nWhy:  \n{explanation}\nFeedback? (approve / adjust / reject / suggest)"
            chatbox = chatbox + [{"role": "assistant", "content": chat_msg}]
            return (
                gr.update(value=next_card, visible=True),
                gr.update(visible=True), gr.update(visible=True), gr.update(visible=True), gr.update(visible=True),
                next_idx, feedback_log, chatbox, "", gr.update(visible=False)
            )
        else:
            # Update agent memory after feedback loop is finished
            updated_profile = load_user_profile(user_id_state) if user_id_state else {}
            updated_memory = format_memory(updated_profile) if updated_profile else ""
            return (
                gr.update(value="All feedback collected. Thank you!", visible=True),
                gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False),
                next_idx, feedback_log, chatbox, "", updated_memory, gr.update(visible=False)
            )

    for btn, ftype in zip([approve_btn, adjust_btn, reject_btn, suggest_btn], ["approve", "adjust", "reject", "suggest"]):
        btn.click(
            feedback_action,
            inputs=[gr.State(ftype), recs_state, rec_index_state, feedback_log_state, user_id_state, agent_memory, chatbox],
            outputs=[recommendations, approve_btn, adjust_btn, reject_btn, suggest_btn, rec_index_state, feedback_log_state, chatbox, chat_input, send_btn]
        )

    # Bind send_btn to reason_action for collecting reason
    send_btn.click(
        reason_action,
        inputs=[chat_input, recs_state, rec_index_state, feedback_log_state, user_id_state, agent_memory, chatbox],
        outputs=[recommendations, approve_btn, adjust_btn, reject_btn, suggest_btn, rec_index_state, feedback_log_state, chatbox, chat_input, send_btn]
    )


    def on_profile_submit(uid, blurb):
        try:
            result_text, data = build_profile_from_bio(uid, blurb)
            msg = f"✅ Profile created for **{uid}**.\n\n**Summary:** {result_text}"
            # Show the 'See Recommendations' button after profile creation
            return (
                gr.update(visible=True),   # profile_section
                gr.update(visible=False),  # recommend_section
                "",                       # recommendations (not used here)
                "",                       # agent_memory (not used here)
                msg,                       # profile_status (just the summary)
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
        inputs=[uid_input, blurb_input],
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

demo.launch()


