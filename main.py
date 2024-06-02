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
# from google_auth_oauthlib.flow import InstalledAppFlow
# import google.oauth2.credentials
# from google.auth.transport.requests import Request

app = FastAPI()
dotenv.load_dotenv()
# cred_path = 'secret.json'
# with open(cred_path) as json_file:
#     credentials_json = json.load(json_file)

# SCOPES = ['https://www.googleapis.com/auth/assistant-sdk-prototype']

# flow = InstalledAppFlow.from_client_config(credentials_json, SCOPES)
# credentials = flow.run_local_server(port=0)

# token_path = 'token.json'
# with open(token_path, 'w') as token:
    # token.write(credentials.to_json())

# with open(token_path) as token_file:
    # credentials_data = json.load(token_file)
    # credentials = google.oauth2.credentials.Credentials(
        # token=credentials_data['token'],
        # refresh_token=credentials_data['refresh_token'],
        # token_uri=credentials_data['_token_uri'],
        # client_id=credentials_data['client_id'],
        # client_secret=credentials_data['client_secret']
    # )

# Refresh credentials if expired
# if credentials.expired and credentials.refresh_token:
#     credentials.refresh(Request())
#     with open(token_path, 'w') as token_file:
#         token_file.write(credentials.to_json())

# Initialize the Google Assistant
# assistant = Assistant(credentials, 'my-device')

# def send_command(command):
#     with assistant_helpers.Conversation(assistant) as conversation:
#         conversation.send_text_query(command)
#         response = conversation.get_response()
#         print('Received response: ', response)

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

def play_music(query):
    print("playing music")
    send_command(f"Play {query} on youtube music")
    print(query)

def start_timer(args):
    print("starting timer")
    send_command(f"set a timer: {args}")
    print(args)

def jone(conversation_history):
    """
      Here we can do things like:
      - choose to use a smarter model
      - do some logical reasoning
      - generating a few responses and rating them, choosing the best one
      - web search
      - ...start a timer
      - ...play some music
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
        
        tool_name = tool_called.split('(')[0].strip()
        args = tool_called.split('(')[1].strip().rstrip(')')
        if tool_name == "play_music":
            play_music(args)
            return "Playing music"
        if tool_name == "start_timer":
            start_timer(args)
            return "Timer set"  
        response = f"TOOL CALLED: {tool_name}, ARGUMENTS: {args}"

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

@app.post("/api/chat/completions", response_model=ChatResponse)
async def chat_endpoint(request: Request):
    try:
        body = await request.json()
        chat_request = ChatRequest(**body)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid request body")
    #{"model":"Jone3","keep_alive":"5m","options":{},"messages":[{"role":"user","content":"\ntest","images":[]}]}
    return StreamingResponse(message_generator(chat_request.model, chat_request.messages), media_type="application/json")


@app.get("/api/version")
async def version():
    return {"version": "3.0"}

# @app.get("/api/tags/{url_idx}")
# async def tags(url_idx: str = None, user: dict = {}):
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
            "families": "",
            "parameter_size": "70B",
            "quantization_level": "Q4_0"
          }
        }
    ]
}

@app.get("/")
async def home():
  return {"Jone is running 8)"} 