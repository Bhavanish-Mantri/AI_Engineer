import ast
import json
import operator as op
import os

from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient


# ============================================================
# 1. SETUP
# ============================================================

load_dotenv()

groq = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

tavily = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)

MODEL = "openai/gpt-oss-120b"
MAX_ITERATIONS = 5


# ============================================================
# 2. TOOL 1 — WEB SEARCH
# ============================================================

def web_search(query: str) -> str:
    """
    Search the web for current or changing information.
    """

    try:
        response = tavily.search(
            query=query,
            max_results=3,
            search_depth="basic"
        )

        results = response.get("results", [])

        if not results:
            return "No search results found."

        formatted_results = []

        for result in results:

            title = result.get("title", "N/A")
            url = result.get("url", "N/A")
            content = result.get("content", "N/A")

            formatted_results.append(
                f"Title: {title}\n"
                f"URL: {url}\n"
                f"Content: {content}"
            )

        return "\n\n".join(formatted_results)

    except Exception as e:
        return f"Web search failed: {e}"


# ============================================================
# 3. TOOL 2 — SAFE CALCULATOR
# ============================================================

# Only these mathematical operations are allowed.
ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
    ast.FloorDiv: op.floordiv,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}


def evaluate_node(node):
    """
    Recursively evaluate an AST node.

    Only numbers and explicitly allowed
    mathematical operators are supported.
    """

    # Numbers
    if isinstance(node, ast.Constant):

        if isinstance(node.value, (int, float)):
            return node.value

        raise ValueError(
            "Only numbers are allowed."
        )

    # Binary operations
    # Example: 10 + 5
    if isinstance(node, ast.BinOp):

        operator_type = type(node.op)

        if operator_type not in ALLOWED_OPERATORS:
            raise ValueError(
                "Operator is not allowed."
            )

        left = evaluate_node(node.left)
        right = evaluate_node(node.right)

        return ALLOWED_OPERATORS[operator_type](
            left,
            right
        )

    # Unary operations
    # Example: -5
    if isinstance(node, ast.UnaryOp):

        operator_type = type(node.op)

        if operator_type not in ALLOWED_OPERATORS:
            raise ValueError(
                "Operator is not allowed."
            )

        operand = evaluate_node(node.operand)

        return ALLOWED_OPERATORS[operator_type](
            operand
        )

    raise ValueError(
        "Unsupported mathematical expression."
    )


def calculate(expression: str) -> str:
    """
    Safely evaluate a mathematical expression.
    """

    try:

        tree = ast.parse(
            expression,
            mode="eval"
        )

        result = evaluate_node(tree.body)

        return str(result)

    except Exception as e:

        return f"Calculation failed: {e}"


# ============================================================
# 4. TOOL REGISTRY
# ============================================================

AVAILABLE_TOOLS = {
    "web_search": web_search,
    "calculate": calculate,
}


# ============================================================
# 5. TOOL DEFINITIONS FOR THE LLM
# ============================================================

tools = [

    {
        "type": "function",

        "function": {

            "name": "web_search",

            "description": (
                "Search the web for current or changing "
                "information such as news, recent events, "
                "prices, statistics, or up-to-date facts."
            ),

            "parameters": {

                "type": "object",

                "properties": {

                    "query": {

                        "type": "string",

                        "description": (
                            "A specific and concise "
                            "web search query."
                        )
                    }
                },

                "required": ["query"]
            }
        }
    },

    {
        "type": "function",

        "function": {

            "name": "calculate",

            "description": (
                "Perform mathematical calculations such as "
                "addition, subtraction, multiplication, "
                "division, percentages, powers, and modulo."
            ),

            "parameters": {

                "type": "object",

                "properties": {

                    "expression": {

                        "type": "string",

                        "description": (
                            "A mathematical expression such as "
                            "'2500 * 0.15' or '(100 + 50) / 2'."
                        )
                    }
                },

                "required": ["expression"]
            }
        }
    }
]


# ============================================================
# 6. SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are an AI research assistant with access to tools.

Rules:

1. Use web_search when the user asks for current,
   recent, changing, or real-world information.

2. Use calculate whenever mathematical computation
   is required.

3. Do not perform complicated arithmetic mentally
   when the calculator tool can do it.

4. You may use tools multiple times.

5. You can use different tools in the same task.

6. After receiving tool results, decide whether
   another tool is required.

7. When you have enough information, provide
   a clear final answer.

8. When web_search is used, include useful source
   URLs from the search results when appropriate.

9. Do not claim that you searched the web unless
   you actually used the web_search tool.

10. Always answer in plain text.

11. Do NOT use LaTeX formatting.

12. Do NOT use:
    \\( \\)
    \\[ \\]
    \\times
    \\div
    superscripts
    subscripts
    or other LaTeX commands.

13. For mathematical answers, use normal characters.

    Good:
    789 * 987 = 778743

    Bad:
    \\(789 \\times 987 = 778{,}743\\)

14. Keep terminal answers simple and readable.
"""


# ============================================================
# 7. CLEAN FINAL OUTPUT
# ============================================================

def clean_output(text: str) -> str:
    """
    Remove common LaTeX formatting so the final
    answer looks clean in the terminal.
    """

    if not text:
        return ""

    replacements = {

        r"\(": "",
        r"\)": "",

        r"\[": "",
        r"\]": "",

        r"\times": "*",
        r"\cdot": "*",

        r"\div": "/",

        r"\pm": "+/-",

        r"\leq": "<=",
        r"\geq": ">=",

        r"\neq": "!=",

        r"\approx": "~",

    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Remove LaTeX curly braces
    text = text.replace("{", "")
    text = text.replace("}", "")

    return text.strip()


# ============================================================
# 8. AGENT LOOP
# ============================================================

def run_agent(
    user_query: str,
    max_iterations: int = MAX_ITERATIONS
) -> str:

    # Conversation history
    messages = [

        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },

        {
            "role": "user",
            "content": user_query
        }
    ]


    # --------------------------------------------------------
    # Iterative Agent Loop
    # --------------------------------------------------------

    for iteration in range(
        1,
        max_iterations + 1
    ):

        print(
            f"\n========== ITERATION {iteration} =========="
        )


        # ----------------------------------------------------
        # Ask LLM what to do
        # ----------------------------------------------------

        try:

            response = groq.chat.completions.create(

                model=MODEL,

                messages=messages,

                tools=tools,

                tool_choice="auto"
            )

        except Exception as e:

            return f"LLM request failed: {e}"


        message = response.choices[0].message


        # ----------------------------------------------------
        # Save assistant message
        # ----------------------------------------------------

        messages.append(message)


        # ----------------------------------------------------
        # No tool call = final answer
        # ----------------------------------------------------

        if not message.tool_calls:

            final_answer = clean_output(
                message.content
            )

            print("\nFINAL ANSWER:\n")
            print(final_answer)

            return final_answer


        # ----------------------------------------------------
        # Tool calls requested
        # ----------------------------------------------------

        print(
            f"LLM requested "
            f"{len(message.tool_calls)} tool(s)"
        )


        # ----------------------------------------------------
        # Execute each tool
        # ----------------------------------------------------

        for tool_call in message.tool_calls:

            tool_name = tool_call.function.name

            print(
                f"\nTool requested: {tool_name}"
            )


            # ------------------------------------------------
            # Check whether tool exists
            # ------------------------------------------------

            if tool_name not in AVAILABLE_TOOLS:

                tool_result = (
                    f"Unknown tool: {tool_name}"
                )

            else:

                # --------------------------------------------
                # Parse tool arguments
                # --------------------------------------------

                try:

                    arguments = json.loads(
                        tool_call.function.arguments
                    )

                except json.JSONDecodeError as e:

                    tool_result = (
                        f"Invalid tool arguments: {e}"
                    )

                else:

                    print(
                        f"Arguments: {arguments}"
                    )


                    # ----------------------------------------
                    # Execute tool
                    # ----------------------------------------

                    try:

                        function = AVAILABLE_TOOLS[
                            tool_name
                        ]

                        tool_result = function(
                            **arguments
                        )

                    except Exception as e:

                        tool_result = (
                            f"Tool execution failed: {e}"
                        )


            print("Tool result received.")


            # ------------------------------------------------
            # Send tool result back to LLM
            # ------------------------------------------------

            messages.append({

                "role": "tool",

                "tool_call_id": tool_call.id,

                "content": tool_result
            })


    # ========================================================
    # Maximum iterations reached
    # ========================================================

    return (
        "I couldn't complete the task within "
        f"the maximum limit of {max_iterations} iterations."
    )


# ============================================================
# 9. MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("AI RESEARCH AGENT")
    print("=" * 60)

    question = input(
        "\nAsk me anything: "
    )

    run_agent(question)