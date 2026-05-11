import streamlit as st
import requests
import pandas as pd
import pydeck as pdk
from datetime import datetime
import math
import json
import os

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="FishAI Elite Tactical",
    page_icon="🎣",
    layout="wide"
)

# =========================================================
# TACTICAL UI STYLING
# =========================================================

st.markdown("""
<style>

/* GLOBAL */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.main {
    background: linear-gradient(to bottom right, #0f172a, #111827);
    color: white;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}

/* HEADINGS */

h1, h2, h3 {
    color: white;
    letter-spacing: -0.03em;
}

/* SIDEBAR */

section[data-testid="stSidebar"] {
    background: #0b1220;
    border-right: 1px solid #1e293b;
}

/* TABS */

.stTabs [data-baseweb="tab-list"] {
    gap: 12px;
}

.stTabs [data-baseweb="tab"] {
    background: #1e293b;
    border-radius: 12px;
    padding: 10px 20px;
    color: white;
    font-weight: 700;
}

.stTabs [aria-selected="true"] {
    background: #2563eb;
}

/* METRIC CARDS */

.metric-card {
    background: linear-gradient(145deg, #1e293b, #111827);
    border-radius: 18px;
    padding: 18px;
    border: 1px solid #334155;
    margin-bottom: 15px;
    box-shadow: 0px 6px 18px rgba(0,0,0,0.35);
}

.metric-label {
    color: #94a3b8;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 700;
}

.metric-value {
    color: white;
    font-size: 1.4rem;
    font-weight: 800;
    margin-top: 6px;
}

/* GEAR ITEMS */

.gear-item {
    background: #1e293b;
    padding: 8px 16px;
    border-radius: 999px;
    display: inline-block;
    margin: 6px;
    color: white;
    border: 1px solid #334155;
    font-weight: 600;
}

/* MAP */

iframe {
    border-radius: 22px !important;
    overflow: hidden !important;
}

/* EXPANDERS */

.streamlit-expanderHeader {
    background-color: #1e293b;
    border-radius: 12px;
}

/* BUTTONS */

.stButton button {
    border-radius: 12px;
    background: linear-gradient(to right, #2563eb, #1d4ed8);
    color: white;
    border: none;
    font-weight: 700;
    padding: 0.6rem 1rem;
}

.stButton button:hover {
    background: linear-gradient(to right, #3b82f6, #2563eb);
    color: white;
}

/* INPUTS */

.stTextInput input,
.stNumberInput input,
.stSelectbox div {
    background-color: #111827 !important;
    color: white !important;
    border-radius: 10px !important;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# DATABASE
# =========================================================

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

ALL_SPECIES = sorted([
    "Largemouth Bass",
    "Smallmouth Bass",
    "Striped Bass",
    "Bull Shark",
    "Rainbow Trout",
    "Bluefish",
    "Catfish",
    "Musky",
    "Walleye"
])

ALL_LURES = sorted([
    "Senko (Green Pumpkin)",
    "Hollow Body Frog",
    "Chatterbait Jackhammer",
    "Ned Rig",
    "Whopper Plopper",
    "Keitech Swimbait",
    "Bucktail Jig",
    "Squarebill",
    "Jerkbait"
])

species_colors = {
    "Largemouth Bass": [0, 255, 120, 255],
    "Smallmouth Bass": [255, 170, 0, 255],
    "Striped Bass": [0, 180, 255, 255],
    "Bull Shark": [255, 50, 50, 255],
    "Rainbow Trout": [180, 0, 255, 255]
}

# =========================================================
# DATA STORAGE
# =========================================================

DB_FILE = "fishing_master_db.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {"catches": [], "lures": []}

def save_data():
    data = {
        "catches": st.session_state['my_catches'],
        "lures": st.session_state['lures_owned']
    }

    with open(DB_FILE, "w") as f:
        json.dump(data, f)

# =========================================================
# INITIALIZE SESSION
# =========================================================

if 'init' not in st.session_state:

    saved = load_data()

    st.session_state['my_catches'] = saved.get("catches", [])
    st.session_state['lures_owned'] = saved.get("lures", [])
    st.session_state['locked_spot'] = None
    st.session_state['user_coords'] = (40.13, -75.06)

    st.session_state['init'] = True

# =========================================================
# UTILITY FUNCTIONS
# =========================================================

def haversine(lat1, lon1, lat2, lon2):

    r = 3958.8

    p1 = math.radians(lat1)
    p2 = math.radians(lat2)

    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)

    a = math.sin(dp / 2)**2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2)**2

    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def get_weather_intel(lat, lon):

    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,surface_pressure,wind_speed_10m"
            f"&temperature_unit=fahrenheit"
        )

        res = requests.get(url).json()

        c = res['current']

        return {
            "temp": c['temperature_2m'],
            "pres": round(c['surface_pressure'] * 0.02953, 2),
            "wind": c['wind_speed_10m']
        }

    except:
        return None

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("🦅 Tactical Ops")

    loc_input = st.text_input(
        "Current Base:",
        value="Huntingdon Valley, PA"
    )

    if st.button("Sync GPS"):

        st.session_state['user_coords'] = (
            (38.93, -74.90)
            if "Cape May" in loc_input
            else (40.13, -75.06)
        )

        st.rerun()

    st.divider()

    st.header("🧰 Gear Locker")

    new_lures = st.multiselect(
        "Stock Your Bag:",
        ALL_LURES,
        default=st.session_state['lures_owned']
    )

    if new_lures != st.session_state['lures_owned']:
        st.session_state['lures_owned'] = new_lures
        save_data()

    if st.session_state['locked_spot']:

        st.success(f"Objective Locked: {st.session_state['locked_spot']}")

        if st.button("Abort Mission"):
            st.session_state['locked_spot'] = None
            st.rerun()

# =========================================================
# MAIN TABS
# =========================================================

tabs = st.tabs([
    "🎯 Strategy",
    "📊 Intel",
    "📸 Logbook",
    "🎒 Locker"
])

# =========================================================
# TAB 1 - STRATEGY
# =========================================================

with tabs[0]:

    st.title("🎯 Target Acquisition")

    target = st.selectbox(
        "Select Target Species:",
        [None] + ALL_SPECIES
    )

    if target:

        u_lat, u_lon = st.session_state['user_coords']

        matches = []

        map_points = [{
            "lat": u_lat,
            "lon": u_lon,
            "name": "YOUR POSITION",
            "color": [0, 255, 180, 255]
        }]

        for name, d in SITES.items():

            if d[0] == target:

                matches.append({
                    "name": name,
                    "dist": round(haversine(u_lat, u_lon, d[1], d[2]), 1),
                    "tip": d[5],
                    "lat": d[1],
                    "lon": d[2]
                })

                map_points.append({
                    "lat": d[1],
                    "lon": d[2],
                    "name": name,
                    "color": species_colors.get(target, [255,255,255,255])
                })

        map_df = pd.DataFrame(map_points)

        # PATHS

        line_data = []

        for m in matches:

            line_data.append({
                "path": [
                    [u_lon, u_lat],
                    [m["lon"], m["lat"]]
                ]
            })

        # VIEW

        view_state = pdk.ViewState(
            latitude=u_lat,
            longitude=u_lon,
            zoom=11,
            pitch=50,
            bearing=15
        )

        # LAYERS

        line_layer = pdk.Layer(
            "PathLayer",
            data=line_data,
            get_path="path",
            get_color=[0, 255, 255],
            width_scale=6,
            width_min_pixels=2,
            get_width=4,
            opacity=0.45
        )

        scatter_layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position='[lon, lat]',
            get_fill_color='color',
            get_radius=180,
            opacity=0.85,
            pickable=True,
            stroked=True,
            filled=True,
            radius_min_pixels=8,
            radius_max_pixels=25,
            line_width_min_pixels=2
        )

        text_layer = pdk.Layer(
            "TextLayer",
            data=map_df,
            get_position='[lon, lat]',
            get_text='name',
            get_size=14,
            get_color=[255,255,255],
            get_alignment_baseline="'bottom'"
        )

        # MAP

        st.pydeck_chart(
            pdk.Deck(
                map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
                initial_view_state=view_state,
                layers=[
                    line_layer,
                    scatter_layer,
                    text_layer
                ],
                tooltip={
                    "html": """
                    <div style="
                        background-color:#111827;
                        padding:12px;
                        border-radius:12px;
                        color:white;
                    ">
                        <b>{name}</b>
                    </div>
                    """,
                    "style": {
                        "backgroundColor": "transparent",
                        "color": "white"
                    }
                }
            ),
            use_container_width=True
        )

        # LOCATION CARDS

        for m in matches:

            with st.expander(f"📍 {m['name']} ({m['dist']} mi)"):

                st.write(f"### Tactical Notes")
                st.write(m['tip'])

                if st.button("Lock Location", key=m['name']):

                    st.session_state['locked_spot'] = m['name']
                    st.rerun()

# =========================================================
# TAB 2 - INTEL
# =========================================================

with tabs[1]:

    if not st.session_state['locked_spot']:

        st.info("Awaiting location lock from Strategy tab.")

    else:

        spot = st.session_state['locked_spot']

        lat, lon = SITES[spot][1], SITES[spot][2]

        intel = get_weather_intel(lat, lon)

        st.title(f"📊 Live Intel — {spot}")

        if intel:

            c1, c2 = st.columns(2)

            with c1:

                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Atmospheric Conditions</div>
                    <div class="metric-value">
                        {intel["temp"]}°F | {intel["pres"]} inHg
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with c2:

                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Wind Velocity</div>
                    <div class="metric-value">
                        {intel["wind"]} mph
                    </div>
                </div>
                """, unsafe_allow_html=True)

            score = 75

            if intel['pres'] < 30.0:
                score += 10

            if 6 <= datetime.now().hour <= 9:
                score += 15

            st.markdown(f"""
            <div class="metric-card"
                 style="border-left: 6px solid #00ffff;">
                <div class="metric-label">
                    Probability of Strike
                </div>
                <div class="metric-value"
                     style="font-size:2.5rem;">
                    {min(score,100)}%
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.subheader("🛡️ Tactical Recommendation")

        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">
                Primary Loadout
            </div>

            <div class="metric-value"
                 style="font-size:1rem; line-height:1.8;">
                 
                <b>Rod:</b> 7'0 Medium-Heavy Fast Action<br>
                <b>Line:</b> 15lb Fluorocarbon Mainline<br>
                <b>Primary Objective:</b> Wind-blown points and hard cover.<br>
                <b>Best Retrieve:</b> Slow roll with pauses near structure.
            </div>
        </div>
        """, unsafe_allow_html=True)

# =========================================================
# TAB 3 - LOGBOOK
# =========================================================

with tabs[2]:

    st.title("📸 Recon Logs")

    with st.form("new_catch"):

        f_spec = st.selectbox(
            "Species:",
            ALL_SPECIES
        )

        f_weight = st.number_input(
            "Weight (lbs):",
            min_value=0.1
        )

        submitted = st.form_submit_button("Confirm Catch")

        if submitted:

            st.session_state['my_catches'].append({
                "spec": f_spec,
                "w": f_weight,
                "date": datetime.now().strftime("%x")
            })

            save_data()

            st.rerun()

    st.divider()

    for c in st.session_state['my_catches'][::-1]:

        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{c['date']}</div>
            <div class="metric-value">
                {c['spec']} — {c['w']} lbs
            </div>
        </div>
        """, unsafe_allow_html=True)

# =========================================================
# TAB 4 - LOCKER
# =========================================================

with tabs[3]:

    st.title("🎒 Equipment Inventory")

    if not st.session_state['lures_owned']:

        st.write("Locker is currently empty. Add gear in the sidebar.")

    else:

        for lure in st.session_state['lures_owned']:

            st.markdown(
                f'<div class="gear-item">🛡️ {lure}</div>',
                unsafe_allow_html=True
            )
