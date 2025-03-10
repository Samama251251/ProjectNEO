import datetime
import time
import threading
from plyer import notification
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
    system_instruction=os.getenv("SAMPLE_PERSONALITY") + os.getenv("CHAT_SETTINGS"),
    safety_settings={
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
)

reminders = []

def add_reminder(reminder_text, reminder_time):
    reminders.append({"text": reminder_text, "time": reminder_time})

def check_reminders():
    while True:
        now = datetime.datetime.now()
        for reminder in reminders:
            if reminder["time"] <= now:
                notification.notify(
                    title="Reminder",
                    message=reminder["text"],
                    timeout=10
                )
                reminders.remove(reminder)
        time.sleep(60)

def start_reminder_service():
    reminder_thread = threading.Thread(target=check_reminders)
    reminder_thread.daemon = True
    reminder_thread.start()

chat = model.start_chat(history=[])

async def reminder_controller(prompt):
    try:
        content = chat.send_message(prompt)
        print(content.text)
        cleaned_content = clean_content(content.text)
        add_reminder(cleaned_content['response'], cleaned_content['time'])
    except Exception as e:
        print(e)