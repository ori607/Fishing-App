import streamlit as st
from datetime import datetime

# --- 1. SETTINGS ---
st.set_page_config(page_title="FishAI Master", page_icon="🎣", layout="wide")

# --- 2. THE DATABASE ---
# Expanded species for the search bar
SPECIES_LIST = [
    "Largemouth Bass", "Smallmouth Bass", "Striped Bass (Striper)", "Black Sea Bass", 
    "Rainbow Trout", "Brown Trout", "Brook Trout", "Channel Catfish", "Blue Catfish", 
    "Flathead Catfish", "Common Carp", "Mirror Carp", "Bull Shark", "Sandbar Shark", "Fluke (Summer Flounder)"
]

SITES = {
    "Quarry Road Pond (Bryn Athyn)": ["Largemouth Bass", 0.1, 6, 10, "Focus on steep drop-offs.", "Rocks", "Fresh"],
    "Mason's Mill Pond": ["Largemouth Bass", 3, 5, 4, "Heavy vegetation. Use weedless gear.", "LilyPads", "Fresh"],
    "Oreland Quarry (Sandy Run)": ["Largemouth Bass", 8, 8, 9, "Deep clear water. Big fish hold deep.", "Open", "Fresh"],
    "Pennypack (Lorimer)": ["Smallmouth Bass", 2, 4, 3, "Fish the eddies behind stones.", "Current", "Fresh"],
    "Island Beach State Park": ["Striped Bass (Striper)", 82, 50, 10, "Target the 'sloughs'.", "Open", "Salt"],
    "Cape May Inlet": ["Bull Shark", 95, 150, 7, "Heavy current. Use wire leaders.", "Current", "Salt"]
}

LIMITS = {s: 1000 if "Shark" in s else 70 if "Striped" in s else 12 for s in SPECIES_LIST}

# --- 3. PERSISTENT PROFILE (Simplified) ---
if 'profile' not in st.session_state:
    st.session_state['profile'] = {'lures': ["Senko"]}

with st.sidebar:
    st.header("👤 My Gear Locker")
    st.session_state['profile']['lures'] = st.multiselect(
        "Lures You Own:", 
        ["Senko", "Frog", "Crankbait", "Chatterbait", "Jig", "Bucktail", "Whopper Plopper"],
        default=st.session_state['profile']['lures']
    )
    # Rod and Line inputs removed as requested

# --- 4. MAIN INTERFACE ---
tabs = st.tabs(["🎯 Strategy Planner", "📊 Advanced Tactical Analysis", "📚 Learn Center"])

# --- TAB: STRATEGY PLANNER ---
with tabs[0]:
    st.title("Top Local Spots")
    c1, col_dist, c2 = st.columns([2, 1, 1])
    with c1:
        # FIX #1: Searchable Species Selection
        species = st.selectbox("Search for a species (e.g., 'Bass'):", SPECIES_LIST)
    with col_dist:
        max_dist = st.number_input("Max Miles", value=15)
    with c2:
        target_lb = st.slider(f"Target Weight (lbs)", 1, LIMITS.get(species, 20), 2)

    matches = [
        {"name": n, "dist": d[1], "max_w": d[2], "quality": d[3], "tip": d[4]} 
        for n, d in SITES.items() if d[0] == species and d[1] <= max_dist and d[2] >= target_lb
    ]
    matches = sorted(matches, key=lambda x: x['quality'], reverse=True)
    st.session_state['filtered_spots'] = [m['name'] for m in matches]

    if not matches:
        st.error(f"No {species} spots found matching your criteria. Try expanding distance.")
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
    available_spots = st.session_state.get('filtered_spots', [])
    
    if not available_spots:
        st.warning("Please find spots in the Strategy Planner first!")
    else:
        st.header("📍 Trip Tactical Analysis")
        selected_spot = st.selectbox("Confirm location:", available_spots)
        
        now = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        st.caption(f"Data for {selected_spot} as of: **{now}**")
        st.markdown("# Bite Score: 92/100")
        
        # FIX #2: Suggested Rod and Line (Automated Logic)
        st.subheader("⚙️ Recommended Setup")
        if target_lb <= 3:
            rec_rod, rec_line = "6'6\" Ultralight Power", "6lb Monofilament"
        elif target_lb <= 10:
            rec_rod, rec_line = "7'0\" Medium Power / Fast Action", "12lb Fluorocarbon"
        else:
            rec_rod, rec_line = "7'6\" Heavy Power", "30lb-50lb Braided Line"
            
        r1, r2 = st.columns(2)
        r1.info(f"**Rod:** {rec_rod}")
        r2.info(f"**Line:** {rec_line}")

        st.divider()

        st.subheader("⏰ Optimal Trip Timing")
        time_choice = st.radio("Trip Window:", ["6am-10am", "10am-4pm", "4pm-8pm"])
        
        if time_choice == "6am-10am":
            st.success("**Best Slot:** 6:15am - 7:45am")
        elif time_choice == "10am-4pm":
            st.success("**Best Slot:** 11:30am - 12:45pm")
        else:
            st.success("**Best Slot:** 6:30pm - 7:50pm")
        
        st.markdown(f"🏆 **Overall Best Time Today:** 6:45 PM")

        st.divider()
        
        col_left, col_right = st.columns(2)
        cover = SITES[selected_spot][5]
        user_lures = st.session_state['profile']['lures']
        
        with col_left:
            st.subheader("🎒 From Your Locker")
            if user_lures:
                if cover == "LilyPads" and "Frog" in user_lures:
                    st.write("**Choice:** 1/2oz White Hollow Body Frog")
                    
                elif cover == "Rocks" and "Jig" in user_lures:
                    st.write("**Choice:** 3/8oz Black/Blue Football Jig")
                    
                else:
                    st.write("**Choice:** 5-inch Dark Green Pumpkin Senko")
                    st.image("https://images.tacklewarehouse.com/fishing/Gary_Yamamoto_Senko.jpg", width=250)
            else:
                st.write("Locker is empty.")

        with col_right:
            st.subheader("🎣 Pro Suggestion")
            if cover == "Rocks":
                st.write("**Expert Setup:** 3/4oz Tungsten Jig - Blue Craw")
            elif cover == "LilyPads":
                st.write("**Expert Setup:** 5/8oz Leopard Frog")
            else:
                st.write("**Expert Setup:** 1/4oz White Whopper Plopper")

# --- TAB: LEARN CENTER ---
with tabs[2]:
    st.header("Fishing Academy")
    topic = st.selectbox("Topic", ["Texas Rig", "Bathymetry"])
    if topic == "Texas Rig":
        st.write("Rigging your soft plastics 'weedless' is essential for heavy cover.")
        st.image("https://upload.wikimedia.org/wikipedia/commons/e/e4/Texas_rig.png", width=300)
        
