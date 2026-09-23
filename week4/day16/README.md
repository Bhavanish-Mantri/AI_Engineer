# Day 16: RAG Evaluation

This folder contains scripts and datasets for evaluating a Retrieval-Augmented Generation (RAG) system using Large Language Models (LLMs) as judges.

## Files
- `rag_eval.py`: The main script that performs RAG evaluation across precision, recall, faithfulness, relevancy, and correctness using Groq LLMs.
- `knowledge.json`: The knowledge base dataset that serves as ground truth and documents.

## Usage
1. Make sure to have a `.env` file with `GROQ_API_KEY`, `QDRANT_URL`, and `QDRANT_API_KEY`.
2. Run `python rag_eval.py`.
