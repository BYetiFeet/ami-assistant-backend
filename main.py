from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
import requests  # NEW: For logging to Google Sheets

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the data model
class UserMessage(BaseModel):
    message: str
    role: str
    user_id: str

@app.post("/ask")
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
        # Generate AMI's reply
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

        # Log to Google Sheets (non-blocking)
        webhook_url = "https://script.google.com/macros/s/AKfycbzrpW3Vj_Xz2UTsvlyI4B9fe1d3uIvMry5FI9DIUhTJfQFErVYxY659VYCBzu0xwh8i/exec"
        log_payload = {
            "role": data.role,
            "user_id": data.user_id,
            "message": data.message,
            "reply": reply
        }
        try:
            requests.post(webhook_url, json=log_payload, timeout=5)
        except Exception as log_error:
            print(f"[Logging failed] {log_error}")

        return {"reply": reply}

    except Exception as e:
        return {"reply": f"Sorry, there was a problem: {str(e)}"}
