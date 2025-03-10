from google import generativeai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv
from library.helper_functions import clean_content
import os

load_dotenv()

#* Configurations
load_dotenv()
generativeai.configure(api_key = os.getenv("GOOGLE_GENAI_API2"))

#* Initializing Model
model = generativeai.GenerativeModel(
    model_name='gemini-1.5-flash', 
    system_instruction=os.getenv("TESTER_SETTINGS"),
    safety_settings={
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
)

chat = model.start_chat(history=[])

async def tester(code, output):
    content = chat.send_message("The coding module has given the code:" + code + " The output of which is " + str(output))
    print(content.text)
    response = clean_content(content.text)
    return response
