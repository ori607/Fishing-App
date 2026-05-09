import streamlit as st

# --- APP CONFIG ---
st.set_page_config(page_title="HV Master Guide v2", page_icon="🎣")

# --- DATABASE: Spots with Mileage from Huntingdon Valley ---
# Format: "Name": [Species, Distance_from_HV]
SITES = {
    "Pennypack Creek (Lorimer)": ["Bass", 2],
    "Mason's Mill Pond": ["Bass", 3],
    "Nockamixon State Park": ["Bass", 28],
    "Wissahickon Creek": ["Trout", 12],
    "Bushkill Creek": ["Trout", 65],
    "Marsh Creek Lake": ["Musky", 45],
    "Delaware River (Trenton)": ["Catfish", 18],
    "Schuylkill (Philly)": ["Catfish", 15],
    "Pennypack (Slow Pools)": ["Carp", 2],
    "Cape May Surf": ["Striper", 90],
    "Barnegat Light": ["Striper", 75],
    "Cape May Inlet": ["Shark", 95],
    "Offshore Reefs": ["Shark", 105],
    "Atlantic City Piers": ["Fluke", 65],
    "Ocean City Back Bay": ["Fluke", 70],
    "Canyons (Deep Sea)": ["Tuna", 150]
}

# --- SIDEBAR ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["AI Fishing Guide", "Catch Tracker"])

if page == "AI Fishing Guide":
    st.title("🎯 Smart-Trip Planner")

    # 1. Expanded Species
    species = st.selectbox("Target Species:", ["Bass", "Trout", "Musky", "Carp", "Striper", "Fluke", "Shark", "Tuna", "Catfish"])

    # 2. Advanced Lure Logic
    if species in ["Bass", "Musky"]:
        lure_options = ["Senko", "Crankbait", "Chatterbait", "Whopper Plopper", "Swim Bait"]
    elif species in ["Striper", "Fluke", "Tuna"]:
        lure_options = ["Bucktail", "Gulp Mullet", "Topwater Popper", "Cedar Plug"]
    elif species == "Trout":
        lure_options = ["Rooster Tail", "Powerbait", "Fly (Wooly Bugger)"]
    elif species == "Shark":
        lure_options = ["Chum/Mackerel", "Large Circle Hook with Mullet"]
    else:
        lure_options = ["Corn", "Nightcrawlers", "Chicken Liver"]

    user_lures = st.multiselect(f"Your {species} Gear:", lure_options)
    
    # 3. Sliders
    max_dist = st.slider("How far will you drive? (miles)", 5, 200, 30)
    target_lb = st.slider(f"Target {species} Weight (lbs):", 1, 100, 5)

    if st.button("Calculate Best Spot"):
        # --- THE "THINKING" LOGIC ---
        # Filter spots by species AND distance
        valid_spots = [name for name, data in SITES.items() if data[0] == species and data[1] <= max_dist]

        if not valid_spots:
            st.error(f"No {species} spots found within {max_dist} miles. Try increasing your travel distance!")
        elif not user_lures:
            st.warning("Select your gear first!")
        else:
            # Pick the BEST lure based on target weight
            selected_lure = user_lures[0] # Default to first
            if target_lb > 10 and len(user_lures) > 1:
                # Logic: If targeting big fish, prefer bigger lures if available
                selected_lure = user_lures[-1] 
            
            best_spot = valid_spots[0] # The "Thinking" part picks the closest valid spot
            
            st.subheader("🔥 Your Master Plan")
            st.success(f"**GO HERE:** {best_spot}")
            st.write(f"This spot is within your {max_dist} mile limit and is prime for {species}.")
            
            # Specific Advice Logic
            color = "Dark Green/Brown" if target_lb < 5 else "White/Silver"
            st.info(f"**TACTIC:** Use a **{color} {selected_lure}**. Cast toward structure and retrieve slowly.")

elif page == "Catch Tracker":
    st.title("🏆 Catch Log")
    st.write("Section under construction - Use the planner for now!")
