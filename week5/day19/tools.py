import math
import os
from typing import Any, Dict
from dotenv import find_dotenv, load_dotenv
from groq import Groq
from tavily import TavilyClient

# Load environment keys
load_dotenv(find_dotenv())

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set in environment or .env file.")
if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY is not set in environment or .env file.")

groq_client = Groq(api_key=GROQ_API_KEY)
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

MODEL_NAME = "qwen/qwen3.8-27b"


class TokenTracker:
    def __init__(self):
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0
        self.calls = 0

    def add(self, usage: Any) -> None:
        if usage:
            p = getattr(usage, "prompt_tokens", 0) or 0
            c = getattr(usage, "completion_tokens", 0) or 0
            t = getattr(usage, "total_tokens", p + c) or (p + c)
            self.prompt_tokens += p
            self.completion_tokens += c
            self.total_tokens += t
            self.calls += 1

    def summary(self) -> Dict[str, int]:
        return {
            "calls": self.calls,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
        }


def web_search(query: str) -> str:
    """Search the web using Tavily."""
    try:
        response = tavily_client.search(query=query, max_results=3)
        results = response.get("results", [])
        if not results:
            return "No search results found."
        formatted = []
        for i, item in enumerate(results, 1):
            title = item.get("title", "No Title")
            content = item.get("content", "")
            formatted.append(f"[{i}] {title}: {content}")
        return "\n\n".join(formatted)
    except Exception as e:
        return f"Error executing web search: {str(e)}"


SAFE_MATH_GLOBALS = {
    "__builtins__": {},
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "sum": sum,
    "pow": pow,
    "math": math,
}


def python_calculator(expression: str) -> str:
    """Safely evaluate arithmetic and math expressions or short multi-line math scripts."""
    cleaned = expression.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    if cleaned.startswith("`") and cleaned.endswith("`"):
        cleaned = cleaned.strip("`")
    if cleaned.startswith("="):
        cleaned = cleaned[1:].strip()

    if any(k in cleaned for k in ["import", "open", "os", "sys", "exec", "eval", "__", ";"]):
        return "Error: Unsupported or unsafe expression."

    try:
        # First attempt: single expression
        result = eval(cleaned, SAFE_MATH_GLOBALS, {})
        return str(result)
    except Exception:
        # Second attempt: multi-line assignments with exec
        try:
            local_vars: Dict[str, Any] = {}
            exec(cleaned, SAFE_MATH_GLOBALS, local_vars)
            if local_vars:
                # Return the last assigned variable or formatted dict
                last_val = list(local_vars.values())[-1]
                return f"{last_val} (Variables: {local_vars})"
            return "Execution completed successfully."
        except Exception as e:
            return f"Error evaluating expression '{expression}': {str(e)}"



# Groq tool schema definitions
TOOL_SEARCH_DEF = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Searches the web for facts, numbers, current dates, and live statistics.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query."}
            },
            "required": ["query"],
        },
    },
}

TOOL_CALCULATOR_DEF = {
    "type": "function",
    "function": {
        "name": "python_calculator",
        "description": "Calculates the exact result of mathematical expressions or code statements (e.g. '1200 * 1.15', 'pct=(4950-4010)/4010*100').",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression or code to evaluate.",
                },
                "code": {
                    "type": "string",
                    "description": "The python code snippet to calculate the result.",
                },
            },
        },
    },
}

TOOL_PYTHON_DEF = {
    "type": "function",
    "function": {
        "name": "python",
        "description": "Executes python code or arithmetic expression to perform calculations.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate.",
                },
                "code": {
                    "type": "string",
                    "description": "The python code to execute.",
                },
            },
        },
    },
}
