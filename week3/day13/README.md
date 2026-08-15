# Day 13: Full RAG (Retrieval-Augmented Generation) Pipeline

A complete, lightweight Retrieval-Augmented Generation (RAG) pipeline built using local sentence embeddings, vector retrieval via cosine similarity, and text generation via the Groq API.

## Overview

This project builds upon the embeddings concepts from Day 12 to implement a full, end-to-end RAG workflow:
1. **Knowledge Base**: A local corpus of document strings representing company policy (leave days, remote work schedule, travel and internet reimbursements, notice periods).
2. **Local Embedding Generation**: Converting the knowledge base documents into 384-dimensional dense vectors using the Hugging Face `all-MiniLM-L6-v2` model from `sentence-transformers`.
3. **Semantic Retrieval**: 
   - Encoding the user's query into the same vector space.
   - Calculating the cosine similarity between the query embedding and each document embedding using `numpy`.
   - Retrieving the document with the highest similarity score to act as context.
4. **Augmented LLM Generation**:
   - Sending the retrieved context and user query to the Groq API utilizing the `llama-3.3-70b-versatile` model.
   - Instructing the LLM via system prompts to answer strictly in one line based on the provided context without hallucinating.

## Project Structure

```
day13/
├── pyproject.toml      # Project configuration and dependencies
├── uv.lock             # Lockfile for project dependencies
├── README.md           # Project documentation
├── .gitignore          # Git ignore patterns for Day 13
├── .python-version     # Python runtime version identifier
├── main.py             # Entrypoint script
└── full_rag.py         # Complete RAG pipeline (Retrieval + Generation)
```

## Features

- **Local Vector Encoding**: Uses `sentence-transformers` to generate embeddings locally.
- **Custom Similarity Engine**: Computes cosine similarity manually using `numpy`:
  $$\text{Cosine Similarity}(a, b) = \frac{a \cdot b}{\|a\| \|b\|}$$
- **State-of-the-Art Language Model**: Integrates the `llama-3.3-70b-versatile` model via the `groq` SDK for fast, high-quality generation.
- **Strict Context Control**: System prompts force the model to answer in exactly one line, using only the provided context to prevent hallucinations.
- **Modern Packaging**: Configured with `pyproject.toml` and lock files ready for `uv` or standard Python virtual environments.

## Setup & Installation

### Prerequisites

1. Install [uv](https://github.com/astral-sh/uv) (recommended) or use standard Python.
2. Obtain a Groq API Key from the [Groq Console](https://console.groq.com/).

### 1. Install Dependencies

Using `uv`:
```bash
uv sync
```

Or using standard `pip` and virtualenv:
```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate

pip install -r pyproject.toml
```

### 2. Configure Environment Variables

Create a `.env` file in the root of the `day13` directory:
```env
GROQ_API_KEY=your_actual_groq_api_key_here
```

## Running the Application

To execute the full RAG pipeline:

```bash
python full_rag.py
```

### Example

- **User Query**: `"How many days of vacation do any employee get in a year ?"`
- **Retrieved Context**: `"Employees receive 30 days of paid leave per year."`
- **LLM Output**: `30 days of paid leave per year.`
