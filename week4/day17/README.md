# Day 17 - AI Agent - Tools and Function Calling

A practical introduction to building an **AI Agent** using an LLM, Python functions, APIs, tool schemas, system prompts, and automatic tool selection.

This project demonstrates how an LLM can move beyond generating text by using external tools to perform tasks such as **mathematical calculations and web searches**.

---

## 🎯 Overview

A normal LLM can generate text, but it cannot directly perform every real-world action.

For example:
- Mathematical calculations can be handled by a calculator.
- Current information can be obtained through web search.
- Flight booking can be performed through a flight API.
- Messages can be sent using a messaging API.

An **AI Agent** combines an LLM with such tools.

```text
LLM + Tools
    ↓
AI Agent
    ↓
Decision Making
    ↓
Tool Execution
    ↓
Final Answer
```

---

## 🤖 What is an AI Agent?

An AI Agent can be understood as:
```text
AI Agent = LLM + Tools
```

The LLM understands the user's request and decides whether a tool is required.

**Example 1:**
```text
User: What is 10 × 21?
  ↓
LLM
  ↓
Calculator Tool
  ↓
210
```

**Example 2:**
```text
User: Who is Pratyush Narayan?
  ↓
LLM
  ↓
Web Search Tool
  ↓
Search Result
```

The important idea is that the LLM itself does not perform every operation. It can use external tools when required. 

---

## 🆚 LLM vs AI Agent

| LLM | AI Agent |
| :--- | :--- |
| Generates text | Generates text + performs actions |
| Works mainly with learned knowledge | Can access external tools |
| Cannot directly call external functions | Can call functions/APIs |
| Example: ChatGPT as an LLM | LLM + Calculator/Web Search |

```text
LLM  →  Add Tools  →  AI Agent
```

---

## 🛠️ What is a Tool?

A **tool** is a function or API that an LLM can use to perform a specific task.

Examples:
* Calculator
* Web Search
* Flight Booking API
* Payment API
* Email API

In Python, a tool can simply be a normal function:
```python
def calculate(expression):
    # perform calculation
    return result
```

Functions available to an agent are exposed as **tools** to the LLM. 

---

## 🔍 Example Agent Tools

This project uses two main tools:
1. **Calculator**
2. **Web Search**

### Calculator
Used for mathematical operations.
*Example: `25 * 15`*

### Web Search
Used for information that may be current or changing.
*Examples: Current events, Prices, Recent facts, Statistics, Latest information.*

Web search is used for information that may change after the model's training period. 

---

## 📋 Tool Schema

The LLM needs information about the tools available to it. A tool definition generally contains:
- **Type**
- **Name**
- **Description**
- **Parameters**

Example:
```json
{
  "type": "function",
  "name": "web_search",
  "description": "Search the web for current information.",
  "parameters": {
    "query": {
      "type": "string"
    }
  }
}
```

The tool schema tells the LLM **what the tool does, when to use it, and what input it requires**. 

### Tool Description
The description tells the LLM **when the tool should be used**.
For example:
> *"Search the web for current information and recent facts."*

This helps the LLM understand that web search should be used for information that may have changed.

### Tool Parameters
Parameters define the input required by a tool.
* **Web Search**: `query: string` (e.g. "Who is Pratyush Narayan?")
* **Calculator**: `expression: string` (e.g. "25 * 15")

---

## 🗣️ System Prompt

The system prompt provides instructions to the AI Agent.

Example:
> *"You are an AI Agent. Use web search for current information. Use calculator for mathematical calculations."*

The system prompt helps guide the LLM's tool selection and overall behavior.

---

## ⚙️ Automatic Tool Selection

The project uses `tool_choice = "auto"`.

This allows the LLM to automatically decide which tool should be called based on the user's query.
* `10 * 21` → **Calculator**
* `Who is Pratyush Narayan?` → **Web Search**

The LLM makes this decision using the tool descriptions and parameters provided to it. 

---

## 🔄 Agent Workflow

The complete workflow can be represented as:

```text
                    User Query
                         │
                         ▼
                       LLM
                         │
                         ▼
                 Analyze the Query
                         │
                         ▼
                 Select Appropriate Tool
                    /            \
                   /              \
                  ▼                ▼
             Calculator       Web Search
                  │                │
                  └───────┬────────┘
                          ▼
                     Tool Result
                          │
                          ▼
                         LLM
                          │
                          ▼
                    Final Answer
```

---

## 🔁 Multi-Step Agent & Iterations

An agent may need more than one tool call to complete a complex task.

Example:
```text
Find a person's YouTube channel
        ↓
Search for the person
        ↓
Find the YouTube channel
        ↓
Search the channel
        ↓
Find required information
        ↓
Final Answer
```

An **iteration** represents another cycle of the agent's reasoning and tool execution.

A maximum iteration limit (e.g., `Max Iterations = 3`) helps control:
* Token usage
* API usage
* Tool costs
* Infinite loops

---

## 🚀 Project Workflow

The implementation follows these major steps:
1. Create Python Functions
2. Define Available Tools
3. Create Tool Schemas
4. Add Tool Descriptions
5. Define Parameters
6. Create System Prompt
7. Send Tools to the LLM
8. Set `tool_choice = "auto"`
9. Receive Tool Call
10. Execute Function
11. Return Tool Result
12. Generate Final Answer

---

## 🔑 Setup and API Keys

The web search tool uses the **Tavily API**. API keys are stored in an environment `.env` file rather than directly inside the source code:
```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Run the agent:
```bash
python agent.py
```

---

## 🧠 Connection to LangGraph

Manually building an agent becomes increasingly complex when:
* More tools are added.
* Multiple agents are introduced.
* Tasks require multiple steps.
* Different agents need to coordinate.

Managing large agent workflows manually becomes difficult. This leads to frameworks such as **LangGraph**, which orchestrate and manage complex agent workflows. 

---

## 💡 Key Learnings

By completing this project, you will understand:
1. What an AI Agent is.
2. Difference between an LLM and an AI Agent.
3. What tools are and how Python functions/APIs become tools.
4. Why tool descriptions and schemas are important.
5. How system prompts guide agents.
6. How automatic tool selection (`tool_choice="auto"`) works.
7. What agent iterations are and why iteration limits are required.
8. How multi-step tool calling works.
9. Why frameworks like LangGraph become useful for complex agents.

---

## ✨ Summary: The Important Concept

The most important idea from this project is:
```text
LLM + Tools + Tool Descriptions + System Instructions + Tool Calling = AI Agent
```

Instead of only generating text, an AI Agent can **Understand the Query → Choose a Tool → Call the Tool → Receive the Result → Continue Reasoning → Generate Final Answer**.
