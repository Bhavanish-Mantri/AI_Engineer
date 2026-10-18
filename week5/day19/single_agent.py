import json
from typing import Any, Dict, List, Optional
from tools import (
    MODEL_NAME,
    TOOL_CALCULATOR_DEF,
    TOOL_PYTHON_DEF,
    TOOL_SEARCH_DEF,
    TokenTracker,
    groq_client,
    python_calculator,
    web_search,
)


def ask_llm(
    messages: List[Dict[str, Any]],
    tools: Optional[List[Dict[str, Any]]] = None,
    tracker: Optional[TokenTracker] = None,
) -> Any:
    """Single ask_llm function that queries Groq with available tools."""
    kwargs: Dict[str, Any] = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.1,
    }
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"

    response = groq_client.chat.completions.create(**kwargs)
    if tracker and response.usage:
        tracker.add(response.usage)
    return response.choices[0].message


def run_single_agent(user_query: str) -> Dict[str, Any]:
    print("\n" + "=" * 60)
    print("▶ RUNNING SINGLE AGENT SYSTEM")
    print("=" * 60)

    tracker = TokenTracker()
    max_attempts = 5
    tools = [TOOL_SEARCH_DEF, TOOL_CALCULATOR_DEF, TOOL_PYTHON_DEF]

    messages: List[Dict[str, Any]] = [
        {
            "role": "system",
            "content": (
                "You are an AI assistant with access to tools: 'web_search' and 'python_calculator'. "
                "Always format your tool call arguments strictly as valid JSON. "
                "Once all research and calculations are completed, present your final response directly as "
                "clear, natural, well-formatted English text (do not output JSON or raw code for your final response)."
            ),
        },
        {"role": "user", "content": user_query},
    ]

    final_answer = ""
    for attempt in range(1, max_attempts + 1):
        print(f"\n[Single Agent] Iteration {attempt}/{max_attempts}")
        assistant_msg = ask_llm(messages, tools=tools, tracker=tracker)

        # Convert to dictionary for conversation history
        msg_dict: Dict[str, Any] = {"role": "assistant"}
        if assistant_msg.content:
            msg_dict["content"] = assistant_msg.content
        if assistant_msg.tool_calls:
            msg_dict["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in assistant_msg.tool_calls
            ]
        messages.append(msg_dict)

        # If LLM didn't call any tools, it has reached its final answer
        if not assistant_msg.tool_calls:
            print("[Single Agent] Finished without further tool calls.")
            final_answer = assistant_msg.content or ""
            break

        # Process tool calls
        for tool_call in assistant_msg.tool_calls:
            fn_name = tool_call.function.name
            args_str = tool_call.function.arguments
            try:
                fn_args = json.loads(args_str)
            except Exception:
                fn_args = {}

            print(f"  [Tool Call]: {fn_name}({fn_args})")
            if fn_name == "web_search":
                result = web_search(fn_args.get("query", ""))
            elif fn_name in ["python_calculator", "python"]:
                # Support both expression and code arguments from gpt-oss models
                expr = fn_args.get("expression") or fn_args.get("code") or ""
                result = python_calculator(expr)
            else:
                result = f"Error: Tool {fn_name} not found"

            preview = (result[:100] + "...") if len(result) > 100 else result
            print(f"  [Tool Output]: {preview}")

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": fn_name,
                    "content": result,
                }
            )
    else:
        print("[Single Agent] Max attempts reached, synthesizing final answer...")
        # Collect all previous tool outputs for clean synthesis
        collected_context = []
        for m in messages:
            if m.get("role") == "tool":
                collected_context.append(f"Tool Output ({m.get('name')}):\n{m.get('content')}")

        synth_messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant. Synthesize a complete final answer based on the facts collected.",
            },
            {
                "role": "user",
                "content": (
                    f"Original Question:\n{user_query}\n\n"
                    f"Research & Data gathered:\n" + "\n\n".join(collected_context) + "\n\n"
                    "Provide your complete, final calculated answer now."
                ),
            },
        ]
        closing_res = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=synth_messages,
            temperature=0.1,
        )
        if tracker and closing_res.usage:
            tracker.add(closing_res.usage)
        final_answer = closing_res.choices[0].message.content or ""

    return {"answer": final_answer, "tracker": tracker}


if __name__ == "__main__":
    test_query = (
        "Find the current market cap or valuation of Apple (AAPL) and Microsoft (MSFT) in billions of USD, "
        "calculate their combined total valuation, calculate the percentage difference between the two "
        "(how much higher the larger company is compared to the smaller one), and calculate "
        "what 15% of their combined valuation would be."
    )

    print("Query:", test_query)
    result = run_single_agent(test_query)
    print("\n--- FINAL ANSWER ---")
    print(result["answer"])
    print("\n--- TOKEN USAGE ---")
    print(result["tracker"].summary())
