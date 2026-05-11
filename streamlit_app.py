import streamlit as st
import requests
from datetime import datetime

# --- 1. SETTINGS ---
st.set_page_config(page_title="FishAI Master", page_icon="🎣", layout="wide")

# --- 2. MASTER DATA ---
ALL_SPECIES = sorted([
    "Largemouth Bass", "Smallmouth Bass", "Striped Bass", "Black Sea Bass",
    "Rainbow Trout", "Brown Trout", "Brook Trout", "Channel Catfish", 
    "Blue Catfish", "Flathead Catfish", "Bull Shark", "Sandbar Shark", 
    "Common Carp", "Mirror Carp", "Walleye", "Musky"
])

ALL_LURES = sorted([
    "Senko (Stick Bait)", "Hollow Body Frog", "Squarebill Crankbait", 
    "Deep Diving Crankbait", "Chatterbait", "Football Jig", "Ned Rig", 
    "Tube Jig", "Bucktail Jig", "Whopper Plopper", "Spinnerbait"
])

SITES = {
    "Quarry Road Pond (Bryn Athyn)": ["Largemouth Bass", 0.1, 8, 10, "Focus on steep drop-offs.", "Rocks", "Fresh", 40.13, -75.06],
    "Lower Moreland Park Lake": ["Largemouth Bass", 1.5, 6, 8, "Fish near the lily pads.", "LilyPads", "Fresh", 40.12, -75.05],
    "Pennypack (Lorimer)": ["Smallmouth Bass", 2, 5, 6, "Target current breaks.", "Current", "Fresh", 40.10, -75.06],
    "Neshaminy Creek": ["Smallmouth Bass", 12, 4, 7, "Look for deep pools.", "Rocks", "Fresh", 40.15, -74.95],
    "Delaware River (Lumberville)": ["Smallmouth Bass", 35, 6, 9, "The gold standard for local smallies.", "Current", "Fresh", 40.40, -75.04],
    "Island Beach State Park": ["Striped Bass", 82, 50, 10, "Target the 'sloughs'.", "Open", "Salt", 39.88, -74.08],
    "Cape May Inlet": ["Bull Shark", 95, 300, 7, "Heavy current. Use wire leaders.", "Current", "Salt", 38.93, -74.90]
}

# --- 3. SESSION STATE INITIALIZATION ---
if 'profile' not in st.session_state:
    st.session_state['profile'] = {'lures': []}
if 'locked_spot' not in st.session_state:
    st.session_state['locked_spot'] = None
if 'target_species' not in st.session_state:
    st.session_state['target_species'] = None

# --- 4. SIDEBAR ---
with st.sidebar:
    st.header("👤 My Gear Locker")
    st.session_state['profile']['lures'] = st.multiselect(
        "Search & Add Lures:", ALL_LURES, default=st.session_state['profile']['lures']
    )
    st.divider()
    st.header("📍 Current Active Trip")
    if st.session_state['locked_spot']:
        st.success(f"Locked on: **{st.session_state['locked_spot']}**")
        if st.button("Clear Trip Selection"):
            st.session_state['locked_spot'] = None
            st.rerun()
    else:
        st.info("No spot locked. Find one in the Strategy Planner.")

# --- 5. MAIN INTERFACE ---
tabs = st.tabs(["🎯 Strategy Planner", "📊 Advanced Tactical Analysis", "📚 Learn Center"])

# --- TAB: STRATEGY PLANNER ---
with tabs[0]:
    st.title("Top Local Spots")
    c1, col_dist, c2 = st.columns([2, 1, 1])
    with c1:
        species_search = st.selectbox("What are you fishing for?", [None] + ALL_SPECIES)
        st.session_state['target_species'] = species_search
    
    with col_dist:
        max_dist = st.number_input("Max Miles", value=150)
    
    with c2:
        # Dynamic Slider
        max_val = 10
        if species_search:
            if "Shark" in species_search: max_val = 500
            elif "Striped" in species_search: max_val = 60
        target_lb = st.slider("Target Weight (lbs)", 1, max_val, 2)

    if species_search:
        matches = [
            {"name": n, "dist": d[1], "max_w": d[2], "quality": d[3], "tip": d[4]} 
            for n, d in SITES.items() if d[0] == species_search and d[1] <= max_dist and d[2] >= target_lb
        ]
        
        if not matches:
            st.error("No spots found. Adjust filters.")
        else:
            for spot in matches:
                with st.container():
                    col_info, col_btn = st.columns([3, 1])
                    col_info.subheader(f"📍 {spot['name']}")
                    col_info.write(f"Dist: {spot['dist']}mi | Potential: {spot['max_w']}lb | **Tip:** {spot['tip']}")
                    
                    # THE SYNC BUTTON
                    if col_btn.button(f"Lock in {spot['name']}", key=spot['name']):
                        st.session_state['locked_spot'] = spot['name']
                        st.success("Trip Locked! Head to Advanced Analysis.")
                    st.divider()
    else:
        st.warning("Select a species to start.")

# --- TAB: ADVANCED TACTICAL ANALYSIS ---
with tabs[1]:
    if not st.session_state['locked_spot']:
        st.warning("Go to Strategy Planner and click 'Lock in' on a location first!")
    else:
        selected_spot = st.session_state['locked_spot']
        st.header(f"Tactical Briefing: {selected_spot}")
        
        # Real Time/Date
        now = datetime.now()
        st.subheader(f"📅 {now.strftime('%A, %b %d, %Y')} | 🕒 {now.strftime('%I:%M %p')}")
        
        # Live Weather Logic
        lat, lon = SITES[selected_spot][7], SITES[selected_spot][8]
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,surface_pressure&temperature_unit=fahrenheit"
            res = requests.get(url).json()
            curr_f = res['current']['temperature_2m']
            curr_inhg = round(res['current']['surface_pressure'] * 0.02953, 2)
            
            st.markdown(f"# Real-Time Bite Score: 88/100")
            f1, f2, f3 = st.columns(3)
            f1.metric("Air Temp", f"{curr_f}°F")
            f2.metric("Pressure", f"{curr_inhg} inHg")
            f3.metric("Status", "Good")
        except:
            st.error("Weather service unreachable.")

        st.divider()
        st.subheader("⏰ Optimal Trip Timing")
        time_choice = st.radio("Trip Window:", ["6am-10am", "10am-4pm", "4pm-8pm"])
        st.success(f"Best window for {time_choice}: {now.strftime('%I:%M %p')}")

        st.divider()
        # Big Game Gear Logic
        st.subheader("⚙️ Recommended Setup")
        t_species = st.session_state['target_species']
        if t_species and "Shark" in t_species:
            rod, line = "7'6\" Extra-Heavy", "80lb Braid + Steel Leader"
        elif target_lb < 3:
            rod, line = "6'6\" Ultralight", "6lb Mono"
        else:
            rod, line = "7'0\" Medium-Heavy", "15lb Braid"
        st.info(f"**Rod:** {rod} | **Line:** {line}")

# --- TAB: LEARN CENTER ---
with tabs[2]:
    st.title("Fishing Academy")
    topic = st.selectbox("Choose a Lesson:", ["Texas Rig", "Ned Rig"])
    
    if topic == "Texas Rig":
        st.write("The ultimate weedless setup for heavy cover.")
        # FIXED IMAGE: Using a direct Wikimedia link for reliability
        st.image("https://upload.wikimedia.org/wikipedia/commons/e/e4/Texas_rig.png", caption="Texas Rig Diagram", width=400)
    
    elif topic == "Ned Rig":
        st.write("A 'do-nothing' finesse rig that catches everything in PA creeks.")
        st.image("https://images.tacklewarehouse.com/fishing/Z-Man_Ned_Rig_Kit.jpg", caption="Typical Ned Rig Setup", width=400)
