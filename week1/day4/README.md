# Day 4 - Pydantic & JSON

## Overview

On Day 4, I learned how to generate **structured JSON output** from a Large Language Model (LLM) using the Groq API and validate it with **Pydantic**.

Instead of receiving free-form text, the model is instructed to return data in a predefined JSON format. The JSON response is then parsed and converted into a Python object using a Pydantic model.

## Objective

- Understand structured outputs from LLMs.
- Create data schemas using Pydantic.
- Generate JSON responses from the model.
- Parse and validate JSON data.
- Convert JSON into Python objects.

## Project Structure

```
day4/
│── json_pydantic.py    # Main implementation
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
- Pydantic
- python-dotenv
- JSON

## What This Project Does

The program:

1. Loads the Groq API key from the `.env` file.
2. Creates a Pydantic model to define the expected output structure.
3. Generates a JSON schema from the Pydantic model.
4. Sends the schema to the LLM through a system prompt.
5. Requests the model to extract information from customer text.
6. Receives the response as a JSON object.
7. Parses the JSON into a Python dictionary.
8. Validates the data using the Pydantic model.
9. Accesses individual fields like any Python object.

## Pydantic Schema

```python
class Ticket(BaseModel):
    name: str
    email: str
    Issue: str
```

## Example Input

```text
Hello, My name is Bhavanish Mantri.
I have a phone which is not working that I bought from your shop.
I live in Delhi and my email is abc@gmail.com.
```

## Example Output

```json
{
  "name": "Bhavanish Mantri",
  "email": "abc@gmail.com",
  "Issue": "Phone is not working"
}
```

After parsing, the values can be accessed as:

```python
ticket.name
ticket.email
ticket.Issue
```

## Concepts Covered

- Large Language Models (LLMs)
- Structured Output
- JSON Response Format
- Pydantic Models
- JSON Schema
- Data Validation
- Prompt Engineering
- Information Extraction

## Key Learnings

- LLMs can generate structured JSON instead of plain text.
- Pydantic simplifies data validation and parsing.
- JSON schemas help guide the model toward consistent outputs.
- Structured responses are easier to integrate into real-world applications.
- Parsed Pydantic objects can be used directly in Python programs.

## References

- Groq API Documentation
- Pydantic Documentation
- Python JSON Module
