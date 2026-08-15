# Day 13 - Full RAG (Retrieval-Augmented Generation) Pipeline

A complete implementation of **Retrieval-Augmented Generation (RAG)** using sentence embeddings, cosine similarity for semantic retrieval, and the Groq API for LLM-based answer generation.

Day 13 combines the concepts learned previously:

- **Day 11:** Basic RAG with keyword-based retrieval
- **Day 12:** Sentence embeddings and cosine similarity
- **Day 13:** Full RAG using semantic retrieval and LLM generation

---

## Overview

Day 13 focuses on building a complete **RAG pipeline** by replacing simple keyword-based retrieval with embedding-based semantic retrieval.

In the earlier RAG implementation, retrieval depended on exact keywords. This creates problems when the user's query and the knowledge base express the same meaning using different words.

For example:

```text
Knowledge Base:
"Employees receive 30 days of paid leave per year."

Query:
"How many days of vacation do employees get?"
```

The word `vacation` does not appear in the knowledge base, but `vacation` and `paid leave` have similar meanings.

Using sentence embeddings, both the knowledge-base documents and the user query are converted into vectors. **Cosine similarity** is then used to determine which document is semantically closest to the query.

The retrieved document becomes the context provided to the LLM for generating the final answer.

```text
Knowledge Base
      ↓
Document Embeddings
      ↓
User Query → Query Embedding
      ↓
Cosine Similarity
      ↓
Most Similar Document
      ↓
Retrieved Context
      ↓
LLM
      ↓
Final Answer
```

---

## RAG Pipeline

The Day 13 implementation consists of the following steps:

```text
1. Create Knowledge Base
        ↓
2. Generate Document Embeddings
        ↓
3. Receive User Query
        ↓
4. Generate Query Embedding
        ↓
5. Calculate Cosine Similarity
        ↓
6. Retrieve Highest-Scoring Document
        ↓
7. Use Document as Context
        ↓
8. Send Context + Query to LLM
        ↓
9. Generate Final Answer
```

---

## Part 1 - Knowledge Base

The knowledge base contains company-related information.

```python
knowledge_base_documents = [
    "Employees receive 30 days of paid leave per year.",

    "Employees work from the office on Tuesday, Wednesday and Thursday. "
    "Monday and Friday are optional work-from-home days.",

    "Employees receive Rs 5000 per month for travel reimbursement.",

    "Employees can claim Rs 2000 per month for home internet.",

    "Employees have a 60 day notice period."
]
```

Each item represents a document that can later be retrieved based on the user's question.

---

## Part 2 - Document Embeddings

The project uses the Sentence Transformer model:

```text
all-MiniLM-L6-v2
```

The model converts text into **384-dimensional vectors**.

```python
from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)
```

The entire knowledge base is converted into embeddings:

```python
Embedding = embedding_model.encode(
    knowledge_base_documents
)
```

Conceptually:

```text
Document 1 ──→ Embedding 1
Document 2 ──→ Embedding 2
Document 3 ──→ Embedding 3
Document 4 ──→ Embedding 4
Document 5 ──→ Embedding 5
```

Each embedding is a numerical representation of the meaning of its corresponding document.

---

## Part 3 - Query Embedding

The user's query must also be converted into an embedding.

Example:

```python
query = "How many days of vacation do any employee get in a year?"
```

The query is encoded using the same embedding model:

```python
query_embedding = embedding_model.encode(query)
```

Now both the query and the knowledge-base documents exist in the same vector space.

```text
User Query
    ↓
Sentence Transformer
    ↓
384-Dimensional Query Vector
```

---

## Part 4 - Cosine Similarity

Cosine similarity is used to compare the query embedding with each document embedding.

```python
def cosine_similarity(a, b):
    return np.dot(a, b) / (
        np.linalg.norm(a) * np.linalg.norm(b)
    )
```

The formula is:

```text
              A · B
Cosine = ───────────────
         ||A|| × ||B||
```

A higher similarity score means that the query and document are more semantically related.

---

## Part 5 - Semantic Retrieval

The `retrieve()` function compares the query embedding with every document embedding.

```python
def retrieve(query_embedding):
    scores = []

    for i, doc_embedding in enumerate(Embedding):

        score = cosine_similarity(
            query_embedding,
            doc_embedding
        )

        scores.append(
            (score, knowledge_base_documents[i])
        )

    scores.sort(reverse=True)

    return scores[0]
```

The process is:

```text
                    Query Embedding
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
     Document 1      Document 2      Document 3
     Embedding       Embedding       Embedding
          │               │               │
          ▼               ▼               ▼
       Score 1          Score 2          Score 3
          │               │               │
          └───────────────┼───────────────┘
                          ▼
                     Sort Scores
                          ↓
                  Highest Similarity
                          ↓
                   Relevant Document
```

The document with the highest similarity score becomes the context.

---

## Part 6 - Retrieved Context

Consider the query:

```text
How many days of vacation do any employee get in a year?
```

The knowledge base contains:

```text
Employees receive 30 days of paid leave per year.
```

There is no exact `vacation` keyword in the document.

However:

```text
vacation ≈ paid leave
```

Because embeddings represent semantic meaning, the system can identify the paid-leave document as the most relevant result.

```text
Query:
"How many days of vacation do employees get?"

                    ↓

              Query Embedding

                    ↓

             Similarity Search

                    ↓

Retrieved Context:
"Employees receive 30 days of paid leave per year."
```

---

## Part 7 - LLM Generation

After retrieving the relevant context, it is passed to the Groq LLM.

The project uses:

```text
llama-3.3-70b-versatile
```

The LLM function receives:

```python
ask_llm(question, context)
```

The system prompt is:

```python
system_prompt = f"""
Answer in 1 line Only and answer this question
strictly based on this context,
Do not hallucinate.

Context: {context}
"""
```

The LLM receives:

```text
Retrieved Context
       +
User Question
       ↓
     Groq LLM
       ↓
 Final Answer
```

---

## Complete Architecture

```text
┌────────────────────────────┐
│       Knowledge Base       │
│                            │
│ Leave Policy               │
│ Work From Home Policy      │
│ Travel Reimbursement       │
│ Internet Reimbursement     │
│ Notice Period              │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│    Sentence Transformer    │
│     all-MiniLM-L6-v2       │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│    Document Embeddings     │
│     384-D Vectors          │
└─────────────┬──────────────┘
              │
              │
              │
       ┌──────▼──────┐
       │ User Query  │
       └──────┬──────┘
              │
              ▼
┌────────────────────────────┐
│      Query Embedding       │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│     Cosine Similarity      │
│                            │
│ Query ↔ Document Vectors   │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│   Highest Similarity       │
│          Score             │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│     Retrieved Context      │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│          Groq LLM          │
│ llama-3.3-70b-versatile    │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│        Final Answer        │
└────────────────────────────┘
```

---

## Example

### User Query

```text
How many days of vacation do any employee get in a year?
```

### Retrieved Context

```text
Employees receive 30 days of paid leave per year.
```

### Final Answer

```text
30 days of paid leave per year.
```

The important point is that the query uses `vacation`, while the knowledge base uses `paid leave`.

Semantic retrieval allows the correct information to be retrieved without requiring exact keyword matching.

---

## Handling Unrelated Queries

The current retrieval function always returns the document with the highest similarity score.

This creates a limitation.

For example:

```text
Query:
"I love you baby"
```

This query has nothing to do with the company knowledge base.

However, because the system always selects the highest score, some document will still be returned.

A better approach is to introduce a **similarity threshold**.

```text
Highest Similarity Score
          │
          ▼
   Is score relevant?
      /         \
    Yes          No
     │            │
     ▼            ▼
Use Context    No Relevant
     │         Information
     ▼
    LLM
```

This prevents unrelated questions from receiving irrelevant context.

---

## Day 11 → Day 12 → Day 13

| Day | Concept |
|---|---|
| Day 11 | Basic RAG using keyword retrieval |
| Day 12 | Sentence embeddings and cosine similarity |
| Day 13 | Full RAG using semantic retrieval |

The progression is:

```text
Day 11
Keyword-Based RAG
      ↓
Day 12
Embeddings
      +
Cosine Similarity
      ↓
Day 13
Embedding-Based Retrieval
      +
Context
      +
LLM
      ↓
Full RAG
```

---

## Project Structure

```text
day13/
├── pyproject.toml
├── uv.lock
├── README.md
├── .gitignore
├── .python-version
├── main.py
└── full_rag.py
```

---

## Technologies Used

- Python
- Sentence Transformers
- `all-MiniLM-L6-v2`
- NumPy
- Groq API
- `llama-3.3-70b-versatile`
- python-dotenv
- UV

---

## Current Limitation

The current implementation stores all generated embeddings directly in memory.

```text
Knowledge Base
      ↓
Generate Embeddings
      ↓
Store Embeddings in RAM
```

For a few documents this is completely manageable.

However, a real-world company can have:

```text
Thousands of documents
        ↓
Millions of text chunks
        ↓
Millions of embeddings
```

Keeping all those embeddings directly in memory becomes inefficient.

There is another scalability problem with retrieval.

The current implementation performs:

```text
Query Embedding
      ↓
Compare with Document 1
      ↓
Compare with Document 2
      ↓
Compare with Document 3
      ↓
...
      ↓
Compare with Every Document
```

If there are millions of documents, calculating cosine similarity against every document for every query becomes inefficient.

---

## Why Vector Databases?

This limitation leads to the next important concept:

**Vector Databases**

Instead of storing and searching all embeddings manually:

```text
Documents
    ↓
Embeddings
    ↓
RAM
    ↓
Linear Similarity Search
```

a vector database can be used:

```text
Documents
    ↓
Embeddings
    ↓
Vector Database
    ↓
Efficient Similarity Search
    ↓
Relevant Context
```

Vector databases are designed to store and retrieve large numbers of embeddings efficiently.

This makes them an important component when RAG systems need to work with much larger knowledge bases.

---

## Key Learnings

- Understanding the complete RAG workflow
- Moving from keyword retrieval to semantic retrieval
- Creating embeddings for knowledge-base documents
- Creating embeddings for user queries
- Comparing vectors using cosine similarity
- Retrieving the most relevant document
- Using retrieved information as LLM context
- Generating context-based answers using Groq
- Understanding the limitation of always selecting the highest similarity score
- Understanding why similarity thresholds can be useful
- Understanding the scalability limitations of in-memory embeddings
- Understanding why vector databases are needed for larger RAG systems

---

## Summary

Day 13 combines the concepts of **RAG, sentence embeddings, cosine similarity, semantic retrieval, and LLM generation** into one complete pipeline.

```text
Knowledge Base
      ↓
Document Embeddings
      ↓
User Query
      ↓
Query Embedding
      ↓
Cosine Similarity
      ↓
Most Relevant Document
      ↓
Retrieved Context
      ↓
Groq LLM
      ↓
Final Answer
```

Unlike the basic keyword-based RAG from Day 11, this implementation can retrieve semantically related information even when the user's query does not contain the exact words present in the knowledge base.

This completes the basic end-to-end RAG workflow and introduces the scalability problem that leads to the use of **Vector Databases**.
