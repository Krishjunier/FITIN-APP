import streamlit as st
import pandas as pd
import numpy as np
import groq
import joblib
import os

# Load trained model and scaler
model_path = "Model/workout_recommender.pkl"

if os.path.exists(model_path):
    model = joblib.load(model_path)
else:
    st.error("Error: Model file not found!")

# Function to calculate BMI, BFP, and category
def calculate_bmi_bfp_category(weight, height, age, gender):
    bmi = weight / (height ** 2)
    if gender == "Male":
        bfp = (1.20 * bmi) + (0.23 * age) - 16.2
    else:
        bfp = (1.20 * bmi) + (0.23 * age) - 5.4

    # Categorizing BMI
    if bmi < 16:
        bmi_category = "Severe Thinness"
    elif 16 <= bmi < 17:
        bmi_category = "Moderate Thinness"
    elif 17 <= bmi < 18.5:
        bmi_category = "Mild Thinness"
    elif 18.5 <= bmi < 25:
        bmi_category = "Normal"
    elif 25 <= bmi < 30:
        bmi_category = "Overweight"
    elif 30 <= bmi < 35:
        bmi_category = "Obese"
    else:
        bmi_category = "Severe Obese"

    return round(bmi, 2), round(bfp, 2), bmi_category

# Function to generate workout plan using Groq API
def generate_workout(plan_id, fitness_goal):
    api_key = "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"
    client = groq.Client(api_key=api_key)

    prompt = f"Generate a detailed workout plan for someone assigned to exercise plan {plan_id} with the goal of {fitness_goal}."
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a fitness expert."},
            {"role": "user", "content": prompt},
        ]
    )
    return response.choices[0].message.content

# Streamlit UI
st.title("AI Personal Workout Recommender")

# User inputs
weight = st.number_input("Enter your weight (kg):", min_value=30.0, max_value=200.0, step=0.1)
height = st.number_input("Enter your height (m):", min_value=1.0, max_value=2.5, step=0.01)
age = st.number_input("Enter your age:", min_value=10, max_value=100, step=1)
gender = st.selectbox("Select your gender:", ["Male", "Female"])
fitness_goal = st.text_input("Enter your fitness goal (e.g., weight loss, muscle gain):")

if st.button("Get Workout Plan"):
    # Calculate BMI, BFP, and category
    bmi, bfp, bmi_category = calculate_bmi_bfp_category(weight, height, age, gender)

    # Display BMI and BFP results
    st.subheader("Your Fitness Analysis:")
    st.write(f"**BMI:** {bmi}")
    st.write(f"**Body Fat Percentage (BFP):** {bfp}")
    st.write(f"**BMI Category:** {bmi_category}")

    # Predict workout plan
    input_data = np.array([[weight, height, bmi, bfp, 0 if gender == "Male" else 1, age, 4]])
    predicted_plan = model.predict(input_data)[0]

    # Generate personalized plan
    personalized_plan = generate_workout(predicted_plan, fitness_goal)

    st.subheader("Your Personalized Workout Plan:")
    st.write(personalized_plan)
