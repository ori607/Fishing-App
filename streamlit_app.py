import streamlit as st
from datetime import datetime

# --- 1. SETTINGS ---
st.set_page_config(page_title="FishAI Master", page_icon="🎣", layout="wide")

# --- 2. THE DATABASE ---
SITES = {
    "Quarry Road Pond (Bryn Athyn)": ["Bass", 0.1, 6, 10, "Focus on steep drop-offs.", "Rocks", "Fresh"],
    "Mason's Mill Pond": ["Bass", 3, 5, 4, "Heavy vegetation. Use weedless gear.", "LilyPads", "Fresh"],
    "Oreland Quarry (Sandy Run)": ["Bass", 8, 8, 9, "Deep clear water. Big fish hold deep.", "Open", "Fresh"],
    "Island Beach State Park": ["Striper", 82, 50, 10, "Target the 'sloughs'.", "Open", "Salt"],
    "Cape May Inlet": ["Shark", 95, 150, 7, "Heavy current. Use wire leaders.", "Current", "Salt"]
}

LIMITS = {"Bass": 12, "Striper": 70, "Shark": 1000, "Catfish": 60}

# --- 3. PERSISTENT PROFILE ---
if 'profile' not in st.session_state:
    st.session_state['profile'] = {'lures': ["Senko"], 'rod_type': "7'0\" Medium", 'line_type': "12lb Mono"}

with st.sidebar:
    st.header("👤 My Gear Locker")
    st.session_state['profile']['lures'] = st.multiselect(
        "Lures You Own:", 
        ["Senko", "Frog", "Crankbait", "Chatterbait", "Jig", "Bucktail", "Whopper Plopper"],
        default=st.session_state['profile']['lures']
    )
    st.session_state['profile']['rod_type'] = st.text_input("Rod Type:", value=st.session_state['profile']['rod_type'])
    st.session_state['profile']['line_type'] = st.text_input("Line Type:", value=st.session_state['profile']['line_type'])
    
    st.divider()
    st.header("📍 Current Trip")
    st.session_state['selected_spot'] = st.selectbox("Select location to analyze:", list(SITES.keys()))

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
        target_lb = st.slider(f"Target {species} Weight (lbs)", 1, LIMITS[species], 2)

    matches = [
        {"name": n, "dist": d[1], "max_w": d[2], "quality": d[3], "tip": d[4]} 
        for n, d in SITES.items() if d[0] == species and d[1] <= max_dist and d[2] >= target_lb
    ]
    matches = sorted(matches, key=lambda x: x['quality'], reverse=True)

    if not matches:
        st.error("No matches found. Adjust distance or weight.")
    else:
        for i, spot in enumerate(matches):
            rank = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
            with st.container():
                st.subheader(f"{rank} {spot['name']}")
                col_a, col_b, col_c = st.columns([1,1,2])
                col_a.metric("Distance", f"{spot['dist']}mi")
                col_b.metric("Potential", f"{spot['max_w']}lb")
                col_c.write(f"**Tip:** {spot['tip']}")
                st.divider()

# --- TAB: ADVANCED TACTICAL ANALYSIS ---
with tabs[1]:
    spot_name = st.session_state.get('selected_spot')
    if spot_name:
        st.header(f"Tactical Briefing: {spot_name}")
        
        now = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        st.caption(f"Gathering environmental data for {spot_name} as of: **{now}**")
        
        st.markdown(f"# Bite Score: 92/100")
        
        f1, f2, f3, f4, f5 = st.columns(5)
        f1.caption(f"**Moon:** New Moon")
        f2.caption(f"**Clarity:** High")
        f3.caption(f"**SST:** 64.1°F")
        f4.caption(f"**Chlorophyll:** 2.1mg/m³")
        f5.caption(f"**Pressure:** 30.01inHg")

        st.divider()
        col_left, col_right = st.columns(2)
        
        spot_data = SITES[spot_name]
        cover = spot_data[5]
        
        with col_left:
            st.subheader("🎒 From Your Locker")
            user_lures = st.session_state['profile']['lures']
            if user_lures:
                # Logic to pick the best owned lure
                if cover == "LilyPads" and "Frog" in user_lures:
                    best_owned = "Frog"
                    st.write("**Primary Choice:** 1/2oz White Hollow Body Frog")
                    
                elif cover == "Rocks" and "Jig" in user_lures:
                    best_owned = "Jig"
                    st.write("**Primary Choice:** 3/8oz Black/Blue Football Jig")
                    
                else:
                    best_owned = "Senko"
                    st.write("**Primary Choice:** 5-inch Dark Green Pumpkin Senko")
                    st.image("https://images.tacklewarehouse.com/fishing/Gary_Yamamoto_Senko.jpg", width=250)
                    
            else:
                st.write("Locker is empty! Add gear in the sidebar.")

        with col_right:
            st.subheader("🎣 Pro Suggestion (The Perfect Tool)")
            if cover == "Rocks":
                st.write("**Expert Setup:** 3/4oz Tungsten Jig - Blue Craw")
                
            elif cover == "LilyPads":
                st.write("**Expert Setup:** 5/8oz Leopard Frog - Yellow Belly")
                
            else:
                st.write("**Expert Setup:** 1/4oz White Whopper Plopper")
                
    else:
        st.warning("Select a spot in the sidebar to begin analysis.")

# --- TAB: LEARN CENTER ---
with tabs[2]:
    st.header("Fishing Academy")
    topic = st.selectbox("Topic", ["Texas Rig", "Bathymetry"])
    if topic == "Texas Rig":
        st.write("Essential for fishing the weeds at Mason's Mill or the rocks at the Quarry.")
        st.image("https://upload.wikimedia.org/wikipedia/commons/e/e4/Texas_rig.png", width=300)
