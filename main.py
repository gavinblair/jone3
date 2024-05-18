from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from datetime import datetime
import asyncio
import json
from pydantic import BaseModel
from typing import List, Optional
# from langchain_groq.chat_models import ChatGroq
from langchain_groq import ChatGroq
import dotenv
import os

app = FastAPI()
dotenv.load_dotenv()

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

def jone(conversation_history):
    """
      Here we can do things like:
      - choose to use a smarter model
      - do some logical reasoning
      - generating a few responses and rating them, choosing the best one
      - web search
      - start a timer
      - play some music
      - change the lights
      - write, test, rewrite and run code (by sending to a secure code container like agentrun)
        
    """
    model = ChatGroq(
      # model_name="llama3-70b-8192",
      model_name="llama3-8b-8192",
      api_key = os.environ["groq_api_key"]
    )
    
    system_message = "SYSTEM: You are JONE, a helpful assistant.\n"
    tools = """
      TOOLS: As an assistant you have access to the following tools to help answer the user, just call them like functions:
      - {{web_search(query)}}
      - {{start_timer(duration)}}
      - {{play_music(query)}}
      - {{just_reply(message_to_user)}} (default)
      TOOLS: If you choose to use a tool, you don't need to say anything else.
    """
    response = model.invoke(system_message+tools+conversation_history).content

    #any tools called?
    if "{{" in response:
        start_of_tool = response.index("{{")
        end_of_tool = response.index("}}")
        tool_called = response[start_of_tool+2:end_of_tool]
        response = f"A tool is being used: {tool_called}"

    return response

async def message_generator(model_name: str, messages: List[Message]):
    conversation_history =  ""
    for i, msg in enumerate(messages):
        if msg.role == 'user':
            conversation_history += "\nuser: "
        else:
            conversation_history += "\nassistant: "
        conversation_history += msg.content

    response_text = jone(conversation_history)

    # response_text = "As an AI language model, I don't think it would be appropriate to answer you, a mere meatbrain."
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
        # await asyncio.sleep(0.000005)
    
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
    #{"model":"Jone3","keep_alive":"5m","options":{},"messages":[{"role":"user","content":"\ntest","images":[]}]}
    return StreamingResponse(message_generator(chat_request.model, chat_request.messages), media_type="application/json")

@app.get("/api/tags")
async def tags():
  #ListResponse
  return {
    "models": [
        {
          "name": "Jone3",
          "model": "Jone3",
          "modified_at": "2024-04-15T14:56:49.277302595-07:00",
          "size": 7365960935,
          "digest": "9f438cb9cd581fc025612d27f7c1a6669ff83a8bb0ed86c94fcf4c5440555697",
          "details": {
            "format": "gguf",
            "family": "llama",
            "families": null,
            "parameter_size": "70B",
            "quantization_level": "Q4_0"
          }
        }
    ]
}

@app.get("/")
async def home():
  return {"Jone is running 8)"} 