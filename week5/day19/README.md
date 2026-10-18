# Day 19 - Multi-Agent Systems: Implementation and Token Usage Comparison

A practical implementation of Single-Agent and Multi-Agent Systems using Python, Groq, Tavily web search, and a Python calculator. This project explores how a single LLM can handle multiple tools and how a manager can delegate tasks to specialized agents.

## Overview

A **Single-Agent System** uses one LLM to manage a task, select tools, and generate the final answer.

A **Multi-Agent System** divides responsibilities among multiple agents. A manager coordinates the workflow, while specialist agents perform specific tasks.

This project compares both approaches using a query that requires current web information and mathematical calculations.

## What Is a Single-Agent System?

A Single-Agent System uses one LLM to understand the user's query, decide which tools to call, process their results, and generate the final answer.

For example, a query asking for today's gold price and how much gold can be purchased with ₹1 crore requires both web search and calculation.

```text
User Query
    |
    v
Single LLM
    |
    +----> Web Search
    |
    +----> Calculator
    |
    v
Final Answer
```

### Responsibilities

- Understand the user query.
- Select the appropriate tool.
- Execute tool calls and interpret results.
- Decide whether additional tool calls are necessary.
- Generate the final answer.

### Advantages

- Simple architecture.
- Lower coordination overhead.
- Generally fewer LLM calls.
- Easier debugging and maintenance.

## What Is a Multi-Agent System?

A Multi-Agent System divides a task among agents with specialized responsibilities. A manager assigns tasks, receives results, and decides what should happen next.

An analogy is a YouTube production team: a teacher creates the content, an editor prepares the video, and an uploader publishes it. A manager coordinates the work rather than performing every task.

In this implementation, the system has three agent roles:

| Agent | Responsibility | Tool Access |
|---|---|---|
| Manager LLM | Delegate tasks and track results | No direct task-tool access intended |
| Search LLM | Retrieve information | Tavily web search |
| Maths LLM | Perform calculations | Python calculator |

The manager sends each specialist a focused task and combines their results into the final answer.

## Do Multiple Agents Need Different LLM Models?

No. Multiple agents can use the same LLM model and API client while having different system prompts and tool permissions.

```text
Manager LLM  ──┐
Search LLM   ──┼── Same Model / Client
Maths LLM    ──┘
```

Different models can be used when tasks require different capabilities, such as advanced reasoning for research and a smaller model for simple formatting.

The choice depends on performance, cost, latency, and the problem requirements.

## System Prompts and Tool Access

A system prompt defines an agent's role and expected behavior.

### Manager

- Understand the complete query.
- Select the Search or Maths Agent.
- Track returned results.
- Decide whether more work is required.
- Finish when the task is complete.

### Search Agent

- Use web search to retrieve requested information.
- Return relevant findings.
- Avoid performing calculations.

### Maths Agent

- Use the calculator for mathematical operations.
- Process the numerical values supplied by the manager.
- Return the calculated results.

Tool access should also be restricted in the application code. A system prompt alone does not guarantee that an LLM will follow every instruction.

## Why Use Multi-Agent Systems?

Specialized agents can be useful when a workflow contains distinct tasks requiring different tools, instructions, or models.

For example, the Search Agent can retrieve financial data while the Maths Agent calculates the combined valuation and percentage difference.

However, a Multi-Agent System introduces additional coordination, communication, and failure points.

**Practical rule:** Start with a Single-Agent System. Introduce multiple agents when evaluation shows that specialization provides a meaningful improvement.

## Single-Agent vs Multi-Agent

| Feature | Single-Agent | Multi-Agent |
|---|---|---|
| Agent functions | One main agent | Manager and specialist agents |
| Task handling | One agent manages the workflow | Work is delegated |
| Tool access | One agent may access multiple tools | Tools can be separated by role |
| Coordination | Relatively simple | Requires inter-agent communication |
| Complexity | Lower | Higher |
| Token usage | Often lower for suitable tasks | Can be higher |
| Debugging | Fewer components | More possible failure points |
| Best suited for | Straightforward workflows | Complex workflows with distinct responsibilities |

More agents do not automatically produce better answers. Their benefits must justify their additional cost and complexity.

## Understanding Token Usage

Tokens are units of text processed by an LLM.

- **Prompt tokens:** Input processed by the model, including instructions and conversation context.
- **Completion tokens:** Output generated by the model.
- **Total tokens:** Prompt tokens plus completion tokens.

Formula:

```text
Total Tokens = Prompt Tokens + Completion Tokens
```

Multi-Agent Systems can consume more tokens because each agent may require its own instructions, context, and response. The manager may also need to record and pass information between agents.

However, token usage depends on the actual implementation. It is not guaranteed that every Multi-Agent System will consume more tokens.

## Project Task: Apple and Microsoft Market Capitalization

The test query used in the project is:

> Find the current market capitalization of Apple (AAPL) and Microsoft (MSFT) in billions of USD. Calculate their combined valuation, the percentage by which the larger company exceeds the smaller one, and 15% of their combined valuation.

The task requires two types of operations:

1. Search the web for both companies' market capitalizations.
2. Calculate the combined valuation, percentage difference, and 15% value.

### Mathematical Formulas

Let:

- \(A\) = Apple's market capitalization in billions of USD.
- \(M\) = Microsoft's market capitalization in billions of USD.

**Combined valuation**

\[
\text{Combined Valuation}=A+M
\]

**Percentage difference relative to the smaller value**

\[
\text{Percentage Difference}
=\frac{|A-M|}{\min(A,M)}\times100
\]

**15% of the combined valuation**

\[
\text{15\% Value}=(A+M)\times0.15
\]

The values retrieved from the web should be passed to the calculator for these operations.

## Single-Agent Implementation

The Single-Agent System uses one main LLM function with two tools: web search and a calculator.

Its execution process is:

```text
Receive Query
     |
     v
LLM Selects Tool
     |
     v
Execute Tool
     |
     v
Return Tool Result
     |
     v
LLM Decides Next Step
     |
     v
Final Answer
```

The agent can repeat this process when more than one tool call is needed.

The demonstrated configuration uses a maximum of five iterations to prevent the agent from making tool calls indefinitely.

Conceptually:

```python
while attempts < max_attempts:
    response = ask_llm()

    if response requests a tool:
        execute_tool()
        append_tool_result()
    else:
        return final_answer
```

This is a simplified illustration of the agent loop, not the complete project implementation.

## Multi-Agent Implementation

The Multi-Agent System divides the same task among the manager and specialist agents.

```text
User Query
    |
    v
Manager LLM
    |
    +----> Search Agent: Apple market cap
    |
    +----> Search Agent: Microsoft market cap
    |
    +----> Maths Agent: Perform calculations
    |
    v
Manager Combines Results
    |
    v
Final Answer
```

The manager may need multiple iterations to collect the required information and complete the task.

### Manager Notes

The manager maintains a record of the results returned by helper agents. For example:

```text
Apple market cap: Retrieved
Microsoft market cap: Retrieved
Combined valuation: Pending
Percentage difference: Pending
15% calculation: Pending
```

The supplied execution log shows that the manager saved its notes to `manager_notes.txt`.

Tracking results helps the manager avoid losing information between steps, although maintaining and passing this context can add token overhead.

## Example Token Usage Results

The supplied execution log records the following results:

| Metric | Single-Agent | Multi-Agent |
|---|---:|---:|
| LLM calls | 5 | 13 |
| Prompt tokens | 16,008 | 15,826 |
| Completion tokens | 559 | 1,620 |
| Total tokens | 16,567 | 17,446 |

These figures belong to the specific successful runs provided with the project.

### Token Difference

The Multi-Agent System used:

\[
17,446-16,567=879
\]

additional tokens.

Percentage increase relative to the Single-Agent System:

\[
\frac{879}{16,567}\times100\approx5.30\%
\]

Therefore, the Multi-Agent System used approximately **5.3% more total tokens** in this run.

### Interpreting the Results

The Multi-Agent System made more LLM calls because the manager and specialist agents performed separate steps. Its completion-token count was also higher.

This does not establish a universal token increase for all Multi-Agent Systems. The result depends on prompt length, model behavior, number of calls, and context management.

The market-cap estimates also differed between the two runs. Since market data changes and search results can vary, these logs should be treated as an execution comparison rather than a controlled benchmark of answer accuracy.

A fair comparison should use consistent input data and evaluate answer quality alongside token consumption.

## Evaluation Before Choosing an Architecture

Architecture decisions should be based on measured performance rather than the assumption that multiple agents are always better.

```text
Start with Single-Agent
          |
          v
     Evaluate Results
          |
          v
  Does it meet requirements?
       /           \
     Yes            No
      |              |
      v              v
  Keep it       Identify failures
                     |
                     v
            Consider specialization
                     |
                     v
             Evaluate Multi-Agent
                     |
                     v
           Compare quality, cost,
             latency, reliability
```

The lecture mentions approximately 85% accuracy as an illustrative benchmark. It is not a universal threshold; acceptable performance depends on the application's requirements and risk.

Useful evaluation metrics include:

- Answer correctness.
- Tool selection accuracy.
- Task completion rate.
- Token usage and API cost.
- Response latency.
- Reliability and ease of debugging.

## Common Implementation Challenges

### 1. Invalid Tool-Call Arguments

The execution logs show a Groq API error because generated Python statements were supplied where valid JSON tool arguments were expected.

**Lesson:** Define clear tool schemas and validate arguments before executing tools.

### 2. Unsupported Calculator Expressions

The calculator rejected certain assignment-based or multi-statement expressions before accepting a supported mathematical expression.

**Lesson:** The LLM must follow the calculator's input contract. Do not assume the calculator supports arbitrary Python code.

### 3. Restricted Tool Calls

The transcript discusses the manager attempting to call a tool despite being intended to have no direct task-tool access.

**Lesson:** Enforce tool permissions in application code rather than relying only on prompts.

### 4. Excessive Tool Calls

An agent may repeat searches or calculations unnecessarily.

**Lesson:** Set iteration limits and clear completion conditions.

### 5. API Rate Limits

Repeated LLM calls can exceed provider rate limits.

**Lesson:** Monitor usage and implement appropriate error handling and retry strategies.

### 6. Inconsistent Search Results

Market-cap values may differ because of changing prices, different sources, or timestamps.

**Lesson:** Use consistent sources and timestamps when comparing system accuracy.

## Security and Reliability

Important safeguards for tool-using agents include:

- Validate tool arguments against defined schemas.
- Restrict tools according to agent responsibilities.
- Treat retrieved web content as untrusted input.
- Use a safe calculator instead of unrestricted code execution.
- Set execution and iteration limits.
- Handle API errors and rate limits.
- Log tool calls and results for debugging.
- Verify calculations and factual claims before returning high-impact answers.

## Technologies Used

| Technology / Component | Purpose |
|---|---|
| Python | Application logic and tool implementation |
| Groq | LLM API access |
| Tavily | Web search |
| Python calculator | Mathematical calculations |
| Environment variables | Store API keys and configuration |
| Token tracking | Measure prompt, completion, and total tokens |

The supplied material does not establish exact dependency versions.

## Project Workflow

```text
1. Set up Python environment
             |
             v
2. Configure API keys
             |
             v
3. Implement web search and calculator
             |
             v
4. Build Single-Agent System
             |
             v
5. Run test query and record usage
             |
             v
6. Build manager and specialist agents
             |
             v
7. Run the same test query
             |
             v
8. Compare results, tokens, and complexity
```

The implementation is developed without LangGraph to demonstrate the underlying orchestration logic directly.

## Key Learnings

- A Single-Agent System can manage multiple tools through one LLM.
- A Multi-Agent System divides work among a manager and specialist agents.
- Multiple agents can use the same model and client.
- System prompts define responsibilities, while application code should enforce tool restrictions.
- The manager can track results using notes or other state-management mechanisms.
- Additional agents can increase LLM calls, token usage, latency, and complexity.
- A Multi-Agent System is useful when specialization provides measurable benefits.
- Token usage should be measured from actual execution logs.
- Invalid tool arguments and unsupported calculator expressions require validation and error handling.
- Iteration limits help prevent repeated tool calls.
- In the supplied run, the Single-Agent System used 16,567 tokens and the Multi-Agent System used 17,446 tokens.
- The Multi-Agent System used approximately 5.3% more tokens in that particular run.
- Architecture decisions should consider answer quality, cost, latency, reliability, and maintainability.

## Summary

This project compares a Single-Agent System with a Multi-Agent System using Python, Groq, Tavily web search, and a calculator.

The Single-Agent System handles the complete workflow through one agent. The Multi-Agent System delegates information retrieval and calculations to specialist agents coordinated by a manager.

The supplied execution logs show that the Multi-Agent System made more LLM calls and consumed approximately 5.3% more tokens in the recorded run.

The central lesson is to **choose the simplest architecture that reliably meets the requirements**. Multiple agents should be introduced when evaluation demonstrates that specialization and coordination justify their additional cost and complexity.
