from fastapi import FastAPI, Body
import uvicorn

app = FastAPI()

@app.post("/v1/completions")
async def completions(
    prompt: str = Body(..., embed=True),
    max_tokens: int = 256,
    temperature: float = 1.0,
    top_p: float = 1.0,
    frequency_penalty: float = 0.0,
    presence_penalty: float = 0.0,
    stop: str = None,
  ):
  return {"choices": [{"text": "Hello World"}]}#, "index": 0, "logprobs": {"token_logprobs": [1.0], "tokens": ["Hello World"]}, "finish_reason": "stop"}]}


@app.get("/api/tags")
async def tags():
  return {"tags"}

@app.post("/api/chat")
async def chat():
  return {"chat"}

@app.post("/api/generate")
async def generate():
  return {"generate"}


@app.get("/")
async def home():
  return {"Jone is running 8)"} 