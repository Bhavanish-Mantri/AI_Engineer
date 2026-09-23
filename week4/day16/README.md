# Day 16 - RAG Evaluation

This repository contains scripts and datasets for comprehensively evaluating a **Retrieval-Augmented Generation (RAG)** system using Large Language Models (LLMs) as judges.

RAG evaluation is critical for identifying whether your system retrieves the right information and generates a correct, relevant, and grounded answer.

## 🎯 Why Evaluate RAG?

A RAG system can fail in three primary ways:
1. **Knowledge Base Issues**: The knowledge base contains incorrect or outdated information.
2. **Retrieval Issues**: The retriever returns incorrect or incomplete context.
3. **Generation Issues**: The LLM receives correct context but hallucinates, generating a wrong or irrelevant answer.

By evaluating the system, you can isolate these issues and tune your RAG pipeline effectively.

## 📁 Repository Structure
- `rag_eval.py`: The main script that performs RAG evaluation across five core metrics using Groq LLMs.
- `knowledge.json`: The **Golden Dataset** that serves as the ground truth and source documents for evaluation. 
- `main.py`: Base script for the project.

## 📊 Key Evaluation Metrics

This project evaluates the RAG system across five essential dimensions:

### 1. Precision
Measures how much of the retrieved context is actually relevant to the question.
* **Formula**: `Relevant Retrieved / Total Retrieved`
* **Example**: If 3 chunks are retrieved and 2 are relevant, Precision = `66%`.

### 2. Recall
Measures how much of the relevant information was successfully retrieved.
* **Formula**: `Relevant Retrieved / Total Relevant`
* **Example**: If 2 relevant chunks exist and 1 is retrieved, Recall = `50%`.

### 3. Faithfulness
Checks whether the generated answer is grounded in and supported by the retrieved context. 
* *Note: If the context says "12 days" but the model answers "10 days", the answer is not faithful.*

### 4. Correctness
Checks whether the final generated answer matches the ground-truth answer in the Golden Dataset.
* **Faithful + Correct**: Correct context retrieved + Correct answer generated.
* **Faithful but Incorrect**: Wrong context retrieved + Answer matches the wrong context.

### 5. Relevance
Checks whether the answer actually addresses the user's original question directly. Factually correct answers can still be irrelevant if they don't answer what was asked.

## 🛠️ Debugging Using Metrics

Use the evaluation scores to diagnose and fix your RAG system:

| Problem | Possible Area | Recommended Fix |
| :--- | :--- | :--- |
| **Low Precision** | Retrieval / Top-K | Reduce `top_k` or increase similarity threshold. |
| **Low Recall** | Retrieval / Similarity Threshold | Increase `top_k` or lower similarity threshold. |
| **Good Retrieval but Wrong Answer** | LLM / Knowledge Base | Check document quality or update LLM model. |
| **Low Faithfulness** | System Prompt / Hallucination | Improve system prompt instructions to stick to context. |
| **Low Relevance** | Prompt / Answer Instructions | Tune the prompt to address questions directly. |


## 🧠 Evaluation Architecture

```text
Question
   ↓
Query Embedding
   ↓
Vector Database (Qdrant)
   ↓
Relevant Context
   ↓
LLM Generation (Groq)
   ↓
Final Answer
   ↓
LLM-as-a-Judge Evaluation
   ├── Precision
   ├── Recall
   ├── Faithfulness
   ├── Correctness
   └── Relevance
```

### Key Takeaways
* **Precision** → Are retrieved chunks relevant?
* **Recall** → Did we retrieve all important information?
* **Faithfulness** → Is the answer supported by the context?
* **Correctness** → Does the answer match the ground truth?
* **Relevance** → Does the answer address the question?
