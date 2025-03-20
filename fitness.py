from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import google.generativeai as genai
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

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
        model = genai.GenerativeModel("gemini-1.5-pro")  # Changed from gemini-1.0-pro
        prompt = f"""
        Create a personalized fitness and nutrition plan for a {age}-year-old,
        weighing {weight}kg, height {height}cm. 
        Goal: {goal}.
        Dietary restrictions: {diet}.
        """
        response = model.generate_content(prompt)
        return templates.TemplateResponse("index.html", {"request": request, "plan": response.text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
