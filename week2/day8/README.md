# Day 8 - Prompt Chaining

## Overview

Day 8 introduces **Prompt Chaining**, a technique for solving complex tasks by breaking them into a sequence of smaller prompts instead of relying on a single large prompt.

Each prompt is designed to perform one specific task, and its output is passed to the next prompt in the chain. This modular approach makes AI workflows easier to debug, maintain, optimize, and scale, making Prompt Chaining a widely used design pattern in production LLM applications.

---

# Objective

- Understand Prompt Chaining.
- Learn how to divide complex AI tasks into multiple LLM calls.
- Build a modular AI workflow.
- Compare candidate skills with job requirements.
- Generate an automated hiring score and verdict.

---

# Technologies Used

- Python
- Groq API
- Llama 3.3 70B Versatile
- python-dotenv

---

# Project Structure

```text
day8/
│── chaining.py          # Prompt Chaining implementation
│── main.py             
│── pyproject.toml
│── uv.lock
└── README.md
```

---

# Prompt Chaining Workflow

```text
Resume
   │
   ▼
Extract Resume Skills
   │
   ▼
Candidate Skills
   │
   ▼
Extract JD Skills
   │
   ▼
Job Skills
   │
   ▼
Compare Both
   │
   ▼
Score + Verdict
```

---

# Step 1 – Resume Skill Extraction

The first LLM call receives the candidate's resume and extracts only the technical skills.

Prompt responsibilities:

- Read the resume.
- Extract only skills.
- Return comma-separated values.
- Avoid inventing information.

Example Output

```text
Python, FastAPI, MySQL, Docker, REST APIs, Git
```

---

# Step 2 – Job Description Skill Extraction

The second LLM call reads the job description and extracts only the required technical skills.

Example Output

```text
Python, FastAPI, PostgreSQL, Docker, AWS, REST APIs
```

---

# Step 3 – Candidate Matching

The final LLM call receives:

- Candidate Skills
- Job Skills

The model compares both lists and produces:

- Matching Score (1–100)
- Short Hiring Verdict

Example

```text
Score: 82/100

Verdict:
The candidate is a good fit for the Backend Python Developer role but lacks PostgreSQL and AWS experience.
```

---
# Prompt Chaining Pipeline

```text
Resume
   │
   ▼
┌──────────────────────────────┐
│ Step 1                       │
│ Extract Candidate Skills      │
└──────────────┬───────────────┘
               │
               │ Candidate Skills
               ▼
        ┌───────────────┐
        │               │
        │               │
        │               │
Job Description          │
       │                 │
       ▼                 │
┌──────────────────────────────┐
│ Step 2                       │
│ Extract JD Skills            │
└──────────────┬───────────────┘
               │
               │ JD Skills
               ▼
      ┌────────────────────────┐
      │ Step 3                 │
      │ Compare Candidate      │
      │ Skills with JD Skills  │
      │ Generate Score         │
      │ Generate Verdict       │
      └─────────────┬──────────┘
                    │
                    ▼
        Final Candidate Evaluation
```

---

# Why Prompt Chaining?

Compared to one large prompt, Prompt Chaining provides several advantages:

- Easier debugging.
- Modular design.
- Reusable prompts.
- Better maintainability.
- Higher reliability.
- Easier prompt optimization.
- Ability to replace or improve individual steps without changing the entire workflow.

---

# Key Functions

### `ask_llm()`

A reusable function that sends system and user prompts to the Groq API and returns the model's response.

---

### `resume_extract()`

Extracts technical skills from the candidate's resume.

---

### `jd_extract()`

Extracts required skills from the job description.

---

### `matching()`

Compares extracted candidate skills with job requirements and generates a score and hiring recommendation.

These three functions together form the Prompt Chaining pipeline. :contentReference[oaicite:1]{index=1}

---

# Concepts Covered

- Prompt Chaining
- Multi-Step AI Workflows
- Prompt Engineering
- LLM Pipelines
- Resume Parsing
- Skill Extraction
- Candidate Matching
- Modular AI Design
- HR Automation

---

# Key Learnings

- Complex AI tasks should be divided into smaller independent prompts.
- Each prompt should focus on solving only one problem.
- Outputs from one LLM call can become inputs for another.
- Modular workflows are easier to debug and improve.
- Prompt Chaining is widely used in production AI systems for reliability and maintainability.

---

# References

- Groq API Documentation
- Llama 3.3 70B Versatile
- Prompt Engineering Best Practices
