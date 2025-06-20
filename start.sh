#!/bin/bash

# Update system packages
apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Start the FastAPI application
uvicorn rnd_smoothen2:app --host 0.0.0.0 --port 8000 