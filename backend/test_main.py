from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
# from ollama_client import query_ollama
# from logger import prompt_logger, periodic_health_logger
# from health import get_system_health
# from uploader import upload_logs_to_drive
# from config import settings

import asyncio
import os

app = FastAPI()

class PromptRequest(BaseModel):
    prompt: str

@app.get("/")
def root():
    print("[TEST BACKEND] GET / called")
    return {"status": "Test backend running"}

@app.get("/health")
def health_check():
    print("[TEST BACKEND] GET /health called")
    # health = get_system_health()
    # print(f"[TEST BACKEND] Health status: {health}")
    return {"status": "Health check placeholder"}

@app.post("/query")
async def handle_prompt(request: PromptRequest):
    prompt = request.prompt
    print(f"[TEST BACKEND] POST /query received prompt: {prompt}")
    # prompt_logger.info(f"[TEST BACKEND] Received prompt: {prompt}")

    try:
        # response = await query_ollama(prompt)
        # print(f"[TEST BACKEND] Model response: {response}")
        # prompt_logger.info(f"[TEST BACKEND] Model response: {response}")
        response = f"Echo: {prompt}"
        return {"response": response}
    except Exception as e:
        print(f"[TEST BACKEND] Error querying model: {e}")
        # prompt_logger.exception("[TEST BACKEND] Error querying model")
        raise HTTPException(status_code=500, detail="Error processing prompt")

@app.on_event("startup")
def ensure_log_dir():
    print("[TEST BACKEND] Ensuring log directory exists")
    # os.makedirs(settings.LOG_DIR, exist_ok=True)

@app.on_event("startup")
async def startup_tasks():
    print("[TEST BACKEND] Starting background tasks")
    # asyncio.create_task(upload_logs_to_drive())
    # asyncio.create_task(periodic_health_logger())

if __name__ == "__main__":
    import uvicorn
    print("[TEST BACKEND] Starting test backend server on 0.0.0.0:8001")
    uvicorn.run("test_main:app", host="0.0.0.0", port=8001, reload=True)
