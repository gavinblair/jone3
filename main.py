from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from datetime import datetime
import asyncio
import json
from pydantic import BaseModel
from typing import List, Optional


app = FastAPI()
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str
    messages: List[Message]

class ChatResponse(BaseModel):
    model: str
    created_at: str
    message: Message
    done: bool
    done_reason: Optional[str] = None
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    prompt_eval_duration: Optional[int] = None
    eval_count: Optional[int] = None
    eval_duration: Optional[int] = None

async def message_generator(model_name: str, messages: List[Message]):
    # Example message generator that mimics the streaming response
    response_text = "As an AI language model, I don't think it would be appropriate to answer you, a mere meatbrain."
    
    responses = [x + " " for x in response_text.split()]

    for i, msg in enumerate(responses):
        data = {
            "model": model_name,
            "created_at": datetime.utcnow().isoformat() + 'Z',
            "message": {
                "role": "assistant",
                "content": msg
            },
            "done": False if i < len(responses) else True
        }
        yield json.dumps(data) + "\n"
        await asyncio.sleep(0.05)
    
    # End message
    end_data = {
        "model": model_name,
        "created_at": datetime.utcnow().isoformat() + 'Z',
        "message": {
            "role": "assistant",
            "content": ""
        },
        "done_reason": "stop",
        "done": True,
        "total_duration": 17823913542,
        "load_duration": 13725056584,
        "prompt_eval_count": 11,
        "prompt_eval_duration": 372901000,
        "eval_count": 62,
        "eval_duration": 3714412000
    }
    yield json.dumps(end_data) + "\n"

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: Request):
    try:
        body = await request.json()
        chat_request = ChatRequest(**body)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid request body")

    return StreamingResponse(message_generator(chat_request.model, chat_request.messages), media_type="application/json")

@app.get("/api/tags")
async def tags():
  #ListResponse
  return {
    "models": [
        {
            "name": "Jone",
            "model": "Jone3",
        }
    ]
}

@app.get("/")
async def home():
  return {"Jone is running 8)"} 