# Day 5 - Resume Parser & AI Resume Evaluator

## Overview
This project is part of my AI Engineering learning journey. It combines all the concepts learned during Week 1 into a practical mini-project that demonstrates how LLMs can automate resume screening and candidate evaluation.

 This is the first mini-project of this AI Engineering series. The goal is to build an AI-powered Resume Evaluator that helps HR teams automatically compare multiple resumes with a job description and rank candidates based on their suitability.

Instead of manually reading every resume, the application:

- Extracts structured information from a Job Description.
- Reads resumes in PDF and DOCX formats.
- Parses resumes into structured data using LLMs.
- Compares each resume against the Job Description.
- Generates a match score along with strengths, weaknesses, and a final recommendation.

This project combines the concepts learned throughout Week 1, including Prompt Engineering, Structured Outputs, Pydantic Models, and JSON Parsing.

---

# Project Workflow

```
Job Description
        │
        ▼
Parse Job Description
        │
        ▼
Structured Job Object
        │
        ▼
Read Resume Files
(PDF / DOCX)
        │
        ▼
Extract Resume Text
        │
        ▼
Parse Resume
        │
        ▼
Structured Resume Object
        │
        ▼
Compare Resume vs Job Description
        │
        ▼
Match Score + Feedback
```

---

# Technologies Used

- Python
- Groq API
- Instructor
- Pydantic
- PyPDF
- python-docx
- python-dotenv

---

# Project Structure

```text
day5/
│── resumes/
│   ├── sample_resume1.pdf
│   ├── sample_resume2.pdf
│   ├── sample_resume3.pdf
│   └── sample_resume4.docx
│
│── resume_parser.py      # Main AI Resume Evaluator implementation
│── main.py               # Entry point
│── pyproject.toml        # Project configuration
│── uv.lock               # Dependency lock file
│── README.md
```
---

# Part 1 - Parsing the Job Description

The first step is to convert an unstructured Job Description into a structured object.

Instead of comparing raw text, the LLM extracts important information such as:

- Role
- Required Skills
- Preferred Skills
- Minimum Experience
- Educational Requirements
- Responsibilities

This structured format makes later comparisons much easier.

Example:

```text
Software Development Engineer
Required Skills:
- Java
- Python
- DSA
- OOP

Preferred Skills:
- AWS
- Docker
- Kubernetes
```

---

# Part 2 - Designing the Resume Schema

Unlike Job Descriptions, resumes don't follow a fixed format.

Some resumes contain:

- Experience
- Projects
- Certifications
- Skills
- Education

while others may omit some sections completely.

To handle this variability, a flexible Resume schema is created using Pydantic.

The Resume model contains fields like:

- Name
- Email
- Phone
- Skills
- Experience
- Projects
- Certifications
- Education
- Total Experience

Optional fields allow resumes with missing sections to be parsed successfully.

---

# Part 3 - Reading Resume Files

The application supports two resume formats:

- PDF
- DOCX

Separate helper functions read each file type and convert the entire resume into plain text.

```
PDF
   │
   ▼
Text

DOCX
   │
   ▼
Text
```

After this step, every resume is available as a string regardless of its original format.

---

# Part 4 - Parsing the Resume

The extracted resume text is sent to the LLM.

Using the predefined Resume schema, the model extracts structured information including:

- Personal Information
- Skills
- Work Experience
- Education
- Projects
- Certifications

Anything irrelevant is ignored.

Example output:

```json
{
  "name": "John Doe",
  "skills": [
    "Python",
    "Java",
    "AWS"
  ],
  "experience": [
    {
      "company": "Amazon",
      "role": "SDE Intern"
    }
  ]
}
```

---

# Part 5 - Resume Evaluation & Scoring

Once both objects are ready:

- Structured Job Description
- Structured Resume

they are compared using another LLM prompt.

The model returns:

- Candidate Name
- Matching Skills
- Missing Skills
- Experience Match
- Overall Score (0-100)
- Final Verdict

Example:

```
Candidate: John Doe

Match Score: 89%

Matching Skills
- Python
- Java
- AWS

Missing Skills
- Docker

Experience Requirement
✓ Satisfied

Verdict
Highly Recommended
```

This score helps HR quickly shortlist the best candidates.

---

# Concepts Covered

- Prompt Engineering
- Structured Outputs
- Pydantic Models
- Instructor Library
- JSON Parsing
- Resume Parsing
- Job Description Parsing
- PDF Reading
- DOCX Reading
- Information Extraction
- AI-based Resume Matching

---

# What I Learned

- Why structured data is better than raw text.
- Designing reusable Pydantic schemas.
- Parsing documents using LLMs.
- Reading PDF and DOCX files in Python.
- Comparing structured objects instead of text.
- Building a complete AI-powered workflow.

---

# References

- Groq API
- Instructor Library
- Pydantic
- PyPDF
- python-docx
