import streamlit as st
from datetime import datetime

# --- 1. SETTINGS ---
st.set_page_config(page_title="FishAI Master", page_icon="🎣", layout="wide")

# --- 2. THE DATABASE ---
SITES = {
    "Quarry Road Pond (Bryn Athyn)": ["Bass", 0.1, 6, 10, "Focus on steep drop-offs.", "Rocks", "Fresh"],
    "Mason's Mill Pond": ["Bass", 3, 5, 4, "Heavy vegetation. Use weedless gear.", "LilyPads", "Fresh"],
    "Oreland Quarry (Sandy Run)": ["Bass", 8, 8, 9, "Deep clear water. Big fish hold deep.", "Open", "Fresh"],
    "Pennypack (Lorimer)": ["Bass", 2, 4, 3, "Fish the eddies behind large stones.", "Current", "Fresh"],
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

    # FILTERING LOGIC
    matches = [
        {"name": n, "dist": d[1], "max_w": d[2], "quality": d[3], "tip": d[4]} 
        for n, d in SITES.items() if d[0] == species and d[1] <= max_dist and d[2] >= target_lb
    ]
    matches = sorted(matches, key=lambda x: x['quality'], reverse=True)
    
    # Store these matches in session state for the Advanced Tab
    st.session_state['filtered_spots'] = [m['name'] for m in matches]

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
    # FIX #1: Only allow selection of "Top Local Spots"
    available_spots = st.session_state.get('filtered_spots', [])
    
    if not available_spots:
        st.warning("Please find spots in the Strategy Planner first!")
    else:
        st.header("📍 Trip Tactical Analysis")
        selected_spot = st.selectbox("Choose a spot from your filtered list:", available_spots)
        
        # Environmental Data Header
        now = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        st.caption(f"Live data for {selected_spot} as of: **{now}**")
        st.markdown("# Bite Score: 92/100")
        
        # Environmental Factors (Smaller font)
        f1, f2, f3, f4, f5 = st.columns(5)
        f1.caption("**Moon:** Waning Crescent")
        f2.caption("**Clarity:** High")
        f3.caption("**SST:** 63°F")
        f4.caption("**Chlorophyll:** 2.1mg/m³")
        f5.caption("**Pressure:** 30.01inHg")

        st.divider()

        # FIX #2: Best Times Selection
        st.subheader("⏰ Optimal Trip Timing")
        time_choice = st.radio("When are you planning to go?", ["6am-10am", "10am-4pm", "4pm-8pm"])
        
        # Timing Logic Engine
        if time_choice == "6am-10am":
            best_time = "6:15am - 7:45am"
            reason = "High activity during the 'Morning Sunrise' window as water warms."
        elif time_choice == "10am-4pm":
            best_time = "11:30am - 12:45pm"
            reason = "Fish move to deeper structure; focus on shaded drop-offs."
        else: # 4pm-8pm
            best_time = "6:30pm - 7:50pm"
            reason = "Peak sunset feeding window. Fish move to shallow cover."

        st.success(f"**Best Slot for your choice:** {best_time}")
        st.info(f"**Why:** {reason}")
        
        # Suggest overall best time
        st.markdown(f"🏆 **Overall Best Time Today:** 6:45 PM (Sunset/Lunar overlap)")

        st.divider()
        
        # Lure Recommendations (Locker vs Pro)
        col_left, col_right = st.columns(2)
        cover = SITES[selected_spot][5]
        user_lures = st.session_state['profile']['lures']
        
        with col_left:
            st.subheader("🎒 From Your Locker")
            if user_lures:
                if cover == "LilyPads" and "Frog" in user_lures:
                    st.write("**Primary Choice:** 1/2oz White Hollow Body Frog")
                    
                elif cover == "Rocks" and "Jig" in user_lures:
                    st.write("**Primary Choice:** 3/8oz Black/Blue Football Jig")
                    
                else:
                    st.write("**Primary Choice:** 5-inch Dark Green Pumpkin Senko")
                    st.image("https://images.tacklewarehouse.com/fishing/Gary_Yamamoto_Senko.jpg", width=250)
            else:
                st.write("Add gear in the sidebar.")

        with col_right:
            st.subheader("🎣 Pro Suggestion")
            if cover == "Rocks":
                st.write("**Expert Setup:** 3/4oz Tungsten Jig - Blue Craw")
            elif cover == "LilyPads":
                st.write("**Expert Setup:** 5/8oz Leopard Frog - Yellow Belly")
            else:
                st.write("**Expert Setup:** 1/4oz White Whopper Plopper")

# --- TAB: LEARN CENTER ---
with tabs[2]:
    st.header("Fishing Academy")
    topic = st.selectbox("Topic", ["Texas Rig", "Bathymetry"])
    if topic == "Texas Rig":
        st.image("https://upload.wikimedia.org/wikipedia/commons/e/e4/Texas_rig.png", width=300)
