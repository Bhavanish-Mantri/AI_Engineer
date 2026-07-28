import os
from pathlib import Path
from time import sleep
from dotenv import load_dotenv
from groq import Groq
import re

load_dotenv()
my_api_key=os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("API key kaha hai bhai")

client=Groq(api_key=my_api_key)
model="llama-3.3-70b-versatile"

# create tools

def get_product_price(product):
    if product == 'Iphone 17':
        return 1000
    elif product == 'Iphone 15':
        return 500
    else:
        return "bhai, iska price mereko nhi pta"

def calculator(expression):
    try:
        return eval(expression)
    except:
        return "math nhi aata kya bhai"

# tools registry

tools = {
    "get_product_price": get_product_price,
    "calculator": calculator
}

system_prompt = """
you are a shopping assistant

you have these tools:
get_product_price(product)
calculator(expression)
IMPORTANT:
call these tools exactly these examples

Action: get_product_price("Iphone 17")
Action: calculator("5000 - 1000")

Never write:
get_product_price(product="iPhone 17")

Never write:
calculator(expression="$5000 - $1000")

Follow these rules:

1. Decide what you need to do next.
2. Call ONLY ONE tool at a time.
3. After writing an Action, STOP immediately.
4. Never guess or invent a tool result.
5. Wait until you receive an Observation.
6. Then decide your next action.
7. When the task is complete, give the Final Answer.

Format: 
Thought : what you need to do
Action : tool_name(argument)

When Finished:
Final Answer : your answer
"""

def run_agent(question):

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": question
        }
    ]

# Limit the agent to a maximum of 5 tool-use cycles (steps)

    for step in range(5):

        print("\n------------------")
        print("STEP", step + 1)
        print("------------------")

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0
        )

        answer = response.choices[0].message.content

        print(answer)

# Agent has finished task 
        if "Final Answer" in answer:
            break


# Find the Action
        match = re.search(
            r"Action\s*:\s*(\w+)\((.*?)\)",
            answer
        )


        if match:

            tool_name = match.group(1)

            tool_input = match.group(2)

            tool_input = tool_input.strip()

            tool_input = tool_input.strip("'\"")


# Run the tool
            if tool_name in tools:

                tool = tools[tool_name]

                observation = tool(tool_input)

            else:

                observation = "Tool not found"


            print(
                "Observation:",
                observation
            )


# Add LLM response to memory
            messages.append({
                "role": "assistant",
                "content": answer
            })


# Give tool result back to LLM
            messages.append({
                "role": "user",
                "content":
                    "Observation: "
                    + str(observation)
            })
            sleep(5)



prompt="""
I have $9000. What is the price of an iphone 17?
and how much money will I have left if i purchase it?
"""
run_agent(prompt)