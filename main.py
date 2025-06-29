from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("Missing OPENAI_API_KEY environment variable")

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

@app.post("/ask")
async def ask_ami(data: UserMessage):
    try:
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

        from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": data.message}
    ],
    temperature=0.6,
    max_tokens=300,
)

return {"reply": response.choices[0].message.content.strip()}
        )

        return {"reply": response.choices[0].message["content"].strip()}

    except Exception as e:
        return {"reply": f"Sorry, there was a problem: {str(e)}"}
