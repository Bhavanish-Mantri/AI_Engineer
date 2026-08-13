# Day 11 - Simple Retrieval-Augmented Generation (RAG)

A simple implementation of **Retrieval-Augmented Generation (RAG)** using Python, the Groq API, and keyword-based retrieval.

## Overview

Day 11 introduces **Retrieval-Augmented Generation (RAG)** and explains how an LLM can answer questions using additional information that is not part of its original knowledge.

The basic idea of RAG is simple:

```text
Knowledge Base
      │
      ▼
   Retrieval
      │
      ▼
Relevant Context
      │
      ▼
      LLM
      │
      ▼
Generated Answer
```

Instead of providing the entire knowledge base to the LLM for every question, a retrieval system first looks for information relevant to the user's query. The retrieved information is then provided to the LLM as context so that the model can generate an answer based on that information.

This Day 11 implementation demonstrates the **first and simplest iteration of RAG**, where the knowledge base is stored locally and relevant information is retrieved using keyword matching.

> This is intentionally a simple implementation for understanding the core RAG workflow. It does not use embeddings or a vector database.

---

## What is RAG?

RAG stands for:

- **R** - Retrieval
- **A** - Augmented
- **G** - Generation

In simple terms:

```text
Retrieve relevant information
            +
Give that information to the LLM
            =
Generate an answer using the retrieved information
```

An LLM may not know private, internal, or newly provided information. RAG allows additional information to be supplied at query time instead of relying only on the model's existing knowledge.

---

## Why is RAG Needed?

LLMs are trained on large amounts of data, but they do not automatically know every piece of private or domain-specific information.

For example, an LLM may know general information available publicly on the internet, but it will not automatically know private information about a person or internal information about a company.

One possible solution is to directly provide the information to the model. However, this becomes inefficient when the knowledge base becomes large.

A large organization may have many documents containing:

- Architecture information
- Software design
- Implementation details
- Coding documentation
- Testing documentation
- Usage documentation

Sending all of these documents to the LLM for every question would be inefficient and would consume a large number of tokens.

RAG solves this problem by retrieving only the information relevant to the user's question before sending it to the LLM. :contentReference[oaicite:0]{index=0}

---

## Part 1 - Knowledge Base

The first step in RAG is creating a **Knowledge Base**.

A knowledge base contains the information that the LLM needs to answer questions about a specific domain.

A knowledge base can be stored in different forms, such as:

- PDF
- JSON
- Dictionary
- Database
- Documents

For this simple implementation, the knowledge base is represented locally using a Python dictionary.

Example:

```python
knowledge_base = {
    "age": "The age of Bhavanish Mantri is 22 years.",
    "interests": "Bhavanish Mantri is interested in AI and Machine Learning."
}
```

The knowledge base contains information that is not expected to be available to the LLM by default.

---

## Part 2 - Retrieval

The second step is **Retrieval**.

The retrieval function receives the user's question and searches the knowledge base for relevant information.

The simplified retrieval process is:

```text
User Question
      │
      ▼
Convert Question to Lowercase
      │
      ▼
Check for Known Keywords
      │
      ├── "age" found
      │       │
      │       ▼
      │   Retrieve age information
      │
      ├── "interests" found
      │       │
      │       ▼
      │   Retrieve interests information
      │
      └── No keyword found
              │
              ▼
             None
```

The retrieval function checks whether specific keywords exist in the user's question.

For example:

```text
Question:
"What is Bhavanish's age?"

Keyword:
"age"

Retrieved Context:
"The age of Bhavanish is 22 years."
```

The retrieved information is then passed to the LLM as context.

---

## Part 3 - Augmented Generation

After retrieval, the relevant information is added to the LLM prompt as **context**.

The process becomes:

```text
User Question
      │
      ▼
Retrieve Relevant Information
      │
      ▼
Retrieved Context
      │
      ▼
Question + Context
      │
      ▼
     LLM
      │
      ▼
Final Answer
```

The LLM is instructed to answer based only on the retrieved context.

The system prompt follows the basic idea:

```text
Answer in one line only.

Answer only based on this context.

Do not hallucinate.
```

This prevents the model from relying on unrelated information when the required information is available in the retrieved context.

---

## Part 4 - Complete RAG Workflow

The complete workflow implemented in Day 11 is:

```text
                    User
                     │
                     ▼
                User Question
                     │
                     ▼
              Retrieval Function
                     │
                     ▼
              Keyword Matching
                     │
             ┌───────┴────────┐
             │                │
        Match Found       No Match
             │                │
             ▼                ▼
      Relevant Context       None
             │                │
             └───────┬────────┘
                     │
                     ▼
                LLM Prompt
          Question + Context
                     │
                     ▼
                  Groq
                     │
                     ▼
              Generated Answer
```

---

## Architecture

```text
┌──────────────────────┐
│       User           │
│   Question           │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│      Retrieval       │
│      Function        │
│                      │
│ Keyword Matching     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│    Knowledge Base    │
│                      │
│ age                  │
│ interests            │
│ other information    │
└──────────┬───────────┘
           │
           │ Relevant Context
           ▼
┌──────────────────────┐
│     Prompt Builder   │
│                      │
│ Question + Context   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│      Groq LLM        │
│ llama-3.3-70b-       │
│ versatile            │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│    Final Answer      │
└──────────────────────┘
```

## LLM Integration

The LLM is responsible for the **Generation** part of RAG.

The application uses the Groq API with:

```text
llama-3.3-70b-versatile
```

The LLM receives:

```text
System Prompt
+
Retrieved Context
+
User Question
```

and generates the final answer.

The retrieval stage and generation stage therefore have separate responsibilities:

```text
Retrieval
    │
    └── Finds relevant information

Generation
    │
    └── Uses the information to generate an answer
```

---

## Prompt Design

The system prompt is designed to keep the generated response restricted to the retrieved context.

The main instructions are:

```text
Answer in one line only.
Answer only based on this context.
Do not hallucinate.
```

The one-line restriction also keeps the generated response short and reduces unnecessary token usage.

---

## Example

### Knowledge Base

```python
knowledge_base = {
    "age": "The age of Bhavanish Mantri is 25 years.",
    "interests": "Bhavanish Mantri is interested in AI and Machine Learning."
}
```

### Query

```text
What is Bhavanish's age?
```

### Retrieval

```text
The age of Bhavanish is 22 years.
```

### LLM Context

```text
Context:
The age of Bhavanish Mantri is 22 years.

Question:
What is Bhavanish's age?
```

### Output

```text
Bhavanish is 22 years old.
```

---

## What Happens When Information Is Not Available?

If the retrieval function cannot find a matching keyword, it returns:

```python
None
```

The LLM then does not receive relevant information from the knowledge base.

This is important because the retrieval system should not invent information that does not exist in the knowledge base.

---

## Limitations of This Simple RAG

This implementation is intentionally simple and demonstrates the first iteration of RAG.

Keyword-based retrieval has several limitations.

### 1. Exact Keyword Dependency

The retriever depends on specific words appearing in the question.

For example:

```text
What is Bhavaish's age?
```

contains:

```text
age
```

so the information can be retrieved.

But:

```text
How old is Bhavanish?
```

does not contain the keyword:

```text
age
```

so the simple retriever may fail to retrieve the same information.

The lecture demonstrates this limitation and explains that the simple retrieval system is very rigid because it directly checks keywords in the question. :contentReference[oaicite:1]{index=1}

---

### 2. Spelling Mistakes

A simple keyword matcher may also fail when the user makes a spelling mistake.

For example:

```text
What is Bhavanish's ag?
```

The retriever may not recognize:

```text
age
```

even though the meaning of the question is clear to an LLM.

---

### 3. Synonyms

Different users can ask the same question using different words.

For example:

```text
What is his age?
How old is he?
How many years old is he?
```

A keyword-based retriever may not treat these questions as equivalent.

---

### 4. Limited Scalability

A dictionary with a few keywords is useful for learning the concept, but it is not suitable for a large knowledge base containing thousands or millions of documents.

As the knowledge base grows, manually maintaining keyword rules becomes increasingly difficult.

---

## Why Vector Databases Are Needed

The simple keyword-based approach is only the **first iteration** of RAG.

Modern RAG systems generally use more advanced retrieval methods.

The lecture introduces the idea of storing knowledge using **Vector Databases** and explains that the retrieval mechanism evolves beyond simple keyword matching. :contentReference[oaicite:2]{index=2}

The progression can be viewed as:

```text
Simple Keyword Retrieval
          │
          ▼
Better Retrieval Techniques
          │
          ▼
Embeddings
          │
          ▼
Vector Database
          │
          ▼
Semantic Retrieval
```

Vector databases and embeddings are not implemented in this Day 11 project. They are introduced as the next step for improving the retrieval system.

---

## Project Structure

```text
day11/
├── pyproject.toml
├── uv.lock
├── README.md
├── .gitignore
├── main.py
└── simple_rag.py
```

---

## Features

- Simple local knowledge base
- Keyword-based retrieval
- Context-based LLM generation
- Groq API integration
- Restricted LLM prompting
- One-line answers
- Basic hallucination prevention
- Easy-to-understand RAG pipeline

---

## Technologies Used

- Python
- Groq API
- Llama 3.3 70B Versatile
- python-dotenv
- UV

---

## Example

```text
Query:
What is the interests of Bhavanish Mantri?

Output:
Bhavanish Mantri is interested in AI and Machine Learning.
```

The answer is generated using information retrieved from the local knowledge base.

---

## Key Learnings

- RAG stands for Retrieval-Augmented Generation.
- RAG combines retrieval with LLM generation.
- A knowledge base can contain private or domain-specific information.
- Retrieval identifies information relevant to the user's question.
- The retrieved information is passed to the LLM as context.
- The LLM uses the context to generate the final response.
- Simple keyword matching can demonstrate the basic RAG concept.
- Keyword retrieval is rigid and has limitations with synonyms, spelling variations, and different question structures.
- Modern RAG systems use more advanced retrieval techniques such as embeddings and vector databases.
- Retrieval and generation are separate stages of the RAG pipeline.

---

## RAG in One Line

```text
RAG = Retrieve Relevant Information + Give It to the LLM + Generate an Answer
```

---

## Summary

Day 11 introduces the fundamental idea behind **Retrieval-Augmented Generation**.

The implementation demonstrates the first iteration of RAG using a local knowledge base and simple keyword-based retrieval. Instead of asking the LLM to answer using only its existing knowledge, relevant information is first retrieved and then supplied to the model as context.

The core workflow is:

```text
Knowledge Base
      ↓
User Question
      ↓
Retrieve Relevant Information
      ↓
Retrieved Context
      ↓
LLM
      ↓
Generated Answer
```

This simple implementation provides the foundation for understanding more advanced RAG systems that use embeddings, vector databases, and semantic retrieval.
