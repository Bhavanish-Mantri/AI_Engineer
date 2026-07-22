# Day 1 - Hello LLM with Groq

## Overview

This project is my first step in learning AI Engineering. The goal of this project is to understand how to interact with a Large Language Model (LLM) using the Groq API.

The program sends a prompt to the **Llama 3.3 70B Versatile** model and prints both the complete API response and the generated answer.

## What I Learned

- How LLM APIs work
- Creating a Groq client
- Loading API keys securely using environment variables
- Sending prompts to an AI model
- Reading responses returned by the model

## Project Structure

```
day1/
│── hello_llm.py        # Main program
│── main.py             # Basic Python entry file
│── pyproject.toml      # Project configuration
│── uv.lock             # Dependency lock file
│── .gitignore
│── .python-version
└── README.md
```

## Requirements

- Python 3.13+
- Groq API Key

## Dependencies

- groq
- python-dotenv

## How It Works

1. Loads the API key from the `.env` file.
2. Creates a Groq client.
3. Selects the `llama-3.3-70b-versatile` model.
4. Sends a prompt to the model.
5. Receives the response.
6. Prints the generated answer.

## Sample Prompt

```
Do you know MS Dhoni
```

You can replace this prompt with any question to interact with the model.

## Files

### `hello_llm.py`

Contains the complete implementation for:
- Loading environment variables
- Initializing the Groq client
- Sending prompts
- Receiving responses
- Printing the model output

### `main.py`

A simple Python entry file used for testing the project setup.

## Concepts Covered

- Large Language Models (LLMs)
- API Integration
- Environment Variables
- Prompting
- Chat Completions
- Python Packages

## References

- Groq API
- Python Dotenv
- Llama 3.3 70B Versatile
