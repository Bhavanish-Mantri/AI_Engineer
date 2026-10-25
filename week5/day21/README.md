# 🛠️ Autonomous Java Bug-Fixing Coding Agent

An autonomous, lightweight coding agent designed to diagnose, locate, and fix bugs in Java codebases from natural language descriptions—built purely with Python, the **Groq API**, and the **`openai/gpt-oss-120b`** model without heavyweight orchestrators like LangGraph or LangChain.

---

## 📌 Architecture & Design Philosophy

Rather than using complex agent frameworks, this project demonstrates how to build an agent loop from scratch using standard LLM function calling (tools) and a verification feedback cycle.

```
                    ┌─────────────────────────┐
                    │ Natural Language Report │
                    └───────────┬─────────────┘
                                │
                                ▼
              ┌─────────────────────────────────────┐
              │  Autonomous Loop (Groq API LLM)     │
              │       Model: openai/gpt-oss-120b    │
              └──────┬──────────────┬───────────────┘
                     │              │
    ┌────────────────▼───┐    ┌─────▼────────────────┐
    │ 1. search_files    │    │ 2. search_in_file    │
    │    Locate candidates│    │    Inspect line nos. │
    └────────────────────┘    └──────────────────────┘
                     │
                     ▼
              ┌──────────────────┐
              │ 3. replace_line  │
              │    Modify code   │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │ Verify: javac    │
              │  Compile & Run   │
              └────────┬─────────┘
            Pass?      │       Fail?
        ┌──────────────┴──────────────┐
        ▼                             ▼
  [Bug Solved]               [Compiler Feedback]
  Keep changes               Re-enter Loop (Max 3)
                             Fail -> Restore Snapshot
```

---

## ✨ Features

- **No Framework Overhead**: Implemented with standard Python and official SDKs (`groq`, `python-dotenv`), making the agent loop transparent and easy to debug.
- **Three Core Primitives**:
  - `search_files(keyword)`: Locates relevant workspace files by file name or contents.
  - `search_in_file(path, keyword)`: Inspects code with 1-indexed line numbers (supports full-file view with empty string).
  - `replace_line(path, line_number, new_line)`: Surgical single-line replacements that automatically maintain original whitespace indentation.
- **Verification Loop**: Uses the local Java compiler (`javac`) and JVM (`java`) to verify syntax and output. Compilation errors are automatically passed back to the model for self-correction.
- **Fail-Safe Rollback**: A file snapshot is captured before any modifications. If the agent cannot solve the bug within 3 attempts, all modified files and compiled artifacts are restored to their pristine state.

---

## 📁 Repository Structure

```text
day21/
├── java_project/                 # Isolated target Java project
│   └── Calculator.java           # Sample file containing business logic / bug
├── main.py                       # Core agent loop, LLM interaction, & verification
├── tools.py                      # Tool implementations & Groq function schemas
├── pyproject.toml                # Project metadata
└── README.md                     # Documentation
```

---

## 🚀 Getting Started

### Prerequisites

1. **Python 3.11+**
2. **Java Development Kit (JDK 17+)**: Ensure `javac` and `java` are available in your system `PATH`:
   ```bash
   javac -version
   java -version
   ```
3. **Groq API Key**: Obtain a key from the [Groq Console](https://console.groq.com/).

### Installation

1. Create and activate a virtual environment:

   ```powershell
   # Windows PowerShell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

2. Install dependencies:

   ```bash
   pip install groq python-dotenv
   ```

3. Set up your environment variables:
   Create a `.env` file in your workspace root (or in this directory):
   ```env
   GROQ_API_KEY=gsk_your_groq_api_key_here
   ```

---

## 💻 Usage

Run the agent via CLI:

```bash
python main.py
```

You will be prompted to enter the bug description in plain English:

```text
Describe the bug in simple English: In Calculator.java calculateTotal is subtracting tax instead of adding it. Please fix it.
```

You can also pass the workspace path as a command-line argument:

```bash
python main.py java_project
```

### Sample Session Output

```text
============================================================
MINI CODING AGENT (JAVA)
============================================================
Workspace: D:\AI_Engineer\week5\day21\java_project
Files    : Calculator.java

Describe the bug in simple English: In Calculator.java calculateTotal is subtracting tax instead of adding it. Please fix it.

============================================================
ATTEMPT 1 of 3
============================================================

[step 1] asking the LLM what to do next ...
[step 1] TOOL CALLED -> search_files
           args: {'keyword': 'Calculator'}
           result:
           | Calculator.java  (1 matches)

[step 2] asking the LLM what to do next ...
[step 2] TOOL CALLED -> search_in_file
           args: {'keyword': '', 'path': 'Calculator.java'}
           result:
           |    1: public class Calculator {
           |    2: 
           |    3:     public static double calculateTotal(double[] prices, double taxRate) {
           |    4:         double subtotal = 0.0;
           |    5:         for (double price : prices) {
           |    6:             subtotal += price;
           |    7:         }
           |    8:         // BUG: subtracting tax instead of adding it
           |    9:         double total = subtotal - (subtotal * taxRate);
           |   10:         return Math.round(total * 100.0) / 100.0;
           |   11:     }

[step 3] asking the LLM what to do next ...
[step 3] TOOL CALLED -> replace_line
           args: {'line_number': 9, 'new_line': '        double total = subtotal + (subtotal * taxRate);', 'path': 'Calculator.java'}
           result:
           | Line 9 of Calculator.java replaced.
           | before: double total = subtotal - (subtotal * taxRate);
           | after : double total = subtotal + (subtotal * taxRate);

[step 4] asking the LLM what to do next ...
[step 4] LLM finished (no tool call)

LLM summary:
           | Replaced line 9 in Calculator.java to add the tax instead of subtracting it.

------------------------------------------------------------
VERIFY: compiling and running Java code with javac & java
------------------------------------------------------------
Compile: OK
Program output:
           | Items subtotal: 175.0, tax: 10%
           | Calculated Total: 192.5
           | Expected Total  : 192.5

Is the bug fixed? (y/n): y
============================================================
BUG FIXED in attempt 1
============================================================
```

---

## 🛡️ Error Handling & Self-Correction

- **Compiler Error Reflection**: If an edit introduces a syntax error, `javac` compilation output is fed directly back into the conversation context as a user message:
  ```text
  Your change does not compile in Java. Compiler errors:
  Calculator.java:9: error: ';' expected
  Fix the code.
  ```
- **Max Retry Guardrail**: A strict budget of 3 attempts prevents infinite recursion and runaway token usage.
- **State Rollback**: Any incomplete or failed run automatically restores original byte contents.

---

## 📖 Key Takeaways

1. **Keep Tools Simple & Predictable**: LLMs perform significantly better with focused tools that return plain text and line numbers than complex abstract AST tools.
2. **Deterministic Indentation**: Preserving original indentation prevents syntactical or stylistic regressions in target files.
3. **Execution as Ground Truth**: Compiling and running code provides a reliable oracle that removes model hallucinations from the evaluation loop.
