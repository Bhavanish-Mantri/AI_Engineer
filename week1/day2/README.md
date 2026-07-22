# Day 2 - System role & Temperature

## Overview

On Day 2, I explored how to control the behavior of a Large Language Model (LLM) using **System Prompts** and the **Temperature** parameter.

Instead of sending only a user prompt, this project introduces a **system message** that defines the AI's role and response style. It also demonstrates how increasing the temperature makes the model generate more creative responses.

## Objective

- Learn the purpose of system prompts.
- Understand the difference between system and user messages.
- Explore the effect of the temperature parameter.
- Generate AI-powered brand name suggestions.

## Project Structure

```
day2/
│── system_temp.py      # Main implementation
│── main.py             # Basic Python entry file
│── pyproject.toml      # Project configuration
│── uv.lock             # Dependency lock file
│── .gitignore
│── .python-version
└── README.md
```

## Technologies Used

- Python
- Groq API
- Llama 3.3 70B Versatile
- python-dotenv

## What This Project Does

The program:

1. Loads the API key from the `.env` file.
2. Creates a Groq client.
3. Defines a **System Prompt** that tells the AI to behave like a Brand Manager.
4. Sends a user prompt asking for a clothing company name.
5. Uses a higher temperature to generate a more creative response.
6. Prints the generated result.

## Example

### System Prompt

```
You are a Brand Manager. Suggest one unique name for my new clothing company.
```

### User Prompt

```
Suggest name for my new clothing company
```

### Possible Output

```
Veloura
```

Every execution may produce a different result because the temperature is set to **2**, which encourages more creative responses.

## Concepts Covered

- Large Language Models (LLMs)
- System Prompt
- User Prompt
- Prompt Engineering
- Temperature
- Creativity Control
- Chat Completions API

## Key Learnings

- A **System Prompt** defines the AI's role and behavior.
- A **User Prompt** contains the actual request.
- The system prompt has a strong influence on how the model responds.
- Higher temperature values produce more diverse and creative outputs.
- Lower temperature values generate more consistent and deterministic responses.

## References

- Groq API Documentation
- Llama 3.3 70B Versatile
- Python Dotenv
