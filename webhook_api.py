from fastapi import FastAPI, HTTPException, Request
import requests
import os
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Leonardo AI configuration
LEONARDO_API_KEY = os.getenv("LEONARDO_API_KEY")
LEONARDO_API_BASE_URL = "https://cloud.leonardoapi.com/api/rest/v1"

@app.get("/")
def read_root():
    return {"message": "Bank Mega Image Generator API", "status": "running", "api_key_set": bool(LEONARDO_API_KEY)}

@app.post("/generate-image")
async def generate_image(request: Request):
    """
    Generate an image using the Leonardo AI API
    """
    
    # Parse JSON data from request body
    try:
        data = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON in request body")
    
    # Extract parameters from request data
    prompt = data.get("prompt")
    if not prompt:
        raise HTTPException(status_code=400, detail="prompt is required")
    
    model_id = data.get("model_id", "6bef9f1b-29cb-40c7-b9df-32b51c1f67d3")
    width = data.get("width", 512)
    height = data.get("height", 512)
    photo_real = data.get("photo_real", False)
    image_prompt_id = data.get("image_prompt_id")
    init_image_id = data.get("init_image_id")
    init_strength = data.get("init_strength", 0.5)
    
    if not LEONARDO_API_KEY:
        raise HTTPException(status_code=500, detail="API key not configured")
    
    headers = {
        "Authorization": f"Bearer {LEONARDO_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Prepare the payload based on the PhotoReal setting
    payload = {
        "prompt": prompt,
        "width": width,
        "height": height
    }
    
    # Add model ID
    payload["modelId"] = model_id
    
    # Add PhotoReal settings if enabled
    if photo_real:
        payload["photoReal"] = True
        payload["photoRealVersion"] = "v2"
        payload["alchemy"] = True
        payload["presetStyle"] = "CINEMATIC"
        
        # PhotoReal v2 requires compatible model (Leonardo Kino XL)
        if model_id == "6bef9f1b-29cb-40c7-b9df-32b51c1f67d3":
            payload["modelId"] = "aa77f04e-3eec-4034-9c07-d0f619684628"  # Leonardo Kino XL
    
    # Add reference image if provided
    if image_prompt_id:
        payload["imagePrompts"] = [{"id": image_prompt_id, "weight": 0.5}]
    
    # Add init image for image-to-image generation if provided
    if init_image_id:
        payload["init_image_id"] = init_image_id
        payload["init_strength"] = max(0.1, min(0.9, init_strength))  # Clamp between 0.1 and 0.9
    
    try:
        logger.info(f"Sending request to Leonardo API: {payload}")
        response = requests.post(
            f"{LEONARDO_API_BASE_URL}/generations",
            headers=headers,
            json=payload
        )
        
        response.raise_for_status()
        generation_data = response.json()
        logger.info(f"Generation initiated with ID: {generation_data['sdGenerationJob']['generationId']}")
        return generation_data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Leonardo API: {str(e)}")
        if hasattr(e, 'response') and e.response:
            error_detail = e.response.text
            status_code = e.response.status_code
        else:
            error_detail = str(e)
            status_code = 500
        
        raise HTTPException(status_code=status_code, detail=error_detail) 