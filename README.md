---
title: Coachable Course Agent
emoji: 📚
colorFrom: yellow
colorTo: indigo
sdk: gradio
app_file: app.py
pinned: false
sdk_version: 5.43.1
---

# Coachable Course Agent

An AI-powered, feedback-aware course recommendation system designed for human-AI interaction in HR tech.  
This agent doesn't just rank courses — it walks alongside the user, learning from feedback and helping shape a career path.

---

This project started as a clever demo. It has since grown into something more fundamental: a principled foundation for human-AI interaction in learning and career growth.

The goal is simple but ambitious:  
**Align what’s technically possible with what is humanly meaningful.**

Guided by the [Google People + AI Guidebook](https://pair.withgoogle.com/guidebook/) and best practices from UX research, the agent is designed not just to recommend courses, but to *listen, adapt, and explain itself*. Every recommendation is transparent, every piece of feedback shapes the next interaction, and every design choice centers on trust and user agency.

This repo is intentionally unfinished in places. It leaves space for collaboration, critique, and refinement — because building human-centered AI is not a solo act.
I believe that a project like this can make a difference in the world: helping people see their skills, grow their potential, and find paths they might not have imagined. 

As Muse once sang, let’s 
🎵 *“conspire to ignite all the souls that would die just to feel alive.”* 🎵


## ✨ Key Features

- **Profile Builder Agent**: Extracts skills, goals, and intent from a LinkedIn-style blurb using LLMs and ESCO skill matching.
- **Course Recommender Agent**: Suggests courses tailored to missing skills, learning preferences, and inferred goals.
- **Structured Feedback Loop**: Supports "approve", "adjust", "reject", or open-ended suggestions, and updates the profile accordingly.
- **Semantic Skill Matching**: Uses a ChromaDB vector store populated with ESCO skill embeddings for robust skill inference.
- **Extensible Architecture**: Built with LangChain agents and Groq-hosted LLaMA models.

## 🧱 Tech Stack

- 🦜 LangChain (`AgentType.CONVERSATIONAL_REACT_DESCRIPTION`)
- 🧠 LLM: `llama3-70b-8192` via Groq API
- 🧬 ESCO Skill Data (v1.2)
- 🔎 ChromaDB (for skill and course vector similarity)
- 📚 HuggingFace Sentence Transformers (`all-MiniLM-L6-v2`)

## Further Reading
- Medium Story: [More Than Thumbs-Up: A Feedback-Aware Course Recommendations](https://medium.com/data-science-collective/more-than-thumbs-up-feedback-aware-course-recommendations-guided-by-feedback-not-just-clicks-bfba3fbb214c)

## 🚀 Quickstart

1. **Clone the repo**  
   ```bash
   git clone https://huggingface.co/spaces/rdisipio/coachable-course-agent
   cd coachable-course-agent
   ```

2.   Install dependencies
```
pipenv install
pipenv shell
```

3. Prepare Data
Load ESCO skills and course catalog:

```
python scripts/load_skills.py
python scripts/load_courses.py
```

4. Run Agent
Start the interactive profile builder and course recommender:

```
python scripts/build_profile_from_linkedin.py
python scripts/get_recommendations.py
```

🧠 Future Directions
Incorporate org charts and role progression paths

Add pacing preferences (e.g. 3 months vs 12 months)


---

## 👤 Author

Built by Riccardo Di Sipio, exploring how agents can collaborate and not just recommend.

---

## 📖 License

MIT License


### 📦 Setup & Data

#### 🔹 ESCO Skill Dataset

To enable skill normalization, this project uses the [ESCO](https://esco.ec.europa.eu/en/download) framework.

**Steps to download:**
1. Go to: [https://esco.ec.europa.eu/en/download](https://esco.ec.europa.eu/en/download)
2. Download the latest CSV archive (ESCO v1.2 or newer).
3. Extract the archive to `data/esco`. Make sure it contains a file called `skills_en.csv`.

📁 A placeholder file with instructions is available at:
```
data/esco/readme.txt
```