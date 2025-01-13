from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from groq import Groq
from flask import Flask, request, jsonify, session

app = Flask(__name__)
app.secret_key = 'supersecretkey'
load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
client = Groq(api_key=GROQ_API_KEY)

def suggest_recipes_and_ingredients(invitees, cuisine_type, food_preference, meal_types, preferences, occasion):
    preferences_str = ', '.join(preferences) if preferences else "no specific preferences"
    meal_types_str = ', '.join(meal_types) if meal_types else "no specific meals"
    
    prompt = (
        f"Suggest recipes with ingredients listed first for {invitees} people. "
        f"Cuisine type: {cuisine_type}. Food preference: {food_preference}. "
        f"Meal types required: {meal_types_str}. Occasion: {occasion}. "
        f"Consider the following preferences: {preferences_str}. "
        f"For each meal, tell an intersting fact about that dish, list the ingredients first, followed by the preparation steps."
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama3-70b-8192",
    )
    
    response_content = chat_completion.choices[0].message.content
    
    return {
        "plan": response_content
    }

@app.route('/event_food_planning', methods=['POST'])
def event_food_planning():
    data = request.get_json()
    invitees = data.get('invitees')
    cuisine_type = data.get('cuisine_type')
    food_preference = data.get('food_preference')
    meal_types = data.get('meal_types')
    preferences = data.get('preferences')
    occasion = data.get('occasion')

    if invitees == "0":
        return jsonify({"error": "Please provide a valid number of invitees."}), 400

    recipe_data = suggest_recipes_and_ingredients(invitees, cuisine_type, food_preference, meal_types, preferences, occasion)

    return jsonify(recipe_data)
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/search"

client = Groq(api_key=GROQ_API_KEY)
app.secret_key = 'SunRaku'

def find_recipe_by_name(recipe_name):
    prompt = f"Find a detailed recipe for {recipe_name} with ingredients and instructions."
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama3-70b-8192",
    )

    response = chat_completion.choices[0].message.content
    
    try:
        if "Ingredients:" in response and "Instructions:" in response:
            recipe_info, rest = response.split("Ingredients:", 1)
            ingredients_section, recipe_section = rest.split("Instructions:", 1)
            recipe_info = recipe_info.strip()
            ingredients = ingredients_section.strip()
            instructions = recipe_section.strip()
        else:
            recipe_info = response.strip()
            ingredients = "Ingredients not explicitly mentioned."
            instructions = "Instructions not explicitly mentioned."
    except Exception as e:
        recipe_info = "Error in parsing recipe name."
        ingredients = "Error in parsing ingredients."
        instructions = "Error in parsing instructions."

    return recipe_info, ingredients, instructions
import requests
import requests
yurl = "https://www.googleapis.com/youtube/v3/search"
GOOGLE_API_KEY = "AIzaSyCVDoR3U-WDV-_DmeXlt76ubLeNTOw2n64"
yapi = "AIzaSyAmHt_sP0eyVNj-N2VnaGLXohYNuP-IdK8"
def find_youtube_tutorial(recipe_name):
    # Define parameters for YouTube API request
    params = {
        'part': 'snippet',
        'q': f"{recipe_name} recipe tutorial",
        'key': yapi,
        'maxResults': 3,
        'type': 'video'
    }
    
    # Make the API request
    response = requests.get(yurl, params=params)
    
    # Get the video items from the response
    videos = response.json().get('items', [])
    
    # Initialize a string to store the video links
    video_string = ""
    
    # Loop through the videos and extract details
    for video in videos:
        video_title = video['snippet']['title']
        video_id = video['id']['videoId']
        video_link = f"https://www.youtube.com/watch?v={video_id}"
        
        # Add the video title and link to the string
        video_string += f"{video_title}: {video_link}\n"
    
    # Return the final string with all video links
    return video_string



@app.route('/find_recipe', methods=['POST'])
def find_recipe():
    data = request.get_json()
    recipe_name = data.get('recipe_name')

    if not recipe_name:
        return jsonify({"error": "Please specify a recipe name"}), 400

    recipe_info, ingredients, instructions = find_recipe_by_name(recipe_name)
    youtube_links = find_youtube_tutorial(recipe_name)

    return jsonify({
        "recipe_name": recipe_info,
        "ingredients": ingredients,
        "instructions": instructions,
        "youtube_tutorials": youtube_links
    })




def suggest_cultural_dish(country, region=None):
    prompt = f"Suggest a single authentic dish from {country} cuisine and provide the ingredients."
    
    if region:
        prompt += f" Specifically from the region of {region}."

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama3-70b-8192",
    )

    response = chat_completion.choices[0].message.content
    
    if "Ingredients:" in response:
        dish_info, ingredients = response.split("Ingredients:", 1)
        dish_info = dish_info.strip()
        ingredients = ingredients.strip()
    else:
        dish_info = response.strip()
        ingredients = "Ingredients not explicitly mentioned."

    return (dish_info + " "  + ingredients)

def ans_followup(question, last_dish):
    prompt = f"Based on the dish: {last_dish}, can you answer the following question: {question}"
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama3-70b-8192",
    )

    return chat_completion.choices[0].message.content




@app.route('/explore_cuisine', methods=['POST'])
def explore_cuisine():
    data = request.get_json()
    country = data.get('country')
    region = data.get('region')

    if not country:
        return jsonify({"error": "Please specify a country"}), 400

    dish_info = suggest_cultural_dish(country, region)

    session['last_dish'] = dish_info

    return jsonify({
        "dish": dish_info
    })




@app.route('/ask_dish', methods=['POST'])
def ask_dish():
    data = request.get_json()
    question = data.get('question')

    if 'last_dish' not in session:
        return jsonify({"error": "No dish in context. Please request a dish first."}), 400

    last_dish = session['last_dish']

    answer_result = ans_followup(question, last_dish)

    return jsonify({"answer": answer_result})

############################################ MEAL PLAN ############################################

def generate_meal_plan(age, height, weight, days, food_preference, gender, diet_type, allergies, diseases, activity_level, meal_frequency):
    prompt = (
        f"Generate a meal plan for a {age}-year-old {gender} who is {height} cm tall and weighs {weight} kg. "
        f"They are following a {diet_type} diet for {days} days with a preference for {food_preference} food. "
        f"Activity level: {activity_level}. They prefer {meal_frequency} meals per day. "
        f"Allergies and restrictions: {allergies or 'None'}. Diseases: {diseases or 'None'}."
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama3-70b-8192",
    )

    return chat_completion.choices[0].message.content

@app.route('/generate_meal_plan', methods=['POST'])
def meal_plan():
    data = request.get_json()
    
    age = data.get('age')
    height = data.get('height')
    weight = data.get('weight')
    days = data.get('days')
    food_preference = data.get('food_preference',[])
    gender = data.get('gender')
    diet_type = data.get('diet_type')
    allergies = data.get('allergies')
    diseases = data.get('diseases')
    activity_level = data.get('activity_level')
    meal_frequency = data.get('meal_frequency')

    if not age or not height or not weight or not days or not food_preference or not gender or not diet_type or not activity_level or not meal_frequency:
        return jsonify({"error": "Please provide all the required fields"}), 400

    meal_plan_result = generate_meal_plan(age, height, weight, days, food_preference, gender, diet_type, allergies, diseases, activity_level, meal_frequency)
    print(meal_plan_result)
    return jsonify({"meal_plan": meal_plan_result})


from flask import Flask, request, jsonify
import os
import re
from dotenv import load_dotenv
from groq import Groq


def estimate_nutrition(dish_name, servings):
    prompt = (
        f"Provide the following nutritional information for {servings} servings of {dish_name}: "
        f"Provide each in the format 'Nutrient: value' with the values in standard units (g, mg). "
        f"Include ranges if applicable, and be as precise as possible based on typical ingredient quantities and portion sizes."
        f"Output in the format:\n"
        f"Total Calories: [value]\n"
        f"Carbohydrates: [value]g\n"
        f"Protein: [value]g\n"
        f"Calcium: [value]mg\n"
        f"Sugar: [value]g\n"
        f"Fat: [value]g"
    )

    chat_completion = client.chat.completions.create(
        messages=[{
            "role": "user",
            "content": prompt,
        }],
        model="llama3-70b-8192",
    )

    return chat_completion.choices[0].message.content

def extract_nutrition_info(response):
    nutrition_patterns = {
        "Total Calories": r"Total Calories: (\d+-\d+|\d+)",
        "Carbohydrates": r"Carbohydrates: (\d+-\d+)g",
        "Protein": r"Protein: (\d+-\d+)g",
        "Calcium": r"Calcium: (\d+-\d+)mg",
        "Sugar": r"Sugar: (\d+-\d+)g",
        "Fat": r"Fat: (\d+-\d+)g"
    }

    nutrition_info = {}
    for nutrient, pattern in nutrition_patterns.items():
        match = re.search(pattern, response)
        if match:
            value = match.group(1)
            if "Calories" in nutrient:
                nutrition_info[nutrient] = f"{value} kcal"
            elif "Calcium" in nutrient:
                nutrition_info[nutrient] = f"{value} mg"
            else:
                nutrition_info[nutrient] = f"{value} g"
        else:
            nutrition_info[nutrient] = "Not available"

    return nutrition_info

@app.route('/estimate_nutrition', methods=['POST'])
def nutrition_estimator():
    data = request.get_json()

    dish_name = data.get('dish_name')
    servings = data.get('servings')

    if not dish_name or not servings:
        return "Error: Please provide both the dish name and servings.", 400

    nutrition_response = estimate_nutrition(dish_name, servings)
    nutrition_result = extract_nutrition_info(nutrition_response)

    # Convert the nutrition_result dictionary to a string
    response_string = "\n".join([f"{key}: {value}" for key, value in nutrition_result.items()])

    return jsonify({"nutrition_info":response_string})



if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8000, debug=True)
