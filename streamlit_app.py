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
        st.session_state['profile']['weights'] = st.multiselect("
