from groq.types.chat import chat_completion_system_message_param
import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
import numpy as np
from sentence_transformers import SentenceTransformer
import sys

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # 384 dimensions

groq_model = "llama-3.3-70b-versatile"

load_dotenv()

my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("API kaha hai bhai")

client = Groq(api_key=my_api_key)

# Knowledge Base
knowledge_base_documents = [
    "Employees receive 30 days of paid leave per year.",
   
    "Employees work from the office on Tuesday, Wednesday and Thursday. "

    "Monday and Friday are optional work-from-home days.",
   
    "Employees receive Rs 5000 per month for travel reimbursement.",
   
    "Employees can claim Rs 2000 per month for home internet.",
   
    "Employees have a 60 day notice period."
]

# Embedding the knowledge base

Embedding = embedding_model.encode(knowledge_base_documents)   # convert every line in knowledge base into array (mathematical representation)

# 7 kb of array size is generated just from 6 lines and in industry there are lakhs of lines so it becomes huge and expensive to store in RAM
# This problem is solved by Vector Databases in real world

# print(sys.getsizeof(Embedding))

def cosine_similarity(a,b):
    return np.dot(a,b) / (np.linalg.norm(a) * np.linalg.norm(b))   # formula for cosine similarity (measures similarity between two arrays)


def retrieve(query_embedding):
    scores =[]
    for i , doc_embedding in enumerate(Embedding):
        score = cosine_similarity(query_embedding,doc_embedding)   
        scores.append((score,knowledge_base_documents[i]))  # store both score and documents
    scores.sort(reverse = True)
    return scores[0] # return that line which has highest score


def ask_llm(question,context):

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
    response = client.chat.completions.create(model=groq_model, messages=messages)
    answer= response.choices[0].message.content
    return answer


# User input query convert into embedding (array/mathematical representation)

query = "How many days of vacation do any employee get in a year ?"
# query = "I love you baby"   it gives 0 score because it is not related to our knowledge base so it will print this -> There is no information related to your statement in the given context.

query_embedding = embedding_model.encode(query)

score,context = retrieve(query_embedding)

answer = ask_llm(query,context)
print(answer)
