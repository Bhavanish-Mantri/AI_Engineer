# Day10 - Personal Portfolio AI

## Overview

Day 10 focuses on building the backend of an AI-powered web application and understanding how the frontend communicates with Python code through an API.

The session introduces **FastAPI** and explains how it can be used to convert Python code into a web application that can receive HTTP requests and return responses.

The concepts covered include APIs, frontend and backend separation, FastAPI routes, GET and POST requests, request data, Pydantic models, Uvicorn, and connecting existing resume parsing and LLM functionality to a backend API.

## Objective

- Understand the role of a backend in an AI application.
- Understand how a frontend communicates with a backend.
- Learn the purpose of an API.
- Create a basic FastAPI application.
- Create API routes using FastAPI.
- Understand GET and POST requests.
- Use Pydantic models for request data.
- Run a FastAPI application locally.
- Connect resume parsing logic with the backend.
- Connect LLM functionality with an API endpoint.
- Understand how a frontend can communicate with the backend.

## Technologies Used

- Python
- FastAPI
- Uvicorn
- Groq API
- Pydantic
- PyPDF
- python-dotenv
- HTML
- CSS
- JavaScript

## Project Structure

```text
day10/
│
├── backend/
│   ├── main.py
│   ├── resume_parser.py
│   └── resume.pdf
│
├── frontend/
│   ├── public/
│   ├── src/
│   ├── .gitignore
│   ├── .oxlintrc.json
│   ├── README.md
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
│
├── pyproject.toml
├── uv.lock
└── README.md
```
## Part 1 - Frontend and Backend

A web application generally consists of two major parts: the frontend and the backend.

### Frontend

The frontend is the part of the application that the user interacts with.

It contains elements such as:

- Web pages
- Input fields
- Buttons
- Chat interfaces
- Displayed responses

### Backend

The backend contains the application logic that runs behind the user interface.

In this project, the backend is responsible for:

- Reading the resume
- Parsing the resume
- Processing candidate information
- Sending information to the LLM
- Generating responses
- Returning responses to the frontend

## Part 2 - API

An API acts as a communication layer between the frontend and backend.

The basic communication flow is:

```text
Frontend
   │
   │ HTTP Request
   ▼
FastAPI Backend
   │
   │ Process Request
   ▼
Python / LLM Logic
   │
   │ Response
   ▼
FastAPI Backend
   │
   │ HTTP Response
   ▼
Frontend
```

The browser communicates using HTTP requests and responses, while the backend contains the Python application logic.

The API acts as the middle layer that allows these two parts to communicate.

## Part 3 - FastAPI

**FastAPI** is used to create the backend API.

It allows Python functions to be exposed through HTTP endpoints.

A FastAPI application can contain multiple routes for different operations.

For example:

```text
GET  /
POST /chat
```

The root route can be used for the application's home endpoint, while the chat route can receive a user's question and return an AI-generated response.

## Part 4 - Creating a FastAPI Application

A basic FastAPI application can be created using:

```python
from fastapi import FastAPI

app = FastAPI()
```

A route can then be created using a decorator:

```python
@app.get("/")
def home():
    return {"message": "Hire Me AI is running"}
```

The `/` route represents the root endpoint of the application.

When the endpoint is accessed, the backend returns the defined response.

## Part 5 - API Routes

Routes determine what should happen when a particular URL is requested.

For example:

```python
@app.get("/")
def home():
    return {"message": "Hire Me AI is running"}
```

The route:

```text
/
```

represents the root or home endpoint.

FastAPI uses decorators such as:

```python
@app.get()
@app.post()
```

to define how different HTTP requests should be handled.

## Part 6 - GET and POST Requests

### GET

A GET request is generally used to retrieve information.

Example:

```text
GET /
```

The request can be used when the client wants to access a page or retrieve information.

### POST

A POST request is used when the client needs to send data to the backend.

For the chat functionality, the frontend needs to send the user's question to the backend.

Example:

```text
POST /chat
```

The backend receives the question, processes it, and returns a response.

## Part 7 - Request Model

Pydantic can be used to define the structure of incoming request data.

For example, a chat request can contain a question:

```json
{
    "question": "What is the candidate's experience with networking?"
}
```

The backend receives this request and passes the question to the appropriate function.

## Part 8 - Resume Processing

The resume parsing functionality developed earlier is integrated into the backend.

The basic flow is:

```text
Resume PDF
    │
    ▼
Extract Text
    │
    ▼
Parse Resume
    │
    ▼
Structured Resume Data
    │
    ▼
Use Resume Data as LLM Context
```

The resume is first converted into text because the LLM works with text input.

The extracted information is then converted into structured resume data and used when answering questions about the candidate.

## Part 9 - Connecting the LLM

The existing Groq-based LLM functionality is integrated into the FastAPI backend.

The backend receives the user's question and combines it with the parsed resume information.

The overall process becomes:

```text
User Question
      │
      ▼
FastAPI Endpoint
      │
      ▼
Question + Resume Data
      │
      ▼
Groq LLM
      │
      ▼
Generated Answer
      │
      ▼
FastAPI Response
```

This allows the backend to answer questions based on the candidate's resume.

## Part 10 - Chat Endpoint

A separate endpoint is created for the chat functionality.

The endpoint receives a chat request containing the user's question.

The basic flow is:

```text
POST /chat
     │
     ▼
Receive Question
     │
     ▼
Read Resume Data
     │
     ▼
Send Question + Resume to LLM
     │
     ▼
Generate Answer
     │
     ▼
Return Response
```

The endpoint uses a POST request because the client needs to send the user's question to the backend.

## Part 11 - FastAPI Documentation

FastAPI automatically provides interactive API documentation.

This allows the backend endpoints to be tested without creating the frontend first.

The documentation can be used to:

- View available endpoints
- View request methods
- Inspect request formats
- Enter request data
- Execute requests
- View responses

This makes it easier to test and debug the backend.

## Part 12 - Running the Backend

FastAPI applications are commonly run using **Uvicorn**.

The application can be started using:

```bash
uv run uvicorn main:app --reload
```

The `--reload` option allows the development server to automatically reload when changes are made to the code.

After starting the server, the FastAPI application becomes available on the local machine.

## Part 13 - Frontend Integration

The frontend provides the user interface through which the user interacts with the AI application.

Instead of manually testing the API through the FastAPI documentation, the frontend can send requests directly to the backend.

The communication flow becomes:

```text
User
 │
 ▼
Frontend Chat Interface
 │
 │ POST /chat
 ▼
FastAPI Backend
 │
 ▼
Resume + LLM
 │
 ▼
AI Response
 │
 ▼
Frontend
 │
 ▼
User
```

This connects the user interface with the AI backend.

## Architecture

```text
                         USER
                           │
                           ▼
                 ┌──────────────────┐
                 │     FRONTEND     │
                 │   Chat Interface │
                 └────────┬─────────┘
                          │
                          │ HTTP Request
                          ▼
                 ┌──────────────────┐
                 │     FASTAPI      │
                 │     BACKEND      │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │   Chat Endpoint  │
                 │     /chat        │
                 └────────┬─────────┘
                          │
                 ┌────────┴─────────┐
                 │                  │
                 ▼                  ▼
        ┌────────────────┐  ┌────────────────┐
        │ Resume Parser  │  │   Groq LLM     │
        │                │  │                │
        │ PDF → Text →   │  │ Question +     │
        │ Structured Data│  │ Resume Context │
        └───────┬────────┘  └───────┬────────┘
                │                   │
                └─────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │  Generated AI    │
                 │     Response     │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │     FRONTEND     │
                 └────────┬─────────┘
                          │
                          ▼
                         USER
```

## Key Concepts Covered

- Frontend and Backend
- API
- HTTP
- Request and Response
- FastAPI
- Uvicorn
- API Routes
- GET Requests
- POST Requests
- Pydantic
- Request Models
- Localhost
- FastAPI Documentation
- Resume Parsing
- LLM Integration
- Frontend-Backend Communication

## Key Learnings

- Frontend and backend have different responsibilities.
- APIs allow the frontend and backend to communicate.
- FastAPI can expose Python functionality through HTTP endpoints.
- GET and POST requests serve different purposes.
- POST requests can be used to send user input to the backend.
- Pydantic can define and validate request data.
- FastAPI automatically provides interactive API documentation.
- Existing AI logic can be integrated into a backend API.
- A frontend can communicate with the backend through HTTP requests.


## Summary

Day 10 introduces the backend layer required to turn an AI Python script into a web application.

The main communication flow is:

```text
Frontend
    │
    │ HTTP Request
    ▼
FastAPI Backend
    │
    ▼
Python + Resume Data + LLM
    │
    │ HTTP Response
    ▼
Frontend
```

The session provides the foundation for connecting an AI backend with a frontend and building a complete AI-powered web application.
