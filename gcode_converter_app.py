import streamlit as st
import re
import io

# Define team colors (based on typical ETech Chargers colors)
TEAM_BLUE_HEX = "#002060"
TEAM_GREEN_HEX = "#74B44C"
BACKGROUND_COLOR = "#FFFFFF"

def process_gcode(input_content):
    """
    Processes the input G-code content to comment out offending lines
    for 3-axis ShopBot compatibility.
    """
    output_lines = []
    lines = input_content.strip().splitlines()

    for line in lines:
        trimmed = line.strip()
        upper = trimmed.upper()
        parts = trimmed.split(',')
        
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

# --- Configuration for Logo and Colors ---

st.markdown(f"""
<style>
    .css-2trqyj {{
        color: {TEAM_BLUE_HEX};
        display: inline-block;
        margin-left: 10px;
        vertical-align: middle;
    }}
    .stButton>button {{
        background-color: {TEAM_GREEN_HEX} !important;
        border-color: {TEAM_GREEN_HEX} !important;
        color: white !important;
    }}
    .stSuccess {{
        background-color: #E8F5E9;
        color: {TEAM_GREEN_HEX};
    }}
</style>
""", unsafe_allow_html=True)


# --- Interface Headings ---

col1, col2 = st.columns((1, 4))

with col1:
    try:
        # FIXED: Changed use_column_width to 'width'
        st.image("sparky_logo.png", width=100, output_format='PNG')
    except FileNotFoundError:
        st.warning("Logo file 'sparky_logo.png' not found.")

with col2:
    st.title("CNC CAM File Translator")

st.markdown("*Utility used to convert .nc files from PenguinCAM to .sbp files to use for ShopBot MAX CNC*")
st.markdown("See app code at: [https://github.com/ETechChargers5298/CNC-File-Translator](github.com/ETechChargers5298/CNC-File-Translator)")
# --- End of Updated Headings ---

uploaded_file = st.file_uploader("Upload .nc file", type=["nc", "txt"])

if uploaded_file:
    content = uploaded_file.getvalue().decode("utf-8")
    processed_content = process_gcode(content)
    
    original_name = uploaded_file.name
    if "." in original_name:
        name_parts = original_name.rsplit('.', 1)[0] # Get name without extension
        output_name = name_parts + ".SBP"
    else:
        output_name = original_name + ".SBP"

    st.success("File processed successfully!")
    
    st.download_button(
        label="Download Cleaned .SBP File",
        data=processed_content,
        file_name=output_name,
        mime="text/plain"
    )


