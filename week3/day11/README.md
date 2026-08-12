# Day 11: Simple Retrieval-Augmented Generation (RAG)

A lightweight implementation of a Retrieval-Augmented Generation (RAG) system using Python, the Groq API (`llama-3.3-70b-versatile`), and keyword-based retrieval.

## Overview

This project demonstrates the core concepts of RAG:
1. **Knowledge Base**: Storing raw domain-specific data locally (in this case, structured information about Bhavanish Mantri).
2. **Retrieval**: Extracting the most relevant context from the knowledge base based on keywords matching the user's query.
3. **Generation**: Combining the retrieved context with the user's question, formulating a system prompt to prevent hallucinations, and sending the payload to the LLM (Groq) for a precise, context-bounded answer.

## Project Structure

```
day11/
├── pyproject.toml      # Project configuration and dependencies (uv)
├── uv.lock             # Lockfile for project dependencies
├── README.md           # Documentation
├── .gitignore          # Git ignore patterns
├── main.py             # Entrypoint script
└── simple_rag.py       # Simple RAG pipeline implementation
```

## Features

- **Strict Prompting**: System prompt restricts the LLM to answer in exactly one line and strictly base its response on the retrieved context, eliminating hallucination.
- **Local Retrieval**: Keyword lookup indexing matching key phrases in queries to retrieve clean context.
- **Modern Stack**: Designed to run with `uv` and integrates `python-dotenv` for API key management.

## Setup & Installation

### Prerequisites

Ensure you have [uv](https://github.com/astral-sh/uv) installed, or you can use standard Python `pip` with a virtual environment.

### 1. Environment Configuration

Create a `.env` file in the root of this folder (or use the one in the workspace root) and add your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### 2. Install Dependencies

Using `uv`:
```bash
uv sync
```

Alternatively, using standard virtualenv and pip:
```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate

pip install -r pyproject.toml
```

## Running the Application

To run the simple RAG script:

```bash
python simple_rag.py
```

### Example

Query: `"what is the interests of Bhavanish Mantri"`
Output: `Bhavanish Mantri is interested in AI and Machine Learning.`
