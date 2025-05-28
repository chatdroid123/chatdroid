from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os

app = FastAPI()

# Enable CORS so frontend can access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI client with environment key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/")
def root():
    return {"status": "ChatDroid backend is live."}

@app.post("/chat")
async def chat(req: Request):
    try:
        data = await req.json()
        user_message = data.get("message", "")
        print(f"Received message: {user_message}")

        if not user_message:
            return {"reply": "Empty message received."}

        # OpenAI v1.0+ compatible syntax
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ]
        )

        reply = response.choices[0].message.content
        print(f"OpenAI reply: {reply}")
        return {"reply": reply}

    except Exception as e:
        print(f"Error: {str(e)}")
        return {"reply": "Sorry, something went wrong on the server."}
