from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os
import logging


def create_app():
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Configure Gemini API
    genai_api_key = os.getenv("GENAI_API_KEY")
    if not genai_api_key:
        raise ValueError("GENAI_API_KEY not found in environment variables")
    genai.configure(api_key=genai_api_key)
    
    app = FastAPI()
    
    # Enable CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Serve static files
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # Import routes
    from app.routes import router
    app.include_router(router)
    
    return app