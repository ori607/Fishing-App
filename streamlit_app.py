import streamlit as st
import random
from datetime import datetime

# --- DATABASE: Spot Name: [Species, Distance, MaxWeight, Quality, Tip, CoverType, WaterType]
# WaterType: "Fresh" or "Salt" (Crucial for Tides/SST/Chlorophyll)
SITES = {
    "Quarry Road Pond (Bryn Athyn)": ["Bass", 0.1, 6, 9, "Private feel. Focus on the steep drop-offs.", "Rocks", "Fresh"],
    "Mason's Mill Pond": ["Bass", 3, 5, 4, "Heavy vegetation in summer.", "LilyPads", "Fresh"],
    "Island Beach State Park": ["Striper", 82, 50, 10, "Look for 'cuts' in the sand bars.", "Open", "Salt"],
    "Cape May Inlet": ["Shark", 95, 150, 6, "Deep water near the mouth.", "Current", "Salt"],
    "Susquehanna River": ["Catfish", 85, 50, 10, "Heavy current; find the deep holes.", "Current", "Fresh"]
}

if 'profile' not in st.session_state:
    st.session_state['profile'] = {'lures': [], 'rod_type': "Medium", 'line_type': "12lb Mono"}

# --- MAIN NAVIGATION ---
st.title("🎣 FishAI: Tactical Command")
menu = st.tabs(["Strategy Planner", "Advanced Trip Analysis", "Learn Center"])

# --- TAB 1: STRATEGY PLANNER ---
with menu[0]:
    species = st.selectbox("Target Fish", ["Bass", "Striper", "Shark", "Catfish"])
    max_dist = st.number_input("Max Miles", value=50)
    target_lb = st.slider("Target Weight", 1, 100, 5)
    
    matches = [n for n, d in SITES.items() if d[0] == species and d[1] <= max_dist and d[2] >= target_lb]
    
    if matches:
        selected_spot = st.selectbox("Select Location for Tactical Analysis:", matches)
        st.success(f"Selected: {selected_spot}")
    else:
        st.error("No spots match. Adjust distance/weight.")
        selected_spot = None

# --- TAB 2: ADVANCED TRIP ANALYSIS ---
with menu[1]:
    if not selected_spot:
        st.warning("Please select a location in the Strategy Planner first!")
    else:
        st.header(f"📊 Tactical Briefing: {selected_spot}")
        
        # Simulate Environmental Data Fetch
        water_type = SITES[selected_spot][6]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Moon Phase", "Waxing Gibbous", "High Activity")
            st.metric("SST (Water Temp)", "64.2°F", "+1.2°")
        with col2:
            st.metric("Chlorophyll-a", "2.1 mg/m³", "Bait Present")
            st.metric("Barometer", "30.01 inHg", "Steady")
        with col3:
            st.metric("Tide/Current", "Incoming", "Peak Flow")
            st.metric("Bite Score", "88/100", "Excellent")

        st.subheader("⏰ Optimal Feeding Windows")
        st.write("Based on bathymetry and the lunar cycle, your best windows are:")
        st.info("**Major Window:** 5:45 PM – 7:15 PM (Sunset/Tide Overlap) \n\n **Minor Window:** 6:15 AM – 7:30 AM")

        # --- SMART LURE ORDERING ---
        st.subheader("🎒 Gear Priority (Best to Worst)")
        user_lures = st.session_state['profile']['lures']
        
        if not user_lures:
            st.warning("Update your Gear Locker in the sidebar to see ranked lures.")
        else:
            # Logic: If Saltwater + High Chlorophyll, prioritize vibration/flash
            # If Fresh + Lilypads, prioritize weedless
            cover = SITES[selected_spot][5]
            
            ranked_lures = []
            if cover == "LilyPads":
                # Move Frogs and Senkos to top
                ranked_lures = sorted(user_lures, key=lambda x: x in ["Frog", "Senko"], reverse=True)
            elif water_type == "Salt":
                # Move Bucktails and Poppers to top
                ranked_lures = sorted(user_lures, key=lambda x: x in ["Bucktail", "Popper"], reverse=True)
            else:
                ranked_lures = user_lures # Default
            
            for i, lure in enumerate(ranked_lures):
                st.write(f"{i+1}. **{lure}**" + (" - *Top Choice for this cover!*" if i == 0 else ""))

# --- TAB 3: LEARN CENTER ---
with menu[2]:
    st.header("🔬 The Science of Fishing")
    topic = st.selectbox("Advanced Topic", ["Understanding Bathymetry", "The Chlorophyll Connection"])
    
    if topic == "Understanding Bathymetry":
        st.write("Bathymetry is the study of underwater depth. Fish use 'contour lines' like highways.")
        
    elif topic == "The Chlorophyll Connection":
        st.write("Higher Chlorophyll-a levels indicate more plankton, which draws in baitfish (bait balls).")
