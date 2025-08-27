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
**Align what's technically possible with what is humanly meaningful.**

Guided by the [Google People + AI Guidebook](https://pair.withgoogle.com/guidebook/) and best practices from UX research, the agent is designed not just to recommend courses, but to *listen, adapt, and explain itself*. Every recommendation is transparent, every piece of feedback shapes the next interaction, and every design choice centers on trust and user agency.

This repo is intentionally unfinished in places. It leaves space for collaboration, critique, and refinement — because building human-centered AI is not a solo act.

I believe that a project like this can make a difference in the world: helping people see their skills, grow their potential, and find paths they might not have imagined. As Muse once sang, let's 

🎵 *"conspire to ignite all the souls that would die just to feel alive."* 🎵

---

## ✨ Key Features

- **Memory Editor**: Complete user control over profile data with real-time synchronization
- **Intelligent Course Matching**: ESCO framework integration with confidence scoring and detailed explanations
- **Smart Feedback System**: 3-button interface with LLM-powered classification
- **Cross-Platform Experience**: Responsive design optimized for desktop and mobile
- **Privacy-First**: All data stored locally, no external databases

## 🏗️ Technical Stack

- **Frontend**: Gradio with robust output management system
- **LLM**: Groq Llama3-70b for explanations and feedback classification
- **Embeddings**: `all-MiniLM-L6-v2` for semantic similarity
- **Vector Database**: ChromaDB for efficient course retrieval
- **Skills Framework**: ESCO (European Skills, Competences, and Occupations)
- **Agent Framework**: LangChain with conversational react description

## 🚀 Quick Start

```bash
git clone https://huggingface.co/spaces/rdisipio/coachable-course-agent
cd coachable-course-agent
pipenv install && pipenv shell
export GROQ_API_KEY="your_groq_api_key_here"
python app.py
```

## 📊 Course Data Pipeline

The system includes a comprehensive course scraping and consolidation pipeline:

- **42 topics** across 8 domains (Computer Science, Business, Sciences, Environmental Studies, etc.)
- **Multi-platform scraping** (Coursera, Udemy, edX) with 57+ course files
- **ESCO skills matching** for semantic course categorization
- **Deduplication and consolidation** pipeline for clean recommendations

## 📚 Further Reading

- **Medium Story**: [More Than Thumbs-Up: A Feedback-Aware Course Recommendations](https://medium.com/data-science-collective/more-than-thumbs-up-feedback-aware-course-recommendations-guided-by-feedback-not-just-clicks-bfba3fbb214c)
- **Google PAIR Guidelines**: [Human-Centered AI Design](https://pair.withgoogle.com/guidebook/)
- **ESCO Framework**: [European Skills Taxonomy](https://esco.ec.europa.eu/en)

## 🤝 Contributing

This project prioritizes human-centered AI design principles. When contributing:
1. Follow PAIR guidelines for transparency and user agency
2. Test across platforms and consider inclusive design
3. Maintain privacy-first architecture with local data storage
4. Document UX decisions and their impact on user understanding

## 📦 ESCO Data Setup

To enable skill normalization:
1. Download ESCO v1.2+ from: [https://esco.ec.europa.eu/en/download](https://esco.ec.europa.eu/en/download)
2. Extract to `data/esco/` ensuring `skills_en.csv` is present
3. Run: `python scripts/load_esco.py`

---

**Author**: Riccardo Di Sipio  
**License**: MIT  

*This project demonstrates that AI systems can be both technically sophisticated and genuinely user-empowering when built with principled human-centered design.*
