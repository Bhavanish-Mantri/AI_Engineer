# Day 17: AI Research Agent

This folder contains an implementation of an autonomous **AI Research Agent**. The agent uses Large Language Models (LLMs) to reason and act (ReAct) to research information from the web.

## Features
- **Tool Use**: The agent can autonomously decide when and how to search the web to fulfill user queries.
- **Web Search**: Integrates with the `Tavily` search API for real-time web context.
- **Groq LLM**: Uses high-performance Groq LLMs (like `openai/gpt-oss-120b`) for rapid reasoning and final answer generation.

## Files
- `agent.py`: The core script that orchestrates the ReAct loop, parsing LLM decisions, executing web searches, and returning final answers.
- `main.py`: Base setup script.

## Setup & Usage
1. Configure your `.env` file with your API keys:
   ```env
   GROQ_API_KEY=your_groq_api_key
   TAVILY_API_KEY=your_tavily_api_key
   ```
2. Run the agent:
   ```bash
   python agent.py
   ```
3. Type in your prompt when asked to "Ask me anything".
