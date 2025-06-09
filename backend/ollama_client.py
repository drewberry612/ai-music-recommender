import httpx

OLLAMA_URL = "http://localhost:11434/api/generate"  # Default Ollama endpoint
MODEL_NAME = "mistral"  # Adjust based on your setup

async def query_ollama(prompt: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        return response.json().get("response", "")
