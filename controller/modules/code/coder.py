from google import generativeai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv
from library.helper_functions import clean_content
import os

load_dotenv()

#* Configurations
load_dotenv()
generativeai.configure(api_key = os.getenv("GOOGLE_GENAI_API"))

#* Initializing Model
model = generativeai.GenerativeModel(
    model_name='gemini-1.5-flash', 
    system_instruction=os.getenv("CODER_SETTINGS"),
    safety_settings={
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
)

chat = model.start_chat(history=[])

async def coder(instructions, suggestions=""):
    content = chat.send_message("Instructions for code: " + instructions + " Suggestions and problems reported from tester: " + suggestions)
    response = clean_content(content.text)
    return response
