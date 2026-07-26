# Day6 - Prompt Engineering Fundamentals

## Overview

Day 6 introduces one of the most important concepts in Generative AI—**Prompt Engineering**.
This lesson teaches how to communicate effectively with Large Language Models (LLMs). A well-designed prompt produces stable, predictable, and production-ready responses, while a vague prompt often leads to inconsistent and unreliable outputs.

This project demonstrates the transformation of a **bad prompt** into a **well-engineered prompt** by progressively applying six prompt engineering techniques.

---

# Objective

- Understand why Prompt Engineering is important.
- Learn the limitations of vague prompts.
- Build production-ready prompts.
- Improve response consistency.
- Restrict LLM behavior using constraints.
- Design prompts for real-world AI applications.

---

# Technologies Used

- Python
- Groq API
- Llama 3.3 70B Versatile
- python-dotenv

---

# Project Structure

```text
day6/
│── prompt_eng.py          # Prompt Engineering examples
│── main.py                # Entry point
│── pyproject.toml         # Project configuration
│── uv.lock                # Dependency lock file
└── README.md
```

---

# Project Workflow

```
User Complaint
        │
        ▼
Prompt Engineering
(Role + Task + Constraints
+ Output Format + Example + Fallback)
        │
        ▼
Groq Llama Model
        │
        ▼
Structured Classification
```

---

# Part 1 - Why Prompt Engineering?

Large Language Models are **non-deterministic**.

The same question asked multiple times can produce different answers.

Example

```
Tell me about yourself
```

may generate different responses every time.

This becomes a problem when AI is integrated into software systems because downstream code expects predictable outputs.

Prompt Engineering helps make responses:

- Stable
- Consistent
- Predictable
- Easier to process

---

# Part 2 - The Problem with Bad Prompts

A vague prompt provides almost no instructions.

Example:

```text
This is a user complaint:

My laptop is not working.

Classify this.
```

Problems:

- No role defined
- No clear task
- No output format
- No constraints
- No fallback behavior
- Different outputs every execution

Example Output

```
I would classify this complaint as a technical issue related to hardware malfunction...
```

The answer is correct but difficult for software to consume.

---

# Part 3 - Role

The first improvement is defining the AI's role.

Example

```text
ROLE

You are a customer support assistant at a mobile/laptop company.
```

This gives the model context about **who it is**.

Important Note

A role should describe the model's **domain** or **responsibility**, not increase its intelligence.

Good

```
You are a Senior Python Developer.
```

Bad

```
You are a Genius AI.
```

---

# Part 4 - Task

The next step is specifying exactly what the model should do.

Example

```text
TASK

Classify the customer's issue.
```

The task should be clear and unambiguous.

Examples

- Summarize
- Translate
- Extract Information
- Classify
- Generate Code

---

# Part 5 - Constraints

Constraints limit the possible outputs.

Example

```text
The issue must belong to one of these categories:

- Billing
- Technical
- Return
```

Benefits

- Prevents random categories
- Makes outputs predictable
- Improves production reliability

---

# Part 6 - Output Format

Always specify how the answer should look.

Example

```text
Output only ONE word.

Possible outputs:

Billing
Technical
Return
```

Instead of:

```
I believe this is a technical issue because...
```

The model now simply returns:

```
Technical
```

which is much easier for software systems to process.

---

# Part 7 - One-shot / Few-shot Prompting

Providing examples helps the model understand the expected behavior.

Example

```text
If a customer asks for a refund

Output:

Return
```

This is called **One-shot Prompting**.

Multiple examples are called **Few-shot Prompting**.

Examples improve consistency and accuracy.

---

# Part 8 - Fallback

Real-world users may ask unrelated questions.

Example

```
My girlfriend left me.
```

Without a fallback, the model may incorrectly classify it.

A fallback instruction solves this.

Example

```text
If the issue does not belong to any category,
return

Not Applicable
```

This prevents incorrect classifications.

---

# Final Engineered Prompt

```text
ROLE

You are a customer support assistant at a mobile/laptop company.

TASK

Classify the issue.

CONSTRAINTS

Only classify into:

- Billing
- Technical
- Return

OUTPUT FORMAT

Return exactly one word.

EXAMPLE

Refund request → Return

FALLBACK

If unrelated, return

Not Applicable
```

---

# Concepts Covered

- Prompt Engineering
- Bad vs Good Prompts
- Role Prompting
- Task Prompting
- Constraints
- Output Formatting
- One-shot Prompting
- Few-shot Prompting
- Zero-shot Prompting
- Fallback Responses
- Production-ready AI Prompts

---

# Key Learnings

- Small prompt changes significantly improve output quality.
- Production AI systems require predictable responses.
- Every prompt should clearly define the model's role.
- Always specify the required task.
- Restrict the model using constraints.
- Define a strict output format.
- Examples improve model understanding.
- Always include a fallback for unexpected inputs.

---

# References

- Groq API Documentation
- Prompt Engineering Best Practices
- Llama 3.3 70B Versatile
