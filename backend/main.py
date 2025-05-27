from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ollama_client import query_ollama
from logger import prompt_logger, periodic_health_logger
from health import get_system_health
from uploader import upload_logs_to_drive
from config import settings

import asyncio
import os

app = FastAPI()

class PromptRequest(BaseModel):
    prompt: str

@app.get("/")
def root():
    return {"status": "Wavelength backend running"}

@app.get("/health")
def health_check():
    return get_system_health()

@app.post("/query")
async def handle_prompt(request: PromptRequest):
    prompt = request.prompt
    prompt_logger.info(f"Received prompt: {prompt}")

    try:
        response = await query_ollama(prompt)
        prompt_logger.info(f"Model response: {response}")
        return {"response": response}
    except Exception as e:
        prompt_logger.exception("Error querying model")
        raise HTTPException(status_code=500, detail="Error processing prompt")

@app.on_event("startup")
def ensure_log_dir():
    os.makedirs(settings.LOG_DIR, exist_ok=True)

@app.on_event("startup")
async def startup_tasks():
    asyncio.create_task(upload_logs_to_drive())  # make sure uploader handles both files
    asyncio.create_task(periodic_health_logger())
