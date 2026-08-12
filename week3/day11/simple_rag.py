import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("API key kaha hai bhai")

client = Groq(api_key=my_api_key)
model = "llama-3.3-70b-versatile"

# Step 1 : Knowledge Base
knowledge_base ={
"who" : "Bhavanish Mantri is a student of Amity University.",
"age": "Bhavanish Mantri is 22 years old",
"interests": "Bhavanish Mantri is interested in AI and Machine Learning."
}

# Step 2 : Retrieval
def retrieve(question):
    question = question.lower()
    matched_key = None

    for key in knowledge_base:
        if key in question:
            matched_key = key
            break
    
    if matched_key:
        return knowledge_base[matched_key]
    return None

def ask_llm(question):
    context = retrieve(question)

    system_prompt = f"""Answer in 1 line Only and answer this question strictly based on this context, Do not hallucinate. Context: {context}"""

    system_message={
        "role": "system",
        "content": system_prompt
    }

    message={
        "role":"user",
        "content" : question
    }

    messages= [system_message,message]
    response = client.chat.completions.create(model=model, messages=messages)
    answer= response.choices[0].message.content
    return answer

# question = " Do you know Amity University"  #LLM knows this from its training data

question = " what is the interests of Bhavanish Mantri"

print(ask_llm(question))