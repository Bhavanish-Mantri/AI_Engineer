# RAG Evaluation

A practical implementation of **Retrieval-Augmented Generation (RAG) evaluation** using a golden dataset and multiple evaluation metrics to identify whether errors come from the knowledge base, retrieval system, or LLM.

---

## Overview

A RAG system can produce an incorrect answer for different reasons.

The complete RAG pipeline is:

```text
Knowledge Base
      ↓
Embeddings
      ↓
Vector Database
      ↓
Query Embedding
      ↓
Relevant Context
      ↓
     LLM
      ↓
Final Answer
```

RAG evaluation checks whether each important layer is working correctly.

---

# RAG Failure Modes

There are three major failure points in a RAG system.

### 1. Incorrect Knowledge Base

The original information may be wrong.

```text
Wrong Knowledge
      ↓
Wrong Context
      ↓
Wrong Answer
```

### 2. Incorrect Retrieval

The knowledge may be correct, but the vector database may retrieve the wrong or incomplete context.

```text
Correct Knowledge
      ↓
Wrong Retrieval
      ↓
Wrong Context
      ↓
Wrong Answer
```

### 3. LLM Generation Error

The retrieved context may be correct, but the LLM may misunderstand it or generate unsupported information.

```text
Correct Knowledge
      ↓
Correct Context
      ↓
LLM Error
      ↓
Wrong Answer
```

---

# Golden Dataset

A **Golden Dataset** works like test cases in programming.

Each test case contains:

```text
Question
Ground Truth
```

Example:

```json
{
  "question": "How many paid leaves does an employee get?",
  "ground_truth": "Employees receive 12 days of paid leave."
}
```

The ground truth represents the expected correct answer based on the trusted knowledge base.

The number of questions depends on the size and complexity of the knowledge base.

```text
Small Knowledge Base → Fewer Questions
Large Knowledge Base  → More Questions
```

---

# Evaluation Layers

RAG evaluation is performed layer by layer.

```text
                RAG Evaluation
                     │
          ┌──────────┴──────────┐
          │                     │
     Retrieval              Generation
          │                     │
     ┌────┴────┐          ┌─────┼─────┐
     │         │          │     │     │
 Precision   Recall   Faithfulness  Correctness  Relevance
```

The five main metrics are:

1. Precision
2. Recall
3. Faithfulness
4. Correctness
5. Relevance

---

# Retrieval Evaluation

The first step is checking whether the correct context was retrieved.

The two main metrics are:

```text
Precision
Recall
```

---

# Precision

**Precision** measures how much of the retrieved context is relevant to the query.

```text
Precision = Relevant Retrieved Context / Total Retrieved Context
```

Example:

```text
Retrieved Context = 3 lines
Relevant Context  = 2 lines

Precision = 2 / 3
          = 66%
```

So, precision answers:

```text
"Of everything I retrieved, how much was actually relevant?"
```

---

# Recall

**Recall** measures how much of the total relevant information was successfully retrieved.

```text
Recall = Relevant Retrieved Context / Total Relevant Context
```

Example:

```text
Relevant Context Available = 2 lines
Relevant Context Retrieved  = 1 line

Recall = 1 / 2
       = 50%
```

So, recall answers:

```text
"Of all the relevant information available, how much did I retrieve?"
```

---

# Precision vs Recall

Consider a knowledge base containing:

```text
12 days of paid leave
3 days of sick leave
```

The question is:

```text
How many total leaves does an employee get?
```

Both lines are relevant.

If the retriever returns only:

```text
12 days of paid leave
```

Then:

```text
Precision = 100%
Recall    = 50%
```

Why?

The retrieved information is relevant, but one relevant piece of information was missed.

---

## High Recall but Low Precision

Suppose the retriever returns:

```text
12 days of paid leave
Salary information
```

Only one of them is relevant.

Then:

```text
Precision = 50%
Recall    = 100%
```

This means the retriever found the required information but also returned irrelevant information.

---

# Retrieval Tuning

### If Precision is Low

Too much irrelevant context is being retrieved.

Possible solutions:

```text
Reduce top_k
      OR
Increase similarity threshold
```

Example:

```text
top_k = 10
```

can be reduced to:

```text
top_k = 3
```

A similarity threshold can also be applied so that only sufficiently similar vectors are retrieved.

---

### If Recall is Low

Important information is being missed.

Possible solutions:

```text
Increase top_k
      OR
Lower similarity threshold
```

Example:

```text
top_k = 1
```

can be increased to:

```text
top_k = 3
```

---

# Generation Evaluation

If retrieval quality is good but the final answer is still incorrect, the LLM needs to be evaluated.

Three metrics are used:

```text
Faithfulness
Correctness
Relevance
```

---

# Faithfulness

**Faithfulness** checks whether the answer is supported by the retrieved context.

Example context:

```text
Employees receive 12 days of paid leave.
```

If the LLM answers:

```text
Employees receive 10 days of paid leave.
```

the answer is **not faithful** to the context.

```text
Context → 12 days
Answer  → 10 days

Faithfulness → Low
```

This can indicate hallucination.

The main question is:

```text
"Did the LLM answer according to the retrieved context?"
```

---

# Correctness

**Correctness** checks whether the final answer matches the ground truth.

Example:

```text
Ground Truth → 12 days
LLM Answer   → 10 days

Correctness → Incorrect
```

Correctness focuses on the final answer rather than only checking whether the answer follows the retrieved context.

---

# Faithfulness vs Correctness

These two metrics are different.

### Correct Context + Correct Answer

```text
Context      → 12 days
Ground Truth → 12 days
Answer       → 12 days

Faithful  → Yes
Correct   → Yes
```

### Wrong Context + Faithful Answer

```text
Context      → 10 days
Ground Truth → 12 days
Answer       → 10 days

Faithful  → Yes
Correct   → No
```

The LLM followed the context correctly, but the context itself was wrong.

### Correct Answer + Unfaithful Answer

The LLM may produce the correct answer while not following the retrieved context.

```text
Context      → 10 days
Ground Truth → 12 days
Answer       → 12 days

Correct   → Yes
Faithful  → No
```

This distinction helps identify where the RAG system is failing.

---

# Relevance

**Relevance** checks whether the answer actually addresses the user's question.

Example:

```text
Question:
When does promotion happen?
```

Expected:

```text
Promotion happens in November.
```

But the LLM responds with:

```text
Promotion is the process of advancing an employee
to a higher position.
```

The response may describe promotion, but it does not answer **when** promotion happens.

Therefore:

```text
Relevance → Low
```

The main question is:

```text
"Did the answer actually answer the user's question?"
```

---

# Five Evaluation Metrics

| Metric       | What it Measures                                 |
| ------------ | ------------------------------------------------ |
| Precision    | How much retrieved context is relevant           |
| Recall       | How much relevant context was retrieved          |
| Faithfulness | Whether the answer follows the retrieved context |
| Correctness  | Whether the answer matches the ground truth      |
| Relevance    | Whether the answer addresses the question        |

---

# Debugging RAG Using Metrics

The metrics help identify which part of the RAG system needs improvement.

```text
Low Precision
      ↓
Retrieval Problem
      ↓
Reduce top_k / Adjust Threshold
```

```text
Low Recall
      ↓
Retrieval Problem
      ↓
Increase top_k / Lower Threshold
```

```text
High Precision + High Recall
          ↓
      Wrong Answer
          ↓
      Check LLM
```

```text
Low Faithfulness
      ↓
LLM is not following context
      ↓
Improve System Prompt
```

```text
Faithful but Incorrect
      ↓
Context / Knowledge Problem
      ↓
Check Knowledge Base
```

```text
Low Relevance
      ↓
Answer does not address query
      ↓
Improve Prompt / Answer Instructions
```

---

# System Prompt and Faithfulness

If the LLM is not faithful to the retrieved context, the system prompt can explicitly instruct it not to hallucinate.

Example:

```text
Use only the provided context to answer.
Do not hallucinate or add unsupported information.
```

The goal is to make the model answer based on the retrieved context instead of generating unsupported information.

---

# RAG Evaluation Workflow

The complete evaluation process is:

```text
Knowledge Base
      ↓
Build RAG System
      ↓
Create Golden Dataset
      ↓
Run Questions
      ↓
Retrieve Context
      ↓
Evaluate Precision & Recall
      ↓
Generate Answer
      ↓
Evaluate Faithfulness
      ↓
Evaluate Correctness
      ↓
Evaluate Relevance
      ↓
Identify Failure
      ↓
Improve RAG System
```

---

# Project Structure

A typical implementation can be organized as:

```text
rag-evaluation/
│
├── knowledge.json
├── main.py
├── rageval.py
├── requirements.txt
└── README.md
```

### `knowledge.json`

Contains the knowledge used by the RAG system.

### `evaluation.py`

Contains the RAG pipeline and evaluation logic and metrics.

### `main.py`

Runs the complete system.

---

# Golden Dataset Example

A golden dataset can contain:

```json
{
  "question": "How many paid leaves does an employee receive?",
  "ground_truth": "Employees receive 24 days of paid leave per year.",
  "expected": "Employees receive 24 days of paid leave per year."
}
```

The `expected` information can also help evaluate whether the generated response is relevant to the question.

---

# RAG Architecture

```text
                 Knowledge Base
                       │
                       ▼
                  Embeddings
                       │
                       ▼
                Vector Database
                       │
                       │
User Query ───────► Query Embedding
                       │
                       ▼
                 Similarity Search
                       │
                       ▼
                  Retrieved Context
                       │
                       ▼
                       LLM
                       │
                       ▼
                  Final Answer
                       │
                       ▼
                RAG Evaluation
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   Retrieval       Generation      Ground Truth
        │              │
   Precision        Faithfulness
   Recall           Correctness
                    Relevance
```

---

# Key Learnings

By completing this project, I learned:

1. Why RAG systems need evaluation.
2. How a RAG pipeline can fail.
3. What a Golden Dataset is.
4. How Precision evaluates retrieved context.
5. How Recall evaluates retrieved context.
6. The difference between Precision and Recall.
7. How `top_k` affects retrieval.
8. How similarity thresholds affect retrieval.
9. What Faithfulness means.
10. What Correctness means.
11. The difference between Faithfulness and Correctness.
12. What Relevance means.
13. How evaluation metrics help debug RAG systems.
14. How to identify whether the issue is in the knowledge base, retrieval layer, or LLM.
15. How evaluation can be used to systematically improve a RAG system.

---

# Important Concept

The most important idea from this project is:

```text
Wrong Answer
     ↓
Don't immediately blame the LLM
     ↓
Check the entire RAG pipeline
     ↓
Knowledge?
     ↓
Retrieval?
     ↓
Context?
     ↓
    LLM?
```

RAG evaluation is not simply checking whether the final answer is correct.

It is about understanding **why the system produced that answer**.

---

# Summary

RAG evaluation provides a structured way to test and debug Retrieval-Augmented Generation systems.

The five core metrics are:

```text
Precision
    ↓
Retrieved Context Quality

Recall
    ↓
Retrieved Context Coverage

Faithfulness
    ↓
Answer follows Context

Correctness
    ↓
Answer matches Ground Truth

Relevance
    ↓
Answer addresses the Question
```

Together, these metrics help determine whether the problem is in the **knowledge base, retrieval system, or LLM generation layer**.

```text
RAG
 ↓
Evaluate
 ↓
Identify Failure
 ↓
Debug
 ↓
Improve
```
