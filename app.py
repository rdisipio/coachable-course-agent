import gradio as gr
import json

# Load course catalog
with open("data/course_catalog_esco.json", "r") as f:
    course_catalog = json.load(f)

# Load agent memory
with open("data/memory/rdisipio.json", "r") as f:
    agent_memory = json.load(f)

# Company goals (hardcoded)
company_goals = "Support cross-functional collaboration and accelerate internal mobility."


# Format course display
def render_course_card(course):
    skills = ", ".join(skill["name"] for skill in course["skills"])
    return f"""
    ### [{course['title']}]({course['url']})
    **Provider**: {course['provider']}  
    **Duration**: {course['duration_hours']} hrs  
    **Level**: {course['level']} | **Format**: {course['format']}  
    **Skills**: {skills}
    """


# Dummy chatbot function
def chat_response(user_input, history):
    response = f"Echo: {user_input}"  # Replace with actual agent call
    history = history + [[user_input, response]]
    return history, history


# Memory display formatting
def format_memory(memory):
    known = "\n".join(f"- {s['preferredLabel']}" for s in memory["known_skills"])
    missing = "\n".join(f"- {s['preferredLabel']}" for s in memory["missing_skills"])
    feedback = "\n".join(f"- {f['course_id']}: {f['feedback_type']} — {f['reason']}" for f in memory["feedback_log"] if f['feedback_type'])
    return f"""### 🎯 Goal
{memory['goal']}

### ✅ Known Skills
{known}

### 🚧 Missing Skills
{missing}

### 💬 Feedback Log
{feedback}
"""


with gr.Blocks(title="Coachable Course Agent") as demo:
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("## 📚 Recommended Courses")
            for course in course_catalog:
                gr.Markdown(render_course_card(course))

        with gr.Column(scale=1):
            gr.ChatInterface(fn=chat_response)

    with gr.Row():
        with gr.Column():
            gr.Markdown(f"### 🧭 Company Goal\n> {company_goals}")

        with gr.Column():
            gr.Markdown(format_memory(agent_memory))

demo.launch()
