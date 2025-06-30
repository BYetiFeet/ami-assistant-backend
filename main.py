from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from openai import OpenAI
import os
import requests

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Secure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserMessage(BaseModel):
    message: str
    role: str
    user_id: str

@app.post("/ask")
async def ask_ami(data: UserMessage):
    tone_map = {
        "client": "a warm, respectful, supportive assistant",
        "carer": "a calm, confident, encouraging assistant",
        "family": "a compassionate and informative assistant",
        "manager": "a professional, concise, helpful assistant",
    }
    tone = tone_map.get(data.role.lower(), "a supportive assistant")

    system_prompt = (
        f"You are AMI, {tone}. Respond to the user's question clearly, "
        "warmly, and truthfully, in a way that matches their role. "
        "Don't give medical advice. Avoid jargon. Be helpful and kind."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": data.message}
            ],
            temperature=0.6,
            max_tokens=300,
        )
        return {"reply": response.choices[0].message.content.strip()}
    except Exception as e:
        return {"reply": f"Sorry, there was a problem: {str(e)}"}

@app.post("/log-to-sheets")
async def log_to_sheets(req: Request):
    payload = await req.json()
    try:
        r = requests.post(
            "https://script.google.com/macros/s/AKfycbxNt4pS-U-jcpTV3UuI-ROsVEIs2Y2XDsqcFsKCsMWk8_Ov1yTDPZb_JKNCXZvGqReD/exec",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        return {"status": "ok", "sheets_response": r.text}
    except Exception as e:
        return {"error": str(e)}

@app.post("/submit-feedback")
async def submit_feedback(req: Request):
    try:
        payload = await req.json()
        r = requests.post(
            "https://script.google.com/macros/s/AKfycbxNt4pS-U-jcpTV3UuI-ROsVEIs2Y2XDsqcFsKCsMWk8_Ov1yTDPZb_JKNCXZvGqReD/exec",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        return JSONResponse(content={"status": "ok", "google_response": r.text})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
