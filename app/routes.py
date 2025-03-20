from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import google.generativeai as genai
import logging

router = APIRouter()
templates = Jinja2Templates(directory="templates")
logger = logging.getLogger(__name__)

@router.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/generate_plan", response_class=HTMLResponse)
async def generate_fitness_plan(
    request: Request,
    age: int = Form(...),
    weight: float = Form(...),
    height: float = Form(...),
    goal: str = Form(...),
    diet: str = Form(...),
    food_budget: int = Form(...),
    meals_per_day: int = Form(...),
    cooking_time: int = Form(...),
    gym_access: str = Form(...),
    equipment: str = Form(...),
    workout_location: str = Form(...),
    time_available: int = Form(...)
):
    try:
        logger.info(f"Received request with age={age}, weight={weight}, height={height}, goal={goal}")
        
        model = genai.GenerativeModel('gemini-1.5-pro')
        logger.info("Model initialized")
        
        prompt = f"""
        Create a personalized fitness and nutrition plan for someone with the following details:

        PERSONAL INFORMATION:
        - Age: {age} years old
        - Weight: {weight}kg
        - Height: {height}cm
        - Goal: {goal}
        - Dietary restrictions: {diet}

        NUTRITION PREFERENCES:
        - Monthly food budget: ${food_budget}
        - Preferred meals per day: {meals_per_day}
        - Available cooking time: {cooking_time} minutes per day

        WORKOUT RESOURCES:
        - Gym access: {gym_access}
        - Available equipment: {equipment}
        - Preferred workout location: {workout_location}
        - Time available per session: {time_available} minutes

        Please provide a detailed plan including:
        1. Weekly workout schedule tailored to their available time and resources
        2. Specific exercises with sets and reps, using only their available equipment
        3. Alternative exercises when equipment isn't available
        4. Detailed meal plan considering:
           - Their monthly budget (${food_budget})
           - Required meal prep time ({cooking_time} min/day)
           - {meals_per_day} meals per day
           - Their dietary restrictions
        5. Shopping list with estimated costs
        6. Meal prep strategies to save time
        7. Tips for making the most of their workout environment
        8. Progressive overload suggestions based on their resources

        Format the response clearly with headers and bullet points.
        Include a weekly grocery list with estimated costs to help them stay within budget.
        """
        
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        if hasattr(response, 'text') and response.text:
            return templates.TemplateResponse(
                "results.html", 
                {
                    "request": request,
                    "plan": response.text,
                    "age": age,
                    "weight": weight,
                    "height": height,
                    "goal": goal,
                    "diet": diet,
                    "food_budget": food_budget,
                    "meals_per_day": meals_per_day,
                    "cooking_time": cooking_time,
                    "gym_access": gym_access,
                    "equipment": equipment,
                    "workout_location": workout_location,
                    "time_available": time_available,
                    "error": None
                }
            )
        else:
            return templates.TemplateResponse(
                "results.html", 
                {
                    "request": request,
                    "error": "No response generated from the AI model"
                }
            )
            
    except Exception as e:
        logger.error(f"Error generating plan: {str(e)}", exc_info=True)
        return templates.TemplateResponse(
            "results.html", 
            {
                "request": request,
                "error": f"Error generating plan: {str(e)}"
            }
        )




