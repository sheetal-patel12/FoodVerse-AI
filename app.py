import os
import sqlite3
import base64
from io import BytesIO
from flask import Flask, render_template, request
from dotenv import load_dotenv
from PIL import Image
from google import genai
from google.genai import types

load_dotenv()

key = os.getenv("GEMINI_API_KEY", "").strip()

client = None

if key:
    client = genai.Client(api_key=key)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

DB = "data/foodverse.db"
os.makedirs("data", exist_ok=True)


def init_db():
    with sqlite3.connect(DB) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS food_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                food_name TEXT,
                result TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

def save_history(name, result):
    with sqlite3.connect(DB) as con:
        con.execute(
            "INSERT INTO food_history (food_name, result) VALUES (?, ?)",
            (name, result)
        )

def get_history():
    with sqlite3.connect(DB) as con:
        con.row_factory = sqlite3.Row
        return con.execute(
            "SELECT * FROM food_history ORDER BY id DESC LIMIT 10"
        ).fetchall()

def analyze_food(name, image_bytes=None):
    food = (name or "").strip()
    search_name = food.casefold()

    if not food:
        return (
            "Please enter a food name.\n"
            "Example: Pizza, Burger, Apple or Dal."
        )

    # Offline demo nutrition database
    foods = {
        "pizza": ("1 medium slice", 285, 12, 36, 10),
        "burger": ("1 medium burger", 295, 17, 30, 12),
        "apple": ("1 medium apple", 95, 0.5, 25, 0.3),
        "banana": ("1 medium banana", 105, 1.3, 27, 0.4),
        "rice": ("1 cup cooked", 205, 4.3, 45, 0.4),
        "dal": ("1 cup cooked", 180, 10, 26, 4),
        "roti": ("1 medium roti", 110, 3, 20, 2.5),
        "salad": ("1 bowl", 80, 2, 12, 3),
        "pasta": ("1 cup cooked", 220, 8, 43, 1),
        "sandwich": ("1 medium sandwich", 300, 12, 35, 11),
        "paneer": ("100 grams", 265, 18, 4, 20),
        "egg": ("1 large egg", 78, 6.3, 0.6, 5.3),        
        "idli": ("2 medium pieces", 120, 4, 26, 0.5),
        "dosa": ("1 medium plain dosa", 168, 4, 28, 4),
        "poha": ("1 bowl", 250, 5, 45, 7),
        "samosa": ("1 medium piece", 260, 4, 30, 14),
        "biryani": ("1 cup", 290, 12, 38, 10),
        "chole": ("1 cup", 270, 14, 45, 4),
        "curd": ("100 grams", 61, 3.5, 4.7, 3.3),
        "milk": ("1 glass, 250 ml", 150, 8, 12, 8),
        "oats": ("1 bowl cooked", 150, 5, 27, 3),
        "orange": ("1 medium orange", 62, 1.2, 15.4, 0.2),
        "fries": ("100 grams", 312, 3.4, 41, 15),

    }

    matched_food = next(
        (item for item in foods if item in search_name),
        None
    )

    if matched_food is None:
        return (
            f"Food: {food.title()}\n"
            "Mode: Offline Demo\n\n"
            "No nutrition entry is available for this food yet.\n"
            "Try Pizza, Burger, Apple, Banana, Rice, Dal, "
            "Roti, Salad, Pasta, Sandwich, Paneer or Egg."
        )

    serving, calories, protein, carbs, fat = foods[matched_food]

    result = (
        f"Food: {food.title()}\n"
        "Analysis Mode: Offline Demo\n\n"
        f"Estimated Serving: {serving}\n"
        f"Calories: {calories} kcal\n"
        f"Protein: {protein} g\n"
        f"Carbohydrates: {carbs} g\n"
        f"Fat: {fat} g\n\n"
        "Nutrition values are estimates and may vary by recipe "
        "and serving size."
    )

    if image_bytes:
        result += (
            "\n\nNote: Offline Demo uses the entered food name. "
            "It does not identify food from the uploaded image."
        )

    return result


@app.route("/", methods=["GET", "POST"])
def home_page():
    result = ""
    food_name = ""

    if request.method == "POST":
        food_name = (
            request.form.get("food_name", "").strip()
            or request.form.get("food", "").strip()
            or request.form.get("name", "").strip()
        )

        if not food_name:
            food_name = next(
                (v.strip() for v in request.form.values() if v.strip()),
                ""
            )

        if food_name:
            result = analyze_food(food_name)
            save_history(food_name, result)

    history = get_history()

    return render_template(
        "index.html",
        result=result,
        history=history,
        food_name=food_name
    )



@app.route("/health")
def health():
    return "FoodVerse is running!"


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5001)
    