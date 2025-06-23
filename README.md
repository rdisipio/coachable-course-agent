# Coachable Course Agent

*A human-AI course recommendation agent that listens, learns, and adapts.*

---

## 🧠 What It Is

**Coachable Course Agent** is an interactive learning assistant built with [LangChain](https://www.langchain.com/) and powered by [Groq](https://groq.com/), designed to recommend upskilling courses based on structured feedback, memory, and ESCO skill taxonomy.

Unlike traditional recommenders that track clicks and ratings, this agent asks—and remembers—*why* a course did or didn’t work for you.

---

## 🎯 Features

- 🔍 **Semantic course search** using ChromaDB and vectorized ESCO skills  
- 🧠 **Personalized memory** that adapts to user feedback over time  
- 💬 **Conversational interaction** with an LLM-powered agent  
- ✅ **Structured feedback** loop: not just what you liked, but why  
- 🌐 **ESCO-aligned**: all courses linked to official European skill concepts

---

## 📦 Technologies

- 🧱 **LangChain** – Agent architecture
- ⚡ **Groq** – Fast LLM inference backend
- 🧭 **ESCO** – European Skills, Competences and Occupations framework
- 🧠 **ChromaDB** – Vector database for semantic search

---

## 🚀 Coming Soon

- Feedback UI with 4 intuitive categories  
- Editable memory panel  
- Resume/LinkedIn import for profile bootstrap  
- Medium article on the design journey (Human-AI interaction focus)


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
