import streamlit as st
import random

# --- 1. SETTINGS & STYLING ---
st.set_page_config(page_title="FishAI Master", page_icon="🎣", layout="wide")

# --- 2. THE DATABASE (The "Brain") ---
# Format: "Name": [Species, Distance, MaxWeight, Quality, Tip, CoverType, WaterType]
SITES = {
    "Quarry Road Pond (Bryn Athyn)": ["Bass", 0.1, 6, 10, "Focus on the steep drop-offs near the rocks.", "Rocks", "Fresh"],
    "Mason's Mill Pond": ["Bass", 3, 5, 4, "Heavy vegetation. Use weedless gear.", "LilyPads", "Fresh"],
    "Oreland Quarry (Sandy Run)": ["Bass", 8, 8, 9, "Deep clear water. Big fish hold deep.", "Open", "Fresh"],
    "Pennypack (Lorimer)": ["Bass", 2, 4, 3, "Fish the eddies behind large stones.", "Current", "Fresh"],
    "Island Beach State Park": ["Striper", 82, 50, 10, "Target the 'sloughs' between sandbars.", "Open", "Salt"],
    "Cape May Inlet": ["Shark", 95, 150, 7, "Heavy current. Use wire leaders.", "Current", "Salt"]
}

LIMITS = {"Bass": 12, "Striper": 70, "Shark": 1000, "Catfish": 60}

# --- 3. PERSISTENT PROFILE (The Sidebar Locker) ---
if 'profile' not in st.session_state:
    st.session_state['profile'] = {
        'lures': ["Senko"], 
        'rod_type': "7'0\" Medium", 
        'line_type': "12lb Mono"
    }

with st.sidebar:
    st.header("👤 My Gear Locker")
    st.session_state['profile']['lures'] = st.multiselect(
        "Lures You Own:", 
        ["Senko", "Frog", "Crankbait", "Chatterbait", "Jig", "Bucktail", "Topwater Popper"],
        default=st.session_state['profile']['lures']
    )
    st.session_state['profile']['rod_type'] = st.text_input("Rod Type:", value=st.session_state['profile']['rod_type'])
    st.session_state['profile']['line_type'] = st.text_input("Line Type:", value=st.session_state['profile']['line_type'])
    st.info("Gear saved! Use the tabs to plan.")

# --- 4. MAIN INTERFACE ---
tabs = st.tabs(["🎯 Strategy Planner", "📊 Advanced Tactical Analysis", "📚 Learn Center"])

# --- TAB: STRATEGY PLANNER ---
with tabs[0]:
    st.title("Top Local Spots")
    c1, c2 = st.columns(2)
    with c1:
        species = st.selectbox("Target Species", list(LIMITS.keys()))
        max_dist = st.number_input("Max Drive (Miles)", value=15)
    with c2:
        # This is the "Strict" slider you wanted back
        target_lb = st.slider(f"Target {species} Weight (lbs)", 1, LIMITS[species], 2)

    # Filtering Logic (Weight + Distance)
    matches = [
        {"name": n, "dist": d[1], "max_w": d[2], "quality": d[3], "tip": d[4], "cover": d[5]} 
        for n, d in SITES.items() if d[0] == species and d[1] <= max_dist and d[2] >= target_lb
    ]
    
    # Sorting by Quality so Oreland/Quarry Rd come first
    matches = sorted(matches, key=lambda x: x['quality'], reverse=True)

    if not matches:
        st.error("No spots found. Increase your distance or lower the weight target.")
    else:
        # We store the #1 choice in session state so the "Tactical" tab knows what to analyze
        st.session_state['selected_spot'] = matches[0]['name']
        
        for i, spot in enumerate(matches):
            rank = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
            with st.container():
                st.subheader(f"{rank} {spot['name']}")
                col_a, col_b, col_c = st.columns([1,1,2])
                with col_a:
                    st.metric("Distance", f"{spot['dist']}mi")
                with col_b:
                    st.metric("Potential", f"{spot['max_w']}lb")
                with col_c:
                    st.write(f"**Pro Tip:** {spot['tip']}")
                    st.caption(f"Cover Type: {spot['cover']}")
                st.divider()

# --- TAB: ADVANCED TACTICAL ANALYSIS ---
with tabs[1]:
    if 'selected_spot' not in st.session_state:
        st.warning("Select a spot in the Strategy Planner first.")
    else:
        spot_name = st.session_state['selected_spot']
        st.header(f"Tactical Briefing: {spot_name}")
        
        # Pull data for the logic
        spot_data = SITES[spot_name]
        cover = spot_data[5]
        water_type = spot_data[6]
        
        # Env Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Moon Phase", "New Moon", "High Feeding")
        m2.metric("Water Clarity", "High (Quarry)" if "Quarry" in spot_name else "Medium")
        m3.metric("Bite Score", "92/100")

        # SMART LURE RANKING (Logic based on cover)
        st.subheader("🎒 Recommended Lure Order")
        user_lures = st.session_state['profile']['lures']
        
        if not user_lures:
            st.warning("Add lures to your Gear Locker in the sidebar!")
        else:
            # Logic: If LilyPads, Frog is #1. If Rocks, Senko/Jig is #1.
            if cover == "LilyPads":
                ranked = sorted(user_lures, key=lambda x: x == "Frog", reverse=True)
            elif cover == "Rocks":
                ranked = sorted(user_lures, key=lambda x: x in ["Senko", "Jig"], reverse=True)
            else:
                ranked = user_lures
            
            for i, lure in enumerate(ranked):
                st.write(f"{i+1}. **{lure}**" + (" (Recommended for this terrain)" if i == 0 else ""))

# --- TAB: LEARN CENTER ---
with tabs[2]:
    st.header("Fishing Academy")
    topic = st.selectbox("Topic", ["Texas Rig (Weedless)", "Bathymetry"])
    if topic == "Texas Rig (Weedless)":
        st.write("Essential for the Lily Pads at Mason's Mill or the rocks at the Quarry.")
        st.image("https://upload.wikimedia.org/wikipedia/commons/e/e4/Texas_rig.png", width=300)
    else:
        st.write("Bathymetry maps show you where the deep drop-offs are.")
