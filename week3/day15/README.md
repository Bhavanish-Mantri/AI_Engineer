# Day 15: Qdrant Filters and HNSW

Day 15 focuses on two important concepts used in Qdrant-based Retrieval-Augmented Generation (RAG) systems:

- **HNSW (Hierarchical Navigable Small World)** for efficient vector search
- **Payload Filters** for restricting searches based on metadata

These concepts build on the Qdrant RAG pipeline introduced in Day 14.

## Overview

As the number of vectors in a vector database increases, searching every vector individually becomes inefficient.

For example, a linear search would compare a query against:

```text
Query
  ↓
Vector 1
Vector 2
Vector 3
...
Vector 10 Crore
```

This approach may work for a small number of vectors, but it does not scale well to very large collections.

Day 15 introduces two ways Qdrant handles this problem:

- **HNSW** helps perform efficient approximate nearest-neighbor vector search.
- **Filters** reduce the search space by allowing Qdrant to consider only points matching specific conditions.

## HNSW

HNSW stands for:

**Hierarchical Navigable Small World**

It is an algorithm used for efficient nearest-neighbor search in vector databases.

The basic idea is that vectors are connected to other nearby vectors. Instead of comparing the query with every vector, the search can navigate through these connections toward regions containing more relevant vectors.

```text
Query
  ↓
Relevant Region
  ↓
Smaller Relevant Region
  ↓
Nearest Vectors
```

This is different from a linear search:

### Linear Search

```text
Query
  ↓
Vector 1
Vector 2
Vector 3
Vector 4
...
Vector N
```

The lecture explains HNSW using a navigation example: rather than checking every shop between two cities, first move toward the correct city, then the correct area, and finally perform a smaller local search.

The same intuition applies to vector search: move toward the region where the nearest vectors are likely to exist instead of searching the entire vector space.

Qdrant uses HNSW internally for vector similarity search, so it does not need to be implemented manually in the application.

## Filters

A vector database may contain additional information along with each vector.

For example, a knowledge item can contain:

- `text`
- `category`
- `is_active`

These additional fields are stored as the point's payload.

A filter allows the search to consider only points that satisfy specific conditions.

For example:

```text
category = "vacation"
AND
is_active = true
```

Instead of searching the complete collection, Qdrant first restricts the candidates according to the filter and then performs the similarity search.

```text
All Vectors
    ↓
Apply Filter
    ↓
Matching Vectors
    ↓
Similarity Search
    ↓
Top Results
```

This is particularly useful when a collection contains different types of information or multiple versions of the same information.

### Payload Index

When a field is going to be used for filtering, Qdrant can create a payload index for that field.

For example:

- `category`
- `is_active`

The index allows Qdrant to maintain information about which points belong to particular categories or values.

Conceptually:

```text
category
├── vacation
├── workplace
├── reimbursement
└── career


is_active
├── true
└── false
```

This means Qdrant does not need to discover these relationships from scratch during every filtered search.

The lecture demonstrates creating an index for the category field before using it in a filter.

### Filter Conditions

Qdrant provides three important filter conditions discussed in this lesson:

#### `must`

All specified conditions must be satisfied.

For example:

```text
category = "reimbursement"
AND
is_active = true
```

Only points satisfying both conditions are considered.

#### `must_not`

The specified condition must not be satisfied.

For example:

```text
category != "reimbursement"
```

Points belonging to the reimbursement category are excluded.

#### `should`

At least one of the specified conditions should match.

For example:

```text
category = "reimbursement"
OR
is_active = true
```

The lecture relates these concepts to logical operators:

- `must`      → `AND`
- `must_not`  → `NOT`
- `should`    → `OR`

### Filtered Vector Search

A normal vector search retrieves the most similar vectors from the collection.

A filtered vector search adds another condition:

```text
Query
  +
Filter
  ↓
Qdrant
  ↓
Matching Points
  ↓
Similarity Search
  ↓
Top Results
```

For example:

**Query:**
```text
How many days of leave do employees get?
```

**Filter:**
```text
category = "vacation"
is_active = true
```

The search is performed only on documents satisfying the filter.

This is more useful than searching the complete collection when the metadata already tells us which documents are relevant to the query.

## RAG Flow

The concepts from this day fit into the existing Qdrant RAG pipeline:

```text
Knowledge Base
      ↓
Generate Embeddings
      ↓
Store Vectors + Payload
      ↓
Qdrant Collection
      ↓
User Query
      ↓
Query Embedding
      ↓
Apply Payload Filter
      ↓
HNSW Similarity Search
      ↓
Top Relevant Results
      ↓
Retrieved Context
      ↓
LLM
      ↓
Final Answer
```

The filter determines which points can be considered, while vector similarity determines which of those points are most relevant to the query.

## Example

Suppose the knowledge base contains:

**Document 1**
- **Text:** Employees receive 24 days of leave.
- **Category:** vacation
- **is_active:** true

**Document 2**
- **Text:** Employees work eight hours per day.
- **Category:** workplace
- **is_active:** true

**Document 3**
- **Text:** Employees previously received 30 days of leave.
- **Category:** vacation
- **is_active:** false

For the query:

```text
How many days of leave do employees get?
```

we can use:

```text
category = "vacation"
AND
is_active = true
```

This excludes unrelated workplace information and inactive vacation information.

The relevant document is:

> Employees receive 24 days of leave.

The retrieved result can then be passed to the LLM as context.

## Filter Syntax

A simplified representation of the filter used in the lesson is:

```python
query_filter = Filter(
    must=[
        FieldCondition(
            key="category",
            match=MatchValue(value="reimbursement")
        )
    ]
)
```

The filter is then supplied during the vector search:

```python
search(
    query_vector,
    query_filter=query_filter,
    limit=3
)
```

The exact syntax depends on the Qdrant client version being used, but the underlying concept remains the same:

```text
Filter
  ↓
Select matching points
  ↓
Vector similarity search
  ↓
Return top results
```

## Why Filters Matter in RAG

A real knowledge base can contain information from multiple categories and sources.

For example:

```text
HR
├── Leave
├── Salary
├── Workplace
├── Reimbursement
└── Career
```

It can also contain information from multiple companies:

```text
Company
├── Google
├── Akamai
└── Microsoft
```

A query can therefore use metadata to narrow down the search.

For example:

```text
company = "Akamai"
AND
category = "leave"
AND
is_active = true
```

The lecture explains that additional payload fields can be indexed and combined to create more complex filters.

## HNSW + Filters

HNSW and filters solve different parts of the retrieval problem.

- **Filter:** Which documents should be considered?
- **HNSW:** Which considered documents are closest to the query?

Together:

```text
All Documents
      ↓
    Filter
      ↓
Eligible Documents
      ↓
    HNSW
      ↓
Nearest Documents
      ↓
Top Results
```

This combination allows Qdrant to perform more targeted and efficient retrieval.

## Day 14 → Day 15

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

### Day 15
```text
Knowledge Base
      ↓
Embeddings + Payload
      ↓
Qdrant Cloud
      ↓
Payload Filter
      ↓
HNSW Vector Search
      ↓
Relevant Context
      ↓
LLM
```

Day 15 therefore extends the Qdrant RAG pipeline by introducing metadata-based filtering and understanding the role of HNSW in efficient vector retrieval.

## Key Learnings

- Understanding the limitation of linear vector search
- Understanding the basic intuition behind HNSW
- Understanding how Qdrant uses HNSW for vector search
- Understanding payload metadata
- Creating payload indexes
- Using must conditions
- Using must_not conditions
- Using should conditions
- Combining metadata filtering with vector similarity search
- Reducing the search space before retrieving relevant vectors
- Building more targeted RAG retrieval pipelines

## Summary

Day 15 introduces two important concepts that make Qdrant-based RAG systems more practical:

- **HNSW** (Efficient Vector Search)
- **Filters** (Targeted Vector Search)

The complete retrieval process can be summarized as:

```text
User Query
     ↓
Query Embedding
     ↓
Payload Filter
     ↓
HNSW Search
     ↓
Top Relevant Vectors
     ↓
Retrieved Payload
     ↓
LLM
     ↓
Final Answer
```

HNSW helps Qdrant navigate a large vector space efficiently, while filters allow the application to restrict retrieval using structured metadata.
