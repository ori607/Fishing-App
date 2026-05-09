import streamlit as st

# --- APP CONFIG ---
st.set_page_config(page_title="FishAI: Pro Edition", page_icon="🎣")

# --- DATABASE (Species, Distance, MaxWeight, Quality) ---
SITES = {
    "Pennypack Creek (Lorimer)": ["Bass", 2, 4, 3],
    "Mason's Mill Pond": ["Bass", 3, 5, 4],
    "Nockamixon State Park": ["Bass", 28, 9, 8],
    "Marsh Creek Lake": ["Bass", 45, 8, 7],
    "Blue Marsh Lake": ["Bass", 65, 7, 6],
    "Wissahickon Creek": ["Trout", 12, 3, 5],
    "Bushkill Creek": ["Trout", 65, 6, 9],
    "Delaware River (Linden Ave)": ["Catfish", 18, 30, 6],
    "Susquehanna River": ["Catfish", 85, 50, 10],
    "Cape May Surf": ["Striper", 90, 40, 7],
    "Barnegat Inlet": ["Striper", 75, 55, 9],
    "Island Beach State Park": ["Striper", 82, 50, 10],
    "Cape May Inlet": ["Shark", 95, 150, 6],
    "Offshore Canyons": ["Shark", 160, 800, 10],
}

LIMITS = {"Bass": 12, "Trout": 15, "Catfish": 60, "Striper": 70, "Shark": 1000}

# --- USER PROFILE (PERSISTENCE) ---
if 'my_gear' not in st.session_state:
    st.session_state['my_gear'] = []

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("User Profile")
st.session_state['my_gear'] = st.sidebar.multiselect(
    "Your Permanent Gear Locker:", 
    ["Senko", "Crankbait", "Chatterbait", "Jig", "Bucktail", "Topwater", "Live Bait", "Circle Hook"],
    default=st.session_state['my_gear']
)
st.sidebar.info("Gear saved! It will stay here while you use the app.")

page = st.sidebar.radio("Go to", ["Smart Planner", "Catch Log"])

if page == "Smart Planner":
    st.title("🎯 Multi-Spot Trip Planner")

    col1, col2 = st.columns(2)
    with col1:
        species = st.selectbox("Target Species", list(LIMITS.keys()))
        max_dist = st.slider("Max Distance", 5, 200, 30)
    with col2:
        target_lb = st.slider(f"Target Weight (lbs)", 1, LIMITS[species], 2)

    if st.button("Analyze Best Options"):
        # 1. Filter spots
        matches = [
            {"name": n, "dist": d[1], "max_w": d[2], "quality": d[3]} 
            for n, d in SITES.items() if d[0] == species and d[1] <= max_dist and d[2] >= target_lb
        ]
        
        # 2. Sort by Quality
        matches = sorted(matches, key=lambda x: x['quality'], reverse=True)

        if not matches:
            st.error("No spots found matching your strict criteria. Try expanding distance or lowering weight.")
        elif not st.session_state['my_gear']:
            st.warning("Please add gear to your Profile in the sidebar first!")
        else:
            st.subheader(f"Top {len(matches)} Recommendations for {species}")
            
            for i, spot in enumerate(matches):
                # Rank logic
                rank_color = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
                
                with st.expander(f"{rank_color} Rank {i+1}: {spot['name']}"):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"**Distance:** {spot['dist']} miles")
                        st.write(f"**Potential:** {spot['max_w']} lbs")
                        st.write(f"**Spot Quality:** {spot['quality']}/10")
                    with c2:
                        # Logic to pick the best gear from your profile
                        suggested_gear = st.session_state['my_gear'][0]
                        st.success(f"**Best Gear:** {suggested_gear}")
                        st.info(f"**Pro Tip:** At {spot['name']}, focus on depth transitions.")

elif page == "Catch Log":
    st.title("🏆 Catch History")
    st.write("Section under construction.")
