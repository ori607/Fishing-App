import streamlit as st
import requests
import pandas as pd
import pydeck as pdk
from datetime import datetime
import math
import json
import os

# --- 1. SETTINGS & MOBILE STYLING ---
st.set_page_config(page_title="FishAI Mobile Pro", page_icon="🎣", layout="wide")

# Custom CSS to fix mobile spacing and card styling
st.markdown("""
    <style>
    .tactical-card {
        background-color: #f0f2f6;
        border-left: 5px solid #007bff;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        padding-left: 10px;
        padding-right: 10px;
    }
    </style>
    """, unsafe_content_label=True)

# --- 2. THE MASTER DATABASE ---
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

def get_solunar_status():
    hour = datetime.now().hour
    if (6 <= hour <= 9) or (17 <= hour <= 20): return "MAJOR PEAK", 25
    return "Steady", 5

# --- 4. SESSION STATE & STORAGE ---
if 'locked_spot' not in st.session_state: st.session_state['locked_spot'] = None
if 'user_coords' not in st.session_state: st.session_state['user_coords'] = (40.13, -75.06)
if 'my_catches' not in st.session_state: st.session_state['my_catches'] = []
if 'lures_owned' not in st.session_state: st.session_state['lures_owned'] = []

DB_FILE = "catches_db.json"
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f:
        st.session_state['my_catches'] = json.load(f)

def save_catches():
    with open(DB_FILE, "w") as f:
        json.dump(st.session_state['my_catches'], f)

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title("🎛️ Command")
    user_loc = st.text_input("Home Base:", value="Huntingdon Valley, PA")
    if st.button("Update GPS"):
        if "Cape May" in user_loc: st.session_state['user_coords'] = (38.93, -74.90)
        else: st.session_state['user_coords'] = (40.13, -75.06)
        st.rerun()
    
    st.divider()
    st.header("🎒 Gear")
    st.session_state['lures_owned'] = st.multiselect("Your Lures:", ALL_LURES, default=[l for l in st.session_state['lures_owned'] if l in ALL_LURES])

    if st.session_state['locked_spot']:
        st.success(f"Locked: {st.session_state['locked_spot']}")
        if st.button("End Trip"):
            st.session_state['locked_spot'] = None
            st.rerun()

# --- 6. MAIN TABS ---
tabs = st.tabs(["🎯 Strategy", "📊 Analysis", "📸 Log", "📚 Learn"])

# --- TAB 1: STRATEGY (Fixed Map) ---
with tabs[0]:
    st.title("Target Acquisition")
    spec_search = st.selectbox("Search Species:", [None] + ALL_SPECIES)
    
    col_dist, col_lb = st.columns(2)
    with col_dist: max_mi = st.number_input("Max Miles:", value=100)
    with col_lb: 
        m_w = 500 if spec_search and "Shark" in spec_search else 60 if spec_search and "Striped" in spec_search else 15
        t_w = st.slider("Target Lbs:", 1, m_w, 2)

    if spec_search:
        u_lat, u_lon = st.session_state['user_coords']
        matches = []
        map_points = [{"lat": u_lat, "lon": u_lon, "name": "HOME", "color": [0, 150, 255, 255], "radius": 150}]

        for name, d in SITES.items():
            dist = haversine(u_lat, u_lon, d[1], d[2])
            if d[0] == spec_search and dist <= max_mi:
                matches.append({"name": name, "dist": round(dist, 1), "tip": d[5], "lat": d[1], "lon": d[2], "max_w": d[6]})
                map_points.append({"lat": d[1], "lon": d[2], "name": name, "color": [40, 200, 100, 255], "radius": 100})

        if matches:
            # Fixed Mobile Map rendering
            st.pydeck_chart(pdk.Deck(
                map_style='mapbox://styles/mapbox/satellite-streets-v11',
                initial_view_state=pdk.ViewState(latitude=u_lat, longitude=u_lon, zoom=11, pitch=0), # Pitch 0 is better for mobile
                layers=[pdk.Layer('ScatterplotLayer', data=pd.DataFrame(map_points), get_position='[lon, lat]', get_color='color', get_radius=200, pickable=True)],
                tooltip={"text": "{name}"}
            ), use_container_width=True)
            
            for m in matches:
                with st.expander(f"📍 {m['name']} ({m['dist']} mi)"):
                    st.write(f"**Tip:** {m['tip']}")
                    if st.button("Lock Location", key=m['name']):
                        st.session_state['locked_spot'] = m['name']
                        st.session_state['target_spec'] = spec_search
                        st.session_state['target_w'] = t_w
                        st.rerun()

# --- TAB 2: ADVANCED ANALYSIS (Clean Design) ---
with tabs[1]:
    if not st.session_state['locked_spot']:
        st.warning("Lock a location first!")
    else:
        spot = st.session_state['locked_spot']
        s_data = SITES[spot]
        st.header(f"Live Brief: {spot}")
        
        sol_msg, sol_pts = get_solunar_status()
        
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={s_data[1]}&longitude={s_data[2]}&current=temperature_2m,surface_pressure,wind_speed_10m&temperature_unit=fahrenheit"
            res = requests.get(url).json()
            temp, pres, wind = res['current']['temperature_2m'], round(res['current']['surface_pressure'] * 0.02953, 2), res['current']['wind_speed_10m']
            
            score = 65 + sol_pts + (10 if pres < 30.00 else 0)
            st.markdown(f"### Bite Score: {min(score, 100)}/100")
            
            # Mobile Metrics
            m1, m2 = st.columns(2)
            m1.metric("Temp", f"{temp}°F")
            m2.metric("Pres", f"{pres} inHg")
            m3, m4 = st.columns(2)
            m3.metric("Wind", f"{wind} mph")
            m4.metric("Solunar", sol_msg)
        except: st.error("Weather offline.")

        st.divider()
        st.subheader("🛡️ Tactical Setup")
        t_w, t_s = st.session_state.get('target_w', 2), st.session_state.get('target_spec', "")
        
        if "Shark" in t_s: r, l = "Heavy Conv.", "100lb Braid + Steel"
        elif t_w < 4: r, l = "Ultralight", "6lb Mono"
        elif "Striped" in t_s or t_w > 30: r, l = "Heavy Action", "65lb Braid"
        else: r, l = "Med-Heavy", "15lb Flouro"
        
        # Redesigned Gear Layout
        st.markdown(f"""
        <div class="tactical-card">
            <p><b>🎣 Rod:</b> {r}</p>
            <p><b>🧶 Line:</b> {l}</p>
        </div>
        """, unsafe_content_label=True)
        
        st.markdown(f"""
        <div class="tactical-card" style="border-left-color: #28a745;">
            <p><b>💼 Pro Pick:</b> 3/8oz Chatterbait (Chartreuse)</p>
        </div>
        """, unsafe_content_label=True)

# --- TAB 3: CATCH JOURNAL ---
with tabs[2]:
    st.header("📸 Catch Journal")
    with st.form("catch_entry"):
        c_spec = st.selectbox("Fish:", ALL_SPECIES)
        c_w = st.number_input("Weight:", min_value=0.1)
        if st.form_submit_button("Save Catch"):
            st.session_state['my_catches'].append({"spec": c_spec, "w": c_w, "date": datetime.now().strftime("%x")})
            save_catches()
            st.rerun()

    for i, c in enumerate(st.session_state['my_catches'][::-1]):
        col1, col2 = st.columns([4, 1])
        col1.write(f"**{c['date']}** - {c['spec']} ({c['w']} lbs)")
        if col2.button("🗑️", key=f"del_{i}"):
            real_idx = len(st.session_state['my_catches']) - 1 - i
            st.session_state['my_catches'].pop(real_idx)
            save_catches()
            st.rerun()

# --- TAB 4: LEARN CENTER ---
with tabs[3]:
    st.title("Academy")
    topic = st.selectbox("Topic:", ["Texas Rig", "Solunar Theory"])
    if topic == "Texas Rig":
        st.image("https://upload.wikimedia.org/wikipedia/commons/e/e4/Texas_rig.png", width=400)
        st.caption("Weedless setup for heavy cover.")
