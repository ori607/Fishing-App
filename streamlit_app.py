import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import math

# --- 1. SETTINGS ---
st.set_page_config(page_title="FishAI Master Pro", page_icon="🎣", layout="wide")

# --- 2. THE MASTER DATABASE (Expanded & Persistent) ---
# Format: "Name": [Species, Lat, Lon, CoverType, WaterType, Tip, MaxWeight]
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

ALL_SPECIES = sorted(list(set([d[0] for d in SITES.values()])) + [
    "Bluefish", "Channel Catfish", "Blue Catfish", "Flathead Catfish", 
    "Musky", "Walleye", "Brown Trout", "Brook Trout", "Fluke", "Weakfish"
])

ALL_LURES = sorted([
    "Senko (Stick Bait)", "Hollow Body Frog", "Squarebill Crankbait", "Deep Diver",
    "Chatterbait", "Football Jig", "Finesse Jig", "Ned Rig", "Tube Jig", 
    "Bucktail Jig", "Whopper Plopper", "Popper", "Spinnerbait", "Buzzbait",
    "Keitech Swimbait", "Jerkbait", "Inline Spinner", "Marabou Jig"
])

# --- 3. CORE LOGIC FUNCTIONS ---
def haversine(lat1, lon1, lat2, lon2):
    r = 3958.8 
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi, dlambda = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1-a))

def get_solunar_status():
    now = datetime.now()
    # Major windows roughly around dawn/dusk
    if (6 <= now.hour <= 8) or (18 <= now.hour <= 20):
        return "MAJOR Peak", 20
    return "Minor Activity", 5

# --- 4. SESSION STATE ---
if 'locked_spot' not in st.session_state: st.session_state['locked_spot'] = None
if 'user_coords' not in st.session_state: st.session_state['user_coords'] = (40.13, -75.06)
if 'my_catches' not in st.session_state: st.session_state['my_catches'] = []

# --- 5. SIDEBAR (The Control Center) ---
with st.sidebar:
    st.title("Settings")
    user_loc = st.text_input("Home Base:", value="Huntingdon Valley, PA")
    if st.button("Set Location"):
        # Simulated Geocoding
        if "Cape May" in user_loc: st.session_state['user_coords'] = (38.93, -74.90)
        else: st.session_state['user_coords'] = (40.13, -75.06)
        st.rerun()
    
    st.divider()
    st.header("🎒 My Gear Locker")
    if 'lures_owned' not in st.session_state: st.session_state['lures_owned'] = ["Senko", "Frog"]
    st.session_state['lures_owned'] = st.multiselect("Lures in your bag:", ALL_LURES, default=st.session_state['lures_owned'])

    if st.session_state['locked_spot']:
        st.divider()
        st.success(f"Locked: {st.session_state['locked_spot']}")
        if st.button("Reset Selection"):
            st.session_state['locked_spot'] = None
            st.rerun()

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
        # Dynamic Weight Slider
        max_w = 500 if spec_choice and "Shark" in spec_choice else 60 if spec_choice and "Striped" in spec_choice else 15
        target_w = st.slider("Target Weight (lbs):", 1, max_w, 2)

    if spec_choice:
        u_lat, u_lon = st.session_state['user_coords']
        matches = []
        map_points = []
        for name, d in SITES.items():
            dist = haversine(u_lat, u_lon, d[1], d[2])
            if d[0] == spec_choice and dist <= dist_limit and d[6] >= target_w:
                matches.append({"name": name, "dist": round(dist, 1), "tip": d[5], "lat": d[1], "lon": d[2]})
                map_points.append({"lat": d[1], "lon": d[2]})

        if matches:
            st.subheader("📍 Nearby Hotspots")
            st.map(pd.DataFrame(map_points))
            
            for m in matches:
                with st.container():
                    col_txt, col_act = st.columns([3, 1])
                    col_txt.write(f"**{m['name']}** - {m['dist']} miles away")
                    col_txt.caption(f"Pro Tip: {m['tip']}")
                    if col_act.button("Lock Trip", key=m['name']):
                        st.session_state['locked_spot'] = m['name']
                        st.session_state['target_spec'] = spec_choice
                        st.session_state['target_w'] = target_w
                        st.rerun()
                    st.divider()
        else:
            st.warning("No spots found. Try expanding your search radius.")

# --- TAB 2: ADVANCED ANALYSIS ---
with tabs[1]:
    if not st.session_state['locked_spot']:
        st.info("Find a spot in the Strategy Planner and 'Lock Trip' to see live data.")
    else:
        spot = st.session_state['locked_spot']
        s_data = SITES[spot]
        st.header(f"Live Briefing: {spot}")
        
        # TIME & SOLUNAR
        now = datetime.now()
        sol_msg, sol_pts = get_solunar_status()
        
        # WEATHER CALL
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={s_data[1]}&longitude={s_data[2]}&current=temperature_2m,surface_pressure&temperature_unit=fahrenheit"
            res = requests.get(url).json()
            temp = res['current']['temperature_2m']
            pres = round(res['current']['surface_pressure'] * 0.02953, 2)
            
            # COMPLEX BITE SCORE
            bite_score = 60 + sol_pts
            if pres < 29.98: bite_score += 15
            if s_data[4] == "Salt" and (6 <= now.hour <= 12): bite_score += 10 # Simulating tide flood
            
            st.markdown(f"# Bite Score: {min(bite_score, 100)}/100")
            st.subheader(f"{now.strftime('%A, %b %d')} | Window: {sol_msg}")
            
            w1, w2, w3 = st.columns(3)
            w1.metric("Air Temp", f"{temp}°F")
            w2.metric("Pressure", f"{pres} inHg")
            w3.metric("Solunar", sol_msg)
        except:
            st.error("Weather data currently unavailable.")

        st.divider()
        # ACCURATE GEAR LOGIC
        st.subheader("⚙️ Tactical Loadout")
        t_w = st.session_state.get('target_w', 2)
        t_s = st.session_state.get('target_spec', "")
        
        if "Shark" in t_s: r, l = "Heavy Conventional", "100lb Braid + Steel"
        elif t_w < 3: r, l = "6'0\" Ultralight", "4lb Mono"
        elif "Striped" in t_s or t_w > 20: r, l = "7'6\" Heavy", "50lb Braid"
        else: r, l = "7'0\" Medium-Heavy", "12lb Flouro"
        
        st.info(f"**Recommended:** {r} with {l}")

# --- TAB 3: CATCH JOURNAL (NEW FEATURE) ---
with tabs[2]:
    st.header("📸 Personal Catch Log")
    with st.expander("Log a New Catch"):
        c_spec = st.selectbox("Species caught:", ALL_SPECIES)
        c_weight = st.number_input("Weight (lbs):", value=1.0)
        c_img = st.file_uploader("Upload Fish Photo", type=['jpg', 'png'])
        if st.button("Save to Journal"):
            st.session_state['my_catches'].append({"spec": c_spec, "w": c_weight, "date": datetime.now().strftime("%x")})
            st.success("Catch saved!")
    
    if st.session_state['my_catches']:
        for catch in st.session_state['my_catches'][::-1]:
            st.write(f"**{catch['date']}** - {catch['spec']} ({catch['w']} lbs)")
    else:
        st.caption("No catches logged yet. Tight lines!")

# --- TAB 4: LEARN CENTER ---
with tabs[3]:
    st.title("Fishing Academy")
    topic = st.selectbox("Topic:", ["Texas Rig", "Ned Rig", "Solunar Theory"])
    if topic == "Texas Rig":
        st.image("https://upload.wikimedia.org/wikipedia/commons/e/e4/Texas_rig.png", width=400)
    elif topic == "Ned Rig":
        st.image("https://images.tacklewarehouse.com/fishing/Z-Man_Ned_Rig_Kit.jpg", width=400)
    else:
        st.write("Solunar theory suggests fish are more active when the moon is directly overhead or underfoot.")
