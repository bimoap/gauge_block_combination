import streamlit as st
import itertools

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
    
    # Sort descending to prioritize larger blocks (often results in fewer blocks needed)
    blocks_u.sort(reverse=True)

    # Iterative deepening to guarantee the solution with the minimum number of blocks
    for r in range(1, max_blocks + 1):
        for combo in itertools.combinations(blocks_u, r):
            if sum(combo) == target_u:
                return [b / 1000.0 for b in combo]
                
    return None

# ==========================================
# Streamlit UI
# ==========================================
st.set_page_config(page_title="Gauge Block Calculator", layout="centered")

st.title("Gauge Block Combination Calculator")

with st.sidebar:
    st.header("Settings")
    selected_set = st.selectbox("1. Select Gauge Block Set", options=list(GAUGE_SETS.keys()))
    
    st.markdown("---")
    st.header("Missing Blocks Management")
    num_missing = st.number_input("How many blocks are missing from the set?", min_value=0, max_value=20, value=0, step=1)
    
    missing_blocks_list = []
    if num_missing > 0:
        st.write("Enter the sizes of the missing blocks:")
        for i in range(num_missing):
            missing_val = st.number_input(f"Missing Block {i+1} (mm)", min_value=0.000, max_value=200.000, value=1.000, step=0.001, format="%.3f", key=f"missing_{i}")
            missing_blocks_list.append(missing_val)
            
    st.markdown("---")
    st.markdown("App developed & maintained by: **Bimo**")

st.markdown(f"**Active Pool:** {selected_set}")

col1, col2 = st.columns(2)
with col1:
    target_size = st.number_input("2. Target Size (mm)", min_value=0.500, max_value=200.000, value=10.000, step=0.001, format="%.3f")
with col2:
    num_sets = st.number_input("3. Number of concurrent sets needed", min_value=1, max_value=3, value=1, step=1)

if st.button("Calculate Combinations", type="primary"):
    
    # Load a fresh copy of the selected physical block set
    current_pool = GAUGE_SETS[selected_set].copy()
    
    # Process and remove missing blocks from the pool
    if missing_blocks_list:
        blocks_removed = 0
        for missing_size in missing_blocks_list:
            missing_u = int(round(missing_size * 1000))
            # Find and remove the block by matching the integer micron value
            for b in current_pool:
                if int(round(b * 1000)) == missing_u:
                    current_pool.remove(b)
                    blocks_removed += 1
                    break # Only remove one instance
        if blocks_removed > 0:
            st.info(f"Ignored {blocks_removed} missing block(s) from the calculation pool.")
    
    results = []
    failed = False
    
    with st.spinner('Calculating optimal combinations...'):
        for i in range(num_sets):
            # Find a combo from the remaining available blocks
            combo = find_combination(target_size, current_pool)
            
            if combo:
                results.append(combo)
                # Remove the used blocks from the pool so they can't be used in the next set
                for block in combo:
                    current_pool.remove(block)
            else:
                failed = True
                st.error(f"❌ Could not find a valid combination for Set {i + 1} using the available blocks.")
                break
                
    # Display Results
    if not failed:
        st.success("✅ Combinations calculated successfully!")
        
        for idx, combo in enumerate(results):
            st.subheader(f"Set {idx + 1}")
            
            # Format the output clearly
            combo_str = " + ".join([f"{b:.3f}" for b in combo])
            st.code(f"Blocks: {combo_str}\nTotal: {sum(combo):.3f} mm", language="text")
            
            # Show individual blocks as bullet points
            for block in sorted(combo):
                st.markdown(f"- `{block:.3f} mm`")
            st.markdown("---")
