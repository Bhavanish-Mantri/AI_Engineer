# Day 14: Qdrant Cloud RAG

This project builds a simple retrieval-augmented generation (RAG) pipeline:

1. Loads text from `knowledge.txt`.
2. Converts each line into an embedding with `all-MiniLM-L6-v2`.
3. Stores the embeddings in a Qdrant Cloud collection.
4. Retrieves the most relevant documents for a question.
5. Sends the retrieved context to Groq using `llama-3.3-70b-versatile`.

## Requirements

- Python 3.13 or newer
- A Qdrant Cloud URL and API key
- A Groq API key

## Setup

From this directory, create and activate the virtual environment:

```powershell
uv sync
.\.venv\Scripts\Activate.ps1
```

If you are not using `uv`, install the dependencies with:

```powershell
pip install -e .
```

Create a `.env` file in the project root or workspace root:

```env
QDRANT_URL=https://your-qdrant-cluster-url
QDRANT_API_KEY=your-qdrant-api-key
GROQ_API_KEY=your-groq-api-key
```

Do not commit `.env` or expose these keys in source control.

## Run

```powershell
python qdrant.py
```

The script recreates the `knowledge` collection on each run, uploads the
documents, prints search results, and prints the final answer from Groq.

To test another question, update the `question` variable near the end of
`qdrant.py`. Add or edit one document per line in `knowledge.txt`.

## Notes

- The embedding dimension is `384`, matching `all-MiniLM-L6-v2`.
- The Qdrant collection uses cosine distance.
- The current Groq model is `llama-3.3-70b-versatile`.
- The first embedding-model run may download model files from Hugging Face.
