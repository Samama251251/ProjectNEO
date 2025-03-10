from google import generativeai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv
from library.helper_functions import clean_content
from pymongo import MongoClient
from modules.neural_controller.memory_controller import query_memory
import os

#* Load environment variables
load_dotenv()

#* MongoDB configurations
MONGO_URI = os.getenv("MONGO_URI")  # Add your MongoDB URI in the .env file
DB_NAME = "genai_db"
COLLECTION_NAME = "short_long_term_memory"

#* Initialize MongoDB connection
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

#* Generative AI model configurations
generativeai.configure(api_key=os.getenv("GOOGLE_GENAI_API"))

#* Load chat history from MongoDB
def load_memory():
    # Retrieve history from MongoDB
    history_data = collection.find_one({"_id": "chat_history"})
    
    if history_data and "history" in history_data:
        # Return the formatted history
        return history_data["history"]
    
    return []  # Return an empty list if no history is found

#* Save chat history to MongoDB
def save_memory(history):
    # Retrieve existing history from MongoDB
    existing_data = collection.find_one({"_id": "chat_history"})
    existing_history = existing_data.get("history", []) if existing_data else []

    # Format the new history entries
    formatted_history = []
    for i in range(0, len(history), 2):  # Process user-bot pairs
        if i + 1 < len(history):  # Ensure both user and bot content exists
            formatted_history.append({"user": history[i]["content"]})
            formatted_history.append({"you": history[i + 1]["content"]})

    # Append the new formatted history to the existing history
    combined_history = existing_history + formatted_history

    # Save the combined history to MongoDB
    collection.update_one(
        {"_id": "chat_history"},
        {"$set": {"history": combined_history}},
        upsert=True  # Create if it doesn't exist
    )

memory = load_memory()

# Example usage of save_memory
# save_memory(prompt, response, memory)
# Format the memory as part of system instructions
context = "\n".join([f"{list(entry.keys())[0]}: {list(entry.values())[0]}" for entry in memory])

# Combine instructions with memory context
context_history = (f"Conversation so far:\n{context}")
print(context_history)

#* Initialize Model
model = generativeai.GenerativeModel(
    model_name='gemini-2.0-flash-exp', 
    system_instruction=os.getenv("SAMPLE_PERSONALITY") + os.getenv("CHAT_SETTINGS") + context_history,
    safety_settings={
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
)


#* Load chat history from MongoDB 
chat = model.start_chat(history=[])

    # Send the user's prompt
#* Chat function
async def casual_chat(prompt, vector_response, instructions):
    history = []
    content = chat.send_message(
        "Message from user: " + prompt + " Instructions from Neural Network: " + instructions + "Relevant Information from Memory (might or might not be relevant, Keep it as reference and thoughts): " + '.'.join(vector_response)
    )

    # Clean the content using your helper function
    response = clean_content(content.text)

    # Append the user's prompt and the bot's response to the history
    history.append({"content": prompt})
    history.append({"content": response['response']})

    # Save the user's prompt and the bot's response to memory
    save_memory(history)

    # Print the response in color for terminal output
    print("\033[1;32m" + response['response'] + "\033[1;0m")
    print("\033[1;33m" + str(response['emotions']) + "\033[1;0m")


    return response['response']
