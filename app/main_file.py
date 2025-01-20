from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse, FileResponse
import uuid
import os
import torch
from langchain_openai import ChatOpenAI
from models import build_model
from kokoro import generate

# Initialize FastAPI app
app = FastAPI()

# Setup device
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# Load Kokoro model and voicepack
def initialize_kokoro():
    model_path = 'kokoro-v0_19.pth'
    voice_name = 'af'  # Default voice
    model = build_model(model_path, device)
    voicepack = torch.load(f'voices/{voice_name}.pt', weights_only=True).to(device)
    return model, voicepack, voice_name

# Initialize Kokoro and LangChain OpenAI
kokoro_model, kokoro_voicepack, kokoro_voice_name = initialize_kokoro()

llm = ChatOpenAI(
    api_key="ollama",  # Required, even if unused
    base_url="https://sunny-gerri-finsocialdigitalsystem-d9b385fa.koyeb.app/v1",
    model="athene-v2"
)

# Define request model
class ChatRequest(BaseModel):
    text: str

# Generate TTS audio
def generate_audio(text):
    try:
        audio, _ = generate(kokoro_model, text, kokoro_voicepack, lang=kokoro_voice_name[0])
        file_name = f"{uuid.uuid4()}.wav"
        file_path = f"audio/{file_name}"
        os.makedirs("audio", exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(audio)
        return file_path
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating audio: {str(e)}")

# API endpoint for chatbot interaction
@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Generate text response
        response_text = llm.predict(request.text)

        # Generate audio response
        audio_file = generate_audio(response_text)

        return JSONResponse({
            "text_response": response_text,
            "audio_file": audio_file
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# API endpoint to serve audio files
@app.get("/audio/{file_name}")
async def get_audio(file_name: str):
    file_path = f"audio/{file_name}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(file_path, media_type="audio/wav")
