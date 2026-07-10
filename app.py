import streamlit as st
import itertools

# ==========================================
# Gauge Block Set Definitions
# ==========================================
# Note: Standard arrays are provided based on common manufacturing specs. 
# You can adjust the arrays below to match the exact blocks in your physical boxes.

GAUGE_SETS = {
    "87-piece metric gauge block set (Grade 1)": [
        *[round(1.001 + i * 0.001, 3) for i in range(9)],  # 1.001 to 1.009
        *[round(1.01 + i * 0.01, 2) for i in range(49)],   # 1.01 to 1.49
        *[round(0.5 + i * 0.5, 1) for i in range(19)],     # 0.5 to 9.5
        *[float(10 + i * 10) for i in range(10)]           # 10 to 100
    ],
    "83-piece metric gauge block set (Grade 2)": [
        1.005,
        *[round(1.01 + i * 0.01, 2) for i in range(49)],   # 1.01 to 1.49
        *[round(0.5 + i * 0.5, 1) for i in range(19)],     # 0.5 to 9.5
        *[float(10 + i * 10) for i in range(10)],          # 10 to 100
        1.0, 1.001, 1.002, 1.003, 1.004, 1.006, 1.007, 1.008, 1.009 # standard variations
    ],
    "47-piece Ceramic Set (grade 0)": [
        1.005,
        *[round(1.01 + i * 0.01, 2) for i in range(9)],    # 1.01 to 1.09
        *[round(1.1 + i * 0.1, 1) for i in range(9)],      # 1.1 to 1.9
        *[float(1 + i) for i in range(24)],                # 1 to 24
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
                st.error(f"❌ Could not find a valid combination for Set {i + 1} using the remaining blocks in the {selected_set}.")
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
