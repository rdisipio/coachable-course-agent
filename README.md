# 🧭 Coachable Course Agent

An AI-powered, feedback-aware course recommendation system designed for human-AI interaction in HR tech. Inspired by the structure of Dante's Divine Comedy, this agent doesn't just rank courses — it walks alongside the user, learning from feedback and helping shape a career path.

## ✨ Key Features

- **Profile Builder Agent**: Extracts skills, goals, and intent from a LinkedIn-style blurb using LLMs and ESCO skill matching.
- **Course Recommender Agent**: Suggests courses tailored to missing skills, learning preferences, and inferred goals.
- **Structured Feedback Loop**: Supports "approve", "adjust", "reject", or open-ended suggestions — and updates the profile accordingly.
- **Semantic Skill Matching**: Uses a ChromaDB vector store populated with ESCO skill embeddings for robust skill inference.
- **Extensible Architecture**: Built with LangChain agents and Groq-hosted LLaMA models.

## 🧱 Tech Stack

- 🦜 LangChain (`AgentType.CONVERSATIONAL_REACT_DESCRIPTION`)
- 🧠 LLM: `llama3-70b-8192` via Groq API
- 🧬 ESCO Skill Data (v1.2)
- 🔎 ChromaDB (for skill and course vector similarity)
- 📚 HuggingFace Sentence Transformers (`all-MiniLM-L6-v2`)

## 🚀 Quickstart

1. **Clone the repo**  
   ```bash
   git clone https://github.com/rdisipio/coachable-course-agent.git
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

Web interface with feedback memory and visualization

---

## 👤 Author

Built by Riccardo Di Sipio, exploring how agents can collaborate—not just recommend.

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
