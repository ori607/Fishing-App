import streamlit as st

st.set_page_config(page_title="FishAI: Hyper-Local", page_icon="🎣", layout="wide")

# --- 1. THE DATABASE (Added Quarry Rd & Logic Keys) ---
# Format: "Name": [Species, Distance, MaxWeight, Quality, Tip, CoverType]
# CoverType: "Open", "LilyPads", "Rocks", "HeavyBrush", "Current"
SITES = {
    "Quarry Road Pond (Bryn Athyn)": ["Bass", 0.1, 6, 9, "Private feel. Focus on the steep drop-offs.", "Rocks"],
    "Oreland Quarry (Sandy Run)": ["Bass", 8, 8, 8, "Deep water. Use weighted rigs for big fish.", "Open"],
    "Mason's Mill Pond": ["Bass", 3, 5, 4, "Heavy vegetation in summer.", "LilyPads"],
    "Pennypack (Lorimer)": ["Bass", 2, 4, 3, "Moving water. Fish the eddies.", "Current"],
    "Nockamixon State Park": ["Bass", 28, 9, 8, "Massive lake. Find submerged structure.", "HeavyBrush"],
}
LIMITS = {"Bass": 12, "Trout": 15, "Catfish": 60, "Striper": 70}

# --- 2. USER PROFILE (Added Custom Inputs) ---
if 'profile' not in st.session_state:
    st.session_state['profile'] = {'lures': [], 'rod_type': "Medium", 'line_type': "12lb Mono"}

with st.sidebar:
    st.title("👤 My Custom Profile")
    
    # GEAR LOCKER
    st.session_state['profile']['lures'] = st.multiselect("Select Lures:", ["Senko", "Frog", "Crankbait", "Jig", "Spinnerbait", "Whopper Plopper"])
    custom_lure = st.text_input("Don't see your lure? Type it here:")
    if custom_lure and custom_lure not in st.session_state['profile']['lures']:
        st.session_state['profile']['lures'].append(custom_lure)

    # ROD & LINE (Full flexibility)
    st.session_state['profile']['rod_type'] = st.text_input("Rod Specifics (e.g., 7' Heavy, Ultralight):", value=st.session_state['profile']['rod_type'])
    st.session_state['profile']['line_type'] = st.text_input("Line Specifics (e.g., 15lb Braid, 4lb Fluoro):", value=st.session_state['profile']['line_type'])

# --- 3. THE PLANNER (Logical Thinking) ---
st.title("🎯 Hyper-Local Strategy")

col1, col2 = st.columns(2)
with col1:
    species = st.selectbox("Target Fish", list(LIMITS.keys()))
    max_dist = st.number_input("Max Miles from Bryn Athyn", value=15)
with col2:
    target_lb = st.slider("Target Weight (lbs)", 1, LIMITS[species], 2)

if st.button("Generate Strategy"):
    matches = [
        {"name": n, "dist": d[1], "max_w": d[2], "quality": d[3], "tip": d[4], "cover": d[5]} 
        for n, d in SITES.items() if d[0] == species and d[1] <= max_dist and d[2] >= target_lb
    ]
    
    if not matches:
        st.error("No local spots fit this weight/distance combo. Try 28 miles for Nockamixon!")
    else:
        for spot in sorted(matches, key=lambda x: x['quality'], reverse=True):
            with st.expander(f"📍 {spot['name']} ({spot['dist']} miles away)"):
                # --- THE BRAIN: COVER LOGIC ---
                cover = spot['cover']
                my_lures = st.session_state['profile']['lures']
                
                # Logical Lure Selection
                if cover == "LilyPads":
                    rec_lure = "Frog" if "Frog" in my_lures else "Weightless Senko (Rigged weedless)"
                    reasoning = "Because of the Lily Pads, a Frog is required to prevent snagging."
                elif cover == "Current":
                    rec_lure = "Crankbait" if "Crankbait" in my_lures else "Spinnerbait"
                    reasoning = "Moving water requires a lure with vibration like a Crankbait."
                else:
                    rec_lure = my_lures[0] if my_lures else "Nightcrawlers"
                    reasoning = "General purpose lure for this environment."

                st.success(f"**USE THIS:** {rec_lure}")
                st.write(f"**WHY:** {reasoning}")
                st.write(f"**GEAR SETUP:** {st.session_state['profile']['rod_type']} with {st.session_state['profile']['line_type']}")
                st.info(f"**LOCAL SECRET:** {spot['tip']}")

# --- 4. LEARN CENTER ---
st.write("---")
st.title("📚 Learn Center: Visual Guides")
tab1, tab2 = st.tabs(["Texas Rig", "Frog Fishing"])
with tab1:
    st.write("The Texas Rig makes your Senko 'weedless' so it won't get stuck in the Quarry rocks.")
    st.image("https://upload.wikimedia.org/wikipedia/commons/e/e4/Texas_rig.png", width=400)
    
with tab2:
    st.write("When using a frog in the Mason's Mill pads, wait for the 'glub' sound before setting the hook.")
