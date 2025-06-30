from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import requests
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserMessage(BaseModel):
    message: str
    role: str
    user_id: str

GOOGLE_SHEETS_URL = "https://script.google.com/macros/s/AKfycbzrpW3Vj_Xz2UTsvlyI4B9fe1d3uIvMry5FI9DIUhTJfQFErVYxY659VYCBzu0xwh8i/exec"

@app.post("/ask")
from fastapi import Request
import httpx

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzrpW3Vj_Xz2UTsvlyI4B9fe1d3uIvMry5FI9DIUhTJfQFErVYxY659VYCBzu0xwh8i/exec"

@app.post("/log-to-sheets")
async def log_to_sheets(request: Request):
    try:
        payload = await request.json()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                GOOGLE_SCRIPT_URL,
                json=payload,
                headers={"Content-Type": "application/json"}
            )

        return {"status": "forwarded", "google_response": response.text}
    except Exception as e:
        return {"error": str(e)}




async def ask_ami(data: UserMessage):
    stakeholder_tone = {
        "client": "a warm, respectful, supportive assistant",
        "carer": "a calm, confident, encouraging assistant",
        "family": "a compassionate and informative assistant",
        "manager": "a professional, concise, helpful assistant",
    }

    tone = stakeholder_tone.get(data.role.lower(), "a supportive assistant")

    system_prompt = (
        f"You are AMI, {tone}. Respond to the user's question clearly, "
        "warmly, and truthfully, in a way that matches their role. "
        "Don't give medical advice. Avoid jargon. Be helpful and kind."
    )

    try:
        # Generate AMI response
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": data.message}
            ],
            temperature=0.6,
            max_tokens=300,
        )
        reply = response.choices[0].message.content.strip()

        # Log to Google Sheets
        try:
            requests.post(GOOGLE_SHEETS_URL, json={
                "user_id": data.user_id,
                "role": data.role,
                "message": data.message,
                "reply": reply
            })
        except Exception as log_err:
            print(f"Logging failed: {log_err}")

        return {"reply": reply}

    except Exception as e:
        return {"reply": f"Sorry, there was a problem: {str(e)}"}
