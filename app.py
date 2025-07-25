import os
import json
import subprocess
import tarfile
import gradio as gr
from huggingface_hub import hf_hub_download

MEMORY_DIR = "data/memory"
COURSES_PATH = "data/course_catalog_esco.json"
GOALS = "Support cross-functional collaboration and accelerate internal mobility."

# ---------- Download and Extract Prebuilt ChromaDB ----------
def fetch_and_extract(repo_id, filename, target_dir):
    if not os.path.exists(target_dir):
        print(f"Fetching {filename} from {repo_id}...")
        path = hf_hub_download(repo_id=repo_id, filename=filename, repo_type="dataset")
        with tarfile.open(path, "r:gz") as tar:
            tar.extractall(path="data/")

fetch_and_extract("rdisipio/esco-skills", "esco_chroma.tar.gz", "data/esco_chroma")
fetch_and_extract("rdisipio/esco-skills", "courses_chroma.tar.gz", "data/courses_chroma")


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
    skills = ", ".join(skill["name"] for skill in course["skills"])
    return f"""### [{course['title']}]({course['url']})
**Provider**: {course['provider']}  
**Duration**: {course['duration_hours']} hrs  
**Level**: {course['level']} | **Format**: {course['format']}  
**Skills**: {skills}
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


with gr.Blocks(title="Coachable Course Agent") as demo:
    user_id_state = gr.State()
    app_mode = gr.State(value="profile")  # 'profile' or 'recommend'

    with gr.Column() as main_section:
        with gr.Column(visible=True) as profile_section:
            gr.Markdown("## 🔐 Create Your Profile")
            uid_input = gr.Textbox(label="User ID", placeholder="e.g. user_1")
            blurb_input = gr.Textbox(lines=5, label="LinkedIn-style Blurb")
            build_btn = gr.Button("Build Profile and Continue")
            profile_status = gr.Markdown()
            profile_json = gr.JSON(visible=False)

        with gr.Column(visible=False) as recommend_section:
            gr.Markdown("## 🎯 Course Recommendations (Coming Soon)")
            # Placeholder for main recommender UI
            recommend_status = gr.Markdown()
            agent_memory = gr.Markdown()

    with gr.Row() as footer:
        footer_status = gr.Markdown("👋 Ready")

    def on_profile_submit(uid, blurb):
        try:
            result_text, data = build_profile_from_bio(uid, blurb)
            msg = f"✅ Profile created for **{uid}**.\n\n**Summary:** {result_text}"
            # Switch to recommend mode, show agent memory in footer
            return (
                gr.update(visible=False),  # profile_section
                gr.update(visible=True),   # recommend_section
                msg,                       # recommend_status
                "",                        # agent_memory (placeholder)
                "",                        # profile_status (hide)
                uid,                       # user_id_state
                gr.update(value=data, visible=True),  # profile_json
                "",                        # footer_status (hide status)
                "recommend"                # app_mode
            )
        except Exception as e:
            return (
                gr.update(visible=True),   # profile_section
                gr.update(visible=False),  # recommend_section
                "",                       # recommend_status
                "",                       # agent_memory
                f"❌ Error: {e}",          # profile_status
                None,                      # user_id_state
                gr.update(visible=False),  # profile_json
                f"❌ Error: {e}",          # footer_status
                "profile"                  # app_mode
            )

    build_btn.click(
        on_profile_submit,
        inputs=[uid_input, blurb_input],
        outputs=[
            profile_section,      # show/hide
            recommend_section,    # show/hide
            recommend_status,     # update recommend status
            agent_memory,         # update agent memory
            profile_status,       # update profile status
            user_id_state,        # update user id
            profile_json,         # update profile json
            footer_status,        # update footer
            app_mode             # update app mode
        ]
    )

demo.launch()


