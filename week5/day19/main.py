import time
from multi_agent import run_multi_agent
from single_agent import run_single_agent
from tools import TokenTracker


def print_comparison_table(single_tracker: TokenTracker, multi_tracker: TokenTracker):
    print("\n" + "=" * 65)
    print("📊 TOKEN USAGE COMPARISON (Single Agent vs Multi-Agent)")
    print("=" * 65)
    print(f"{'Metric':<24} | {'Single Agent':<15} | {'Multi-Agent':<18}")
    print("-" * 65)
    print(f"{'Total LLM Calls':<24} | {single_tracker.calls:<15} | {multi_tracker.calls:<18}")
    print(f"{'Prompt Tokens':<24} | {single_tracker.prompt_tokens:<15} | {multi_tracker.prompt_tokens:<18}")
    print(f"{'Completion Tokens':<24} | {single_tracker.completion_tokens:<15} | {multi_tracker.completion_tokens:<18}")
    print(f"{'Total Tokens':<24} | {single_tracker.total_tokens:<15} | {multi_tracker.total_tokens:<18}")
    print("-" * 65)

    diff = multi_tracker.total_tokens - single_tracker.total_tokens
    if single_tracker.total_tokens > 0:
        pct = (abs(diff) / single_tracker.total_tokens) * 100
    else:
        pct = 0.0

    if diff > 0:
        print(f"💡 Multi-Agent used {diff:,} MORE tokens (+{pct:.1f}%) than Single Agent.")
    elif diff < 0:
        print(f"💡 Single Agent used {abs(diff):,} MORE tokens (+{pct:.1f}%) than Multi-Agent.")
    else:
        print("💡 Both systems consumed the exact same number of tokens.")
    print("=" * 65)


def main():
    complex_query = (
        "Find the current market cap or valuation of Apple (AAPL) and Microsoft (MSFT) in billions of USD, "
        "calculate their combined total valuation, calculate the percentage difference between the two "
        "(how much higher the larger company is compared to the smaller one), and calculate "
        "what 15% of their combined valuation would be."
    )

    print("=" * 70)
    print("TEST COMPLEX QUERY:")
    print(complex_query)
    print("=" * 70)

    # 1. Run Single Agent System
    t0 = time.time()
    single_res = run_single_agent(complex_query)
    single_duration = time.time() - t0

    # 2. Run Multi-Agent System
    t1 = time.time()
    multi_res = run_multi_agent(complex_query, notes_file="manager_notes.txt")
    multi_duration = time.time() - t1

    # Print summary answers
    print("\n" + "=" * 70)
    print(f"✅ SINGLE AGENT ANSWER (Execution time: {single_duration:.2f}s):")
    print("=" * 70)
    print(single_res["answer"])

    print("\n" + "=" * 70)
    print(f"✅ MULTI-AGENT ANSWER (Execution time: {multi_duration:.2f}s):")
    print("=" * 70)
    print(multi_res["answer"])

    # Token comparison
    print_comparison_table(single_res["tracker"], multi_res["tracker"])


if __name__ == "__main__":
    main()
