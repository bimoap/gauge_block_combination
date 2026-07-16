import streamlit as st
import itertools
import json
import os
from fpdf import FPDF

# ==========================================
# File Storage Setup
# ==========================================
SETTINGS_FILE = "gauge_app_settings.json"

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

# ==========================================
# Export Functions
# ==========================================
def generate_csv(target, results):
    """Generates a CSV string of the calculation results."""
    csv_data = "Target Size (mm),Set Number,Total Verification (mm),Blocks Used (mm)\n"
    for idx, combo in enumerate(results):
        combo_str = " + ".join([f"{b:.3f}" for b in combo])
        total_size = sum(combo)
        # Using quotes around the combo string to prevent commas from breaking the CSV columns
        csv_data += f"{target:.3f},{idx + 1},{total_size:.3f},\"{combo_str}\"\n"
    return csv_data.encode('utf-8')

def generate_pdf(target, results, selected_set):
    """Generates a PDF document of the calculation results."""
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt="Gauge Block Setup Report", ln=True, align='C')
    
    # Metadata
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, txt=f"Target Size: {target:.3f} mm", ln=True)
    pdf.cell(0, 10, txt=f"Equipment: {selected_set}", ln=True)
    pdf.ln(5)

    # Results
    for idx, combo in enumerate(results):
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, txt=f"Set {idx + 1} (Total Check: {sum(combo):.3f} mm)", ln=True)
        
        pdf.set_font("Arial", '', 12)
        combo_str = " + ".join([f"{b:.3f}" for b in combo])
        pdf.cell(0, 8, txt=f"Combination: {combo_str}", ln=True)
        
        for block in sorted(combo):
            pdf.cell(0, 6, txt=f"  - {block:.3f} mm", ln=True)
        pdf.ln(5)
    
    # Output to string/bytes for download
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# Gauge Block Set Definitions
# ==========================================
GAUGE_SETS = {
    "87-piece metric gauge block set (Grade 1)": [
        *[round(1.001 + i * 0.001, 3) for i in range(9)],  
        *[round(1.01 + i * 0.01, 2) for i in range(49)],   
        *[round(0.5 + i * 0.5, 1) for i in range(19)],     
        *[float(10 + i * 10) for i in range(10)]           
    ],
    "83-piece metric gauge block set (Grade 2)": [
        1.005,
        *[round(1.01 + i * 0.01, 2) for i in range(49)],   
        *[round(0.5 + i * 0.5, 1) for i in range(19)],     
        *[float(10 + i * 10) for i in range(10)],          
        1.0, 1.001, 1.002, 1.003, 1.004, 1.006, 1.007, 1.008, 1.009 
    ],
    "47-piece Ceramic Set (grade 0)": [
        1.005,
        *[round(1.01 + i * 0.01, 2) for i in range(9)],    
        *[round(1.1 + i * 0.1, 1) for i in range(9)],      
        *[float(1 + i) for i in range(24)],                
        25.0, 50.0, 75.0, 100.0
    ],
    "76-piece": [
        1.005,
        *[round(1.01 + i * 0.01, 2) for i in range(49)],
        *[round(0.5 + i * 0.5, 1) for i in range(19)],
        10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0
    ],
    "103-piece": [
        1.005,
        *[round(1.01 + i * 0.01, 2) for i in range(49)],
        *[round(0.5 + i * 0.5, 1) for i in range(49)],
        25.0, 50.0, 75.0, 100.0
    ],
    "112-piece": [
        1.0005,
        *[round(1.001 + i * 0.001, 3) for i in range(9)],
        *[round(1.01 + i * 0.01, 2) for i in range(49)],
        *[round(0.5 + i * 0.5, 1) for i in range(49)],
        25.0, 50.0, 75.0, 100.0
    ],
    "32-piece": [
        1.005,
        *[round(1.01 + i * 0.01, 2) for i in range(9)],
        *[round(1.1 + i * 0.1, 1) for i in range(9)],
        1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0,
        10.0, 20.0, 30.0, 50.0
    ],
    "34-piece": [
        1.005,
        *[round(1.01 + i * 0.01, 2) for i in range(9)],
        *[round(1.1 + i * 0.1, 1) for i in range(9)],
        1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0,
        10.0, 20.0, 30.0, 40.0, 50.0
    ]
}

# ==========================================
# Algorithm Definition
# ==========================================
def find_combination(target, available_blocks, max_blocks=5):
    """
    Finds the exact combination of gauge blocks to meet the target.
    Uses integers (microns) to prevent floating point inaccuracies.
    """
    target_u = int(round(target * 1000))
    blocks_u = [int(round(b * 1000)) for b in available_blocks]
    
    blocks_u.sort(reverse=True)

    for r in range(1, max_blocks + 1):
        for combo in itertools.combinations(blocks_u, r):
            if sum(combo) == target_u:
                return [b / 1000.0 for b in combo]
                
    return None

# ==========================================
# Streamlit UI
# ==========================================
st.set_page_config(page_title="Gauge Block Calculator", layout="centered")

saved_settings = load_settings()

st.title("Gauge Block Combination Calculator")

with st.sidebar:
    st.header("Settings")
    
    set_options = list(GAUGE_SETS.keys())
    default_set_index = set_options.index(saved_settings["selected_set"]) if saved_settings["selected_set"] in set_options else 0
    
    selected_set = st.selectbox("1. Select Gauge Block Set", options=set_options, index=default_set_index)
    
    st.markdown("---")
    st.header("Missing Blocks Management")
    
    num_missing = st.number_input("How many blocks are missing?", min_value=0, max_value=20, value=saved_settings["num_missing"], step=1)
    
    missing_blocks_list = []
    if num_missing > 0:
        st.write("Enter the sizes of the missing blocks:")
        for i in range(num_missing):
            saved_val = saved_settings["missing_blocks"][i] if i < len(saved_settings["missing_blocks"]) else 1.000
            
            missing_val = st.number_input(f"Missing Block {i+1} (mm)", min_value=0.000, max_value=200.000, value=float(saved_val), step=0.001, format="%.3f", key=f"missing_{i}")
            missing_blocks_list.append(missing_val)
    
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

st.markdown(f"**Active Pool:** {selected_set}")

col1, col2 = st.columns(2)
with col1:
    target_size = st.number_input("2. Target Size (mm)", min_value=0.500, max_value=200.000, value=10.000, step=0.001, format="%.3f")
with col2:
    num_sets = st.number_input("3. Number of concurrent sets needed", min_value=1, max_value=3, value=1, step=1)

if st.button("Calculate Combinations", type="primary"):
    
    current_pool = GAUGE_SETS[selected_set].copy()
    
    if missing_blocks_list:
        blocks_removed = 0
        for missing_size in missing_blocks_list:
            missing_u = int(round(missing_size * 1000))
            for b in current_pool:
                if int(round(b * 1000)) == missing_u:
                    current_pool.remove(b)
                    blocks_removed += 1
                    break 
        if blocks_removed > 0:
            st.info(f"Ignored {blocks_removed} missing block(s) from the calculation pool.")
    
    results = []
    failed = False
    
    with st.spinner('Calculating optimal combinations...'):
        for i in range(num_sets):
            combo = find_combination(target_size, current_pool)
            
            if combo:
                results.append(combo)
                for block in combo:
                    current_pool.remove(block)
            else:
                failed = True
                st.error(f"❌ Could not find a valid combination for Set {i + 1} using the available blocks.")
                break
                
    if not failed:
        st.success("✅ Combinations calculated successfully!")
        
        # Display Results
        for idx, combo in enumerate(results):
            st.subheader(f"Set {idx + 1}")
            
            combo_str = " + ".join([f"{b:.3f}" for b in combo])
            st.code(f"Blocks: {combo_str}\nTotal: {sum(combo):.3f} mm", language="text")
            
            for block in sorted(combo):
                st.markdown(f"- `{block:.3f} mm`")
            st.markdown("---")
            
        # Display Export Buttons
        st.subheader("Export Results")
        ex_col1, ex_col2 = st.columns(2)
        
        with ex_col1:
            csv_file = generate_csv(target_size, results)
            st.download_button(
                label="📄 Download as CSV",
                data=csv_file,
                file_name=f"Gauge_Setup_{target_size:.3f}mm.csv",
                mime="text/csv"
            )
            
        with ex_col2:
            pdf_file = generate_pdf(target_size, results, selected_set)
            st.download_button(
                label="📥 Download as PDF",
                data=pdf_file,
                file_name=f"Gauge_Setup_{target_size:.3f}mm.pdf",
                mime="application/pdf"
            )
