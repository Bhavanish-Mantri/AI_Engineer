"""
Mini Coding Agent for Java -- based on the reference repository architecture (No LangGraph).

Ek LLM (Groq: openai/gpt-oss-120b) + 3 tools:
    search_files    -> kaunsi files bug se related hain
    search_in_file  -> file mein kaunsi lines (line numbers ke saath)
    replace_line    -> ek line ko nayi line se badlo

Flow:
    1. Tum bug simple English mein batate ho
    2. LLM tools chala ke bug dhoondhta hai aur line badalta hai
    3. Agent code ko javac se compile + java se run karta hai, output dikhata hai
    4. Compile fail -> agla attempt. Compile pass -> output verify hota hai
    5. 3 attempts mein nahi hua -> "cannot solve" aur files wapas pehle jaisi (clean state)

Run:
    python main.py                 # java_project/ folder pe kaam karega
    python main.py some/other/dir  # kisi aur folder pe
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from dotenv import load_dotenv, find_dotenv
from groq import BadRequestError, Groq

from tools import TOOLS, code_files, make_tools


# ============================================================
# SETUP
# ============================================================

load_dotenv(find_dotenv())

# Windows terminal LLM ke unicode characters pe crash na kare
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

groq = Groq(api_key=os.getenv("GROQ_API_KEY"), max_retries=10)

MODEL = "openai/gpt-oss-120b"
ROOT = Path(__file__).parent

MAX_ATTEMPTS = 3  # itne attempts mein bug theek nahi hua to haar maan lo
MAX_STEPS = 10    # ek attempt ke andar LLM kitni baar tools chala sakta hai

TOKENS = {"calls": 0, "total": 0}

SYSTEM_PROMPT = """
You are a coding agent that fixes small bugs in a Java project.
You can only see and change the code through your tools:
- search_files(keyword): find which files are related to the bug.
- search_in_file(path, keyword): see matching lines with their line numbers.
  An empty keyword shows the whole file.
- replace_line(path, line_number, new_line): replace one whole line.

How to work:
1. Find the related file, then read the related code before changing anything.
2. Change as few lines as possible. Fix only the bug the user described.
3. Take line numbers from search_in_file. new_line must be one complete, compiling line of Java.
4. When you are done, reply WITHOUT a tool call: say which line you changed and why, in 1-3 sentences.
"""


# ============================================================
# PRINT HELPERS
# ============================================================


def header(title: str, char: str = "="):
    print("\n" + char * 60)
    print(title)
    print(char * 60)


def show(text: str, max_lines: int = 15):
    """Lambe tool results ko terminal pe chhota karke dikhao. LLM ko poora result jaata hai."""
    lines = text.splitlines() or [""]
    for line in lines[:max_lines]:
        print(f"           | {line}")
    if len(lines) > max_lines:
        print(f"           | ... ({len(lines) - max_lines} more lines sent to the LLM)")


def ask(question: str) -> str:
    try:
        return input(question).strip()
    except EOFError:
        return ""


# ============================================================
# ONE ATTEMPT (LLM + tools ka loop)
# ============================================================


def run_attempt(messages: list, functions: dict) -> str | None:
    """LLM ko tools chalane do jab tak wo khud na bole 'done'. Uski summary return karo."""

    for step in range(1, MAX_STEPS + 1):
        print(f"\n[step {step}] asking the LLM what to do next ...")

        try:
            response = groq.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS)
        except BadRequestError:
            print(f"[step {step}] Groq rejected a malformed tool call, asking again")
            continue

        TOKENS["calls"] += 1
        TOKENS["total"] += response.usage.total_tokens
        message = response.choices[0].message

        # koi tool call nahi -> LLM ke hisaab se kaam ho gaya
        if not message.tool_calls:
            messages.append({"role": "assistant", "content": message.content or ""})
            print(f"[step {step}] LLM finished (no tool call)")
            return message.content or "(no summary)"

        if message.content:
            print(f"[step {step}] LLM says: {message.content.strip()}")

        messages.append({
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": [tc.model_dump() for tc in message.tool_calls],
        })

        for tool_call in message.tool_calls:
            name = tool_call.function.name
            print(f"[step {step}] TOOL CALLED -> {name}")

            try:
                args = json.loads(tool_call.function.arguments or "{}")
                print(f"           args: {args}")
                if name not in functions:
                    result = f"Unknown tool '{name}'. Available tools: {', '.join(functions)}"
                else:
                    result = functions[name](**args)
            except Exception as e:
                result = f"Tool call failed: {e}"

            print("           result:")
            show(result)

            messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": result})

    return None


# ============================================================
# VERIFY (compile + run with javac & java)
# ============================================================


def compile_and_run(workspace: Path) -> tuple[bool, str]:
    """(compile hua?, compiler errors ya program ka output) return karta hai."""
    if shutil.which("javac") is None:
        return True, "(javac not found, skipped compiling. Check the code yourself.)"

    sources = [str(p) for p in workspace.rglob("*.java")]
    if not sources:
        return True, "(No .java files found to compile)"

    # Compile all java source files into workspace
    build = subprocess.run(["javac", "-d", str(workspace), *sources], capture_output=True, text=True)
    if build.returncode != 0:
        return False, build.stderr[:3000]

    # Find the main class (the class that contains main method)
    main_class = None
    for src in sources:
        with open(src, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            if "public static void main" in content:
                main_class = Path(src).stem
                break

    if not main_class:
        return True, "Compiled OK. (No main method found to run)"

    try:
        run = subprocess.run(
            ["java", "-cp", str(workspace), main_class],
            capture_output=True,
            text=True,
            timeout=10,
            stdin=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired:
        return True, "Program did not finish in 10 seconds (infinite loop?)"

    return True, (run.stdout + run.stderr)[:3000]


# ============================================================
# MAIN
# ============================================================


def main():
    workspace = (Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "java_project").resolve()
    files = code_files(workspace)

    header("MINI CODING AGENT (JAVA)")
    print(f"Workspace: {workspace}")
    print(f"Files    : {', '.join(f.name for f in files) or '(none)'}")
    if not files:
        return

    bug = ask("\nDescribe the bug in simple English: ")
    if not bug:
        print("No bug given. Bye!")
        return

    functions = make_tools(workspace)

    # Agent fail ho jaaye to files wapas pehle jaisi clean kar denge
    snapshot = {f: f.read_bytes() for f in files}

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Bug report:\n{bug}"},
    ]

    for attempt in range(1, MAX_ATTEMPTS + 1):
        header(f"ATTEMPT {attempt} of {MAX_ATTEMPTS}")

        summary = run_attempt(messages, functions)
        if summary is None:
            print(f"\nLLM used all {MAX_STEPS} steps without finishing.")
            messages.append({"role": "user", "content": (
                f"You used all {MAX_STEPS} steps without finishing. Be more direct: read the code, then fix it."
            )})
            continue

        print("\nLLM summary:")
        show(summary)

        header("VERIFY: compiling and running Java code with javac & java", "-")
        compiled, output = compile_and_run(workspace)

        if not compiled:
            print("Compile: FAILED")
            show(output, max_lines=20)
            messages.append({"role": "user", "content": (
                f"Your change does not compile in Java. Compiler errors:\n{output}\nFix the code."
            )})
            continue

        print("Compile: OK")
        print("Program output:")
        show(output, max_lines=30)

        # In non-interactive or testing setups, check whether output contains the expected total
        user_fixed = ask("\nIs the bug fixed? (y/n): ")
        if user_fixed.lower().startswith("y"):
            header(f"BUG FIXED in attempt {attempt}")
            break

        what = ask("What is still wrong? (Enter to skip): ")
        messages.append({"role": "user", "content": (
            "The bug is NOT fixed yet.\n"
            f"Program output now:\n{output}\n"
            f"User says: {what or '(no details)'}\n"
            "Look at the code again and fix it."
        )})

    else:
        # Loop finished without fix -> Clean up and restore original files
        header(f"Sorry, I could not solve this bug in {MAX_ATTEMPTS} attempts.")
        for f, original in snapshot.items():
            f.write_bytes(original)
        # Remove any compiled .class artifacts
        for c in workspace.glob("*.class"):
            try:
                c.unlink()
            except Exception:
                pass
        print("Your files are restored to how they were before the agent started.")

    # Cleanup .class files at the end of the session
    for c in workspace.glob("*.class"):
        try:
            c.unlink()
        except Exception:
            pass

    print(f"\nLLM calls: {TOKENS['calls']}   tokens used: {TOKENS['total']}")


if __name__ == "__main__":
    main()
