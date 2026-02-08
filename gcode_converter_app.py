import streamlit as st
import re
import io
import matplotlib.pyplot as plt

# Define team colors
TEAM_BLUE_HEX = "#002060"
TEAM_GREEN_HEX = "#74B44C"
SHOPBOT_X_RED = "#FF0000"   # Red for X
SHOPBOT_Y_GREEN = "#00AA00" # Green for Y
START_COLOR = "#0000FF"     # Blue for Start
END_COLOR = "#FFD700"       # Yellow (Gold) for End

def process_gcode(input_content):
    """
    Processes the input G-code content to comment out offending lines
    and specifically intercepts PenguinCAM's default park (X0.5 Y24.0)
    to redirect to (0,0).
    """
    output_lines = []
    lines = input_content.strip().splitlines()

    for line in lines:
        trimmed = line.strip()
        upper = trimmed.upper()
        parts = trimmed.split(',')
        
        if "Y24.0" in upper or "Y 24.0" in upper:
            output_lines.append(f"' Redirected PenguinCAM Park ({line}) to Home:")
            output_lines.append("J2, 0, 0")
            continue

        isOffending = False

        if (any(x in upper for x in ['A', 'B']) or
            upper.startswith("M4") or upper.startswith("M5") or
            upper.startswith("J4") or upper.startswith("J5") or
            upper.startswith("S") or upper.startswith("T") or
            upper.startswith("M7") or upper.startswith("M8") or 
            upper.startswith("M9") or len(parts) > 4):
            isOffending = True

        if isOffending:
            output_lines.append(f"' {line}")
        else:
            output_lines.append(line)
            
    return "\n".join(output_lines)

def generate_preview(content):
    plt.clf() # Clear plot to prevent overlap
    x_coords = []
    y_coords = []
    cur_x, cur_y = 0.0, 0.0

    for line in content.splitlines():
        clean_line = re.sub(r'\(.*?\)', '', line).strip().upper()
        if not clean_line or clean_line.startswith("'"):
            continue

        updated = False
        x_match = re.search(r'X\s*([-+]?\d*\.\d+|[-+]?\d+)', clean_line)
        y_match = re.search(r'Y\s*([-+]?\d*\.\d+|[-+]?\d+)', clean_line)
        
        if x_match or y_match:
            if x_match: cur_x = float(x_match.group(1))
            if y_match: cur_y = float(y_match.group(1))
            updated = True
        else:
            parts = clean_line.split(',')
            if len(parts) >= 3:
                try:
                    cur_x = float(parts[1])
                    cur_y = float(parts[2])
                    updated = True
                except ValueError:
                    pass

        if updated:
            x_coords.append(cur_x)
            y_coords.append(cur_y)

    if not x_coords:
        return None

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(x_coords, y_coords, color=TEAM_BLUE_HEX, linewidth=1.2, label="Tool Path", zorder=3)
    
    x_range = max(x_coords) - min(x_coords) if x_coords else 1
    arrow_len = max(x_range * 0.1, 0.5) 
    
    # X-Axis Arrow (Red)
    ax.annotate('', xy=(arrow_len, 0), xytext=(0, 0),
                arrowprops=dict(edgecolor=SHOPBOT_X_RED, facecolor=SHOPBOT_X_RED, width=2, headwidth=8))
    ax.text(arrow_len, -arrow_len*0.1, 'X', color=SHOPBOT_X_RED, fontweight='bold', ha='center')

    # Y-Axis Arrow (Green)
    ax.annotate('', xy=(0, arrow_len), xytext=(0, 0),
                arrowprops=dict(edgecolor=SHOPBOT_Y_GREEN, facecolor=SHOPBOT_Y_GREEN, width=2, headwidth=8))
    ax.text(-arrow_len*0.1, arrow_len, 'Y', color=SHOPBOT_Y_GREEN, fontweight='bold', va='center')

    ax.scatter(x_coords[0], y_coords[0], color=START_COLOR, s=60, label="Start Point", zorder=5, edgecolors='black')
    ax.scatter(x_coords[-1], y_coords[-1], color=END_COLOR, s=60, label="End Point (Home)", zorder=6, edgecolors='black')
    
    ax.set_xlabel("X axis", color=SHOPBOT_X_RED, fontweight='bold')
    ax.set_ylabel("Y axis", color=SHOPBOT_Y_GREEN, fontweight='bold')
    ax.set_aspect('equal', adjustable='datalim')
    ax.set_title("ShopBot Preview", color=TEAM_BLUE_HEX, fontweight='bold')
    ax.grid(True, linestyle=':', alpha=0.5)
    ax.legend(loc='upper right', framealpha=0.9)
    
    return fig

# --- UPDATED STYLING SECTION ---
st.markdown(f"""
<style>
    .st-emotion-cache-2trqyj {{ color: {TEAM_BLUE_HEX}; }}
    
    /* Targets BOTH standard buttons and download buttons */
    .stButton>button, .stDownloadButton>button {{
        background-color: {TEAM_GREEN_HEX} !important;
        border-color: {TEAM_GREEN_HEX} !important;
        color: white !important;
    }}
    
    /* Change hover behavior to be slightly darker */
    .stButton>button:hover, .stDownloadButton>button:hover {{
        background-color: #5e923d !important;
        border-color: #5e923d !important;
    }}

    .stSuccess {{ background-color: #E8F5E9; color: {TEAM_GREEN_HEX}; }}
</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns((1, 4))
with col1:
    try:
        # Explicit width syntax for future compatibility
        st.image("sparky_logo.png", width=100)
    except:
        pass

with col2:
    st.title("CNC CAM File Translator")

st.markdown("*Convert PenguinCAM .nc to ShopBot .sbp | Origin Home Redirect Enabled*")

st.subheader("1. Upload NC File")
uploaded_file = st.file_uploader("Select .nc file:", type=["nc", "txt"])

if uploaded_file:
    raw_content = uploaded_file.getvalue().decode("utf-8")
    processed_content = process_gcode(raw_content)
    output_name = uploaded_file.name.rsplit('.', 1)[0] + ".SBP"

    # Moved success message between 1 and 2
    st.success("File processed successfully!")
    
    st.subheader("2. CNC Toolpath Cut Preview")
    fig = generate_preview(processed_content)
    
    if fig:
        # Modern width parameter to clear console warnings
        st.pyplot(fig, width='stretch')
    else:
        st.warning("No coordinate data found.")

    st.subheader("3. Download SBP File")
    st.download_button(
        label="Click to Download .sbp File",
        data=processed_content,
        file_name=output_name,
        mime="text/plain"
    )

    st.subheader("4. Run SBP File from Shopbot Software")
    st.write("Send the file to the computer directly connected to the ShopBot machine (Slack, Google Drive, etc.)")
