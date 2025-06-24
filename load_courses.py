#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from tqdm import tqdm
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from coachable_course_agent.load_data import load_courses

# 1. Load course catalog (including ESCO-linked skills)
courses = load_courses("data/course_catalog_esco.json")

# 2. Initialize embedding model
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2", show_progress=True)

# 3. Convert to LangChain documents
course_docs = []
for course in tqdm(courses, desc="Processing courses"):
    skill_names = ", ".join([s["name"] for s in course.get("skills", [])])
    content = f"{course['title']}. Skills: {skill_names}"
    metadata = {
        "id": course["id"],
        "title": course["title"],
        "provider": course["provider"],
        "duration_hours": course.get("duration_hours", 0),
        "level": course.get("level", "Unknown"),
        "format": course.get("format", "Unknown"),
        "url": course.get("url", ""),
        "skills": skill_names
    }
    course_docs.append(Document(page_content=content, metadata=metadata))

# 4. Save to persistent ChromaDB
persist_dir = "data/courses_chroma"
vectorstore = Chroma.from_documents(
    documents=course_docs,
    embedding=embedding_model,
    persist_directory=persist_dir
)

vectorstore.persist()
print(f"✅ Stored {len(course_docs)} courses to ChromaDB at '{persist_dir}'")
