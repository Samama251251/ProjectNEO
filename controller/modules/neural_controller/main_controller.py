import threading
import time
import json
from google import generativeai
from google.generativeai.types import HarmBlockThreshold, HarmCategory
from dotenv import load_dotenv
from library.helper_functions import clean_content
from modules.shell.shell_actions import shell_actions
from modules.chat.chat_module import casual_chat
from modules.web.web_controller import web_controller
from modules.reasoning.reasoning import reason
from modules.creative.writer import write
from modules.creative.image_generator import generate_image
from modules.code.code_controller import code_controller
from modules.neural_controller.memory_controller import query_memory
from pymongo import MongoClient
import asyncio
import os

# Configurations
load_dotenv()
generativeai.configure(api_key=os.getenv("GOOGLE_GENAI_API"))

#* MongoDB configurations
MONGO_URI = os.getenv("MONGO_URI")  # Add your MongoDB URI in the .env file
DB_NAME = "genai_db"
COLLECTION_NAME = "short_long_term_memory"

#* Initialize MongoDB connection
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def load_memory():
    # Retrieve history from MongoDB
    history_data = collection.find_one({"_id": "chat_history"})
    
    if history_data and "history" in history_data:
        # Return the formatted history
        return history_data["history"]
    
    return []  # Return an empty list if no history is found


memory = load_memory()

# Example usage of save_memory
# save_memory(prompt, response, memory)
# Format the memory as part of system instructions
context = "\n".join([f"{list(entry.keys())[0]}: {list(entry.values())[0]}" for entry in memory])

# Combine instructions with memory context
context_history = (f"Conversation so far:\n{context}")


# Initializing Model
model = generativeai.GenerativeModel(
    model_name='gemini-2.0-flash-exp',
    system_instruction="I am using Windows" +
    " You are: " + os.getenv("SAMPLE_PERSONALITY") +
    os.getenv("NEURAL_MODEL_SETTINGS") +
    "context and conversations: " + context_history
    ,
    safety_settings={
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
)

chat = model.start_chat(history=[])

# Timeout Config
THREAD_TIMEOUT = 30  # Timeout in seconds

def run_with_timeout(target_function, args=(), timeout=THREAD_TIMEOUT):
    """
    Runs a function in a separate thread with a timeout.
    If the thread takes longer than the timeout, it terminates.
    Supports async functions via asyncio.
    """
    output = {"result": None, "error": None}
    done_event = threading.Event()

    def thread_function():
        try:
            # If target_function is async, run it with asyncio
            if asyncio.iscoroutinefunction(target_function):
                result = asyncio.run(target_function(*args))
            else:
                result = target_function(*args)
            output["result"] = result
            print(result)
        except Exception as e:
            output["error"] = str(e)
            print(str(e))
        finally:
            done_event.set()

    thread = threading.Thread(target=thread_function)
    thread.start()
    thread.join(timeout)

    if output["result"] is not None:
        return output

    if thread.is_alive():
        # Thread exceeded timeout
        output["error"] = "Operation timed out after {} seconds".format(timeout)
        done_event.set()
        thread.join()  # Ensure thread cleanup
    return output


# Neural Function Controller
async def neural_fx(prompt):
    print(prompt)
    output = []
    chat_response = ""
    vector_query = query_memory(prompt)
    print(vector_query)
    try:
        res = chat.send_message(prompt + "\nRelevant information from Long-Term Memory, might or might not be relevant. Keept it only as a reference: " + '.'.join(vector_query))
        response = clean_content(res.text)
        print(res.text)
        followup_required = response['followup']['required']

        for action in response['actions']:
            if action['action'] == 'shell':
                thread_result = run_with_timeout(shell_actions, args=(f"prompt from the user: {prompt}." +
                                                                        f" Instructions from neural controller, {action['instructions']}",))
                output.append(thread_result["result"] if not thread_result["error"] else thread_result["error"])

            elif action['action'] == 'conversation':
                if len(response['actions']) > 1 or (followup_required is True or followup_required == 'true'):
                    chat_response = await casual_chat(prompt, vector_query, "respond to user with:" +
                                                        action['instructions'] +
                                                        (f" The output from the module is {', '.join(output)}" if output else ""))
                else:
                    chat_response = await casual_chat(prompt, vector_query, "")
                yield json.dumps({'response': chat_response, "type": "chat"})

            elif action['action'] == 'web_scraping':
                thread_result = run_with_timeout(web_controller, args=(prompt, action['instructions'],))
                output.append(thread_result["result"] if not thread_result["error"] else thread_result["error"])

            elif action['action'] == 'logical_reasoning':
                thread_result = run_with_timeout(reason, args=(action['instructions'],))
                output.append(thread_result["result"] if not thread_result["error"] else thread_result["error"])

            elif action['action'] == 'text_generation':
                thread_result = run_with_timeout(write, args=(action['instructions'],))
                output.append(thread_result["result"] if not thread_result["error"] else thread_result["error"])
                yield json.dumps({'response': thread_result, 'type': 'text_content'})

            elif action['action'] == 'coding':
                thread_result = run_with_timeout(code_controller, args=(action['instructions'],))
                output.append(thread_result["result"] if not thread_result["error"] else thread_result["error"])

            elif action['action'] == 'image_generation':
                thread_result = run_with_timeout(generate_image, args=(prompt,))
                output.append(thread_result["result"] if not thread_result["error"] else thread_result["error"])
                yield json.dumps({'response': thread_result, 'type': 'images'})

        if followup_required is True or followup_required == 'true':
            if response['followup']['for'] == 'user':
                chat_response = await casual_chat(prompt, "respond to user with:" + response['followup']['query'])
        else:
            prompt = ""

    except Exception as e:
        print(e)
        yield json.dumps({"response": str(e)})
