#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
courses_collection = Chroma(
    persist_directory="data/courses_chroma",
    embedding_function=embedding_model
)

# Print number of stored courses
try:
    n_courses = courses_collection._collection.count()
    print(f"Number of stored courses in Chroma: {n_courses}")
except Exception as e:
    print(f"Could not count courses: {e}")

# Print a few sample documents (if any)
try:
    docs = courses_collection._collection.get(limit=3)
    print("Sample documents:")
    for i, doc in enumerate(docs["documents"]):
        print(f"--- Document {i+1} ---")
        print(doc)
except Exception as e:
    print(f"Could not fetch sample documents: {e}")
