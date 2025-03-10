
from google import generativeai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from .image_generator_logic import generate_images_links
import os
import dotenv
dotenv.load_dotenv()

generativeai.configure(api_key=os.getenv("GOOGLE_GENAI_API2"))

model = generativeai.GenerativeModel(
    model_name='gemini-2.0-flash-exp', 
    system_instruction=os.getenv("IMAGE_GENERATION"),
    safety_settings={
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
)

chat = model.start_chat(history=[])

# Generate image links for the prompt
async def generate_image(prompt):
    try:
        response = chat.send_message(prompt)
        print(response.text)
        # Generate image links
        print("Generating image links for the prompt...")
        image_links = await generate_images_links(response.text)
        return [image for image in image_links if not (image.endswith(".js") or image.endswith(".svg"))]
    except Exception as e:
        print(f"An error occurred: {e}")
