from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from openai import OpenAI
import os

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting with IP exception
OWNER_IP = "136.41.192.83"

def custom_key_func(request: Request):
    client_ip = get_remote_address(request)
    if client_ip == OWNER_IP:
        return "owner-bypass"
    return client_ip

limiter = Limiter(key_func=custom_key_func)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"reply": "❌ You've reached the daily limit of 10 messages. Please try again tomorrow."}
    )

# OpenAI API client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Dean Dental configuration
DEAN_DENTAL_PROMPT = (
    "You are the AI receptionist for Dean Dental, a fictional dental clinic at 742 Evergreen Terrace, Austin, TX. "
    "You ONLY answer questions about Dean Dental. Open Mon–Fri 8am–5pm. "
    "Services: cleanings, whitening, root canals, Invisalign, pediatric care. "
    "Dentists: Dr. Samantha Reed, Dr. Mark Patel, Dr. Olivia Nguyen. "
    "Insurance accepted: Aetna, Cigna, Delta Dental, MetLife. "
    "For bookings, direct users to https://calendly.com/chatdroidhelp."
)

@app.get("/")
def root():
    return {"status": "ChatDroid backend with Dean Dental and IP rate limit is live."}

@app.post("/chat")
@limiter.limit("10/day")
async def chat(req: Request):
    try:
        data = await req.json()
        user_message = data.get("message", "")
        print(f"Received message: {user_message}")

        if not user_message:
            return {"reply": "Empty message received."}

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # or use gpt-4o if you want
            messages=[
                {"role": "system", "content": DEAN_DENTAL_PROMPT},
                {"role": "user", "content": user_message}
            ]
        )

        reply = response.choices[0].message.content
        print(f"OpenAI reply: {reply}")
        return {"reply": reply}

    except Exception as e:
        print(f"Error: {str(e)}")
        return {"reply": "Sorry, something went wrong on the server."}

