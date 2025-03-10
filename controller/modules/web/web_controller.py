from google import generativeai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv
from library.helper_functions import clean_content
from modules.web.scraper import web_scrapper
import os

load_dotenv()

#* Configurations
load_dotenv()
generativeai.configure(api_key = os.getenv("GOOGLE_GENAI_API2"))

#* Initializing Model
controller_model = generativeai.GenerativeModel(
    model_name='gemini-1.5-flash', 
    system_instruction=os.getenv("WEB_CONTROLLER_SETTINGS"),
    safety_settings={
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    },
)

refine_prompt = generativeai.GenerativeModel(
    model_name='gemini-1.5-flash', 
    system_instruction=os.getenv("REFINE_WEB_PROMPT"),
    safety_settings={
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    },
)

async def web_controller(prompt, instructions):
    refined_prompt = refine_prompt.generate_content("User prompt:" + prompt + "Instructions from system:" + instructions)
    query = clean_content(refined_prompt.text)
    print(query)
    scrapped_data = await web_scrapper(query["query"])
    content = controller_model.generate_content(str(scrapped_data))
    content = clean_content(content.text)
    return [content['response'] + "\n Explain"]
