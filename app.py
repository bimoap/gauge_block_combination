import streamlit as st
import itertools
import json
import os

# ==========================================
# File Storage Setup
# ==========================================
SETTINGS_FILE = "gauge_app_settings.json"

# Default settings if the file doesn't exist yet
DEFAULT_SETTINGS = {
    "selected_set": "87-piece metric gauge block set (Grade 1)",
    "num_missing": 0,
    "missing_blocks": []
}

def load_settings():
    """Load settings from the JSON file."""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return DEFAULT_SETTINGS
    return DEFAULT_SETTINGS

def save_settings(settings_dict):
    """Save settings to the JSON file."""
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings_dict, f)

# Load settings at the start of the app
saved_settings = load_settings()

# ... [Insert your GAUGE_SETS dictionary and find_combination function here] ...

# ==========================================
# Streamlit UI
# ==========================================
st.set_page_config(page_title="Gauge Block Calculator", layout="centered")
st.title("Gauge Block Combination Calculator")

with st.sidebar:
    st.header("Settings")
    
    # Use the saved setting as the default index
    set_options = list(GAUGE_SETS.keys())
    default_set_index = set_options.index(saved_settings["selected_set"]) if saved_settings["selected_set"] in set_options else 0
    
    selected_set = st.selectbox("1. Select Gauge Block Set", options=set_options, index=default_set_index)
    
    st.markdown("---")
    st.header("Missing Blocks Management")
    
    # Use the saved number of missing blocks as the default
    num_missing = st.number_input("How many blocks are missing?", min_value=0, max_value=20, value=saved_settings["num_missing"], step=1)
    
    missing_blocks_list = []
    if num_missing > 0:
        st.write("Enter the sizes of the missing blocks:")
        for i in range(num_missing):
            # If we have a saved block size for this index, use it. Otherwise, default to 1.000
            saved_val = saved_settings["missing_blocks"][i] if i < len(saved_settings["missing_blocks"]) else 1.000
            
            missing_val = st.number_input(f"Missing Block {i+1} (mm)", min_value=0.000, max_value=200.000, value=float(saved_val), step=0.001, format="%.3f", key=f"missing_{i}")
            missing_blocks_list.append(missing_val)
    
    # Save Button to lock in the current settings
    if st.button("💾 Save Settings as Default"):
        new_settings = {
            "selected_set": selected_set,
            "num_missing": num_missing,
            "missing_blocks": missing_blocks_list
        }
        save_settings(new_settings)
        st.success("Settings saved! These will load automatically next time.")
            
    st.markdown("---")
    st.markdown("App developed & maintained by: **Bimo**")

# ... [Rest of your UI and calculation logic goes here] ...
