
import os
import json
from groq import Groq
from dotenv import load_dotenv

# Load API key from D:\AI_Engineer\.env
env_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", ".env")
)
load_dotenv(env_path)

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError(f"GROQ_API_KEY not found. Check {env_path}")

client = Groq(api_key=api_key)


def evaluate_agent(expected, actual):
    expected_policy = expected["policy"]
    actual_policy = actual["policy"]
    tools = actual["tools"]

    # Check tool sequence and arguments
    checks = {
        "Trajectory": {
            "passed": expected["tools"] == tools,
            "reason": "Tool sequence matches expected behavior."
        },
        "Arguments": {
            "passed": expected["arguments"] == actual["arguments"],
            "reason": "Tool arguments match expected values."
        },
        "Policy Match": {
            "passed": expected_policy == actual_policy,
            "reason": "Actual policy state matches expected policy state."
        }
    }

    if not checks["Trajectory"]["passed"]:
        checks["Trajectory"]["reason"] = (
            f"Expected {expected['tools']}, but got {tools}."
        )

    if not checks["Arguments"]["passed"]:
        checks["Arguments"]["reason"] = (
            f"Expected {expected['arguments']}, "
            f"but got {actual['arguments']}."
        )

    if not checks["Policy Match"]["passed"]:
        checks["Policy Match"]["reason"] = (
            f"Expected policy {expected_policy}, "
            f"but got {actual_policy}."
        )

    # Enforce business rules independently
    violations = []

    if not actual_policy["order_exists"] and "request_refund" in tools:
        violations.append("Cannot refund an order that does not exist.")

    if actual_policy["already_refunded"] and "request_refund" in tools:
        violations.append("Cannot refund an already-refunded order.")

    if (
        actual_policy["approval_required"]
        and not actual_policy["approval_granted"]
        and "request_refund" in tools
    ):
        violations.append("Refund cannot be submitted before approval.")

    checks["Business Rules"] = {
        "passed": len(violations) == 0,
        "reason": (
            "; ".join(violations)
            if violations
            else "No business-rule violations detected."
        )
    }

    # Ask the LLM to judge semantic outcome correctness
    prompt = f"""
You are a strict evaluator for a refund-support AI agent.

Evaluate whether the actual outcome is correct for the scenario.
Consider the expected outcome, actual outcome, tool calls,
tool arguments, and business policy.

Expected:
{json.dumps(expected, indent=2)}

Actual:
{json.dumps(actual, indent=2)}

Deterministic checks:
{json.dumps({k: v["passed"] for k, v in checks.items()}, indent=2)}

Rules:
- Judge meaning, not exact wording.
- A nonexistent order cannot be refunded.
- An already-refunded order cannot be refunded again.
- A refund requiring approval cannot be submitted before approval.
- Do not treat an unsupported success claim as correct.
- Return only valid JSON with this structure:
{{"passed": true, "reason": "Brief explanation"}}
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            response_format={"type": "json_object"}
        )

        judgment = json.loads(
            response.choices[0].message.content
        )

        outcome_passed = (
            judgment.get("passed") is True
            and checks["Business Rules"]["passed"]
        )

        outcome_reason = judgment.get(
            "reason", "No explanation provided."
        )

        if not checks["Business Rules"]["passed"]:
            outcome_reason += " Business policy validation also failed."

    except Exception as error:
        # Fail safely if the LLM evaluation fails
        outcome_passed = False
        outcome_reason = f"LLM evaluation failed: {error}"

    checks["Outcome"] = {
        "passed": outcome_passed,
        "reason": outcome_reason
    }

    # Print the evaluation report
    passed_count = 0

    for name, result in checks.items():
        status = "PASS" if result["passed"] else "FAIL"
        print(f"\n{name}: {status}")
        print(f"Reason: {result['reason']}")

        if result["passed"]:
            passed_count += 1

    total = len(checks)
    score = passed_count / total * 100

    print(f"\nChecks Passed: {passed_count}/{total}")
    print(f"Pass Rate: {score:.1f}%")
    print(f"Final Status: {'PASS' if passed_count == total else 'FAIL'}")

    return checks
