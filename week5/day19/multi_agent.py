import json
import re
from typing import Any, Dict, List
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

# =========================================================================
# Custom Multi-Agent System (Without LangGraph)
# 3 Ask LLM functions:
# 1. ask_manager_llm: Decides which helper LLM to use and reviews notes.
# 2. ask_search_llm: Has access ONLY to web_search.
# 3. ask_maths_llm: Has access ONLY to python_calculator.
# =========================================================================


def ask_manager_llm(
    original_query: str,
    notes_content: str,
    iteration: int,
    tracker: TokenTracker,
) -> Dict[str, Any]:
    """Manager LLM function: decides helper to use or concludes answer."""
    system_prompt = (
        "You are the Manager Agent orchestrating two specialized helper agents:\n"
        "1. Search Agent: has access ONLY to web_search for factual data.\n"
        "2. Maths Agent: has access ONLY to python_calculator for exact calculations.\n\n"
        "Review the original query and the helper notes accumulated so far.\n"
        "Decide what to do next. You MUST respond ONLY in valid JSON matching this schema:\n"
        "{\n"
        '  "thought": "<your reasoning on what has been found and what is needed next>",\n'
        '  "action": "CALL_SEARCH" | "CALL_MATHS" | "FINISH",\n'
        '  "subtask": "<precise prompt or question for the helper agent, or empty if FINISH>",\n'
        '  "final_answer": "<comprehensive, natural English final answer if action is FINISH, otherwise empty>"\n'
        "}\n"
        "Do not include any other markdown outside the JSON. The final_answer itself should be clear, detailed English text."
    )

    user_content = (
        f"Original User Query:\n{original_query}\n\n"
        f"Manager Notes (Helper Responses History):\n"
        f"{notes_content if notes_content.strip() else '(No notes yet - initial step)'}\n\n"
        f"Current Attempt: {iteration}/5. Output your decision JSON."
    )

    response = groq_client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        temperature=0.1,
        response_format={"type": "json_object"},
    )
    if response.usage:
        tracker.add(response.usage)

    content = response.choices[0].message.content or "{}"
    try:
        return json.loads(content)
    except Exception:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return {"action": "FINISH", "final_answer": content, "thought": "Fallback parse"}


def ask_search_llm(
    subtask: str,
    tracker: TokenTracker,
    max_steps: int = 3,
) -> str:
    """Search LLM function: has access ONLY to the web search tool."""
    system_prompt = (
        "You are a specialized Search Agent. Your ONLY role is to search the web using 'web_search' "
        "to gather factual numbers, dates, or details requested in the subtask. "
        "Extract the precise values and summarize them clearly."
    )

    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": subtask},
    ]

    for _ in range(max_steps):
        response = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=[TOOL_SEARCH_DEF],
            tool_choice="auto",
            temperature=0.1,
        )
        if response.usage:
            tracker.add(response.usage)

        msg = response.choices[0].message
        msg_dict: Dict[str, Any] = {"role": "assistant"}
        if msg.content:
            msg_dict["content"] = msg.content
        if msg.tool_calls:
            msg_dict["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in msg.tool_calls
            ]
        messages.append(msg_dict)

        if not msg.tool_calls:
            return msg.content or "Search finished without text."

        for tc in msg.tool_calls:
            try:
                args = json.loads(tc.function.arguments)
            except Exception:
                args = {}
            query = args.get("query", subtask)
            print(f"    [Search Agent Tool Call]: web_search('{query}')")
            tool_output = web_search(query)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "name": "web_search",
                    "content": tool_output,
                }
            )

    return "Search agent reached maximum tool steps."


def ask_maths_llm(
    subtask: str,
    tracker: TokenTracker,
    max_steps: int = 3,
) -> str:
    """Maths LLM function: has access ONLY to the python calculator tool."""
    system_prompt = (
        "You are a specialized Maths Agent. Your ONLY role is to perform exact arithmetic and calculations "
        "using the 'python_calculator' tool. Always compute values using the tool rather than guessing. "
        "Explain the calculation and state the calculated result clearly."
    )

    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": subtask},
    ]

    for _ in range(max_steps):
        response = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=[TOOL_CALCULATOR_DEF, TOOL_PYTHON_DEF],
            tool_choice="auto",
            temperature=0.1,
        )
        if response.usage:
            tracker.add(response.usage)

        msg = response.choices[0].message
        msg_dict: Dict[str, Any] = {"role": "assistant"}
        if msg.content:
            msg_dict["content"] = msg.content
        if msg.tool_calls:
            msg_dict["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in msg.tool_calls
            ]
        messages.append(msg_dict)

        if not msg.tool_calls:
            return msg.content or "Maths finished without text."

        for tc in msg.tool_calls:
            try:
                args = json.loads(tc.function.arguments)
            except Exception:
                args = {}
            expr = args.get("expression") or args.get("code") or ""
            fn_name = tc.function.name
            print(f"    [Maths Agent Tool Call]: {fn_name}('{expr}')")
            tool_output = python_calculator(expr)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "name": fn_name,
                    "content": tool_output,
                }
            )

    return "Maths agent reached maximum tool steps."


def run_multi_agent(user_query: str, notes_file: str = "manager_notes.txt") -> Dict[str, Any]:
    print("\n" + "=" * 60)
    print("▶ RUNNING MULTI-AGENT SYSTEM (Manager + Search LLM + Maths LLM)")
    print("=" * 60)

    tracker = TokenTracker()
    max_manager_attempts = 5

    # Initialize notes file for tracking helper responses
    with open(notes_file, "w", encoding="utf-8") as f:
        f.write(f"# Manager Agent Notes\nQuery: {user_query}\n\n## Helper Execution Log\n")

    final_answer = ""
    for attempt in range(1, max_manager_attempts + 1):
        with open(notes_file, "r", encoding="utf-8") as f:
            notes_content = f.read()

        print(f"\n[Manager LLM] Iteration {attempt}/{max_manager_attempts}")
        decision = ask_manager_llm(
            original_query=user_query,
            notes_content=notes_content,
            iteration=attempt,
            tracker=tracker,
        )

        thought = decision.get("thought", "")
        action = decision.get("action", "FINISH")
        subtask = decision.get("subtask", "")

        print(f"  Thought: {thought}")
        print(f"  Action : {action}")

        if action == "CALL_SEARCH":
            print(f"  -> Dispatching to Search LLM: {subtask}")
            search_res = ask_search_llm(subtask, tracker=tracker)
            print(f"  <- Search LLM Response: {search_res[:120]}...")

            with open(notes_file, "a", encoding="utf-8") as f:
                f.write(f"\n### Attempt {attempt} - Search LLM\n")
                f.write(f"Subtask: {subtask}\n")
                f.write(f"Response:\n{search_res}\n")

        elif action == "CALL_MATHS":
            print(f"  -> Dispatching to Maths LLM: {subtask}")
            maths_res = ask_maths_llm(subtask, tracker=tracker)
            print(f"  <- Maths LLM Response: {maths_res[:120]}...")

            with open(notes_file, "a", encoding="utf-8") as f:
                f.write(f"\n### Attempt {attempt} - Maths LLM\n")
                f.write(f"Subtask: {subtask}\n")
                f.write(f"Response:\n{maths_res}\n")

        elif action == "FINISH":
            print("  -> Task Completed by Manager.")
            final_answer = decision.get("final_answer", "")
            break
        else:
            final_answer = decision.get("final_answer", "")
            break
    else:
        print("[Manager LLM] Max attempts reached, synthesizing final answer from notes...")
        with open(notes_file, "r", encoding="utf-8") as f:
            notes_content = f.read()
        synth = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": f"Query: {user_query}\n\nNotes:\n{notes_content}\n\nProvide the final answer.",
                }
            ],
            temperature=0.1,
        )
        if synth.usage:
            tracker.add(synth.usage)
        final_answer = synth.choices[0].message.content or ""

    return {"answer": final_answer, "tracker": tracker, "notes_file": notes_file}


if __name__ == "__main__":
    test_query = (
        "Find the current market cap or valuation of Apple (AAPL) and Microsoft (MSFT) in billions of USD, "
        "calculate their combined total valuation, calculate the percentage difference between the two "
        "(how much higher the larger company is compared to the smaller one), and calculate "
        "what 15% of their combined valuation would be."
    )

    print("Query:", test_query)
    result = run_multi_agent(test_query)
    print("\n--- FINAL ANSWER ---")
    print(result["answer"])
    print("\n--- TOKEN USAGE ---")
    print(result["tracker"].summary())
    print("\nManager notes saved to:", result["notes_file"])
