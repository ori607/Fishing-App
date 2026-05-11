import streamlit as st
import requests
import pandas as pd
import pydeck as pdk
from datetime import datetime
import math
import json
import os

# --- 1. SETTINGS & ELITE TACTICAL STYLING ---
st.set_page_config(page_title="FishAI Elite Tactical", page_icon="🎣", layout="wide")

st.markdown("""
    <style>
    /* Global Tactical Theme */
    .main { background-color: #f8f9fa; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        font-size: 14px; 
        font-weight: 600; 
        color: #4a5568; 
    }
    
    /* Tactical Metric Cards */
    .metric-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 15px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 12px;
    }
    .metric-label {
        font-size: 0.75rem;
        color: #718096;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 700;
    }
    .metric-value {
        font-size: 1.1rem;
        color: #2d3748;
        font-weight: 800;
        margin-top: 4px;
    }
    
    /* Gear Locker Item */
    .gear-item {
        background: #edf2f7;
        padding: 5px 12px;
        border-radius: 20px;
        display: inline-block;
        margin: 4px;
        font-size: 0.85rem;
        border: 1px solid #cbd5e0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE HIGH-ACCURACY DATABASE (Fishbrain Precision) ---
# Updated coordinates for Albidale/Lower Moreland and Cathedral/Quarry
SITES = {
    "Albidale Park (Lower Moreland)": ["Largemouth Bass", 40.1238, -75.0532, "LilyPads", "Fresh", "Enter via Warfield Dr; focus on the northwest bank.", 8],
    "Quarry Pond (Cathedral Rd Area)": ["Largemouth Bass", 40.1385, -75.0598, "Rocks", "Fresh", "Deep clear water; use natural colors.", 10],
    "Mason's Mill Pond": ["Largemouth Bass", 40.1512, -75.0705, "LilyPads", "Fresh", "Heavy surface matted vegetation.", 6],
    "Lorimer Park (Pennypack)": ["Smallmouth Bass", 40.0988, -75.0612, "Current", "Fresh", "Target the deep holes below the bridge.", 5],
    "Neshaminy Creek (Tyler)": ["Smallmouth Bass", 40.2115, -74.9618, "Rocks", "Fresh", "Fast water near the dam.", 5],
    "Island Beach State Park": ["Striped Bass", 39.8850, -74.0850, "Open", "Salt", "Find the deeper sloughs at low tide.", 65],
    "Barnegat Inlet": ["Striped Bass", 39.7595, -74.1008, "Rocks", "Salt", "Heavy current; fish the slack tide.", 60],
    "Cape May Inlet": ["Bull Shark", 38.9345, -74.9015, "Current", "Salt", "Heaviest tackle required; use wire.", 450],
    "Wissahickon (Valley Green)": ["Rainbow Trout", 40.0525, -75.2155, "Current", "Fresh", "Stocked pools near the inn.", 4]
}

ALL_SPECIES = sorted(["Largemouth Bass", "Smallmouth Bass", "Striped Bass", "Bull Shark", "Rainbow Trout", "Bluefish", "Catfish", "Musky", "Walleye"])
ALL_LURES = sorted(["Senko (Green Pumpkin)", "Hollow Body Frog", "Chatterbait Jackhammer", "Ned Rig", "Whopper Plopper", "Keitech Swimbait", "Bucktail Jig", "Squarebill", "Jerkbait"])

# --- 3. CORE LOGIC & PERSISTENCE ---
DB_FILE = "fishing_master_db.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {"catches": [], "lures": []}

def save_data():
    data = {"catches": st.session_state['my_catches'], "lures": st.session_state['lures_owned']}
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

if 'init' not in st.session_state:
    saved = load_data()
    st.session_state['my_catches'] = saved.get("catches", [])
    st.session_state['lures_owned'] = saved.get("lures", [])
    st.session_state['locked_spot'] = None
    st.session_state['user_coords'] = (40.13, -75.06) # Default PA
    st.session_state['init'] = True

def haversine(lat1, lon1, lat2, lon2):
    r = 3958.8 
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1-a))

def get_weather_intel(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,surface_pressure,wind_speed_10m&temperature_unit=fahrenheit"
        res = requests.get(url).json()
        c = res['current']
        return {"temp": c['temperature_2m'], "pres": round(c['surface_pressure'] * 0.02953, 2), "wind": c['wind_speed_10m']}
    except: return None

# --- 4. SIDEBAR (The Command Center) ---
with st.sidebar:
    st.title("🦅 Tactical Ops")
    loc_input = st.text_input("Current Base:", value="Huntingdon Valley, PA")
    if st.button("Sync GPS"):
        st.session_state['user_coords'] = (38.93, -74.90) if "Cape May" in loc_input else (40.13, -75.06)
        st.rerun()

    st.divider()
    st.header("🧰 Gear Locker")
    new_lures = st.multiselect("Stock Your Bag:", ALL_LURES, default=st.session_state['lures_owned'])
    if new_lures != st.session_state['lures_owned']:
        st.session_state['lures_owned'] = new_lures
        save_data()

    if st.session_state['locked_spot']:
        st.success(f"Objective Locked: {st.session_state['locked_spot']}")
        if st.button("Abort Mission"):
            st.session_state['locked_spot'] = None
            st.rerun()

# --- 5. MAIN INTERFACE ---
tabs = st.tabs(["🎯 Strategy", "📊 Intel", "📸 Logbook", "🎒 Locker"])

# --- TAB 1: STRATEGY (Pinpoint Accuracy Map) ---
with tabs[0]:
    st.title("Target Acquisition")
    target = st.selectbox("Select Target Species:", [None] + ALL_SPECIES)
    
    if target:
        u_lat, u_lon = st.session_state['user_coords']
        matches = []
        map_points = [{"lat": u_lat, "lon": u_lon, "name": "BASE", "color": [0, 150, 255, 255]}]

        for name, d in SITES.items():
            if d[0] == target:
                matches.append({"name": name, "dist": round(haversine(u_lat, u_lon, d[1], d[2]), 1), "tip": d[5], "lat": d[1], "lon": d[2]})
                map_points.append({"lat": d[1], "lon": d[2], "name": name, "color": [255, 50, 50, 255]})

        # THE MAP: Switch to 'outdoors' style to force Green/Blue visibility
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/outdoors-v12', # High-detail terrain style
            initial_view_state=pdk.ViewState(latitude=u_lat, longitude=u_lon, zoom=12, pitch=0),
            layers=[
                pdk.Layer(
                    'ScatterplotLayer', 
                    data=pd.DataFrame(map_points), 
                    get_position='[lon, lat]', 
                    get_color='color', 
                    get_radius=35, # Small, accurate pings
                    pickable=True
                )
            ],
            tooltip={"text": "{name}"}
        ), use_container_width=True)
        
        for m in matches:
            with st.expander(f"📍 {m['name']} ({m['dist']} mi)"):
                st.write(f"**Field Notes:** {m['tip']}")
                if st.button("Lock Location", key=m['name']):
                    st.session_state['locked_spot'] = m['name']
                    st.rerun()

# --- TAB 2: INTEL (Restored Tactical Analysis) ---
with tabs[1]:
    if not st.session_state['locked_spot']:
        st.info("Awaiting location lock from Strategy tab.")
    else:
        spot = st.session_state['locked_spot']
        lat, lon = SITES[spot][1], SITES[spot][2]
        intel = get_weather_intel(lat, lon)
        
        st.header(f"Live Intelligence: {spot}")
        
        if intel:
            # Row 1: Weather Stats
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f'<div class="metric-card"><div class="metric-label">Atmosphere</div><div class="metric-value">{intel["temp"]}°F | {intel["pres"]} inHg</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="metric-card"><div class="metric-label">Wind Velocity</div><div class="metric-value">{intel["wind"]} mph</div></div>', unsafe_allow_html=True)
            
            # Row 2: Bite Score Logic
            score = 75
            if intel['pres'] < 30.0: score += 10
            if 6 <= datetime.now().hour <= 9: score += 15
            
            st.markdown(f'<div class="metric-card" style="border-left: 5px solid #007bff;"><div class="metric-label">Probability of Strike</div><div class="metric-value" style="font-size: 2rem;">{min(score, 100)}%</div></div>', unsafe_allow_html=True)

        st.divider()
        st.subheader("🛡️ Tactical Recommendation")
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Primary Loadout</div>
            <div class="metric-value" style="font-size: 1rem;">
                <b>Rod:</b> 7'0" Medium-Heavy Fast Action<br>
                <b>Line:</b> 15lb Fluorocarbon Mainline<br>
                <b>Objective:</b> Target wind-blown points and hard cover.
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- TAB 3: LOGBOOK ---
with tabs[2]:
    st.header("📸 Recon Logs")
    with st.form("new_catch"):
        f_spec = st.selectbox("Species:", ALL_SPECIES)
        f_weight = st.number_input("Weight (lbs):", min_value=0.1)
        if st.form_submit_button("Confirm Catch"):
            st.session_state['my_catches'].append({"spec": f_spec, "w": f_weight, "date": datetime.now().strftime("%x")})
            save_data()
            st.rerun()
    
    for i, c in enumerate(st.session_state['my_catches'][::-1]):
        st.markdown(f"**{c['date']}** — {c['spec']} | {c['w']} lbs")

# --- TAB 4: LOCKER (Restored Feature) ---
with tabs[3]:
    st.header("🎒 Equipment Inventory")
    if not st.session_state['lures_owned']:
        st.write("Locker is currently empty. Add gear in the sidebar.")
    else:
        for lure in st.session_state['lures_owned']:
            st.markdown(f'<div class="gear-item">🛡️ {lure}</div>', unsafe_allow_html=True)

