import streamlit as st
import pandas as pd
import datetime

# --- APP CONFIG ---
st.set_page_config(page_title="HV Fishing Guide", page_icon="🎣")

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["AI Fishing Guide", "Catch Tracker", "Learn Center"])

# --- PAGE 1: AI FISHING GUIDE ---
if page == "AI Fishing Guide":
st.title("🎯 Pre-Trip Planner")
st.write("Fill out the details for your custom Master Statement.")

# Multi-select for Species and Lures
species = st.multiselect("What are we targeting today?", ["Bass", "Carp", "Striper", "Catfish"])
lures = st.multiselect("What's in your tackle box?", ["Senko", "Whopper Plopper", "Chatterbait", "Live Bait", "Crankbait"])

# Distance and Weight Sliders
dist = st.slider("How far are you willing to travel (miles)?", 0, 100, 15)
target_weight = st.select_slider("Target Fish Size", options=["Dinks", "Average", "Trophy Lunker"])

# Text input for Location
location = st.text_input("Enter your specific spot (e.g., Pennypack Creek):")

if st.button("Generate Master Statement"):
# This is where your AI logic lives
st.subheader("🔥 Your Master Plan")
st.success(f"With the current pressure dropping, focus on the **edges** at {location}. Since you have {', '.join(lures)}, start with the Whopper Plopper for that {target_weight} Bass. Best window: 5:30 PM - 7:45 PM.")

# --- PAGE 2: CATCH TRACKER ---
elif page == "Catch Tracker":
st.title("🏆 Personal Catch Log")
with st.form("catch_form", clear_on_submit=True):
fish_type = st.selectbox("Species caught", ["Bass", "Carp", "Striper", "Catfish"])
weight = st.number_input("Weight (lbs)", min_value=0.0)
photo = st.file_uploader("Upload a trophy photo")
submitted = st.form_submit_button("Log Catch")

if submitted:
st.write(f"Logged a {weight}lb {fish_type} on {datetime.date.today()}!")

# --- PAGE 3: LEARN CENTER ---
elif page == "Learn Center":
st.title("📚 Fishing Academy")
topic = st.selectbox("What do you want to learn?", ["Texas Rig", "Palomar Knot", "Reading Water"])

if topic == "Texas Rig":
st.write("1. Slide a bullet weight onto the line.")
st.write("2. Tie on an offset worm hook.")
st.write("3. Pierce the head of the worm and pull through.")
st.video("https://www.youtube.com/watch?v=ZpYV_r6pCfs") # Example link