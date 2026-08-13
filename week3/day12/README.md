# Day 12 - Sentence Embeddings and Cosine Similarity

A lightweight implementation demonstrating **sentence embeddings** and **cosine similarity** using Python, `sentence-transformers`, and `numpy`.

This is the next step after the keyword-based retrieval system implemented in Day 11. Instead of relying on exact keyword matching, text is converted into numerical vector representations called **embeddings**, allowing us to compare sentences based on their semantic meaning.

---

## Overview

In the previous RAG implementation, retrieval was performed using simple keyword matching.

For example:

```text
Knowledge Base:
"Bhavanish is interested in Artificial Intelligence."

Query:
"What are Bhavanish's interests?"
```

A keyword-based system may fail because the exact words from the knowledge base may not appear in the query.

Similarly:

```text
"How old is Bhavanish?"
```

and

```text
"What is Bhavanish's age?"
```

have different words but essentially the same meaning.

This is the limitation that **embeddings** help solve.

Instead of comparing text directly, we convert the text into numerical vectors and compare those vectors.

```text
Text
  │
  ▼
Sentence Embedding Model
  │
  ▼
Numerical Vector
  │
  ▼
Cosine Similarity
  │
  ▼
Semantic Similarity Score
```

The lecture introduces embeddings as the next step after simple keyword retrieval because exact keyword search can fail with spelling mistakes, different wording, and semantically similar words.

---

## What is an Embedding?

An **embedding** is a numerical representation of data.

In this project, a sentence is converted into a vector of numbers.

For example:

```text
"Machine Learning is fun"
```

is converted into a vector similar to:

```text
[
    0.021,
   -0.143,
    0.087,
    ...
]
```

The actual vector contains many dimensions.

With the model used in this project:

```text
all-MiniLM-L6-v2
```

each sentence is represented as a **384-dimensional vector**.

Conceptually:

```text
Sentence
   │
   ▼
"Machine Learning is fun"
   │
   ▼
Embedding Model
   │
   ▼
[0.021, -0.143, 0.087, ..., 0.154]
   │
   ▼
384-dimensional vector
```

The lecture explains the basic idea of embeddings as converting knowledge/data into an array based on relevant features so that similar data can be compared numerically.

---

## Why Do We Need Embeddings?

Traditional keyword search depends heavily on matching words.

Consider:

```text
Knowledge:
"There is a traffic jam on the main road."

Query:
"How much traffic is there on the main road?"
```

There may not be an exact keyword match for the important concept, even though the two sentences are semantically related.

Humans can understand that:

```text
"traffic jam"
```

and

```text
"heavy traffic"
```

are related.

A simple keyword-based program cannot reliably understand this relationship.

Embeddings solve this problem by representing text as vectors so that semantically similar sentences can have similar vector representations.

The lecture uses examples such as `"cat"` and `"animal"` to explain why exact word matching is insufficient for semantic retrieval.

---

# How Embeddings Work

The simplified idea is:

```text
Text
  ↓
Convert text into numerical features
  ↓
Represent the text as a vector
  ↓
Compare vectors
  ↓
Determine similarity
```

For example:

```text
Sentence 1:
"I love machine learning."

Sentence 2:
"Machine learning is interesting."
```

Even though the exact wording is different, their embeddings can be relatively close because their meanings are related.

---

# Sentence Transformers

This project uses the Python library:

```text
sentence-transformers
```

Sentence Transformers provides pretrained models that can convert sentences and paragraphs into meaningful vector representations.

The model used here is:

```text
all-MiniLM-L6-v2
```

It is a compact sentence embedding model that produces:

```text
384-dimensional embeddings
```

The lecture demonstrates using `SentenceTransformer` with `all-MiniLM-L6-v2` and explains that the resulting sentence vector has a size of 384.

---

# Cosine Similarity

Once two sentences have been converted into vectors, we need a way to measure how similar those vectors are.

This project uses **Cosine Similarity**.

The basic formula is:

```text
              A · B
Cosine = ───────────────
         ||A|| × ||B||
```

where:

- `A` = first vector
- `B` = second vector
- `A · B` = dot product of the vectors
- `||A||` = magnitude of vector A
- `||B||` = magnitude of vector B

Cosine similarity measures the angle/direction between two vectors.

Conceptually:

```text
        Vector A
           ↗
          /
         /
        / θ
       /________→ Vector B
```

If the vectors point in similar directions, their cosine similarity is high.

If they point in very different directions, the similarity is low.

The lecture explains cosine similarity using the direction/angle between vectors rather than requiring the learner to focus on the mathematical derivation.

---

# Cosine Similarity Score

Cosine similarity theoretically ranges from:

```text
-1 to +1
```

A simplified interpretation is:

| Score | Meaning |
|---:|---|
| `1` | Extremely similar direction |
| `0` | Little or no directional similarity |
| `-1` | Opposite direction |

For sentence embeddings, the actual values depend on the model and the sentences being compared.

For example:

```text
Sentence 1:
"I love programming."

Sentence 2:
"I enjoy coding."
```

may produce a relatively high similarity because the sentences have related meanings.

Whereas:

```text
Sentence 1:
"I love programming."

Sentence 2:
"The weather is cold today."
```

should generally produce a much lower similarity.

The lecture similarly describes a higher cosine similarity as indicating greater similarity and a lower score as indicating less similarity.

---

# Project Workflow

The implementation follows these steps:

```text
                 ┌─────────────────────┐
                 │      Sentence 1     │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Sentence Transformer│
                 └──────────┬──────────┘
                            │
                            ▼
                    Embedding Vector
                            │
                            │
                            │
                 ┌──────────▼──────────┐
                 │ Cosine Similarity    │
                 └──────────▲──────────┘
                            │
                            │
                    Embedding Vector
                            ▲
                            │
                 ┌──────────┴──────────┐
                 │ Sentence Transformer│
                 └──────────▲──────────┘
                            │
                 ┌──────────┴──────────┐
                 │      Sentence 2     │
                 └─────────────────────┘
```

In simple terms:

```text
Sentence 1
    ↓
Embedding 1
    ↓
Cosine Similarity
    ↓
Sentence 2
    ↓
Embedding 2
```

---

# Implementation

The sentence embedding model is initialized using:

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
```

A sentence can then be converted into an embedding using:

```python
embedding = model.encode(text)
```

For example:

```python
text = "Machine Learning is fun"

embedding = model.encode(text)

print(embedding)
```

The result is a numerical vector containing 384 values.

---

# Cosine Similarity Implementation

Cosine similarity can be calculated using NumPy:

```python
import numpy as np


def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
```

The function:

1. Calculates the dot product.
2. Calculates the magnitude of each vector.
3. Divides the dot product by the product of the magnitudes.

---

# Example

Consider:

```text
Sentence 1:
"There are 24 paid leaves."

Sentence 2:
"There are 24 vacation days."
```

The exact words are different:

```text
paid leaves
```

vs.

```text
vacation days
```

However, their meanings are related.

The embedding model converts both sentences into vectors:

```text
Sentence 1
    ↓
Embedding 1

Sentence 2
    ↓
Embedding 2
```

Cosine similarity can then be used to determine how similar the two embeddings are.

The lecture demonstrates this type of example to show that semantic similarity can be measured even when the exact words differ.

---

# Example with Unrelated Sentences

The project can also compare unrelated sentences.

For example:

```text
t1 = "There are 24 paid leaves"

t2 = "My name is Bhavanish"
```

These sentences are semantically unrelated, so their cosine similarity should generally be relatively low.

The exact score can vary depending on the embedding model and implementation.

---

# Day 11 vs Day 12

Day 12 builds directly on the retrieval concept introduced in Day 11.

| Day 11 | Day 12 |
|---|---|
| Keyword Retrieval | Semantic Retrieval Foundation |
| Exact word matching | Vector representation |
| Rule-based | Model-based |
| Can fail with different wording | Can capture semantic relationships |
| No embeddings | Uses embeddings |
| No vector comparison | Uses cosine similarity |

### Day 11

```text
Question
   ↓
Keyword Matching
   ↓
Relevant Information
```

### Day 12

```text
Question
   ↓
Embedding
   ↓
Vector
   ↓
Similarity Search
   ↓
Relevant Information
```

This transition is important because modern RAG systems need retrieval methods that are more flexible than exact keyword matching.

---

# Connection to RAG

Embeddings are one of the important building blocks of modern RAG systems.

A typical embedding-based RAG pipeline looks like:

```text
                 KNOWLEDGE BASE
                       │
                       ▼
                Split into Chunks
                       │
                       ▼
                  Generate
                  Embeddings
                       │
                       ▼
                 Vector Database
                       │
                       │
                       │
User Query ───────► Generate
                   Query Embedding
                       │
                       ▼
                Similarity Search
                       │
                       ▼
               Relevant Documents
                       │
                       ▼
                      LLM
                       │
                       ▼
                  Final Answer
```

Day 12 focuses only on the fundamental building blocks:

```text
Text
 ↓
Embedding
 ↓
Vector
 ↓
Cosine Similarity
```

Vector databases and complete embedding-based RAG pipelines are the natural next step.

The lecture explicitly connects embeddings and cosine similarity to the later concept of vector databases and RAG retrieval.

---

# Features

- Generate sentence embeddings locally
- Uses `sentence-transformers`
- Uses `all-MiniLM-L6-v2`
- Produces 384-dimensional sentence vectors
- Calculates cosine similarity using NumPy
- Demonstrates semantic similarity
- Provides the foundation for vector search
- Connects embeddings with modern RAG systems
- Uses `uv` for modern Python dependency management

---

# Project Structure

```text
day12/
├── pyproject.toml      # Project configuration and dependencies
├── uv.lock             # Locked dependency versions
├── README.md           # Project documentation
├── .gitignore          # Git ignore patterns
├── main.py             # Project entry point
└── embedding_rag.py    # Embedding and cosine similarity implementation
```

---

# Important Concept

The most important idea from this project is not the mathematical formula itself.

It is the transformation:

```text
Human-readable Data
        ↓
Numerical Representation
        ↓
Vector
        ↓
Compare Vectors
        ↓
Measure Similarity
```

Computers work naturally with numerical representations. Sentence embedding models provide a way to represent text as numerical vectors that can then be compared mathematically.

The lecture emphasizes this core idea: convert data into an array/vector based on learned features and then compare the resulting vectors.

---

# Key Learnings

By completing Day 12, I learn:

1. What sentence embeddings are.
2. Why keyword-based retrieval is limited.
3. How text can be represented as numerical vectors.
4. How `sentence-transformers` generates sentence embeddings.
5. What the `all-MiniLM-L6-v2` model does.
6. Why the generated vector has 384 dimensions.
7. What cosine similarity measures.
8. How to calculate cosine similarity using NumPy.
9. How semantic similarity differs from exact keyword matching.
10. How embeddings become useful for modern RAG retrieval.
11. How embeddings lead toward vector databases and vector search.

---

## Summary

Day 12 introduces the mathematical and practical foundation behind **semantic retrieval**.

Instead of asking:

```text
"Do these two sentences contain the same words?"
```

we can ask:

```text
"How similar are the meanings represented by their vectors?"
```

That shift from **keyword matching** to **semantic similarity** is a fundamental concept behind modern vector search and Retrieval-Augmented Generation.

```text
Text
  ↓
Embedding
  ↓
Vector
  ↓
Cosine Similarity
  ↓
Semantic Similarity
  ↓
Vector Search
  ↓
RAG
```
