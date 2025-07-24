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
        path = hf_hub_download(repo_id=repo_id, filename=filename)
        with tarfile.open(path, "r:gz") as tar:
            tar.extractall(path="data/")

fetch_and_extract("datasets/rdisipio/esco-skills", "esco_chroma.tar.gz", "data/esco_chroma")
fetch_and_extract("datasets/rdisipio/esco-skills", "courses_chroma.tar.gz", "data/courses_chroma")


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

with gr.Blocks(title="Coachable Course Agent") as demo:
    user_id_state = gr.State()

    with gr.Column(visible=True) as profile_section:
        gr.Markdown("## 🔐 Create Your Profile")
        uid_input = gr.Textbox(label="User ID", placeholder="e.g. user_1")
        blurb_input = gr.Textbox(lines=5, label="LinkedIn-style Blurb")
        build_btn = gr.Button("Build Profile and Continue")
        profile_status = gr.Markdown()

        def on_profile_submit(uid, blurb):
            success, msg = build_profile(uid, blurb)
            if success:
                return (
                    gr.update(visible=False),
                    gr.update(visible=True),
                    msg,
                    uid
                )
            return None, None, msg, None

        build_btn.click(
            on_profile_submit,
            inputs=[uid_input, blurb_input],
            outputs=[profile_section, gr.Column(), profile_status, user_id_state]
        )

    with gr.Column(visible=False) as main_section:
        gr.Markdown("## 📚 Recommended Courses")
        course_md = gr.Markdown()
        chatbot = gr.ChatInterface(fn=chat_response, chatbot=gr.Chatbot(), title="💬 Ask the Coach")
        footer = gr.Markdown()

        def load_main_ui(uid):
            memory = load_memory(uid)
            courses = load_courses()
            rendered_courses = "\n\n".join(render_course_card(c) for c in courses)
            footer_content = f"### 🗭 Company Goal\n> {GOALS}\n\n" + format_memory(memory)
            return rendered_courses, footer_content

        demo.load(load_main_ui, inputs=[user_id_state], outputs=[course_md, footer])

        def always_show_profile():
            return gr.update(visible=True), gr.update(visible=False), None

        demo.load(always_show_profile, outputs=[profile_section, main_section, user_id_state])


demo.launch()
