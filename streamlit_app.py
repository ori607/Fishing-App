import streamlit as st
import requests
import pandas as pd
import pydeck as pdk
from datetime import datetime
import math

# --- 1. SETTINGS & STYLING ---
st.set_page_config(page_title="FishAI Master Pro", page_icon="🎣", layout="wide")

# --- 2. THE MASTER DATABASE (Full Quality Restoration) ---
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
    now = datetime.now()
    if (6 <= now.hour <= 8) or (18 <= now.hour <= 20):
        return "MAJOR PEAK ACTIVITY", 25
    return "Moderate Activity", 5

# --- 4. SESSION STATE (Crash-Proofing & Quality) ---
if 'locked_spot' not in st.session_state: st.session_state['locked_spot'] = None
if 'user_coords' not in st.session_state: st.session_state['user_coords'] = (40.13, -75.06)
if 'my_catches' not in st.session_state: st.session_state['my_catches'] = []
if 'lures_owned' not in st.session_state: st.session_state['lures_owned'] = ["Senko (Stick Bait)"]

# Cleanup lures to prevent crashes
st.session_state['lures_owned'] = [l for l in st.session_state['lures_owned'] if l in ALL_LURES]

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title("🎛️ Command Center")
    user_loc = st.text_input("Home Base:", value="Huntingdon Valley, PA")
    if st.button("Update Home Coordinates"):
        if "Cape May" in user_loc: st.session_state['user_coords'] = (38.93, -74.90)
        else: st.session_state['user_coords'] = (40.13, -75.06)
        st.rerun()
    
    st.divider()
    st.header("🎒 Tackle Box")
    st.session_state['lures_owned'] = st.multiselect("Lures in your bag:", ALL_LURES, default=st.session_state['lures_owned'])

    if st.session_state['locked_spot']:
        st.divider()
        st.success(f"Trip Locked: {st.session_state['locked_spot']}")
        if st.button("Unlock Trip"):
            st.session_state['locked_spot'] = None
            st.rerun()

# --- 6. MAIN TABS ---
tabs = st.tabs(["🎯 Strategy Planner", "📊 Advanced Analysis", "📸 Catch Journal", "📚 Learn Center"])

# --- TAB 1: STRATEGY PLANNER (Modern Map Integration) ---
with tabs[0]:
    st.title("Target Acquisition")
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        spec_choice = st.selectbox("Search Species:", [None] + ALL_SPECIES)
    with c2:
        dist_limit = st.number_input("Max Miles:", value=100)
    with c3:
        max_w = 500 if spec_choice and "Shark" in spec_choice else 60 if spec_choice and "Striped" in spec_choice else 15
        target_lb = st.slider("Target Weight (lbs):", 1, max_w, 2)

    if spec_choice:
        u_lat, u_lon = st.session_state['user_coords']
        matches = []
        map_points = []
        
        # Add User Location to map (Blue Dot)
        map_points.append({"lat": u_lat, "lon": u_lon, "name": "HOME BASE", "type": "User", "color": [0, 100, 255, 200]})

        for name, d in SITES.items():
            dist = haversine(u_lat, u_lon, d[1], d[2])
            if d[0] == spec_choice and dist <= dist_limit:
                matches.append({"name": name, "dist": round(dist, 1), "tip": d[5], "lat": d[1], "lon": d[2], "max_w": d[6]})
                map_points.append({"lat": d[1], "lon": d[2], "name": name, "type": "Spot", "color": [40, 200, 100, 200]})

        if matches:
            st.subheader("📍 Interactive Tactical Map")
            # Modern PyDeck Map
            st.pydeck_chart(pdk.Deck(
                map_style='mapbox://styles/mapbox/satellite-streets-v11',
                initial_view_state=pdk.ViewState(latitude=u_lat, longitude=u_lon, zoom=9, pitch=45),
                layers=[
                    pdk.Layer(
                        'ScatterplotLayer',
                        data=pd.DataFrame(map_points),
                        get_position='[lon, lat]',
                        get_color='color',
                        get_radius=800,
                        pickable=True,
                    ),
                ],
                tooltip={"text": "{name}"}
            ))
            
            st.divider()
            for m in matches:
                with st.container():
                    col_txt, col_act = st.columns([3, 1])
                    col_txt.write(f"### {m['name']}")
                    col_txt.write(f"📏 Distance: {m['dist']}mi | 🏆 Potential: {m['max_w']}lb")
                    col_txt.caption(f"💡 Tip: {m['tip']}")
                    if col_act.button("Lock Trip", key=m['name']):
                        st.session_state['locked_spot'] = m['name']
                        st.session_state['target_spec'] = spec_choice
                        st.session_state['target_w'] = target_lb
                        st.rerun()
                    st.divider()
    else:
        st.warning("Please select a fish species to begin tactical search.")

# --- TAB 2: ADVANCED ANALYSIS (Full Quality Restoration) ---
with tabs[1]:
    if not st.session_state['locked_spot']:
        st.info("Please 'Lock Trip' in the Strategy Planner first.")
    else:
        spot = st.session_state['locked_spot']
        s_data = SITES[spot]
        st.header(f"Live Briefing: {spot}")
        
        # Time & Solunar Restoration
        now = datetime.now()
        sol_msg, sol_pts = get_solunar_status()
        st.subheader(f"📅 {now.strftime('%A, %b %d')} | {now.strftime('%I:%M %p')}")
        
        # Weather Call
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={s_data[1]}&longitude={s_data[2]}&current=temperature_2m,surface_pressure,wind_speed_10m&temperature_unit=fahrenheit"
            res = requests.get(url).json()
            temp = res['current']['temperature_2m']
            pres = round(res['current']['surface_pressure'] * 0.02953, 2)
            wind = res['current']['wind_speed_10m']
            
            # Complex Bite Score Logic
            bite_score = 65 + sol_pts
            if pres < 30.00: bite_score += 10 # Rising/Stable pressure is okay, dropping is better
            if 65 < temp < 78: bite_score += 5
            
            st.markdown(f"# Real-Time Bite Score: {min(bite_score, 100)}/100")
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Air Temp", f"{temp}°F")
            m2.metric("Pressure", f"{pres} inHg")
            m3.metric("Wind Speed", f"{wind} mph")
            m4.metric("Solunar Status", sol_msg)
        except:
            st.error("Live weather data stream interrupted.")

        st.divider()
        # Gear & Setup Logic Restoration
        st.subheader("⚙️ Recommended Setup")
        t_w = st.session_state.get('target_w', 2)
        t_s = st.session_state.get('target_spec', "")
        
        if "Shark" in t_s: r, l = "7'6\" Heavy Conventional", "100lb Braid + Steel Leader"
        elif t_w < 4: r, l = "6'0\" Ultralight Spinning", "4lb-6lb Monofilament"
        elif "Striped" in t_s or t_w > 30: r, l = "7'10\" Extra-Heavy", "65lb Braid"
        else: r, l = "7'0\" Medium-Heavy / Fast Action", "15lb Fluorocarbon"
        
        st.info(f"**Rod:** {r} | **Line:** {l}")
        
        st.divider()
        # Lure Logic Restoration
        col_l, col_r = st.columns(2)
        with col_l:
            st.subheader("🎒 From Your Bag")
            user_lures = st.session_state['lures_owned']
            if user_lures:
                best = "Senko" if "Senko" in str(user_lures) else user_lures[0]
                st.write(f"**Top Choice:** {best}")
            else: st.write("Add lures in the sidebar!")
        with col_r:
            st.subheader("🎣 Pro Pick")
            st.write("**Expert Recommendation:** 3/8oz Chatterbait (White/Chartreuse)")

# --- TAB 3: CATCH JOURNAL (With Deletion Fix) ---
with tabs[2]:
    st.header("📸 Personal Catch Log")
    
    with st.expander("➕ Log a New Catch"):
        c_spec = st.selectbox("Species:", ALL_SPECIES)
        c_w = st.number_input("Weight (lbs):", min_value=0.1, step=0.1)
        if st.button("Commit to Log"):
            st.session_state['my_catches'].append({
                "id": len(st.session_state['my_catches']), 
                "spec": c_spec, "w": c_w, "date": datetime.now().strftime("%x")
            })
            st.success("Catch saved to the vault.")
            st.rerun()

    st.divider()
    if st.session_state['my_catches']:
        for i, catch in enumerate(st.session_state['my_catches'][::-1]):
            # Use a unique key for each button to allow deletion
            c1, c2 = st.columns([4, 1])
            c1.write(f"**{catch['date']}** - {catch['spec']} ({catch['w']} lbs)")
            if c2.button("🗑️ Delete", key=f"del_{i}"):
                # Remove by reverse index
                idx = len(st.session_state['my_catches']) - 1 - i
                st.session_state['my_catches'].pop(idx)
                st.rerun()
    else:
        st.caption("Your fishing history is currently empty.")

# --- TAB 4: LEARN CENTER ---
with tabs[3]:
    st.title("Fishing Academy")
    topic = st.selectbox("Advanced Topic:", ["Texas Rig", "Solunar Theory", "Reading a Map"])
    if topic == "Texas Rig":
        st.image("https://upload.wikimedia.org/wikipedia/commons/e/e4/Texas_rig.png", width=400)
        st.write("The gold standard for weedless bass fishing.")
    elif topic == "Solunar Theory":
        st.write("Solunar theory tracks the position of the moon to predict feeding frenzies.")
        
    else:
        st.write("A good topological map shows you where the 'holes' are. Look for dark blue spots.")
