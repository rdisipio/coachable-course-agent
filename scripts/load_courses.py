#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from tqdm import tqdm
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from coachable_course_agent.load_data import load_courses

def clean_provider_name(provider):
    """
    Clean provider name by removing duplicate first letters.
    If the first two letters are the same and both uppercase, drop the first one.
    E.g., "IIllinois Tech" -> "Illinois Tech", "IIBM" -> "IBM"
    """
    if not provider or len(provider) < 2:
        return provider
    
    # Check if first two letters are the same and both uppercase
    if provider[0] == provider[1] and provider[0].isupper() and provider[1].isupper():
        return provider[1:]  # Drop the first letter
    
    return provider

# 1. Load course catalog (including ESCO-linked skills)
course_data = load_courses("data/course_catalog_esco.json")

# Handle both old format (direct array) and new format (with metadata)
if isinstance(course_data, dict) and 'courses' in course_data:
    courses = course_data['courses']
    print(f"📊 Loaded {len(courses)} courses from catalog with metadata")
elif isinstance(course_data, list):
    courses = course_data
    print(f"📊 Loaded {len(courses)} courses from legacy format")
else:
    print("❌ Unexpected course data format")
    sys.exit(1)

# 2. Initialize embedding model
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2", show_progress=True)

# 3. Convert to LangChain documents
course_docs = []
for course in tqdm(courses, desc="Processing courses"):
    skill_names = ", ".join([s["name"] for s in course.get("skills", [])])
    content = f"{course['title']}. Skills: {skill_names}"
    
    # Clean the provider name during loading
    cleaned_provider = clean_provider_name(course["provider"])
    
    metadata = {
        "id": course["id"],
        "title": course["title"],
        "provider": cleaned_provider,  # Use cleaned provider name
        "source_platform": course.get("source_platform", ""),
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
