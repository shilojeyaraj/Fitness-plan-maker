from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import google.generativeai as genai
import logging
from typing import List, Dict
import markdown
import asyncio
from concurrent.futures import ThreadPoolExecutor

router = APIRouter()
templates = Jinja2Templates(directory="templates")
logger = logging.getLogger(__name__)

@router.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/generate_plan", response_class=HTMLResponse)
async def generate_fitness_plan(
    request: Request,
    gender: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    height: float = Form(...),
    goal: str = Form(...),
    diet: str = Form(...),
    food_budget: int = Form(...),
    meals_per_day: int = Form(...),
    cooking_time: int = Form(...)
):
    workout_plans = {}
    meal_plans = {}
    shopping_list = ""
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    async def generate_workout(day):
        try:
            model = genai.GenerativeModel('gemini-1.5-pro')
            workout_prompt = f"""Create a {day} workout plan for:
            - Gender: {gender}
            - Age: {age} years
            - Weight: {weight}lbs
            - Height: {height}cm
            - Goal: {goal}

            Return only the exercises in this format:
            <ul>
            <li>Main workout: [4-5 exercises with sets and reps]</li>
            <li>Duration: [total time]</li>
            <li>Key things to focus on during this workout: keep short and concise</li>
            </ul>"""

            workout_response = model.generate_content(workout_prompt)
            return day, workout_response.text if workout_response.text else "<ul><li>Rest Day</li></ul>"
        except Exception as e:
            logger.error(f"Error generating workout for {day}: {str(e)}")
            return day, "<ul><li>Error generating workout plan</li></ul>"

    async def generate_meal(day):
        try:
            model = genai.GenerativeModel('gemini-1.5-pro')
            meal_prompt = f"""Create a {day} meal plan with {meals_per_day} meals.
            Person details:
            - Gender: {gender}
            - Age: {age} years
            - Weight: {weight}lbs
            - Height: {height}cm
            - Diet type: {diet}
            - Daily budget: ${food_budget/30:.2f}
            - Available cooking time: {cooking_time} minutes

            Return only the meals in this format, try to keep meals suitable for the time of day they would be consumed:
            <ul>
            <li>Meal 1: meal name
            Ingredients- 
            Instructions- </li>
             <li>Meal 2: meal name
            Ingredients- 
            Instructions- </li>
            </ul>"""

            meal_response = model.generate_content(meal_prompt)
            return day, [{"description": f"<ul>{meal_response.text}</ul>" if meal_response.text else "<ul><li>Meal plan not available</li></ul>"}]
        except Exception as e:
            logger.error(f"Error generating meal plan for {day}: {str(e)}")
            return day, [{"description": "<ul><li>Error generating meal plan</li></ul>"}]

    async def generate_shopping():
        try:
            model = genai.GenerativeModel('gemini-1.5-pro')
            shopping_prompt = f"""Create a weekly shopping list:
            - Diet type: {diet}
            - Weekly budget: ${food_budget/4:.2f}

            Format as HTML with category headers (h4) and list items along with estimated price, and total price at the bottom"""

            shopping_response = model.generate_content(shopping_prompt)
            return shopping_response.text if shopping_response.text else ""
        except Exception as e:
            logger.error(f"Error generating shopping list: {str(e)}")
            return "<ul><li>Error generating shopping list</li></ul>"

    try:
        # Create tasks for all generations
        workout_tasks = [generate_workout(day) for day in days]
        meal_tasks = [generate_meal(day) for day in days]
        shopping_task = generate_shopping()

        # Run all tasks concurrently
        workout_results, meal_results, shopping_list = await asyncio.gather(
            asyncio.gather(*workout_tasks),
            asyncio.gather(*meal_tasks),
            shopping_task
        )

        # Process results
        for day, workout in workout_results:
            workout_plans[day] = workout

        for day, meal in meal_results:
            meal_plans[day] = meal

        return templates.TemplateResponse(
            "results.html",
            {
                "request": request,
                "workout_plan": workout_plans,
                "meal_plan": meal_plans,
                "shopping_list": shopping_list,
                "gender": gender,
                "age": age,
                "weight": weight,
                "height": height,
                "goal": goal,
                "diet": diet,
                "food_budget": food_budget,
                "meals_per_day": meals_per_day,
                "cooking_time": cooking_time,
                "error": None
            }
        )
    except Exception as e:
        logger.error(f"Error generating plan: {str(e)}", exc_info=True)
        return templates.TemplateResponse(
            "results.html",
            {
                "request": request,
                "workout_plan": workout_plans,
                "meal_plan": meal_plans,
                "shopping_list": shopping_list,
                "error": f"Error generating plan: {str(e)}"
            }
        )














