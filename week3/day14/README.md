# Day 14 - Qdrant Cloud RAG

Day 14 focuses on integrating **Qdrant Cloud**, a vector database, into a RAG system.

In the previous RAG implementation, embeddings were stored and searched directly in Python. This works for small knowledge bases, but it becomes difficult to manage as the number of documents increases.

Qdrant solves this by storing the embeddings and performing similarity search for us.

The main RAG flow is:

```text
Knowledge Base
      ↓
Sentence Embeddings
      ↓
Qdrant Cloud
      ↓
Similarity Search
      ↓
Relevant Context
      ↓
Groq LLM
      ↓
Final Answer
```

## Why Use a Vector Database?

The previous implementation compared the query embedding with every document using a linear search.

This creates three main problems as the knowledge base grows:

- **Time:** Searching every vector becomes slower with a large number of documents.
- **Persistence:** Embeddings stored only on the local machine can be lost if the program or machine is unavailable.
- **Memory:** Storing a large number of embeddings locally requires significant memory.

Qdrant addresses these problems by providing a dedicated system for storing and searching vector embeddings.

## What is Qdrant?

Qdrant is a **vector database** designed to store and search vector embeddings.

Instead of storing embeddings directly inside the Python program:

```text
Python Program
      ↓
Embeddings in Memory
      ↓
Linear Search
```

the embeddings are stored in Qdrant:

```text
Python Program
      ↓
Embeddings
      ↓
Qdrant Cloud
      ↓
Vector Search
```

Qdrant also provides persistence, so the stored vectors remain available even when the local Python program is stopped.

## Qdrant Concepts

Qdrant uses a few important concepts.

### Collection

A **collection** is similar to a table in a traditional database.

The project uses a collection named:

```text
knowledge
```

The collection stores the vectors generated from the knowledge base.

### Point

A **point** represents one stored item in a Qdrant collection.

Each point contains:

```text
ID
Vector
Payload
```

For example:

```text
Point
├── ID
├── Vector
└── Payload
```

### Vector

The vector is the embedding generated from a document.

This project uses:

```text
all-MiniLM-L6-v2
```

which produces:

```text
384-dimensional vectors
```

### Payload

The payload contains the original text from which the vector was created.

This is important because the vector is used for similarity search, but the original text is needed as context for the LLM.

```text
Vector
   +
Payload
```

The vector helps find the relevant document, while the payload provides the actual text that can be sent to the LLM.

## Project Flow

### 1. Load Knowledge Base

The knowledge is stored in:

```text
knowledge.txt
```

Each line represents a document.

```text
Document 1
Document 2
Document 3
...
```

The Python program reads the file and creates a list of documents.

### 2. Generate Embeddings

Each document is converted into an embedding using:

```text
all-MiniLM-L6-v2
```

```text
Document
   ↓
Sentence Transformer
   ↓
384-dimensional Vector
```

### 3. Create Qdrant Collection

A Qdrant collection is created with:

```text
Vector Size: 384
Distance: Cosine
```

The cosine distance is used to measure the similarity between the query vector and stored vectors.

### 4. Create Qdrant Points

Each document embedding is converted into a Qdrant point.

```text
Point
├── ID
├── Vector
└── Payload
      └── Original Document
```

The points are then uploaded to the `knowledge` collection.

### 5. Search Qdrant

When a user asks a question, the question is first converted into an embedding.

```text
User Question
      ↓
Sentence Transformer
      ↓
Query Vector
```

The query vector is then sent to Qdrant.

Qdrant searches the collection and returns the most similar points.

The project requests the top 3 results.

```text
Query Vector
      ↓
Qdrant Search
      ↓
Top 3 Similar Points
      ↓
Payloads
```

### 6. Retrieve Context

The payload from the returned points contains the original text.

For example:

```text
Search Result 1
Score: 0.48
Payload: Employees receive 24 days of paid leave per year.
```

The retrieved text becomes the context for the LLM.

### 7. Generate Answer

The retrieved context and the user's question are sent to the Groq LLM.

```text
Question
   +
Retrieved Context
   ↓
Groq LLM
   ↓
Final Answer
```

The project uses:

```text
llama-3.3-70b-versatile
```

## Complete Architecture

```text
┌──────────────────────────┐
│      knowledge.txt       │
│                          │
│  Document 1              │
│  Document 2              │
│  Document 3              │
│  ...                     │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│   Sentence Transformer   │
│    all-MiniLM-L6-v2      │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│   384-D Embeddings       │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│      Qdrant Cloud        │
│                          │
│       Collection         │
│        knowledge         │
│                          │
│  ┌────────────────────┐  │
│  │ ID                 │  │
│  │ Vector             │  │
│  │ Payload             │  │
│  └────────────────────┘  │
└────────────┬─────────────┘
             │
             │
      User Question
             │
             ▼
┌──────────────────────────┐
│    Query Embedding       │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│      Qdrant Search       │
│                          │
│   Cosine Similarity      │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│     Top 3 Results        │
│                          │
│   Vector + Payload       │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│      Retrieved Context   │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│         Groq LLM         │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│       Final Answer       │
└──────────────────────────┘
```

## Project Structure

```text
day14/
├── .gitignore
├── .python-version
├── README.md
├── knowledge.txt
├── main.py
├── pyproject.toml
├── qdrant.py
└── uv.lock
```

## Technologies Used

- Python
- Qdrant Cloud
- Qdrant Client
- Sentence Transformers
- `all-MiniLM-L6-v2`
- NumPy
- Groq API
- python-dotenv
- UV

---

### Qdrant Search

Qdrant searches the stored document embeddings using the query embedding.

Example:

```text
Score: 0.480

Employees receive 30 days of paid leave per year.
```

Other results may also be returned because the system requests the top 3 matches.

### Retrieved Context

```text
Employees receive 30 days of paid leave per year.
```

### LLM Answer

```text
Employees receive 30 days of paid leave per year.
```

## Upsert

The project uses Qdrant's **upsert** operation to upload points.

Upsert combines:

```text
Insert + Update
```

If a point with the same ID already exists, it can be updated. Otherwise, the point is inserted.

This allows the knowledge-base vectors to be uploaded to the collection without manually handling each case.

## Day 13 vs Day 14

### Day 13

```text
Knowledge Base
      ↓
Embeddings
      ↓
Embeddings Stored in Memory
      ↓
Linear Similarity Search
      ↓
Relevant Context
      ↓
     LLM
```

### Day 14

```text
Knowledge Base
      ↓
Embeddings
      ↓
Qdrant Cloud
      ↓
Vector Search
      ↓
Relevant Context
      ↓
     LLM
```

The main change is that the vector storage and similarity search are now handled by Qdrant instead of being manually implemented in Python.

## Key Learnings

- Why vector databases are needed in RAG
- Problems with linear vector search
- Persistence of embeddings
- Memory limitations of local vector storage
- What Qdrant is
- What a Qdrant collection represents
- What a Qdrant point contains
- Difference between vector and payload
- How embeddings are stored in Qdrant
- How Qdrant performs similarity search
- How to retrieve the top matching documents
- How retrieved payloads are used as LLM context
- How Qdrant fits into an end-to-end RAG pipeline

## Summary

Day 14 replaces the manually implemented vector retrieval from the previous RAG system with **Qdrant Cloud**.

The complete pipeline is:

```text
Knowledge Base
      ↓
Sentence Embeddings
      ↓
Qdrant Collection
      ↓
Vector Search
      ↓
Top Matching Documents
      ↓
Payload / Context
      ↓
Groq LLM
      ↓
Final Answer
```

Qdrant provides persistent vector storage and handles the similarity search, making the RAG architecture more suitable for larger knowledge bases than keeping all embeddings and performing linear search directly inside the Python program.
