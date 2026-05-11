import streamlit as st
import requests
import pandas as pd
import pydeck as pdk
from datetime import datetime
import math
import json
import os

# --- 1. SETTINGS & REFINED MOBILE STYLING ---
st.set_page_config(page_title="FishAI Explore", page_icon="🎣", layout="wide")

st.markdown("""
    <style>
    /* Tactical Card Styling */
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e6e9ef;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    .metric-header {
        color: #5e6c84;
        font-size: 0.8rem;
        text-transform: uppercase;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 1.2rem;
        font-weight: bold;
        color: #172b4d;
    }
    /* Tab Styling for Mobile */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { font-size: 14px; padding: 10px 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE MASTER DATABASE ---
SITES = {
    "Quarry Road Pond (Bryn Athyn)": ["Largemouth Bass", 40.135, -75.064, "Rocks", "Fresh", "Focus on steep drop-offs.", 8],
    "Lower Moreland Park Lake": ["Largemouth Bass", 40.121, -75.055, "LilyPads", "Fresh", "Fish near the drain pipe.", 6],
    "Mason's Mill Pond": ["Largemouth Bass", 40.151, -75.071, "LilyPads", "Fresh", "Heavy vegetation; use weedless.", 5],
    "Pennypack (Lorimer)": ["Smallmouth Bass", 40.101, -75.062, "Current", "Fresh", "Target current breaks behind rocks.", 5],
    "Neshaminy Creek (Tyler Park)": ["Smallmouth Bass", 40.211, -74.962, "Rocks", "Fresh", "Deep pools near the dam.", 4],
    "Delaware River (Lumberville)": ["Smallmouth Bass", 40.401, -75.041, "Current", "Fresh", "Best local smallie fishery.", 6],
    "Island Beach State Park": ["Striped Bass", 39.885, -74.085, "Open", "Salt", "Target the 'sloughs'.", 60],
    "Barnegat Inlet": ["Striped Bass", 39.758, -74.101, "Rocks", "Salt", "High current; use heavy jigs.", 55],
    "Cape May Inlet": ["Bull Shark", 38.933, -74.903, "Current", "Salt", "Use wire leaders and fresh bait.", 400],
    "Wissahickon Creek": ["Rainbow Trout", 40.071, -75.212, "Current", "Fresh", "Stocked sections near valley green.", 4]
}

ALL_SPECIES = sorted(["Largemouth Bass", "Smallmouth Bass", "Striped Bass", "Bull Shark", "Rainbow Trout", "Bluefish", "Channel Catfish", "Walleye", "Carp"])
ALL_LURES = sorted(["Senko", "Frog", "Crankbait", "Chatterbait", "Jig", "Whopper Plopper", "Spinnerbait", "Swimbait"])

# --- 3. CORE LOGIC ---
def haversine(lat1, lon1, lat2, lon2):
    r = 3958.8 
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi, dlambda = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1-a))

# --- 4. SESSION STATE ---
if 'locked_spot' not in st.session_state: st.session_state['locked_spot'] = None
if 'user_coords' not in st.session_state: st.session_state['user_coords'] = (40.13, -75.06)
if 'my_catches' not in st.session_state: st.session_state['my_catches'] = []

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title("🎛️ Command")
    user_loc = st.text_input("Home Base:", value="Huntingdon Valley, PA")
    if st.button("Update GPS"):
        st.session_state['user_coords'] = (38.93, -74.90) if "Cape May" in user_loc else (40.13, -75.06)
        st.rerun()
    
    if st.session_state['locked_spot']:
        st.success(f"Locked: {st.session_state['locked_spot']}")
        if st.button("End Trip"):
            st.session_state['locked_spot'] = None
            st.rerun()

# --- 6. MAIN TABS ---
tabs = st.tabs(["🎯 Strategy", "📊 Analysis", "📸 Log"])

# --- TAB 1: STRATEGY (The Clean Apple-Style Map) ---
with tabs[0]:
    st.title("Target Acquisition")
    spec_search = st.selectbox("Search Species:", [None] + ALL_SPECIES)
    
    if spec_search:
        u_lat, u_lon = st.session_state['user_coords']
        map_points = [{"lat": u_lat, "lon": u_lon, "name": "HOME", "color": [0, 122, 255, 200]}] # Apple Blue

        matches = []
        for name, d in SITES.items():
            if d[0] == spec_search:
                matches.append({"name": name, "dist": round(haversine(u_lat, u_lon, d[1], d[2]), 1), "tip": d[5], "lat": d[1], "lon": d[2]})
                map_points.append({"lat": d[1], "lon": d[2], "name": name, "color": [255, 59, 48, 200]}) # Apple Red

        # MAP FIX: Using "light" style for that Explore look and no-token reliability
        st.pydeck_chart(pdk.Deck(
            map_style='light', 
            initial_view_state=pdk.ViewState(latitude=u_lat, longitude=u_lon, zoom=11, pitch=0),
            layers=[pdk.Layer('ScatterplotLayer', data=pd.DataFrame(map_points), get_position='[lon, lat]', get_color='color', get_radius=300, pickable=True)],
            tooltip={"text": "{name}"}
        ), use_container_width=True)
        
        for m in matches:
            with st.expander(f"📍 {m['name']} ({m['dist']} mi)"):
                st.write(f"**Tip:** {m['tip']}")
                if st.button("Lock Location", key=m['name']):
                    st.session_state['locked_spot'] = m['name']
                    st.rerun()

# --- TAB 2: ANALYSIS (Redesigned Cards) ---
with tabs[1]:
    if not st.session_state['locked_spot']:
        st.info("Please select a spot in the Strategy tab.")
    else:
        spot = st.session_state['locked_spot']
        s_data = SITES[spot]
        
        st.header(f"Live Intelligence: {spot}")
        
        # Weather Card (Simplified Columns)
        col_w1, col_w2 = st.columns(2)
        with col_w1:
            st.markdown(f'<div class="metric-card"><div class="metric-header">Temperature</div><div class="metric-value">62.4°F</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-card"><div class="metric-header">Bite Score</div><div class="metric-value">94/100</div></div>', unsafe_allow_html=True)
        with col_w2:
            st.markdown(f'<div class="metric-card"><div class="metric-header">Pressure</div><div class="metric-value">29.8 inHg</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-card"><div class="metric-header">Wind</div><div class="metric-value">8 mph NW</div></div>', unsafe_allow_html=True)

        st.divider()
        st.subheader("🛠️ Tactical Setup")
        
        # Setup Card
        st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid #34c759;">
            <div class="metric-header">Gear Recommendation</div>
            <div class="metric-value" style="font-size: 1rem;">
                <b>Rod:</b> Medium-Heavy Casting<br>
                <b>Line:</b> 15lb Fluorocarbon<br>
                <b>Lure:</b> 3/8oz Black/Blue Jig
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- TAB 3: LOG ---
with tabs[2]:
    st.header("📸 Catch Journal")
    with st.form("catch_log"):
        fish = st.selectbox("Fish:", ALL_SPECIES)
        weight = st.number_input("Weight:", min_value=0.1)
        if st.form_submit_button("Log Entry"):
            st.session_state['my_catches'].append(f"{fish} ({weight} lbs)")
            st.rerun()
    
    for c in st.session_state['my_catches'][::-1]:
        st.write(f"✅ {c}")

