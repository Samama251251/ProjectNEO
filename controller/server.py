from fastapi import FastAPI, Request
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from library.helper_functions import admin_access
from modules.neural_controller.main_controller import neural_fx
from modules.neural_controller.memory_controller import transfer_memory
from fastapi.responses import StreamingResponse

#* Configurations
app = FastAPI()
load_dotenv()
admin_access()

#* Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    
)

#* Transfer memory to Pinecone
transfer_memory()

@app.get('/')
async def neural_controller(request: Request):
    prompt = request.query_params.get('prompt')
    try:
        # Directly stream the response using StreamingResponse
        return StreamingResponse(neural_fx(prompt), media_type="application/json")
    except Exception as e:
        print(e)
        return {"error": str(e)}