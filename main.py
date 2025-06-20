import os
import uvicorn
from fastapi import FastAPI, HTTPException, Request
import requests

app = FastAPI()

LEONARDO_API_KEY = os.getenv("LEONARDO_API_KEY")
LEONARDO_API_BASE_URL = "https://cloud.leonardoapi.com/api/rest/v1"

@app.get("/")
def read_root():
    return {"message": "Bank Mega Image Generator API", "status": "running", "api_key_set": bool(LEONARDO_API_KEY)}

@app.post("/generate-image")
async def generate_image(request: Request):
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON in request body")
    
    prompt = data.get("prompt")
    if not prompt:
        raise HTTPException(status_code=400, detail="prompt is required")
    
    if not LEONARDO_API_KEY:
        raise HTTPException(status_code=500, detail="API key not configured")
    
    model_id = data.get("model_id", "6bef9f1b-29cb-40c7-b9df-32b51c1f67d3")
    width = data.get("width", 512)
    height = data.get("height", 512)
    
    payload = {
        "prompt": prompt,
        "modelId": model_id,
        "width": width,
        "height": height
    }
    
    headers = {
        "Authorization": f"Bearer {LEONARDO_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{LEONARDO_API_BASE_URL}/generations",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
