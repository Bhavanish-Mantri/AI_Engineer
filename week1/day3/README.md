# Day 3 - Tokens

## Overview

On Day 3, I explored how Large Language Models use **tokens** and how to monitor token usage while interacting with the Groq API.

This project demonstrates sending multiple prompts to an LLM, limiting the output using the `max_tokens` parameter, and analyzing the token statistics returned by the API.

## Objective

- Understand what tokens are.
- Learn how `max_tokens` controls the response length.
- Track prompt and completion token usage.
- Understand the `finish_reason` returned by the model.

## Project Structure

```
day3/
│── tokens.py          # Main implementation
│── main.py            # Basic Python entry file
│── pyproject.toml     # Project configuration
│── uv.lock            # Dependency lock file
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
3. Sends multiple prompts to the LLM.
4. Limits the generated response using `max_tokens`.
5. Displays token usage statistics.
6. Prints the finish reason for each response.

## Prompts Used

```
Hi!
```

```
Explain time travel in detail under 100 words
```

```
Write a 1000 word essay on Machine Learning
```

## Output Information

For every prompt, the program displays:

- Prompt Tokens
- Completion Tokens
- Total Tokens
- Finish Reason

Example:

```
Prompt: Hi!
Prompt Tokens: 8
Completion Tokens: 15
Total Tokens: 23
Finish Reason: stop
```

If the model reaches the maximum token limit before completing its response, the finish reason will be:

```
length
```

Otherwise, if the response completes naturally, it will be:

```
stop
```

## Concepts Covered

- Large Language Models (LLMs)
- Tokens
- Prompt Tokens
- Completion Tokens
- Total Tokens
- max_tokens
- Finish Reason
- API Usage Monitoring

## Key Learnings

- LLMs process text as tokens rather than words.
- Longer prompts and responses consume more tokens.
- `max_tokens` sets the maximum number of output tokens the model can generate.
- The API provides detailed token usage statistics for every request.
- Monitoring token usage is important for managing API costs and optimizing applications.

## References

- Groq API Documentation
- Llama 3.3 70B Versatile
- Python Dotenv
