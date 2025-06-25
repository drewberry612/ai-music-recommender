from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ollama_client import query_ollama
from logger import query_logger, periodic_health_logger
from health import get_system_health
#from uploader import upload_logs_to_drive
from config import settings
import uvicorn

import asyncio
import os

app = FastAPI()

class QueryRequest(BaseModel):
    query: str

@app.get("/")
def root():
    return {"status": "Wavelength backend running"}

@app.get("/health")
def health_check():
    return get_system_health()

@app.post("/query")
async def handle_query(request: QueryRequest):
    query = request.query
    query_logger.info(f"Received query: {query}")

    try:
        response = await query_ollama(query)
        query_logger.info(f"Model response: {response}")
        return {"response": response}
    except Exception as e:
        query_logger.exception("Error querying model")
        raise HTTPException(status_code=500, detail="Error processing query")

@app.on_event("startup")
def ensure_log_dir():
    os.makedirs(settings.LOG_DIR, exist_ok=True)

async def warm_up_model():
    try:
        response = await query_ollama("ping")
        print("Model warm up successful")
    except Exception as e:
        print("Failed to warm up Ollama model on startup")

@app.on_event("startup")
async def startup_tasks():
    asyncio.create_task(warm_up_model())
    #asyncio.create_task(upload_logs_to_drive())  # make sure uploader handles both files
    asyncio.create_task(periodic_health_logger())

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)