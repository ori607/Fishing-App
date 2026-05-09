import streamlit as st

# --- APP CONFIG ---
st.set_page_config(page_title="FishAI Master Guide", page_icon="🎣")

# --- DATABASE: Spot Name: [Species, Distance, MaxWeightPotential, SpotQuality]
# SpotQuality is 1-10 (10 being a Trophy destination)
SITES = {
    "Pennypack Creek (Lorimer)": ["Bass", 2, 4, 3],
    "Mason's Mill Pond": ["Bass", 3, 5, 4],
    "Nockamixon State Park": ["Bass", 28, 9, 8],
    "Marsh Creek Lake": ["Bass", 45, 8, 7],
    "Wissahickon Creek": ["Trout", 12, 3, 5],
    "Bushkill Creek": ["Trout", 65, 6, 9],
    "Delaware River (Linden Ave)": ["Catfish", 18, 30, 6],
    "Susquehanna River": ["Catfish", 85, 50, 10],
    "Pennypack (Slow Pools)": ["Carp", 2, 15, 4],
    "Delaware River Banks": ["Carp", 15, 35, 8],
    "Cape May Surf": ["Striper", 90, 40, 7],
    "Barnegat Inlet": ["Striper", 75, 55, 9],
    "Cape May Inlet": ["Shark", 95, 150, 6],
    "Offshore Canyons": ["Shark", 160, 800, 10],
    "Atlantic City Piers": ["Fluke", 65, 6, 5],
    "Ocean City Back Bay": ["Fluke", 70, 10, 8]
}

# --- SPECIES LIMITS (Max weight a human can actually catch) ---
LIMITS = {
    "Bass": 12,
    "Trout": 15,
    "Catfish": 60,
    "Carp": 50,
    "Striper": 70,
    "Fluke": 20,
    "Shark": 1000
}

st.title("🎯 Advanced FishAI Guide")

# 1. Species Selection
species = st.selectbox("What are we targeting?", list(LIMITS.keys()))

# 2. Dynamic Weight Slider (Strict)
max_possible = LIMITS[species]
target_lb = st.slider(f"Target {species} Weight (lbs):", 1, max_possible, int(max_possible/4))

# 3. Gear Logic
if species == "Bass":
    lure_options = ["Senko", "Crankbait", "Chatterbait", "Jig"]
elif species in ["Striper", "Fluke"]:
    lure_options = ["Bucktail", "Topwater Popper", "Sand Eel"]
elif species == "Shark":
    lure_options = ["Chum/Mackerel", "Large Circle Hook"]
else:
    lure_options = ["Corn", "Nightcrawlers", "Chicken Liver"]

user_lures = st.multiselect("Your Gear:", lure_options)
max_dist = st.slider("Max drive distance (miles):", 5, 200, 25)

if st.button("Find My Spot"):
    # --- LOGIC GATE 1: Filter by Species and Distance ---
    eligible_spots = [
        {"name": n, "dist": d[1], "max_w": d[2], "quality": d[3]} 
        for n, d in SITES.items() if d[0] == species and d[1] <= max_dist
    ]

    # --- LOGIC GATE 2: Filter by Weight Potential ---
    # Removes spots where the fish literally don't grow that big
    capable_spots = [s for s in eligible_spots if s['max_w'] >= target_lb]

    if not capable_spots:
        st.error(f"Search Failed: No spots within {max_dist} miles can produce a {target_lb}lb {species}.")
        st.info("Try increasing your travel distance or lowering your weight expectations.")
    elif not user_lures:
        st.warning("Please select your gear.")
    else:
        # --- LOGIC GATE 3: Pick the BEST spot (Highest Quality) ---
        # Sorts by quality score so you get the best water first
        best_spot = sorted(capable_spots, key=lambda x: x['quality'], reverse=True)[0]
        
        st.subheader("🔥 Official Recommendation")
        st.success(f"**LOCATION:** {best_spot['name']}")
        
        # Build the Tactic
        best_lure = user_lures[0]
        color = "Natural Shad" if target_lb > (max_possible/2) else "Neon/Bright"
        
        st.write(f"This spot has a **{best_spot['max_w']}lb potential**, which fits your {target_lb}lb goal.")
        st.info(f"**STRATEGY:** Use a **{color} {best_lure}**. Since you want a trophy, fish the deepest structure available.")
