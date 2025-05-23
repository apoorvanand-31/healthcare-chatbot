from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random
import re
from typing import List, Dict
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app = FastAPI(title="Health & Hygiene Chatbot")

# ======================= Models =======================
class Message(BaseModel):
    role: str  # "user" or "bot"
    content: str

class ChatRequest(BaseModel):
    message: str
    user_id: str = "default_user"

class ChatResponse(BaseModel):
    response: str
    conversation_history: List[Message]

# ======================= Data Store =======================
conversations: Dict[str, List[Message]] = {}

# ======================= Response Patterns =======================
responses = {
    r'\bhi\b|\bhello\b|\bhey\b': [
        "Hello! I'm your Health & Hygiene Assistant. Ask me anything!",
        "Hi! Need tips on staying clean and healthy?",
        "Hey! What hygiene or health topic would you like to explore?"
    ],
    r'hand|wash': [
        "Wash your hands with soap and water for at least 20 seconds.",
        "Always wash your hands before meals and after using the toilet.",
        "Handwashing is the first defense against many infections."
    ],
    r'food|eat|diet': [
        "A healthy diet includes vegetables, fruits, whole grains, and lean proteins.",
        "Avoid junk food and drink plenty of water.",
        "Eating balanced meals boosts immunity and energy levels."
    ],
    r'flu|cold|fever|ill': [
        "Prevent flu by getting vaccinated, staying clean, and avoiding close contact with the sick.",
        "If you're sick, rest, stay hydrated, and consult a doctor.",
        "Keep your environment clean to reduce chances of getting sick."
    ],
    r'teeth|brush|oral': [
        "Brush your teeth twice daily and floss once a day.",
        "Change your toothbrush every 3 months.",
        "Oral hygiene is crucial to prevent gum disease."
    ],
    r'bath|shower|clean': [
        "Daily bathing keeps skin healthy and removes bacteria.",
        "Clean clothes and body prevent infections and body odor.",
        "Personal hygiene is a daily responsibility."
    ],
    r'sleep|rest': [
        "Adults need 7–8 hours of sleep for good health.",
        "Sleep helps your body repair and boosts immunity.",
        "Lack of sleep can weaken your immune system."
    ],
    r'stress|mental|relax': [
        "Take breaks, talk to friends, or try meditation to reduce stress.",
        "Mental health is as important as physical health.",
        "Stay connected and express your feelings—it helps!"
    ],
    r'thank you|thanks': [
        "You're welcome! Stay healthy!",
        "Anytime! Let me know if you have more questions.",
        "Glad to help!"
    ],
    r'bye|goodbye': [
        "Goodbye! Stay safe and clean!",
        "See you later. Take care of your health!",
        "Bye for now! Keep up the good hygiene habits!"
    ]
}

default_responses = [
    "Sorry, I don't have an answer for that yet. Try asking about hygiene, diet, or illness prevention.",
    "I'm still learning. Can you try rephrasing your question?",
    "That's interesting! Could you ask something related to health or hygiene?"
]

# ======================= Utility =======================
def generate_bot_response(user_input: str) -> str:
    user_input = user_input.lower()
    for pattern, replies in responses.items():
        if re.search(pattern, user_input):
            return random.choice(replies)
    return random.choice(default_responses)

# ======================= Endpoints =======================
@app.get("/ping")
def ping():
    return {"status": "ok", "message": "Health & Hygiene Chatbot is online!"}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    user_id = req.user_id
    user_message = Message(role="user", content=req.message)
    
    bot_reply = generate_bot_response(req.message)
    bot_message = Message(role="bot", content=bot_reply)

    if user_id not in conversations:
        conversations[user_id] = []
    conversations[user_id].extend([user_message, bot_message])

    return ChatResponse(
        response=bot_reply,
        conversation_history=conversations[user_id]
    )

@app.get("/history/{user_id}", response_model=List[Message])
def get_history(user_id: str):
    if user_id not in conversations:
        raise HTTPException(status_code=404, detail="User not found")
    return conversations[user_id]

@app.delete("/reset/{user_id}")
def reset_conversation(user_id: str):
    if user_id in conversations:
        conversations[user_id] = []
        return {"message": f"Conversation for user '{user_id}' has been reset."}
    else:
        return {"message": f"No conversation history found for user '{user_id}'."}
