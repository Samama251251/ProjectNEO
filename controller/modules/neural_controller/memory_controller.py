from google import generativeai
from google.generativeai.types import HarmBlockThreshold, HarmCategory
from dotenv import load_dotenv
from pymongo import MongoClient
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
import os
import time
import numpy as np

# Load environment variables
load_dotenv()

# Pinecone configurations
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = "neo"
if not pc.has_index(index_name):
    pc.create_index(
        name=index_name,
        dimension=768,
        metric="cosine",
        spec=ServerlessSpec(
            cloud='aws', 
            region='us-east-1'
        ) 
    ) 

# Wait for the index to be ready
while not pc.describe_index(index_name).status['ready']:
    time.sleep(1)

index = pc.Index(index_name)
description = index.describe_index_stats()

generativeai.configure(api_key=os.getenv("GOOGLE_GENAI_API2"))

# MongoDB configurations
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "genai_db"
COLLECTION_NAME = "short_long_term_memory"

# Initialize MongoDB connection
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

model = generativeai.GenerativeModel(
    model_name='gemini-2.0-flash-exp',
    system_instruction=os.getenv("RAG_COMPRESSION_SETTINGS"),
    safety_settings={
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
)

# Load chat history from MongoDB
def load_memory():
    history_data = collection.find_one({"_id": "chat_history"})
    if history_data and "history" in history_data:
        return history_data["history"]
    return []

# Split text into smaller chunks to avoid exceeding the payload limit
def split_text(text, max_lines=6):
    chunks = []
    lines = text.split(". ")
    
    # Group lines into chunks of max_lines
    for i in range(0, len(lines), max_lines):
        chunk = "\n".join(lines[i:i + max_lines])
        print('Chunk:', chunk) 
        chunks.append(chunk)
    
    return chunks

# Transfer memory to Pinecone with each chunk as a separate entry
def transfer_memory():
    history_data = collection.find_one({"_id": "chat_history"})
    if history_data:
        print("History collected")
        records = len(history_data['history'])
        print(records)
        if records / 2 > 100:
            print("\033[1;33mTransferring memory to RAG model...\033[0m")
            memory = load_memory() 
            context = "\n".join([f"{list(entry.keys())[0]}: {list(entry.values())[0]}" for entry in memory])

            # Combine instructions with memory context
            context_history = f"Conversation so far:\n{context}"

            history_summary = model.generate_content(context_history)
            print("History summary generated.")

            # Split the context into chunks
            chunks = split_text(history_summary.text)
            print(f"Total chunks: {len(chunks)}")

            for idx, chunk in enumerate(chunks):
                compressed_output = model.generate_content(chunk)
                print("Compressed output generated.")
                
                # Embed each chunk
                embedding_result = generativeai.embed_content(
                    model="models/text-embedding-004",
                    content=compressed_output.text
                )
                embedding = embedding_result['embedding']

                # Use a unique ID for each chunk
                unique_id = f"chunk_{int(time.time())}_{idx}"
                
                # Upsert each chunk into Pinecone
                index.upsert(
                    [(unique_id, embedding, {"context": chunk})]
                )
                print(f"Chunk {idx + 1} upserted to Pinecone with id: {unique_id}")
                time.sleep(5)  # Avoid rate limits

            print("\033[1;32mMemory transferred successfully.\033[0m")

            # Clear chat History from MongoDB after transfer
            collection.update_one(
                {"_id": "chat_history"},
                {"$set": {"history": []}}
            )
            print("Chat history cleared.")
        else:
            print("\033[1;31mNot enough data to transfer memory.\033[0m")

# Query from Pinecone
def query_memory(query):

    print("\033[1;34mQuerying vector database...\033[0m")
    
    # Generate embedding for the query
    embedding_result = generativeai.embed_content(
        model="models/text-embedding-004",
        content=query
    )
    query_embedding = embedding_result['embedding']
    print("Query embedding generated.")
    
    # Search Pinecone for similar vectors
    search_results = index.query(
        top_k=5,  # Retrieve top 5 most similar results
        vector=query_embedding,
        include_metadata=True
    )
    
    print("Search results retrieved.")
    for match in search_results['matches']:
        print(f"Score: {match['score']}")
    
    if search_results['matches']:
        top_results = [match['metadata']['context'] for match in search_results['matches']]
        print("\033[1;32mTop Results:\033[0m")
        for idx, result in enumerate(top_results, start=1):
            print(f"{idx}. {result}\n")
        return top_results  # Return all top_k results as a list
    else:
        print("\033[1;31mNo relevant results found.\033[0m")
        return None
