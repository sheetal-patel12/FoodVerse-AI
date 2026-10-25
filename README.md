# FoodVerse

FoodVerse is a Flask-based food nutrition explorer project.

## Features

- Enter a food name to view nutrition estimates
- Calories, protein, carbohydrates and fat information
- Recent analysis history using SQLite
- Responsive web interface
- Offline demo mode; no paid AI API is required

## Technologies Used

- Python
- Flask
- SQLite
- HTML
- CSS
- JavaScript

## Setup on Windows

1. Install Python.
2. Open CMD inside the project folder.
3. Create a virtual environment:

   python -m venv .venv

4. Activate it:

   .venv\Scripts\activate

5. Install dependencies:

   python -m pip install -r requirements.txt

6. Start the application:

   python -m flask --app app run --debug --port 5001

7. Open in your browser:

   http://127.0.0.1:5001

## Important Notes

This version uses predefined nutrition estimates.
It does not perform real AI food recognition.
Nutrition values are approximate and may vary by serving size.