import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("API key kaha hai yr")

client  = Groq(api_key = my_api_key)

model = "llama-3.3-70b-versatile"

def llm_ans(prompt):
    messages ={
        "role" : "user",
        "content": prompt
    }
    messages = [messages]
    response = client.chat.completions.create(model = model , messages = messages)
    ans = response.choices[0].message.content
    return ans

# bad_prompt = """
# this is a user complaint :
# My laptop is not working
# Classify this.
# """

# print("Bad Prompt Output : ",llm_ans(bad_prompt))   

good_prompt = """
# ROLE: 
you are customer support assistant at mobile/laptop company.
# TASK:
you have to classify the issue in a category
# CONSTRAINTS:
you have to classify the issue in the 3 categories namely Billing , Technical & Return
# OUTPUT FORMAT:
your answer should be in one word only. the one word should be the categories given to you
# EXAMPLE:
for instance if user complain say that he want a refund then category is Return 
# FALLBACK:
if the issue is unrelated to any of the categories mentioned above say Not Applicable

this is a user complaint :
give me a java code for adding 2 numbers

"""
print("Good Prompt Output : ",llm_ans(good_prompt))