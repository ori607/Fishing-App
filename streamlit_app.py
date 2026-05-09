import streamlit as st

st.set_page_config(page_title="FishAI: Ultimate Edition", page_icon="🎣", layout="wide")

# --- DATA: Spots and Limits ---
SITES = {
    "Pennypack Creek (Lorimer)": ["Bass", 2, 4, 3, "Fish the shaded pockets under trees."],
    "Mason's Mill Pond": ["Bass", 3, 5, 4, "Target the lily pads near the fountain."],
    "Nockamixon State Park": ["Bass", 28, 9, 8, "Work the rocky points and submerged roadbeds."],
    "Island Beach State Park": ["Striper", 82, 50, 10, "Look for 'cuts' in the sand bars at low tide."],
    "Susquehanna River": ["Catfish", 85, 50, 10, "Use heavy weights to hold bottom in the current."]
}
LIMITS = {"Bass": 12, "Trout": 15, "Catfish": 60, "Striper": 70, "Shark": 1000}

# --- SESSION STATE: User Profile ---
if 'profile' not in st.session_state:
    st.session_state['profile'] = {
        'lures': [],
        'rods': "7'0\" Medium Action",
        'line': "12lb Monofilament",
        'hooks': ["Offset Worm Hook"],
        'weights': ["1/4oz Bullet Weight"]
    }

# --- SIDEBAR: The Pro Profile ---
with st.sidebar:
    st.title("👤 My Pro Profile")
    
    with st.expander("🎣 Gear Locker", expanded=True):
        all_lures = [
            "Senko", "Crankbait", "Chatterbait", "Jig", "Frog", 
            "Whopper Plopper", "Spinnerbait", "Tube", "Bucktail", "Popper"
        ]
        st.session_state['profile']['lures'] = st.multiselect("Select Lures You Own:", all_lures)
        
        # VISUAL GEAR GUIDE
        if st.session_state['profile']['lures']:
            st.write("---")
            st.write("**Visual Tackle Box:**")
            if "Frog" in st.session_state['profile']['lures']:
                st.caption("🐸 Frog: Best for heavy weeds.")
            if "Senko" in st.session_state['profile']['lures']:
                st.caption("🪱 Senko: Best for slow days.")

    with st.expander("📐 Rod & Line Specs"):
        st.session_state['profile']['rods'] = st.selectbox("Primary Rod:", ["6'6\" Medium", "7'0\" Med-Heavy", "7'6\" Heavy Flip", "9'0\" Surf Rod"])
        st.session_state['profile']['line'] = st.selectbox("Line Type:", ["8lb Fluorocarbon", "12lb Mono", "30lb Braid", "50lb+ Braid"])

    with st.expander("📦 Terminal Tackle"):
        st.session_state['profile']['hooks'] = st.multiselect("Hooks:", ["Circle Hook", "EWG Worm Hook", "Treble", "Jig Head"])
        st.session_state['profile']['weights'] = st.multiselect("Weights:", ["1/8oz", "1/4oz", "1/2oz", "1oz+"])

# --- MAIN APP ---
page = st.radio("Navigation", ["Smart Planner", "Learn Center"], horizontal=True)

if page == "Smart Planner":
    st.title("🎯 Pro Trip Planner")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        species = st.selectbox("Target Fish", list(LIMITS.keys()))
    with col2:
        max_dist = st.number_input("Max Miles", value=30)
    with col3:
        target_lb = st.slider("Target Lbs", 1, LIMITS[species], 2)

    if st.button("Generate Strategy"):
        matches = [
            {"name": n, "dist": d[1], "max_w": d[2], "quality": d[3], "tip": d[4]} 
            for n, d in SITES.items() if d[0] == species and d[1] <= max_dist and d[2] >= target_lb
        ]
        matches = sorted(matches, key=lambda x: x['quality'], reverse=True)

        if not matches:
            st.error("No spots fit these specs. Expand your search!")
        else:
            for i, spot in enumerate(matches):
                with st.container():
                    st.markdown(f"### {i+1}. {spot['name']}")
                    c1, c2, c3 = st.columns([1,1,2])
                    with c1:
                        st.metric("Dist", f"{spot['dist']}mi")
                        st.metric("Quality", f"{spot['quality']}/10")
                    with c2:
                        # Logic to suggest the right lure from your locker
                        my_lures = st.session_state['profile']['lures']
                        rec_lure = my_lures[0] if my_lures else "Live Bait"
                        st.write(f"**Lure:** {rec_lure}")
                        st.write(f"**Rod:** {st.session_state['profile']['rods']}")
                    with c3:
                        st.info(f"**Tactic:** {spot['tip']}")
                        if "Frog" in rec_lure:
                            st.write("Keep your rod tip up and wait 1 second after the strike before setting the hook!")

elif page == "Learn Center":
    st.title("📖 Academy")
    topic = st.selectbox("Choose Tutorial", ["Texas Rig", "Frog Fishing"])
    if topic == "Texas Rig":
        st.write("The Texas Rig is the gold standard for weedless fishing.")
        
    if topic == "Frog Fishing":
        st.write("Walk the frog over heavy mats and lily pads.")
