from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import google.generativeai as genai
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()
GENAI_API_KEY = os.getenv("GENAI_API_KEY")

if not GENAI_API_KEY:
    raise ValueError("GENAI_API_KEY not found in environment variables")

# Configure Gemini API
genai.configure(api_key=GENAI_API_KEY)

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

# Set up templates
templates = Jinja2Templates(directory="templates")

# Add a root endpoint
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# User input model
class UserData(BaseModel):
    age: int
    weight: float
    height: float
    goal: str
    dietary_restrictions: str

# AI-generated fitness plan
@app.post("/generate_plan", response_class=HTMLResponse)
async def generate_fitness_plan(
    request: Request,
    age: int = Form(...),
    weight: float = Form(...),
    height: float = Form(...),
    goal: str = Form(...),
    diet: str = Form(...)
):
    try:
        logger.info(f"Received request with age={age}, weight={weight}, height={height}, goal={goal}")
        
        # Initialize the model
        model = genai.GenerativeModel('gemini-1.5-pro')  # Changed from gemini-1.0-pro
        logger.info("Model initialized")
        
        prompt = f"""
        Create a personalized fitness and nutrition plan for a {age}-year-old,
        weighing {weight}lbs, height {height}cm. 
        Goal: {goal}.
        Dietary restrictions: {diet}.
        Please provide:
        1. Weekly workout schedule
        2. Nutrition guidelines
        3. Specific exercises with sets and reps
        4. Diet recommendations considering the restrictions
        """
        
        logger.info("Generating content...")
        response = model.generate_content(prompt)
        logger.info(f"Response received: {response}")
        
        if hasattr(response, 'text') and response.text:
            logger.info("Successfully generated plan")
            return templates.TemplateResponse(
                "index.html", 
                {
                    "request": request, 
                    "plan": response.text,
                    "error": None
                }
            )
        else:
            logger.error("No response text generated")
            return templates.TemplateResponse(
                "index.html", 
                {
                    "request": request, 
                    "plan": None,
                    "error": "No response generated from the AI model"
                }
            )
            
    except Exception as e:
        logger.error(f"Error generating plan: {str(e)}", exc_info=True)
        return templates.TemplateResponse(
            "index.html", 
            {
                "request": request, 
                "plan": None,
                "error": f"Error generating plan: {str(e)}"
            }
        )

