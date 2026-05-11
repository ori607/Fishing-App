import streamlit as st
import requests
from datetime import datetime

# --- 1. SETTINGS ---
st.set_page_config(page_title="FishAI Master", page_icon="🎣", layout="wide")

# --- 2. EXTENDED MASTER LISTS (For Search Bars) ---
# Massive species list to ensure the search bar feels complete
ALL_SPECIES = sorted([
    "Largemouth Bass", "Smallmouth Bass", "Striped Bass", "Black Sea Bass", "Spotted Bass",
    "Rainbow Trout", "Brown Trout", "Brook Trout", "Steelhead", "Lake Trout",
    "Channel Catfish", "Blue Catfish", "Flathead Catfish", "Bullhead",
    "Bull Shark", "Sandbar Shark", "Blacktip Shark", "Mako Shark", "Hammerhead",
    "Bluefish", "Fluke (Summer Flounder)", "Tautog", "Weakfish", "Red Drum", "Black Drum",
    "Common Carp", "Mirror Carp", "Walleye", "Yellow Perch", "Musky", "Northern Pike"
])

# Comprehensive lure locker for search
ALL_LURES = sorted([
    "Senko (Stick Bait)", "Hollow Body Frog", "Squarebill Crankbait", "Deep Diving Crankbait",
    "Lipless Crankbait", "Chatterbait (Bladed Jig)", "Football Jig", "Finesse Jig", "Swim Jig",
    "Ned Rig", "Tube Jig", "Texas Rig", "Carolina Rig", "Drop Shot", "Bucktail Jig",
    "Whopper Plopper", "Popper", "Walking Bait (Spook)", "Spinnerbait", "Buzzbait",
    "Keitech Swimbait", "Glide Bait", "Jerkbait", "Spoon", "Inline Spinner", "Marabou Jig"
])

# --- 3. THE DATABASE (Expanded Local Spots) ---
# Name: [Species, Distance, MaxWeight, Quality, Tip, CoverType, WaterType, Lat, Lon]
SITES = {
    "Quarry Road Pond (Bryn Athyn)": ["Largemouth Bass", 0.1, 8, 10, "Focus on steep drop-offs.", "Rocks", "Fresh", 40.13, -75.06],
    "Lower Moreland Park Lake": ["Largemouth Bass", 1.5, 6, 8, "Fish near the lily pads and drain pipe.", "LilyPads", "Fresh", 40.12, -75.05],
    "Mason's Mill Pond": ["Largemouth Bass", 3, 5, 4, "Heavy vegetation. Use weedless gear.", "LilyPads", "Fresh", 40.15, -75.07],
    "Pennypack (Lorimer)": ["Smallmouth Bass", 2, 5, 6, "Target current breaks behind rocks.", "Current", "Fresh", 40.10, -75.06],
    "Neshaminy Creek": ["Smallmouth Bass", 12, 4, 7, "Look for deep pools and rocky bottoms.", "Rocks", "Fresh", 40.15, -74.95],
    "Delaware River (Lumberville)": ["Smallmouth Bass", 35, 6, 9, "The gold standard for local smallies.", "Current", "Fresh", 40.40, -75.04],
    "Island Beach State Park": ["Striped Bass", 82, 50, 10, "Target the 'sloughs'.", "Open", "Salt", 39.88, -74.08],
    "Cape May Inlet": ["Bull Shark", 95, 300, 7, "Heavy current. Use wire leaders.", "Current", "Salt", 38.93, -74.90]
}

# --- 4. PERSISTENT PROFILE (Zero-Start Fix) ---
if 'profile' not in st.session_state:
    st.session_state['profile'] = {'lures': []} # Start with nothing

with st.sidebar:
    st.header("👤 My Gear Locker")
    # FIX #2 & #3: Searchable massive lists
    st.session_state['profile']['lures'] = st.multiselect(
        "Search & Add Lures You Own:", 
        ALL_LURES,
        default=st.session_state['profile']['lures']
    )
    st.divider()
    st.header("📍 Current Trip")
    active_spots = st.session_state.get('filtered_spots', [])
    
    # FIX #4: Start with nothing selected
    if not active_spots:
        st.info("Find a spot in Strategy Planner first.")
        selected_spot = None
    else:
        selected_spot = st.selectbox("Select location to analyze:", active_spots)

# --- 5. MAIN INTERFACE ---
tabs = st.tabs(["🎯 Strategy Planner", "📊 Advanced Tactical Analysis", "📚 Learn Center"])

# --- TAB: STRATEGY PLANNER ---
with tabs[0]:
    st.title("Top Local Spots")
    c1, col_dist, c2 = st.columns([2, 1, 1])
    with c1:
        # FIX #4: Search species (Start with nothing selected using None)
        species_search = st.selectbox("What are you fishing for?", [None] + ALL_SPECIES)
    
    with col_dist:
        max_dist = st.number_input("Max Miles", value=150)
    
    with c2:
        # FIX #1: Specific Slider Scale based on Species
        max_val = 10
        if species_search:
            if "Shark" in species_search: max_val = 500
            elif "Striped Bass" in species_search or "Musky" in species_search: max_val = 60
            elif "Catfish" in species_search: max_val = 100
        target_lb = st.slider(f"Target Weight (lbs)", 1, max_val, 2)

    if species_search:
        matches = [
            {"name": n, "dist": d[1], "max_w": d[2], "quality": d[3], "tip": d[4]} 
            for n, d in SITES.items() if d[0] == species_search and d[1] <= max_dist and d[2] >= target_lb
        ]
        matches = sorted(matches, key=lambda x: x['quality'], reverse=True)
        st.session_state['filtered_spots'] = [m['name'] for m in matches]

        if not matches:
            st.error(f"No {species_search} spots found. Try expanding distance or lowering target weight.")
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
    else:
        st.warning("Select a fish species to see local spots!")

# --- TAB: ADVANCED TACTICAL ANALYSIS ---
with tabs[1]:
    if not selected_spot:
        st.warning("Please select a fish and a location in the Strategy Planner first!")
    else:
        st.header(f"Tactical Briefing: {selected_spot}")
        
        # FIX #7: Real Time and Date Restored
        now = datetime.now()
        st.subheader(f"📅 {now.strftime('%A, %b %d, %Y')} | 🕒 {now.strftime('%I:%M %p')}")
        
        # --- LIVE DATA FETCHING ---
        lat, lon = SITES[selected_spot][7], SITES[selected_spot][8]
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,surface_pressure,wind_speed_10m&temperature_unit=fahrenheit"
        
        try:
            res = requests.get(weather_url).json()
            curr_f = res['current']['temperature_2m']
            curr_inhg = round(res['current']['surface_pressure'] * 0.02953, 2)
            curr_wind = res['current']['wind_speed_10m']
            
            bite_score = 75
            if curr_inhg < 29.90: bite_score += 15 
            if 60 < curr_f < 75: bite_score += 10
            
            st.markdown(f"# Real-Time Bite Score: {min(bite_score, 100)}/100")
            
            f1, f2, f3, f4, f5 = st.columns(5)
            f1.metric("Air Temp", f"{curr_f}°F")
            f2.metric("Pressure", f"{curr_inhg} inHg")
            f3.metric("Wind", f"{curr_wind} mph")
            f4.metric("Moon", "Waning Crescent")
            f5.metric("Trend", "Falling" if curr_inhg < 30.00 else "Stable")
        except:
            st.error("Live weather connection failed.")

        st.divider()
        
        # FIX #6: Suggested Time Slot Restored
        st.subheader("⏰ Optimal Trip Timing")
        time_choice = st.radio("Select your intended window:", ["6am-10am", "10am-4pm", "4pm-8pm"])
        if time_choice == "6am-10am": st.success("**Best Slot:** 6:45am - 8:15am (Dawn feeding)")
        elif time_choice == "10am-4pm": st.success("**Best Slot:** 11:30am - 1:00pm (Deep structure focus)")
        else: st.success("**Best Slot:** 6:15pm - 7:45pm (Golden hour)")
        st.info("🏆 **Overall Best:** 7:00 PM Tonight")

        st.divider()

        # FIX #5: Accurate Setup for Big Game
        st.subheader("⚙️ Recommended Setup")
        if "Shark" in species_search:
            rec_rod = "7'6\" Extra-Heavy Conventional"
            rec_line = "80lb-100lb Braid with 200lb Steel Leader"
        elif target_lb >= 30:
            rec_rod = "7'10\" Heavy Action / Mag-Heavy"
            rec_line = "65lb Braided Line"
        elif target_lb < 3:
            rec_rod = "6'6\" Ultralight / Fast Action"
            rec_line = "4lb-6lb Monofilament"
        else:
            rec_rod = "7'0\" Medium-Heavy / Fast Action"
            rec_line = "12lb-15lb Fluorocarbon"
            
        col_gear1, col_gear2 = st.columns(2)
        col_gear1.info(f"**Rod:** {rec_rod}")
        col_gear2.info(f"**Line:** {rec_line}")

        st.divider()
        
        # Lure Logic
        col_left, col_right = st.columns(2)
        cover = SITES[selected_spot][5]
        user_lures = st.session_state['profile']['lures']
        
        with col_left:
            st.subheader("🎒 From Your Locker")
            if user_lures:
                # Logic to suggest the best detailed lure from user's list
                suggestion = "5-inch Green Pumpkin Senko"
                if "Frog" in str(user_lures) and cover == "LilyPads": suggestion = "White Hollow Body Frog"
                elif "Jig" in str(user_lures) and cover == "Rocks": suggestion = "3/8oz Black/Blue Football Jig"
                
                st.write(f"**Primary Choice:** {suggestion}")
                if "Senko" in suggestion:
                    st.image("https://images.tacklewarehouse.com/fishing/Gary_Yamamoto_Senko.jpg", width=250)
            else:
                st.write("No owned lures selected in sidebar!")

        with col_right:
            st.subheader("🎣 Pro Suggestion")
            if "Shark" in species_search: st.write("**Expert Pick:** Large Chunked Mackerel or Menhaden")
            elif cover == "Current": st.write("**Expert Pick:** 1/8oz Ned Rig - Coppertreuse")
            elif cover == "LilyPads": st.write("**Expert Pick:** 5/8oz Leopard Frog")
            else: st.write("**Expert Pick:** 3/8oz Black/Blue Jig")

# --- TAB: LEARN CENTER ---
with tabs[2]:
    st.header("Fishing Academy")
    topic = st.selectbox("Topic", ["Texas Rig", "Bathymetry"])
    if topic == "Texas Rig":
        st.write("Essential for fishing the weeds at Mason's Mill.")
        st.image("https://upload.wikimedia.org/wikipedia/commons/e/e4/Texas_rig.png", width=300)
