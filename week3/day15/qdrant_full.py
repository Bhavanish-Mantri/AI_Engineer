import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue, MatchAny, PayloadSchemaType
from sentence_transformers import SentenceTransformer
from groq import Groq
import json

# Load variables from .env
load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")



# CONNECT TO QDRANT

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    timeout=60.0
)

print("Qdrant Cloud se connect ho gya!")



# CREATE QDRANT COLLECTION

COLLECTION_NAME = "knowledge_filter"
EMBEDDING_SIZE = 384


# Delete collection if it already exists

if client.collection_exists(COLLECTION_NAME):
    print(f"Deleting existing collection: {COLLECTION_NAME}")
    client.delete_collection(COLLECTION_NAME)


# Create collection

client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(
        size=EMBEDDING_SIZE,
        distance=Distance.COSINE,
    ),
)

print(f"Created collection: {COLLECTION_NAME}")
print(f"Vector size: {EMBEDDING_SIZE}")
print("Distance: COSINE")

# creating index so that filter could work, so this will create index on category field so that we can filter on category field


client.create_payload_index(     
    collection_name = COLLECTION_NAME,
    field_name = "category",    # category pe filter use karna chahte hai
    field_schema = PayloadSchemaType.KEYWORD
)


# LOAD OUR KNOWLEDGE

with open("knowledge.json", "r", encoding="utf-8") as f:
    documents = json.load(f)

print(f"Loaded {len(documents)} documents")


# CREATE EMBEDDINGS FOR TEXT


print("Loading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

print("Embedding model ready!")

# read the document and extract the 'text' from the document and create a list of text from the documents

texts = [document["text"] for document in documents]

embeddings = model.encode(texts)

print(f"Generated {len(embeddings)} embeddings")
print(f"Embedding size: {len(embeddings[0])}")


# CREATE QDRANT POINTS

points = []

for i in range(len(documents)):

    point = PointStruct(
        id=i + 1,
        vector=embeddings[i].tolist(),
        payload= documents[i]    # inside the document, everything is payload
    )

    points.append(point)


# UPLOAD POINT TO QDRANT
 
# upsert points to qdrant collection, so that we can search the points later

client.upsert(
    collection_name=COLLECTION_NAME,
    points=points
)

print(f"Uploaded {len(points)} documents to Qdrant!")



# SEARCH QDRANT

def search(query, top_k=3):

    # Convert question into embedding
    query_vector = model.encode(query).tolist()

    # Search Qdrant
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    ).points

    return results


def search_with_filter(query, query_filter = None, top_k = 3):
    query_vector = model.encode(query).tolist()

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        with_payload=True,
        query_filter=query_filter
    ).points

    return results

reimbeursement_filter = Filter(
    must=[
        FieldCondition(
            key="category",
            match=MatchValue(value="reimbursement")
        )
    ]
)

  
# TEST SEARCH


# query = "Where is the nearest coffee shop?"
query = "How many vacation days do I get?"

results = search_with_filter(query, reimbeursement_filter, top_k=3)

print("\nSearch results:")

for result in results:
    print(f"Score: {result.score:.3f}")
    print(result.payload["text"])
    print()


# CONNECT TO GROQ


groq_client = Groq(api_key=GROQ_API_KEY)

print("Connected to Groq!")



# ASK THE LLM

def ask_llm(question, context):

    prompt = f"""
Answer the question using only the information provided below.

Context:
{context}

Question:
{question}

If the answer is not present in the context, say:
"I don't know based on the provided information."
"""

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content


# COMPLETE RAG PIPELINE

# question = "Where is the nearest coffee shop?"
question = "how many vacation do i get?"

results = search(question, top_k=3)


# Extract text from search results
context = "\n".join(
    result.payload["text"]
    for result in results
)


answer = ask_llm(question, context)


print("\nFinal Answer:")
print(answer)