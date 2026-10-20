
import json
from evaluator import evaluate_agent


def main():
    with open("test_cases.json", "r", encoding="utf-8") as file:
        test_cases = json.load(file)

    summary = []

    for test in test_cases:
        print("\n" + "=" * 50)
        print(f"TEST CASE: {test['name']}")
        print("=" * 50)

        results = evaluate_agent(test["expected"], test["actual"])
        passed = sum(item["passed"] for item in results.values())
        total = len(results)

        summary.append({
            "name": test["name"],
            "passed": passed,
            "total": total,
            "status": "PASS" if passed == total else "FAIL"
        })

    print("\n" + "=" * 50)
    print("FINAL EVALUATION REPORT")
    print("=" * 50)

    for item in summary:
        print(
            f"{item['name']}: {item['passed']}/{item['total']} "
            f"| {item['status']}"
        )

    total_passed = sum(item["passed"] for item in summary)
    total_checks = sum(item["total"] for item in summary)
    passed_cases = sum(item["status"] == "PASS" for item in summary)

    print("-" * 50)
    print(f"Passed Checks: {total_passed}/{total_checks}")

    if total_checks:
        print(
            f"Overall Pass Rate: "
            f"{total_passed / total_checks * 100:.1f}%"
        )

    print(f"Fully Passed Cases: {passed_cases}/{len(summary)}")


if __name__ == "__main__":
    main()
