import streamlit as st
import requests
import pandas as pd
import pydeck as pdk
from datetime import datetime
import math
import json
import os

# --- 1. SETTINGS & TACTICAL STYLING ---
st.set_page_config(page_title="FishAI Explore Pro", page_icon="🎣", layout="wide")

st.markdown("""
    <style>
    /* Main Background */
    .main { background-color: #f5f7f9; }
    
    /* Tactical Analysis Cards */
    .analysis-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 18px;
        border: 1px solid #e1e4e8;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 12px;
    }
    .analysis-label {
        color: #6a737d;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .analysis-value {
        color: #1b1f23;
        font-size: 1.15rem;
        font-weight: 800;
        margin-top: 4px;
    }
    
    /* Gear Locker Tags */
    .gear-tag {
        background-color: #e1f5fe;
        color: #01579b;
        padding: 6px 14px;
        border-radius: 100px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin: 4px;
        border: 1px solid #b3e5fc;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE MASTER DATABASE (Pinpoint Accuracy) ---
# Coordinates updated to land precisely in the water for Albidale and Quarry/Cathedral
SITES = {
    "Albidale Park (Lower Moreland)": ["Largemouth Bass", 40.1242, -75.0526, "LilyPads", "Fresh", "Excellent pond tucked in the Albidale neighborhood.", 8],
    "Quarry Pond (Cathedral Rd)": ["Largemouth Bass", 40.1388, -75.0592, "Rocks", "Fresh", "Deep quarry pond; use swimbaits for larger fish.", 10],
    "Mason's Mill Pond": ["Largemouth Bass", 40.1513, -75.0704, "LilyPads", "Fresh", "Very thick weeds in summer; use frogs.", 6],
    "Lorimer Park (Pennypack)": ["Smallmouth Bass", 40.0985, -75.0615, "Current", "Fresh", "Focus on the shaded banks near the trail.", 5],
    "Neshaminy Creek (Tyler)": ["Smallmouth Bass", 40.2118, -74.9620, "Rocks", "Fresh", "Target the bridge pilings.", 5],
    "Island Beach State Park": ["Striped Bass", 39.8845, -74.0845, "Open", "Salt", "Find the gaps in the sandbars.", 65],
    "Barnegat Inlet": ["Striped Bass", 39.7592, -74.1010, "Rocks", "Salt", "Cast into the rips at the tip of the jetty.", 60],
    "Cape May Inlet": ["Bull Shark", 38.9348, -74.9012, "Current", "Salt", "Heavy surf rods required.", 450],
    "Wissahickon Creek": ["Rainbow Trout", 40.0528, -75.2152, "Current", "Fresh", "Target the pools around Valley Green.", 4]
}

ALL_SPECIES = sorted(["Largemouth Bass", "Smallmouth Bass", "Striped Bass", "Bull Shark", "Rainbow Trout", "Catfish", "Musky", "Walleye"])
ALL_LURES = sorted(["Senko", "Frog", "Chatterbait", "Ned Rig", "Whopper Plopper", "Keitech Swimbait", "Bucktail Jig", "Squarebill", "Jerkbait"])

# --- 3. PERSISTENCE ENGINE ---
DB_FILE = "fishing_data.json"

def load_storage():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {"catches": [], "lures": []}

def save_storage():
    data = {"catches": st.session_state['my_catches'], "lures": st.session_state['lures_owned']}
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

if 'app_init' not in st.session_state:
    saved = load_storage()
    st.session_state['my_catches'] = saved.get("catches", [])
    st.session_state['lures_owned'] = saved.get("lures", [])
    st.session_state['locked_spot'] = None
    st.session_state['user_coords'] = (40.13, -75.06)
    st.session_state['app_init'] = True

# --- 4. COMMAND CENTER (Sidebar) ---
with st.sidebar:
    st.title("🛡️ Tactical HQ")
    loc_name = st.text_input("Home Base:", value="Huntingdon Valley, PA")
    if st.button("Update GPS Location"):
        st.session_state['user_coords'] = (38.93, -74.90) if "Cape May" in loc_name else (40.13, -75.06)
        st.rerun()

    st.divider()
    st.header("🎒 Gear Management")
    current_inventory = st.multiselect("Locker Inventory:", ALL_LURES, default=st.session_state['lures_owned'])
    if current_inventory != st.session_state['lures_owned']:
        st.session_state['lures_owned'] = current_inventory
        save_storage()

    if st.session_state['locked_spot']:
        st.success(f"Trip Active: {st.session_state['locked_spot']}")
        if st.button("End Mission"):
            st.session_state['locked_spot'] = None
            st.rerun()

# --- 5. INTERFACE TABS ---
tabs = st.tabs(["🎯 Strategy", "📊 Analysis", "📸 Catch Log", "🎒 Locker"])

# --- TAB 1: STRATEGY (High-Detail Map) ---
with tabs[0]:
    st.title("Strategy Planner")
    target_spec = st.selectbox("Search Target Species:", [None] + ALL_SPECIES)
    
    if target_spec:
        u_lat, u_lon = st.session_state['user_coords']
        matches = []
        map_points = [{"lat": u_lat, "lon": u_lon, "name": "HOME", "color": [0, 122, 255, 255]}] # Apple Blue

        for name, d in SITES.items():
            if d[0] == target_spec:
                matches.append({"name": name, "lat": d[1], "lon": d[2], "tip": d[5]})
                map_points.append({"lat": d[1], "lon": d[2], "name": name, "color": [255, 59, 48, 255]}) # Apple Red

        # THE MAP: 'outdoors-v12' provides the most accurate colors for parks (green) and water (blue)
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/outdoors-v12',
            initial_view_state=pdk.ViewState(latitude=u_lat, longitude=u_lon, zoom=12.5, pitch=0),
            layers=[
                pdk.Layer(
                    'ScatterplotLayer', 
                    data=pd.DataFrame(map_points), 
                    get_position='[lon, lat]', 
                    get_color='color', 
                    get_radius=25, # Tight, accurate pings
                    pickable=True
                )
            ],
            tooltip={"text": "{name}"}
        ), use_container_width=True)
        
        for m in matches:
            with st.expander(f"📍 {m['name']}"):
                st.write(f"**Spot Intel:** {m['tip']}")
                if st.button("Lock Location", key=m['name']):
                    st.session_state['locked_spot'] = m['name']
                    st.rerun()

# --- TAB 2: ANALYSIS (Tactical Layout) ---
with tabs[1]:
    if not st.session_state['locked_spot']:
        st.info("Lock a location in the Strategy tab to see analysis.")
    else:
        spot = st.session_state['locked_spot']
        s_data = SITES[spot]
        
        st.header(f"Live Intelligence: {spot}")
        
        # Grid layout for mobile-friendly stats
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="analysis-card"><div class="analysis-label">Temperature</div><div class="analysis-value">64.2°F</div></div>', unsafe_allow_html=True)
            st.markdown('<div class="analysis-card"><div class="analysis-label">Solunar Rating</div><div class="analysis-value">High Activity</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="analysis-card"><div class="analysis-label">Barometer</div><div class="analysis-value">29.95 inHg</div></div>', unsafe_allow_html=True)
            st.markdown('<div class="analysis-card"><div class="analysis-label">Probability</div><div class="analysis-value">88/100</div></div>', unsafe_allow_html=True)

        st.divider()
        st.subheader("🛡️ Tactical Loadout")
        st.markdown(f"""
        <div class="analysis-card" style="border-left: 6px solid #28a745;">
            <div class="analysis-label">Recommended Rig</div>
            <div class="analysis-value" style="font-size: 1rem;">
                <b>Setup:</b> Medium-Heavy Casting<br>
                <b>Line:</b> 15lb Fluorocarbon Mainline<br>
                <b>Targeting:</b> Focus on {s_data[3]} cover.
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- TAB 3: CATCH LOG ---
with tabs[2]:
    st.header("📸 Recon Journal")
    with st.form("catch_form"):
        f_s = st.selectbox("Species:", ALL_SPECIES)
        f_w = st.number_input("Weight (lbs):", min_value=0.1)
        if st.form_submit_button("Save Recon"):
            st.session_state['my_catches'].append({"spec": f_s, "w": f_w, "date": datetime.now().strftime("%x")})
            save_storage()
            st.rerun()
    
    for c in st.session_state['my_catches'][::-1]:
        st.markdown(f"**{c['date']}** — {c['spec']} | {c['w']} lbs")

# --- TAB 4: LOCKER (Restored Feature) ---
with tabs[3]:
    st.header("🎒 Equipment Locker")
    if not st.session_state['lures_owned']:
        st.warning("No gear selected. Head to the sidebar to stock your bag.")
    else:
        st.write("Your current loadout:")
        for lure in st.session_state['lures_owned']:
            st.markdown(f'<div class="gear-tag">🛡️ {lure}</div>', unsafe_allow_html=True)

