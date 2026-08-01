# Day 7 - ReAct (Reasoning + Action) AI Agent

## Overview

Day 7 introduces the **ReAct (Reasoning + Action)** framework, one of the most important concepts used in modern AI Agents.

Unlike a traditional LLM that directly answers a question, a ReAct agent **thinks step-by-step**, decides which tool should be used, executes that tool, observes the result, and continues this reasoning loop until it reaches the final answer.

In this project, a shopping assistant AI agent is built using the **Groq API** and the **Llama 3.3 70B Versatile** model. The agent can use Python functions as tools to answer multi-step questions.

---

# Objective

- Understand the ReAct (Reasoning + Action) architecture.
- Learn how AI Agents use external tools.
- Implement a tool-calling workflow.
- Execute reasoning in multiple steps.
- Build a simple shopping assistant capable of solving multi-step queries.

---

# Technologies Used

- Python
- Groq API
- Llama 3.3 70B Versatile
- python-dotenv
- Regular Expressions (`re`)

---

# Project Structure

```text
day7/
│── reAct.py              # ReAct AI Agent implementation
│── main.py               # Entry point
│── pyproject.toml        # Project configuration
│── uv.lock               # Dependency lock file
└── README.md
```

---

# Project Workflow

```text
User Question
      │
      ▼
System Prompt
      │
      ▼
LLM Reasoning
(Thought)
      │
      ▼
Choose Tool
(Action)
      │
      ▼
Execute Python Function
      │
      ▼
Observation
      │
      ▼
Reason Again
      │
      ▼
Final Answer
```

---

# Tools Used

The agent is provided with two Python functions that act as external tools.

### 1. Product Price Tool

```python
get_product_price(product)
```

Returns the predefined price of supported products.

Example

```
Iphone 17 → 1000
Iphone 15 → 500
```

---

### 2. Calculator Tool

```python
calculator(expression)
```

Evaluates mathematical expressions and returns the calculated value.

Example

```
5000 - 1000
```

returns

```
4000
```

These tools are stored in a dictionary so the agent can dynamically choose and execute them. :contentReference[oaicite:1]{index=1}

---

# System Prompt

The system prompt transforms the LLM into a **Shopping Assistant**.

It instructs the model to:

- Think before acting.
- Use only available tools.
- Call one tool at a time.
- Never invent tool outputs.
- Wait for observations.
- Continue reasoning.
- Produce a final answer only after completing all steps.

It also defines a fixed output format:

```
Thought:
Action:
Final Answer:
```

This structure enables the ReAct reasoning loop. :contentReference[oaicite:2]{index=2}

---

# ReAct Loop

The agent follows these steps:

1. Receive the user's question.
2. Analyze the problem.
3. Decide which tool is required.
4. Execute the selected tool.
5. Receive the observation.
6. Store the observation in conversation memory.
7. Continue reasoning.
8. Repeat until the final answer is generated.

The implementation limits execution to a maximum of **5 reasoning steps** to prevent infinite loops. :contentReference[oaicite:3]{index=3}

---

# Example Question

```text
I have $9000.
What is the price of an Iphone 17?
How much money will I have left after purchasing it?
```

### Step 1

```
Thought:
Need to find the product price.

Action:
get_product_price("Iphone 17")
```

Observation

```
1000
```

---

### Step 2

```
Thought:
Calculate remaining money.

Action:
calculator("9000 - 1000")
```

Observation

```
8000
```

---

### Step 3

```
Final Answer:
The price of the Iphone 17 is $1000.
You will have $8000 remaining after purchasing it.
```

---

# Concepts Covered

- ReAct (Reasoning + Action)
- AI Agents
- Tool Calling
- Multi-step Reasoning
- Prompt Engineering
- System Prompts
- Function Calling
- Conversation Memory
- Regular Expressions
- Observation Loop

---

# Key Learnings

- LLMs become significantly more powerful when they can use external tools.
- ReAct enables the model to reason before taking an action.
- Breaking problems into smaller steps improves reliability.
- Tool outputs (observations) are reused in future reasoning steps.
- Conversation history acts as the agent's memory.
- Regular expressions help extract tool names and arguments from model responses.
- Limiting reasoning iterations prevents endless execution loops.

---

# References

- Groq API Documentation
- ReAct (Reasoning + Acting) Framework
- Llama 3.3 70B Versatile
