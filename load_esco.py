#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script loads ESCO skills from a CSV file and adds them to a ChromaDB vector
store using HuggingFace's sentence-transformers for embedding.
"""

import pandas as pd
import chromadb
from chromadb.config import Settings
from transformers import pipeline
from tqdm import tqdm


# Load the ESCO CSV file (e.g., data/esco/skills_en.csv)
esco_path = "data/esco/skills_en.csv"
skills_df = pd.read_csv(esco_path)

# Set up HuggingFace embedding pipeline
embedding_pipeline = pipeline(
    "feature-extraction",
    model="sentence-transformers/all-MiniLM-L6-v2",
    tokenizer="sentence-transformers/all-MiniLM-L6-v2"
)

def get_embedding(text):
    output = embedding_pipeline(text, truncation=True, padding=True, return_tensors="pt")
    return [float(x) for x in output[0][0]]  # Use mean-pooled first token for simplicity

# Initialize ChromaDB
client = chromadb.Client(Settings(
    persist_directory="data/chroma"  # <-- will persist here
))
collection = client.get_or_create_collection(name="esco_skills")

# Add ESCO skills to the vector store
for _, row in tqdm(skills_df.iterrows(), total=len(skills_df), desc="Embedding ESCO skills"):
    skill_name = row["preferredLabel"]
    concept_uri = row["conceptUri"]

    embedding = get_embedding(skill_name)

    collection.add(
        documents=[skill_name],
        embeddings=[embedding],
        ids=[concept_uri],
        metadatas=[{"name": skill_name, "uri": concept_uri}]
    )

print(f"Persisting ESCO skills to ChromaDB at {client.persist_directory}")
client.persist()
print("ESCO skills successfully added to ChromaDB.")
