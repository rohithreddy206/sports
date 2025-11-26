from fastapi import APIRouter
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("Warning: GEMINI_API_KEY not found in .env file")

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

# Load sports club data
try:
    with open("sportsclub_data.txt", "r", encoding="utf-8") as f:
        CLUB_DATA = f.read()
except FileNotFoundError:
    CLUB_DATA = "Sports Club information not available."
    print("Warning: sportsclub_data.txt not found")

# Initialize Gemini model
# Dynamically find a supported model to avoid 404 errors
model_name = "gemini-1.5-flash" # Default fallback

try:
    print("Listing available Gemini models...")
    available_models = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            available_models.append(m.name)
    
    print(f"Available models: {available_models}")
    
    # Priority list of models to try (optimized for free tier with better quotas)
    priorities = [
        "models/gemini-2.5-flash",
        "models/gemini-2.0-flash", 
        "models/gemini-flash-latest",
        "models/gemini-2.0-flash-lite",
        "models/gemini-2.5-flash-lite"
    ]
    
    found = False
    for p in priorities:
        if p in available_models:
            model_name = p
            found = True
            break
            
    if not found and available_models:
        model_name = available_models[0] # Pick first available if none of the priorities match
        
    print(f"Selected Gemini model: {model_name}")

except Exception as e:
    print(f"Error listing models, using default: {e}")

model = genai.GenerativeModel(model_name)

@router.post("/chat", response_model=ChatResponse)
async def chat_ai(req: ChatRequest):
    if not GEMINI_API_KEY:
        return ChatResponse(
            reply="AI assistant is currently unavailable. Please check the GEMINI_API_KEY configuration."
        )
    
    try:
        prompt = f"""You are a Sports Club AI Assistant.
Use ONLY the following club data to answer the user's question:

{CLUB_DATA}

User Question: {req.message}

Please provide a helpful, friendly, and professional response based only on the information above."""

        response = model.generate_content(prompt)

        # Extract reply safely (Gemini 1.5 Flash)
        reply_text = ""

        if hasattr(response, "text") and response.text:
            reply_text = response.text

        elif hasattr(response, "candidates") and response.candidates:
            parts = response.candidates[0].content.parts
            if parts and hasattr(parts[0], "text"):
                reply_text = parts[0].text

        if not reply_text or reply_text.strip() == "":
            reply_text = "Sorry, I couldn't find an answer based on the provided sports club information."

        return ChatResponse(reply=reply_text)

    except Exception as e:
        print(f"Gemini API Error: {str(e)}")
        return ChatResponse(
            reply="I'm experiencing technical difficulties. Please try again later."
        )
