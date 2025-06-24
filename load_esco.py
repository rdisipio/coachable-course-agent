#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script loads ESCO skills from a CSV file and adds them to a ChromaDB vector
store using HuggingFace's sentence-transformers for embedding.
"""

import pandas as pd
from langchain.schema import Document
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

# Load ESCO skill CSV
skills_df = pd.read_csv("data/esco/skills_en.csv")

# Initialize embedding model
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2", show_progress=True)

# Convert skills to LangChain documents
documents = [
    Document(
        page_content=row["description"],
        metadata={
            "uri": row["conceptUri"],
            "label": row["preferredLabel"]
        }
    )
    for _, row in skills_df.iterrows()
]

# Create and persist vector store
persist_dir = "data/esco_chroma"
vectorstore = Chroma.from_documents(
    documents=documents,
    embedding=embedding_model,
    persist_directory=persist_dir
)

vectorstore.persist()
print(f"ESCO skill vectors saved to {persist_dir}")
