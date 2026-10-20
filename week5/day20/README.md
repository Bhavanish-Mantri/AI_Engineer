# Day 20 - AI Agent Evaluation with an LLM Judge

This project demonstrates how to evaluate AI agent behavior using an LLM-as-a-judge approach combined with rule-based validation.

The project uses LLM to evaluate the semantic correctness of an agent's final response. Python checks the agent's tool sequence, arguments, policy consistency, and business-rule compliance.

This project was built as a learning exercise to understand the fundamentals of AI agent evaluation.

## Features

- **LLM-as-a-Judge**: Uses a LLM to evaluate whether an agent's response matches the expected outcome.
- **Trajectory Evaluation**: Checks whether tool calls occur in the expected sequence.
- **Argument Validation**: Compares actual tool arguments with expected arguments.
- **Policy Validation**: Checks whether the actual policy state matches the expected policy state.
- **Business-Rule Validation**: Detects violations such as refunding nonexistent orders, refunding an already-refunded order, or submitting a refund before required approval.
- **Golden Dataset**: Uses predefined JSON test cases to evaluate different agent behaviors.
- **Evaluation Report**: Displays individual check results, explanations, scores, and an overall pass rate.

## How It Works

The project evaluates simulated customer-support agent behavior for refund-related scenarios.

1. **Load test cases**: `main.py` reads the expected and actual results from `test_cases.json`.
2. **Evaluate the trajectory**: Python compares the expected tool sequence with the actual sequence.
3. **Validate arguments**: Python checks whether the actual tool arguments match the expected values.
4. **Check policy state**: Python compares the expected policy state with the actual policy state.
5. **Validate business rules**: Python checks for explicitly defined refund-policy violations.
6. **Judge the outcome**: The Groq LLM evaluates the semantic correctness of the agent's response using the scenario and validation context.
7. **Generate a report**: The application displays the results of each check and calculates the overall pass rate.

## Evaluation Checks

Each test case is evaluated using five checks:

| Check | Purpose |
|---|---|
| **Trajectory** | Verifies the expected order of tool calls |
| **Arguments** | Compares expected and actual tool arguments |
| **Policy Match** | Compares expected and actual policy states |
| **Business Rules** | Detects explicitly defined refund-policy violations |
| **Outcome** | Uses an LLM to assess the correctness of the final response |

A test case passes only when all five checks pass.

## Golden Dataset

The current dataset contains six simulated test cases:

| Test Case | Purpose |
|---|---|
| **Successful Refund** | Tests a correctly handled refund request |
| **Incorrect Refund Process** | Tests an incorrect tool sequence and failed outcome |
| **Incorrect Order ID** | Tests mismatched order arguments and a nonexistent order |
| **Invalid Order** | Tests how the agent handles an order that cannot be found |
| **Already Refunded Order** | Tests prevention of duplicate refunds |
| **Refund Requires Approval** | Tests a scenario where approval is required before submitting a refund |

These test cases are stored in `test_cases.json`. The expected and actual behaviors are predefined to make evaluation repeatable.

## Evaluation Results

In one local run, the project produced the following results:

| Metric | Result |
|---|---|
| Test cases | 6 |
| Individual checks | 30 |
| Passed checks | 24 |
| Overall check pass rate | 80.0% |
| Fully passed test cases | 4/6 |

These values describe one execution of the current simulated dataset. They are not a benchmark of general LLM accuracy, and the LLM's judgments may vary.

## Key Learnings

Through this project, I explored:
- Why evaluating AI agents requires more than checking their final responses.
- How an LLM can act as a judge for semantic correctness.
- How tool trajectories and arguments can be evaluated deterministically.
- How golden datasets support repeatable testing.
- How business rules can expose failures that a plausible final response might hide.
- How to generate evaluation reports that make failures easier to understand.

## Limitations

- **Simulated behavior**: The agent's actual outputs, tool calls, and policy states are predefined in JSON. This project does not run a live customer-support agent.
- **No real refund processing**: The application does not connect to an order database or execute refund transactions.
- **Policy-state trust**: Policy matching and business-rule checks use the policy values supplied in the test data. They do not independently verify real-world order or approval status.
- **LLM judgment**: The outcome evaluation may occasionally be inconsistent or incorrect.
- **Limited coverage**: Six test cases demonstrate the concepts but are not sufficient for production validation.
- **Pass rate interpretation**: The overall pass rate measures passed evaluation checks, not general AI accuracy.
