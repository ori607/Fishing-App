import streamlit as st
import requests
from datetime import datetime, timedelta
import math

# --- 1. SETTINGS & STYLING ---
st.set_page_config(page_title="FishAI Master", page_icon="🎣", layout="wide")

# --- 2. MASTER DATA ---
ALL_SPECIES = sorted([
    "Largemouth Bass", "Smallmouth Bass", "Striped Bass", "Bluefish",
    "Rainbow Trout", "Brown Trout", "Channel Catfish", "Blue Catfish", 
    "Bull Shark", "Sandbar Shark", "Fluke (Summer Flounder)", "Musky"
])

# Expanded database with Coordinates
SITES = {
    "Quarry Road Pond (Bryn Athyn)": ["Largemouth Bass", 40.135, -75.064, "Rocks", "Fresh", "Focus on steep drop-offs."],
    "Lower Moreland Park Lake": ["Largemouth Bass", 40.121, -75.055, "LilyPads", "Fresh", "Fish near the drain pipe."],
    "Pennypack (Lorimer)": ["Smallmouth Bass", 40.101, -75.062, "Current", "Fresh", "Target current breaks."],
    "Island Beach State Park": ["Striped Bass", 39.885, -74.085, "Open", "Salt", "Target the 'sloughs' at low tide."],
    "Cape May Inlet": ["Bull Shark", 38.933, -74.903, "Current", "Salt", "Heavy current; use wire leaders."]
}

# --- 3. HELPER FUNCTIONS (Solunar & Tides) ---
def get_solunar_score(lat):
    # Simplified Solunar: Peaks occur roughly every 12.5 hours
    # Based on current date/time overlap with lunar cycle
    now = datetime.now()
    # Logic: High activity during moon transit (simplified for app logic)
    lunar_factor = 10 if (now.hour in [6, 7, 18, 19]) else 0
    return lunar_factor

def get_tide_status(lat, lon):
    # In a full production app, this would call a Tides API
    # Here we simulate based on the 6-hour cycle
    hour = datetime.now().hour
    if 0 <= hour % 12 < 6: return "Incoming (Flood)", 15
    return "Outgoing (Ebb)", 5

# Distance Calculator (Haversine Formula)
def haversine(lat1, lon1, lat2, lon2):
    r = 3958.8 # Miles
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1-a))

# --- 4. SESSION STATE ---
if 'locked_spot' not in st.session_state: st.session_state['locked_spot'] = None
if 'user_city' not in st.session_state: st.session_state['user_city'] = "Huntingdon Valley, PA"
if 'user_coords' not in st.session_state: st.session_state['user_coords'] = (40.13, -75.06)

# --- 5. SIDEBAR ---
with st.sidebar:
    st.header("🌍 Your Location")
    # FIX #2: User enters their own location
    user_city = st.text_input("Enter City/Zip:", value=st.session_state['user_city'])
    if st.button("Update Home Base"):
        # This simulates a Geocoding call
        if "Cape May" in user_city: st.session_state['user_coords'] = (38.93, -74.90)
        else: st.session_state['user_coords'] = (40.13, -75.06) # Default back to PA
        st.session_state['user_city'] = user_city
        st.success("Location Updated!")

    st.divider()
    st.header("👤 My Gear Locker")
    if 'profile_lures' not in st.session_state: st.session_state['profile_lures'] = []
    st.session_state['profile_lures'] = st.multiselect("Lures You Own:", ["Senko", "Frog", "Jig", "Ned Rig", "Tube"], default=st.session_state['profile_lures'])

# --- 6. MAIN INTERFACE ---
tabs = st.tabs(["🎯 Strategy Planner", "📊 Advanced Tactical Analysis", "📚 Learn Center"])

# --- TAB: STRATEGY PLANNER ---
with tabs[0]:
    st.title("Top Local Spots")
    c1, col_dist, c2 = st.columns([2, 1, 1])
    with c1:
        species_search = st.selectbox("What are you fishing for?", [None] + ALL_SPECIES)
    with col_dist:
        max_dist = st.number_input("Max Miles from Home", value=50)
    with c2:
        target_lb = st.slider("Target Weight (lbs)", 1, 100, 2)

    if species_search:
        u_lat, u_lon = st.session_state['user_coords']
        matches = []
        for name, data in SITES.items():
            dist = haversine(u_lat, u_lon, data[1], data[2])
            if data[0] == species_search and dist <= max_dist:
                matches.append({"name": name, "dist": round(dist, 1), "tip": data[5]})

        if not matches:
            st.error("No spots found in your area. Try increasing 'Max Miles'.")
        else:
            for spot in matches:
                with st.container():
                    col_info, col_btn = st.columns([3, 1])
                    col_info.write(f"**{spot['name']}** ({spot['dist']} miles away)")
                    if col_btn.button(f"Lock {spot['name']}", key=spot['name']):
                        st.session_state['locked_spot'] = spot['name']
                        st.session_state['target_species'] = species_search
                        st.session_state['target_weight'] = target_lb
                        st.rerun()
                    st.divider()
    else:
        st.warning("Search for a species to find spots near you.")

# --- TAB: ADVANCED TACTICAL ANALYSIS ---
with tabs[1]:
    if not st.session_state['locked_spot']:
        st.warning("Lock in a spot in the Strategy Planner first.")
    else:
        spot = st.session_state['locked_spot']
        data = SITES[spot]
        st.header(f"Tactical Briefing: {spot}")
        
        # --- FIX #3: SOLUNAR & TIDE LOGIC ---
        solunar_bonus = get_solunar_score(data[1])
        tide_msg, tide_bonus = ("N/A", 0)
        if data[4] == "Salt":
            tide_msg, tide_bonus = get_tide_status(data[1], data[2])

        # Weather Call
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={data[1]}&longitude={data[2]}&current=temperature_2m,surface_pressure&temperature_unit=fahrenheit"
            res = requests.get(url).json()
            temp = res['current']['temperature_2m']
            press = round(res['current']['surface_pressure'] * 0.02953, 2)
            
            # Final Advanced Bite Score
            base_score = 65
            if press < 29.95: base_score += 15 # Pressure drop
            base_score += solunar_bonus
            base_score += tide_bonus
            
            st.markdown(f"# Advanced Bite Score: {min(base_score, 100)}/100")
            st.caption(f"Includes Solunar Bonus (+{solunar_bonus}) and Tide Bonus (+{tide_bonus})")
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Air Temp", f"{temp}°F")
            m2.metric("Pressure", f"{press} inHg")
            m3.metric("Tide Status", tide_msg)
        except:
            st.error("Live Data Offline.")

        st.divider()
        # Gear Recommendation based on target weight saved earlier
        weight = st.session_state.get('target_weight', 2)
        spec = st.session_state.get('target_species', "")
        
        st.subheader("⚙️ Recommended Setup")
        if "Shark" in spec: rod, line = "Heavy Conventional", "80lb Braid"
        elif weight < 4: rod, line = "Ultralight / Fast", "6lb Mono"
        else: rod, line = "Medium-Heavy", "15lb Fluorocarbon"
        st.info(f"**Rod:** {rod} | **Line:** {line}")

# --- TAB: LEARN CENTER ---
with tabs[2]:
    st.title("Fishing Academy")
    topic = st.selectbox("Topic:", ["Texas Rig", "Tide Theory"])
    if topic == "Texas Rig":
        st.image("https://upload.wikimedia.org/wikipedia/commons/e/e4/Texas_rig.png", width=400)
    else:
        st.write("The 'Flood' tide (incoming) is generally best as it pushes baitfish toward the shore.")
