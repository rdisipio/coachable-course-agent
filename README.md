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

## ✨ What This Agent Does

The Coachable Course Agent bridges the gap between personal career development and organizational needs by:

- **Analyzing your background and goals** to identify skills and learning gaps using the ESCO framework
- **Finding courses that benefit both** your career growth and company objectives  
- **Explaining recommendations transparently** with confidence scores and detailed reasoning
- **Learning from your feedback** to improve future suggestions through intelligent classification
- **Giving you full control** over your profile data and the AI's "memory"

## 🌟 Key Features

### **🧠 Memory Editor - Complete User Control**
- **View and edit your complete profile** including goals, skills, and feedback history
- **Real-time synchronization** across all interface displays
- **Remove incorrectly identified skills** with one click
- **Clear feedback history** when you want a fresh start
- **Full data ownership** - everything stored locally, not in external databases

### **🎯 Intelligent Course Matching**
- **ESCO framework integration** - Uses human-curated European skills taxonomy
- **Dual-purpose filtering** - Each course evaluated for both personal and organizational value
- **Confidence scoring** - Visual bars show recommendation strength
- **Detailed explanations** - "Why" sections and "Because" chips show reasoning factors

### **💬 Smart Feedback System**
- **3-button interface** - Clean Keep/Adjust/Reject options
- **LLM-powered classification** - Automatically categorizes feedback patterns with emojis
- **Platform-aware design** - Optional explanations work well on mobile and desktop
- **Batch processing** - Feedback improves future recommendation cycles

### **📱💻 Cross-Platform Experience**
- **Desktop optimized** for detailed feedback and course research
- **Mobile friendly** for exploration and quick feedback
- **Progressive disclosure** - Instructions available but not overwhelming
- **Responsive design** - Works seamlessly across devices

## 🏗️ Technical Architecture

### **Core Components**
- **Profile Builder** - Extracts skills from LinkedIn-style descriptions using LLM agents
- **Vector Store** - ChromaDB for semantic course matching with ESCO embeddings
- **Justification Chain** - LLM-powered explanation generation for each recommendation
- **Feedback Processor** - Intelligent feedback classification and storage
- **Memory Store** - Profile management with real-time synchronization
- **Output Manager** - Robust UI state management to prevent interface bugs

### **AI/ML Stack**
- **Embeddings**: `all-MiniLM-L6-v2` for semantic similarity
- **Vector Database**: ChromaDB for efficient course retrieval
- **LLM**: Groq Llama3-70b for explanations and feedback classification
- **Skills Taxonomy**: ESCO (European Skills, Competences, and Occupations) framework
- **Agent Framework**: LangChain with conversational react description

## 🎨 User Experience Design

Built following Google People + AI Research guidelines for responsible AI interaction:

### **Transparency & Trust**
- **Clear capabilities and limitations** explained in comprehensive instructions
- **Confidence scores** for every recommendation with visual indicators
- **Detailed reasoning** showing why each course was suggested
- **Technical transparency** about ESCO framework and batch processing

### **User Agency & Control**
- **Memory Editor** provides unprecedented control over AI's knowledge about you
- **User-initiated workflow** - every step requires explicit user action
- **Data ownership** - all information stored locally, fully exportable
- **Real-time editing** with immediate reflection across the interface

### **Bias Mitigation**
- **Human-curated taxonomy** (ESCO) instead of algorithmic clustering
- **LLM-based feedback classification** to avoid cognitive bias from predefined categories
- **Inclusive design** considerations throughout the interface
- **Open feedback collection** without anchoring users to specific responses

## 🚀 Getting Started

### **Prerequisites**
- Python 3.8+
- Pipenv for dependency management
- Groq API key (for LLM-powered explanations)

### **Installation**
```bash
git clone https://huggingface.co/spaces/rdisipio/coachable-course-agent
cd coachable-course-agent
pipenv install
pipenv shell
```

### **Configuration**
```bash
export GROQ_API_KEY="your_groq_api_key_here"
```

### **Run the Application**
```bash
python app.py
```

Navigate to the provided local URL to access the Gradio interface.

## 📊 Data & Privacy

### **Local Storage Only**
- **No external databases** - Everything remains on your machine
- **JSON profile files** in the `data/memory` directory
- **Full data transparency** - Human-readable files you can inspect anytime
- **Export capability** - Access your raw profile data whenever needed

### **External Services**
- **Groq API** - Only for generating course explanations (no profile data sent)
- **HuggingFace** - Pre-built ESCO embeddings and course database download
- **No tracking** - No analytics or user behavior monitoring

## 🧪 Development

### **Project Structure**
```
coachable-course-agent/
├── app.py                          # Main Gradio interface with GradioOutputManager
├── coachable_course_agent/         # Core agent modules
│   ├── linkedin_tools.py           # Profile extraction and ESCO matching
│   ├── vector_store.py             # Course retrieval and similarity search
│   ├── justifier_chain.py          # LLM-powered explanation generation
│   ├── feedback_processor.py       # Intelligent feedback classification
│   └── memory_store.py             # Profile management and real-time sync
├── scripts/                        # Data loading and utility scripts
├── data/                          # Local data storage and ESCO taxonomy
└── docs/                          # Additional documentation
```

### **Key Design Decisions**
- **Named output management** eliminates UI bugs through type-safe component handling
- **LLM feedback classification** prevents cognitive bias from keyword matching
- **Batch recommendation system** with clear expectations about when feedback takes effect
- **Local data storage** prioritizes user privacy and control
- **Human-curated taxonomy** mitigates algorithmic bias in skill categorization

## 📚 Further Reading

- **Medium Story**: [More Than Thumbs-Up: A Feedback-Aware Course Recommendations](https://medium.com/data-science-collective/more-than-thumbs-up-feedback-aware-course-recommendations-guided-by-feedback-not-just-clicks-bfba3fbb214c)
- **Google PAIR Guidelines**: [Human-Centered AI Design](https://pair.withgoogle.com/guidebook/)
- **ESCO Framework**: [European Skills Taxonomy](https://esco.ec.europa.eu/en)
- **Research Inspiration**: [Who is Coaching Our AI Agents?](https://medium.com/@rheault.claudel/who-is-coaching-our-ai-agents-1d460b20cd5e)

## 🤝 Contributing

This project prioritizes human-centered AI design principles. When contributing:

1. **Follow PAIR guidelines** - Enhance transparency, user agency, or bias mitigation
2. **Test across platforms** - Ensure mobile and desktop experiences work well
3. **Document UX decisions** - Explain how changes improve user understanding or control
4. **Maintain privacy** - Preserve local data storage and user ownership
5. **Consider inclusivity** - Design for diverse users and use cases

## 🧠 Future Directions

- **Organizational integration** - Incorporate role progression paths and team dynamics
- **Learning pacing** - Add preferences for different learning timelines (3 months vs 12 months)
- **Skills trending** - Identify emerging skills within organization contexts
- **Accessibility enhancements** - Continued refinement of cross-platform experience

---

## 👤 Author

Built by Riccardo Di Sipio, exploring how agents can collaborate and not just recommend.

## 📖 License

MIT License

---

### 📦 Setup & Data

#### 🔹 ESCO Skill Dataset

To enable skill normalization, this project uses the [ESCO](https://esco.ec.europa.eu/en/download) framework.

**Steps to download:**
1. Go to: [https://esco.ec.europa.eu/en/download](https://esco.ec.europa.eu/en/download)
2. Download the latest CSV archive (ESCO v1.2 or newer)
3. Extract the archive to `data/esco`. Make sure it contains a file called `skills_en.csv`

📁 A placeholder file with instructions is available at: `data/esco/readme.txt`

*This project demonstrates that AI systems can be both technically sophisticated and genuinely user-empowering when built with principled human-centered design.*

# Coachable Course Agent

An AI-powered, feedback-aware course recommendation system designed for human-AI interaction in HR tech.  
This agent doesn't just rank courses — it walks alongside the user, learning from feedback and helping shape a career path.

---

This project started as a clever demo. It has since grown into something more fundamental: a principled foundation for human-AI interaction in learning and career growth.

The goal is simple but ambitious:  
**Align what’s technically possible with what is humanly meaningful.**

Guided by the [Google People + AI Guidebook](https://pair.withgoogle.com/guidebook/) and best practices from UX research, the agent is designed not just to recommend courses, but to *listen, adapt, and explain itself*. Every recommendation is transparent, every piece of feedback shapes the next interaction, and every design choice centers on trust and user agency.

This repo is intentionally unfinished in places. It leaves space for collaboration, critique, and refinement — because building human-centered AI is not a solo act.

I believe that a project like this can make a difference in the world: helping people see their skills, grow their potential, and find paths they might not have imagined. As Muse once sang, let’s 

🎵 *“conspire to ignite all the souls that would die just to feel alive.”* 🎵

---

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