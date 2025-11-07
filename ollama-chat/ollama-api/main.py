from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import httpx
import json
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

class PromptRequest(BaseModel):
    prompt: str
    model: str = "llama3.2:latest"

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/generate")
async def generate_text(request: PromptRequest):
    ollama_api_url = "http://localhost:11434/api/generate"
    payload = {
        "model": request.model,
        "prompt": request.prompt,
        "stream": True
    }

    async def stream_text():
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("POST", ollama_api_url, json=payload) as response:
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            chunk = data.get("response", "")
                            if chunk:
                                yield chunk
                        except json.JSONDecodeError:
                            continue

    return StreamingResponse(stream_text(), media_type="text/plain")
