# Day 19: Single-Agent vs Multi-Agent Systems (Without LangGraph)

This project demonstrates and benchmarks two agentic architectures using **Groq LLM** (`qwen/qwen3.8-27b`), **Tavily Web Search**, and a sandboxed **Python Calculator**:

1. **Single-Agent System**:
   - 1 LLM with access to both Web Search and Calculator tools.
   - Autonomously determines tool usage and iteration cycles (constrained to a max of 5 attempts).
   - Direct conversational history accumulation.

2. **Multi-Agent System (No LangGraph)**:
   - **Manager Agent**: Coordinates the workflow, inspects helper notes, and delegates tasks via JSON decisions (`CALL_SEARCH`, `CALL_MATHS`, `FINISH`).
   - **Search Agent**: Specialized LLM equipped solely with `web_search`.
   - **Maths Agent**: Specialized LLM equipped solely with `python_calculator`.
   - **Manager Notes File (`manager_notes.txt`)**: External memory tracking helper outputs across iterations.

3. **Benchmarking & Token Usage Comparison**:
   - Tracks prompt tokens, completion tokens, and total API calls for both architectures on complex multi-step queries.

## Project Structure

```
week5/day19/
├── tools.py            # Shared tools (Tavily search, Python calculator) & TokenTracker
├── single_agent.py     # Single-agent implementation (1 LLM + 2 tools, max 5 attempts)
├── multi_agent.py      # Multi-agent system (Manager, Search LLM, Maths LLM, notes)
├── main.py             # Side-by-side benchmark & token usage comparison runner
├── prompt.md           # Project requirements & specifications
├── pyproject.toml      # Project configuration
├── .gitignore          # Git ignore file for Python & virtual environments
└── README.md           # Documentation
```

## Setup & Installation

1. Create and activate a virtual environment:
   ```powershell
   uv venv
   .venv\Scripts\activate
   ```

2. Install dependencies:
   ```powershell
   uv pip install groq tavily-python python-dotenv
   ```

3. Ensure API keys are set in `.env`:
   ```env
   GROQ_API_KEY="your-groq-api-key"
   TAVILY_API_KEY="your-tavily-api-key"
   ```

## Running the Systems

- **Run Single Agent**:
  ```powershell
  python single_agent.py
  ```

- **Run Multi-Agent System**:
  ```powershell
  python multi_agent.py
  ```

- **Run Side-by-Side Benchmark & Token Comparison**:
  ```powershell
  python main.py
  ```
