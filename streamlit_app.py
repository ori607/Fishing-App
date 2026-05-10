import streamlit as st
import requests
from datetime import datetime

# --- 1. SETTINGS ---
st.set_page_config(page_title="FishAI Master", page_icon="🎣", layout="wide")

# --- 2. THE DATABASE (Expanded Local Spots) ---
# Format: "Name": [Species, Distance, MaxWeight, Quality, Tip, CoverType, WaterType, Lat, Lon]
SITES = {
    "Quarry Road Pond (Bryn Athyn)": ["Largemouth Bass", 0.1, 6, 10, "Focus on steep drop-offs.", "Rocks", "Fresh", 40.13, -75.06],
    "Lower Moreland Park Lake": ["Largemouth Bass", 1.5, 5, 8, "Fish near the lily pads and drain pipe.", "LilyPads", "Fresh", 40.12, -75.05],
    "Mason's Mill Pond": ["Largemouth Bass", 3, 5, 4, "Heavy vegetation. Use weedless gear.", "LilyPads", "Fresh", 40.15, -75.07],
    "Pennypack (Lorimer)": ["Smallmouth Bass", 2, 5, 6, "Target current breaks behind rocks.", "Current", "Fresh", 40.10, -75.06],
    "Neshaminy Creek": ["Smallmouth Bass", 12, 4, 7, "Look for deep pools and rocky bottoms.", "Rocks", "Fresh", 40.15, -74.95],
    "Delaware River (Lumberville)": ["Smallmouth Bass", 35, 6, 9, "The gold standard for local smallies.", "Current", "Fresh", 40.40, -75.04],
    "Island Beach State Park": ["Striped Bass", 82, 50, 10, "Target the 'sloughs'.", "Open", "Salt", 39.88, -74.08],
    "Cape May Inlet": ["Bull Shark", 95, 150, 7, "Heavy current. Use wire leaders.", "Current", "Salt", 38.93, -74.90]
}

SPECIES_LIST = sorted(list(set([d[0] for d in SITES.values()])))

# --- 3. PERSISTENT PROFILE ---
if 'profile' not in st.session_state:
    st.session_state['profile'] = {
        'lures': ["Senko", "Frog", "Crankbait", "Chatterbait", "Jig", "Whopper Plopper", "Tube Jig", "Ned Rig"]
    }

with st.sidebar:
    st.header("👤 My Gear Locker")
    st.session_state['profile']['lures'] = st.multiselect(
        "Lures You Own:", 
        ["Senko", "Frog", "Crankbait", "Chatterbait", "Jig", "Bucktail", "Whopper Plopper", "Tube Jig", "Ned Rig", "Spinnerbait"],
        default=st.session_state['profile']['lures']
    )
    st.divider()
    st.header("📍 Current Trip")
    active_spots = st.session_state.get('filtered_spots', list(SITES.keys()))
    st.session_state['selected_spot'] = st.selectbox("Select location to analyze:", active_spots)

# --- 4. MAIN INTERFACE ---
tabs = st.tabs(["🎯 Strategy Planner", "📊 Advanced Tactical Analysis", "📚 Learn Center"])

# --- TAB: STRATEGY PLANNER ---
with tabs[0]:
    st.title("Top Local Spots")
    c1, col_dist, c2 = st.columns([2, 1, 1])
    with c1:
        species_search = st.selectbox("Search Species:", SPECIES_LIST)
    with col_dist:
        max_dist = st.number_input("Max Miles", value=150)
    with c2:
        target_lb = st.slider(f"Target Weight", 1, 50, 2)

    matches = [
        {"name": n, "dist": d[1], "max_w": d[2], "quality": d[3], "tip": d[4]} 
        for n, d in SITES.items() if d[0] == species_search and d[1] <= max_dist and d[2] >= target_lb
    ]
    matches = sorted(matches, key=lambda x: x['quality'], reverse=True)
    st.session_state['filtered_spots'] = [m['name'] for m in matches]

    if not matches:
        st.error(f"No {species_search} spots found. Try expanding distance.")
    else:
        for i, spot in enumerate(matches):
            rank = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
            with st.container():
                st.subheader(f"{rank} {spot['name']}")
                col_a, col_b, col_c = st.columns([1,1,2])
                col_a.metric("Distance", f"{spot['dist']}mi")
                col_b.metric("Potential", f"{spot['max_w']}lb")
                col_c.write(f"**Tip:** {spot['tip']}")
                st.divider()

# --- TAB: ADVANCED TACTICAL ANALYSIS ---
with tabs[1]:
    spot_name = st.session_state.get('selected_spot')
    if not st.session_state.get('filtered_spots'):
        st.warning("Find spots in Strategy Planner first!")
    elif spot_name:
        st.header(f"Tactical Briefing: {spot_name}")
        
        # --- LIVE DATA FETCHING ---
        lat, lon = SITES[spot_name][7], SITES[spot_name][8]
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,surface_pressure,wind_speed_10m&temperature_unit=fahrenheit"
        
        try:
            res = requests.get(weather_url).json()
            curr_f = res['current']['temperature_2m']
            # Convert hPa to inHg
            curr_inhg = round(res['current']['surface_pressure'] * 0.02953, 2)
            curr_wind = res['current']['wind_speed_10m']
            
            # DYNAMIC BITE SCORE LOGIC
            bite_score = 75
            if curr_inhg < 29.90: bite_score += 15 # Low pressure = feeding frenzy
            if 60 < curr_f < 75: bite_score += 10 # Ideal spring temp
            
            st.markdown(f"# Real-Time Bite Score: {min(bite_score, 100)}/100")
            
            f1, f2, f3, f4, f5 = st.columns(5)
            f1.metric("Air Temp", f"{curr_f}°F")
            f2.metric("Pressure", f"{curr_inhg} inHg")
            f3.metric("Wind", f"{curr_wind} mph")
            f4.metric("Moon", "Waning Crescent")
            f5.metric("Status", "High Pressure" if curr_inhg > 30.10 else "Dropping")
            
        except:
            st.error("Live connection failed. Using manual backup.")

        st.divider()
        
        # Timing Choice
        st.subheader("⏰ Optimal Trip Timing")
        time_choice = st.radio("Choose a window:", ["6am-10am", "10am-4pm", "4pm-8pm"])
        if time_choice == "6am-10am": st.success("**Best Slot:** 6:45am - 8:15am")
        elif time_choice == "10am-4pm": st.success("**Best Slot:** 11:00am - 12:30pm")
        else: st.success("**Best Slot:** 6:15pm - 7:45pm")

        st.divider()

        # Rod/Line Recommendations
        st.subheader("⚙️ Recommended Setup")
        rec_rod = "6'0\" Ultralight" if target_lb < 3 else "7'0\" Medium-Heavy"
        rec_line = "6lb Mono" if target_lb < 3 else "15lb Braid"
        st.info(f"**Rod:** {rec_rod} | **Line:** {rec_line}")

        st.divider()
        
        # Lure Logic
        col_left, col_right = st.columns(2)
        cover = SITES[spot_name][5]
        user_lures = st.session_state['profile']['lures']
        
        with col_left:
            st.subheader("🎒 From Your Locker")
            if user_lures:
                if cover == "LilyPads" and "Frog" in user_lures:
                    st.write("**Best Owned:** White 1/2oz Frog")
                elif cover == "Current" and "Tube Jig" in user_lures:
                    st.write("**Best Owned:** 3.5-inch Brownish Tube Jig")
                else:
                    st.write("**Best Owned:** 5-inch Green Pumpkin Senko")
                    st.image("https://images.tacklewarehouse.com/fishing/Gary_Yamamoto_Senko.jpg", width=250)
            else: st.write("Locker is empty!")

        with col_right:
            st.subheader("🎣 Pro Suggestion")
            if cover == "Current": st.write("**Expert Pick:** 1/8oz Ned Rig - Coppertreuse")
            elif cover == "LilyPads": st.write("**Expert Pick:** 5/8oz Leopard Frog")
            else: st.write("**Expert Pick:** 3/8oz Black/Blue Jig")

# --- TAB: LEARN CENTER ---
with tabs[2]:
    st.header("Fishing Academy")
    topic = st.selectbox("Topic", ["Texas Rig", "Bathymetry"])
    if topic == "Texas Rig":
        st.write("Rigging your soft plastics 'weedless' is essential for heavy cover.")
        st.image("https://upload.wikimedia.org/wikipedia/commons/e/e4/Texas_rig.png", width=300)
