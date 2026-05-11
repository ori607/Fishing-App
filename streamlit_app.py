import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import math

# --- 1. SETTINGS ---
st.set_page_config(page_title="FishAI Master Pro", page_icon="🎣", layout="wide")

# --- 2. THE MASTER DATABASE (Expanded & Persistent) ---
SITES = {
    "Quarry Road Pond (Bryn Athyn)": ["Largemouth Bass", 40.135, -75.064, "Rocks", "Fresh", "Focus on steep drop-offs.", 8],
    "Lower Moreland Park Lake": ["Largemouth Bass", 40.121, -75.055, "LilyPads", "Fresh", "Fish near the drain pipe.", 6],
    "Mason's Mill Pond": ["Largemouth Bass", 40.151, -75.071, "LilyPads", "Fresh", "Heavy vegetation; use weedless.", 5],
    "Pennypack (Lorimer)": ["Smallmouth Bass", 40.101, -75.062, "Current", "Fresh", "Target current breaks behind rocks.", 5],
    "Neshaminy Creek (Tyler Park)": ["Smallmouth Bass", 40.211, -74.962, "Rocks", "Fresh", "Deep pools near the dam.", 4],
    "Delaware River (Lumberville)": ["Smallmouth Bass", 40.401, -75.041, "Current", "Fresh", "Best local smallie fishery.", 6],
    "Perkiomen Creek": ["Smallmouth Bass", 40.155, -75.412, "Current", "Fresh", "Fish the eddies.", 5],
    "Island Beach State Park": ["Striped Bass", 39.885, -74.085, "Open", "Salt", "Target the 'sloughs'.", 60],
    "Barnegat Inlet": ["Striped Bass", 39.758, -74.101, "Rocks", "Salt", "High current; use heavy jigs.", 55],
    "Cape May Inlet": ["Bull Shark", 38.933, -74.903, "Current", "Salt", "Use wire leaders and fresh bait.", 400],
    "Wildwood Surf": ["Sandbar Shark", 38.981, -74.821, "Open", "Salt", "Long casts past the breakers.", 150],
    "Wissahickon Creek": ["Rainbow Trout", 40.071, -75.212, "Current", "Fresh", "Stocked sections near valley green.", 4]
}

ALL_SPECIES = sorted([
    "Largemouth Bass", "Smallmouth Bass", "Striped Bass", "Bluefish", "Channel Catfish", 
    "Blue Catfish", "Flathead Catfish", "Musky", "Walleye", "Brown Trout", "Brook Trout", 
    "Rainbow Trout", "Fluke", "Weakfish", "Bull Shark", "Sandbar Shark", "Blacktip Shark",
    "Mako Shark", "Hammerhead", "Tautog", "Red Drum", "Black Drum", "Yellow Perch", 
    "Northern Pike", "Common Carp", "Mirror Carp", "Steelhead", "Lake Trout"
])

ALL_LURES = sorted([
    "Senko (Stick Bait)", "Hollow Body Frog", "Squarebill Crankbait", "Deep Diver",
    "Chatterbait", "Football Jig", "Finesse Jig", "Ned Rig", "Tube Jig", 
    "Bucktail Jig", "Whopper Plopper", "Popper", "Walking Bait", "Spinnerbait", 
    "Buzzbait", "Keitech Swimbait", "Jerkbait", "Inline Spinner", "Marabou Jig"
])

# --- 3. CORE LOGIC ---
def haversine(lat1, lon1, lat2, lon2):
    r = 3958.8 
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi, dlambda = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1-a))

# --- 4. SESSION STATE (With Error-Proofing) ---
if 'locked_spot' not in st.session_state: st.session_state['locked_spot'] = None
if 'user_coords' not in st.session_state: st.session_state['user_coords'] = (40.13, -75.06)
if 'my_catches' not in st.session_state: st.session_state['my_catches'] = []

# FIX: This prevents the Multiselect crash by clearing old data
if 'lures_owned' not in st.session_state: 
    st.session_state['lures_owned'] = []
else:
    # Ensure every lure in session_state actually exists in our current ALL_LURES list
    st.session_state['lures_owned'] = [l for l in st.session_state['lures_owned'] if l in ALL_LURES]

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title("Settings")
    user_loc = st.text_input("Home Base:", value="Huntingdon Valley, PA")
    if st.button("Set Location"):
        if "Cape May" in user_loc: st.session_state['user_coords'] = (38.93, -74.90)
        else: st.session_state['user_coords'] = (40.13, -75.06)
        st.rerun()
    
    st.divider()
    st.header("🎒 My Gear Locker")
    # Updated Multiselect
    st.session_state['lures_owned'] = st.multiselect("Lures in your bag:", ALL_LURES, default=st.session_state['lures_owned'])

# --- 6. MAIN TABS ---
tabs = st.tabs(["🎯 Strategy Planner", "📊 Advanced Analysis", "📸 Catch Journal", "📚 Learn Center"])

# --- TAB 1: STRATEGY PLANNER ---
with tabs[0]:
    st.title("Target Acquisition")
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        spec_choice = st.selectbox("Search Species:", [None] + ALL_SPECIES)
    with c2:
        dist_limit = st.number_input("Max Miles:", value=100)
    with c3:
        max_w = 500 if spec_choice and "Shark" in spec_choice else 60 if spec_choice and "Striped" in spec_choice else 15
        target_w = st.slider("Target Weight (lbs):", 1, max_w, 2)

    if spec_choice:
        u_lat, u_lon = st.session_state['user_coords']
        matches = []
        map_points = []
        for name, d in SITES.items():
            dist = haversine(u_lat, u_lon, d[1], d[2])
            if d[0] == spec_choice and dist <= dist_limit:
                matches.append({"name": name, "dist": round(dist, 1), "tip": d[5], "lat": d[1], "lon": d[2]})
                map_points.append({"lat": d[1], "lon": d[2]})

        if matches:
            st.subheader("📍 Nearby Hotspots")
            st.map(pd.DataFrame(map_points))
            for m in matches:
                with st.container():
                    col_txt, col_act = st.columns([3, 1])
                    col_txt.write(f"**{m['name']}** - {m['dist']} miles away")
                    if col_act.button("Lock Trip", key=m['name']):
                        st.session_state['locked_spot'] = m['name']
                        st.session_state['target_spec'] = spec_choice
                        st.session_state['target_w'] = target_w
                        st.rerun()
                    st.divider()
    else:
        st.warning("Select a species to see local spots.")

# --- TAB 2: ADVANCED ANALYSIS ---
with tabs[1]:
    if not st.session_state['locked_spot']:
        st.info("Lock a trip in the Planner first!")
    else:
        spot = st.session_state['locked_spot']
        s_data = SITES[spot]
        st.header(f"Live Briefing: {spot}")
        
        # Weather Call
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={s_data[1]}&longitude={s_data[2]}&current=temperature_2m,surface_pressure&temperature_unit=fahrenheit"
            res = requests.get(url).json()
            temp, pres = res['current']['temperature_2m'], round(res['current']['surface_pressure'] * 0.02953, 2)
            st.markdown(f"# Bite Score: 85/100")
            st.metric("Air Temp", f"{temp}°F")
            st.metric("Pressure", f"{pres} inHg")
        except:
            st.error("Weather offline.")

# --- TAB 3: CATCH JOURNAL ---
with tabs[2]:
    st.header("📸 Personal Catch Log")
    c_spec = st.selectbox("Species caught:", ALL_SPECIES)
    c_weight = st.number_input("Weight (lbs):", value=1.0)
    if st.button("Save to Journal"):
        st.session_state['my_catches'].append({"spec": c_spec, "w": c_weight, "date": datetime.now().strftime("%x")})
        st.success("Catch saved!")
    
    for catch in st.session_state['my_catches'][::-1]:
        st.write(f"**{catch['date']}** - {catch['spec']} ({catch['w']} lbs)")

# --- TAB 4: LEARN CENTER ---
with tabs[3]:
    st.title("Fishing Academy")
    topic = st.selectbox("Topic:", ["Texas Rig", "Ned Rig"])
    if topic == "Texas Rig":
        st.image("https://upload.wikimedia.org/wikipedia/commons/e/e4/Texas_rig.png", width=400)
