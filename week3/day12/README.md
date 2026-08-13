# Day 12: Sentence Embeddings and Cosine Similarity

A lightweight implementation demonstrating how to generate sentence embeddings and calculate their semantic similarity (cosine similarity) using `sentence-transformers` and `numpy`.

## Overview

This project showcases the foundational techniques used in vector search and Retrieval-Augmented Generation (RAG):
1. **Sentence Embedding**: Converting text into dense vector representations (embeddings) that capture semantic meaning. We use the compact and efficient `all-MiniLM-L6-v2` model (384 dimensions).
2. **Cosine Similarity**: Computing the dot product of two normalized vectors to determine how semantically similar the sentences are (returns a value between -1 and 1, where 1 means highly similar).

## Project Structure

```
day12/
├── pyproject.toml      # Project configuration and dependencies
├── uv.lock             # Lockfile for project dependencies
├── README.md           # Documentation
├── .gitignore          # Local git ignore patterns
├── main.py             # Entrypoint script
└── embedding_rag.py    # Embedding generation and similarity script
```

## Features

- **Local Vector Encoding**: Uses the Hugging Face `sentence-transformers` library to load and execute model inference locally.
- **Cosine Similarity Math**: Built using `numpy` to calculate cosine similarity:
  $$\text{Cosine Similarity}(A, B) = \frac{A \cdot B}{\|A\| \|B\|}$$
- **Modern Packaging**: Configured with `pyproject.toml` ready for use with the `uv` package manager.

## Setup & Installation

### Prerequisites

Ensure you have [uv](https://github.com/astral-sh/uv) installed, or you can use standard Python `pip` with a virtual environment.

### 1. Install Dependencies

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

pip install .
```

## Running the Application

To execute the embedding similarity calculation:

```bash
python embedding_rag.py
```

### Example Output

By default, the script compares:
- $t_1$: `"There are 24 leaves"`
- $t_2$: `"My name is Bhavanish"`

Since these two statements are semantically unrelated, the resulting cosine similarity will be very low (close to `0.05`).
