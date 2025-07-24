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

with gr.Blocks(title="Coachable Course Agent") as demo:
    user_id_state = gr.State()
    main_section_visible = gr.State(value=False)

    with gr.Column(visible=True) as profile_section:
        gr.Markdown("## 🔐 Create Your Profile")
        uid_input = gr.Textbox(label="User ID", placeholder="e.g. user_1")
        blurb_input = gr.Textbox(lines=5, label="LinkedIn-style Blurb")
        build_btn = gr.Button("Build Profile and Continue")
        profile_status = gr.Markdown()

    # Main UI: 2 columns (courses/chat) + footer, all hidden initially
    with gr.Column(visible=False) as main_section:
        with gr.Row():
            with gr.Column(scale=2):
                section_title = gr.Markdown("## 📚 Recommended Courses")
                course_md = gr.Markdown()
            with gr.Column(scale=1):
                chatbot = gr.ChatInterface(fn=chat_response, chatbot=gr.Chatbot(), title="💬 Ask the Coach")
        footer = gr.Markdown()

    # Profile submit logic
    def on_profile_submit(uid, blurb):
        success, msg = build_profile(uid, blurb)
        if success:
            return (
                gr.update(visible=False),  # Hide profile section
                msg,
                uid,
                True,  # Show main section
                gr.update(visible=True)  # Show main section
            )
        return None, msg, None, False, gr.update(visible=False)

    build_btn.click(
        on_profile_submit,
        inputs=[uid_input, blurb_input],
        outputs=[profile_section, profile_status, user_id_state, main_section_visible, main_section]
    )


    def load_main_ui(uid, visible):
        if not visible or uid is None or not os.path.exists(f"{MEMORY_DIR}/{uid}.json"):
            # Hide all children and show warning in footer
            return (
                gr.update(value="", visible=False),  # section_title
                gr.update(value="", visible=False),  # course_md
                gr.update(visible=False),             # chatbot
                gr.update(value="⚠️ No profile found. Please create one above.", visible=True)  # footer
            )
        memory = load_memory(uid)
        courses = load_courses()
        rendered_courses = "\n\n".join(render_course_card(c) for c in courses)
        footer_content = f"### 🗭 Company Goal\n> {GOALS}\n\n" + format_memory(memory)
        return (
            gr.update(value="## 📚 Recommended Courses", visible=True),
            gr.update(value=rendered_courses, visible=True),
            gr.update(visible=True),
            gr.update(value=footer_content, visible=True)
        )

    demo.load(
        load_main_ui,
        inputs=[user_id_state, main_section_visible],
        outputs=[section_title, course_md, chatbot, footer]
    )

    def always_show_profile():
        return gr.update(visible=True), None, False, gr.update(visible=False)

    demo.load(always_show_profile, outputs=[profile_section, user_id_state, main_section_visible, main_section])


demo.launch()
