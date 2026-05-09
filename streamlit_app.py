import streamlit as st
import datetime

# 1. Setup
st.set_page_config(page_title="HV Fishing Guide", page_icon="🎣")

# 2. Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["AI Fishing Guide", "Catch Tracker", "Learn Center"])

# 3. AI Guide Page
if page == "AI Fishing Guide":
    st.title("🎯 Pre-Trip Planner")
    
    species = st.multiselect("Target Species:", ["Bass", "Carp", "Striper", "Catfish"])
    lures = st.multiselect("Your Lures:", ["Senko", "Whopper Plopper", "Chatterbait", "Live Bait", "Crankbait"])
    dist = st.slider("Max Travel (miles):", 0, 100, 15)
    target_weight = st.select_slider("Target Size:", options=["Dinks", "Average", "Trophy"])
    location = st.text_input("Specific Spot:")

    if st.button("Generate Master Statement"):
        st.subheader("🔥 Your Master Plan")
        # Safety check to make sure list isn't empty
        spec_str = ", ".join(species) if species else "Fish"
        lure_str = ", ".join(lures) if lures else "your best lures"
        
        st.success(f"Focus on the edges at {location}. Use {lure_str} to target that {target_weight} {spec_str}.")

# 4. Catch Tracker Page
elif page == "Catch Tracker":
    st.title("🏆 Personal Catch Log")
    with st.form("catch_form", clear_on_submit=True):
        fish_type = st.selectbox("Species caught", ["Bass", "Carp", "Striper", "Catfish"])
        weight = st.number_input("Weight (lbs)", min_value=0.0)
        submitted = st.form_submit_button("Log Catch")
        if submitted:
            st.write(f"Logged a {weight}lb {fish_type}!")

# 5. Learn Center Page
elif page == "Learn Center":
    st.title("📚 Fishing Academy")
    topic = st.selectbox("What do you want to learn?", ["Texas Rig", "Palomar Knot"])
    if topic == "Texas Rig":
        st.write("1. Slide weight on line.2. Tie offset hook.3. Rig worm weedless.")
    elif topic == "Palomar Knot":
        st.write("1. Double 6 inches of line.2. Pass loop through eye.3. Tie overhand knot.")
