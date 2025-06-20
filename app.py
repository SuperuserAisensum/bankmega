import os
import uvicorn
from fastapi import FastAPI, HTTPException, Request
import requests

app = FastAPI()

LEONARDO_API_KEY = os.getenv("LEONARDO_API_KEY")
LEONARDO_API_BASE_URL = "https://cloud.leonardoapi.com/api/rest/v1"

@app.get("/")
def read_root():
    return {"message": "Bank Mega Image Generator API", "status": "running"}

@app.post("/generate-image")
async def generate_image(request: Request):
    try:
        data = await request.json()
        prompt = data.get("prompt")
        if not prompt:
            raise HTTPException(status_code=400, detail="prompt is required")
        
        if not LEONARDO_API_KEY:
            raise HTTPException(status_code=500, detail="API key not configured")
        
        payload = {
            "prompt": prompt,
            "modelId": data.get("model_id", "6bef9f1b-29cb-40c7-b9df-32b51c1f67d3"),
            "width": data.get("width", 512),
            "height": data.get("height", 512)
        }
        
        headers = {
            "Authorization": f"Bearer {LEONARDO_API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(f"{LEONARDO_API_BASE_URL}/generations", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
