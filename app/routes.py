from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import google.generativeai as genai
import logging
from typing import List, Dict
import markdown

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
    # Initialize all plan dictionaries at the start of the function
    workout_plans = {}
    meal_plans = {}
    shopping_list = ""

    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        # Generate workout plans
        for day in days:
            try:
                workout_prompt = f"""Create a {day} workout plan for:
                - Gender: {gender}
                - Age: {age} years
                - Weight: {weight}lbs
                - Height: {height}cm
                - Goal: {goal}

                Include only:
                1. 4-6 exercises with specific sets and reps
                2. Total workout duration
                3. A couple of key points to focus on during the workout, keep short and concise.

                Format as a clean, simple HTML list using <ul> tags. Keep descriptions brief and focused on the exercises only."""

                workout_response = model.generate_content(workout_prompt)
                workout_plans[day] = markdown.markdown(f"<ul>{workout_response.text}</ul>") if workout_response.text else "<ul><li>Rest Day</li></ul>"
            except Exception as e:
                logger.error(f"Error generating workout for {day}: {str(e)}")
                workout_plans[day] = "<ul><li>Error generating workout plan</li></ul>"

        # Generate meal plans
        for day in days:
            try:
                meal_prompt = f"""Create a {day} meal plan with {meals_per_day} meals.
                Person details:
                - Gender: {gender}
                - Age: {age} years
                - Weight: {weight}lbs
                - Height: {height}cm
                - Diet type: {diet}
                - Daily budget: ${food_budget/30:.2f}
                - Available cooking time: {cooking_time} minutes

                Format as HTML list items within <ul> tags."""

                meal_response = model.generate_content(meal_prompt)
                meal_plans[day] = markdown.markdown(f"<ul>{meal_response.text}</ul>") if meal_response.text else "<ul><li>Meal plan not available</li></ul>"
            except Exception as e:
                logger.error(f"Error generating meal plan for {day}: {str(e)}")
                meal_plans[day] = "<ul><li>Error generating meal plan</li></ul>"

        # Generate shopping list
        try:
            shopping_prompt = f"""Create a weekly shopping list:
            - Diet type: {diet}
            - Weekly budget: ${food_budget/4:.2f}

            Return only the items in this format:
            <h4>Category Name</h4>
            <ul>
            <li>Item 1</li>
            <li>Item 2</li>
            </ul>

            Keep it organized by category. Do not include any additional HTML tags or headers."""

            shopping_response = model.generate_content(shopping_prompt)
            shopping_list = markdown.markdown(shopping_response.text) if shopping_response.text else ""
        except Exception as e:
            logger.error(f"Error generating shopping list: {str(e)}")
            shopping_list = "<ul><li>Error generating shopping list</li></ul>"

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
                "workout_plan": workout_plans,  # Send empty/partial results instead of None
                "meal_plan": meal_plans,
                "shopping_list": shopping_list,
                "error": f"Error generating plan: {str(e)}"
            }
        )

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Fitness Plan - Results</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', path='/style.css') }}">
</head>
<body>
    <div class="container">
        <header class="results-header">
            <h1>Your Personalized Fitness Plan</h1>
            <a href="/" class="back-button">Create New Plan</a>
        </header>

        {% if error %}
        <div class="error-message">
            {{ error }}
        </div>
        {% endif %}

        {% if workout_plan %}
        <div class="results-content">
            <div class="user-details">
                <h2>Your Details</h2>
                <ul>
                    <li>Age: {{ age }} years</li>
                    <li>Weight: {{ weight }} lbs</li>
                    <li>Height: {{ height }} cm</li>
                    <li>Goal: {{ goal }}</li>
                    <li>Diet: {{ diet }}</li>
                    <li>Monthly Budget: ${{ food_budget }}</li>
                    <li>Meals per Day: {{ meals_per_day }}</li>
                    <li>Available Cooking Time: {{ cooking_time }} minutes</li>
                </ul>
            </div>

            <div class="plan-content">
                <h2 class="plan-section-title">Your Fitness Plan</h2>
                <div class="plan-sections">
                    <div class="workout-section">
                        <h3>Weekly Workout Schedule</h3>
                        <table class="plan-table">
                            <thead>
                                <tr>
                                    <th>Mon</th>
                                    <th>Tues</th>
                                    <th>Wed</th>
                                    <th>Thurs</th>
                                    <th>Fri</th>
                                    <th>Sat</th>
                                    <th>Sun</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>{{ workout_plan.Monday|safe }}</td>
                                    <td>{{ workout_plan.Tuesday|safe }}</td>
                                    <td>{{ workout_plan.Wednesday|safe }}</td>
                                    <td>{{ workout_plan.Thursday|safe }}</td>
                                    <td>{{ workout_plan.Friday|safe }}</td>
                                    <td>{{ workout_plan.Saturday|safe }}</td>
                                    <td>{{ workout_plan.Sunday|safe }}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    
                    <div class="nutrition-section">
                        <h3>Nutrition Plan</h3>
                        <p>Describe summary of nutrition plan</p>
                        <table class="plan-table">
                            <thead>
                                <tr>
                                    <th>Mon</th>
                                    <th>Tues</th>
                                    <th>Wed</th>
                                    <th>Thurs</th>
                                    <th>Fri</th>
                                    <th>Sat</th>
                                    <th>Sun</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>{{ meal_plan.Monday|safe }}</td>
                                    <td>{{ meal_plan.Tuesday|safe }}</td>
                                    <td>{{ meal_plan.Wednesday|safe }}</td>
                                    <td>{{ meal_plan.Thursday|safe }}</td>
                                    <td>{{ meal_plan.Friday|safe }}</td>
                                    <td>{{ meal_plan.Saturday|safe }}</td>
                                    <td>{{ meal_plan.Sunday|safe }}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <div class="shopping-section">
                        <h3>Shopping List</h3>
                        <div class="shopping-list-content">{{ shopping_list|safe }}</div>
                    </div>
                </div>
            </div>

            <div class="action-buttons">
                <button onclick="window.print()" class="print-button">Print Plan</button>
                <button onclick="location.href='/'" class="new-plan-button">Create New Plan</button>
            </div>
        </div>
        {% endif %}
    </div>
</body>
</html>





















