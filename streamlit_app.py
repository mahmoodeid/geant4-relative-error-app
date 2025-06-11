import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO

# Page configuration
st.set_page_config(
    page_title="Geant4 Relative Error Calculator",
    layout="wide",
)

# Title
st.markdown("# 🎯 Geant4 Relative Error Calculator")

# Sidebar for file uploads
st.sidebar.header("Upload Files")
output_file = st.sidebar.file_uploader(
    "Geant4 Output File", type=["txt", "csv"],
    help="File containing lines of i,j,k,total_val,total_val_sq,entries"
)
macro_file = st.sidebar.file_uploader(
    "Macro File", type=["mac", "txt"],
    help="Geant4 macro file with '/run/beamOn N'"
)

# Function to extract number of runs
@st.cache_data
def get_number_of_runs(macro_content: str) -> int:
    lines = macro_content.splitlines()
    beamon = [l for l in lines if "/run/beamOn" in l]
    if not beamon:
        return None
    return int(beamon[-1].split()[-1])

# Function to parse output data
@st.cache_data
def parse_output(output_content: str) -> pd.DataFrame:
    df_raw = pd.read_csv(
        StringIO(output_content), delim_whitespace=True,
        header=None, comment='#', engine='python'
    )
    # Split first column by commas
    df_split = df_raw[0].str.split(",", expand=True)
    df_split.columns = ["i", "j", "k", "total_val", "total_val_sq", "entries"]
    df_split[["total_val", "total_val_sq", "entries"]] = df_split[["total_val", "total_val_sq", "entries"]].astype(float)
    return df_split

# Color function for relative error

def color_error(val):
    try:
        if val < 15:
            color = '#a8e6a3'  # green
        elif val < 30:
            color = '#ffd59e'  # orange
        else:
            color = '#f28c8c'  # red
    except:
        color = ''
    return f'background-color: {color}'

# Main execution: display table when both files are uploaded
if output_file and macro_file:
    # Read file contents
    macro_text = StringIO(macro_file.getvalue().decode("utf-8")).read()
    output_text = output_file.getvalue().decode("utf-8")

    # Extract number of runs
    n_runs = get_number_of_runs(macro_text)
    if n_runs is None:
        st.error("No '/run/beamOn' command found in macro file.")
    else:
        st.success(f"Number of runs (beamOn): {n_runs:,}")

        # Parse output and compute metrics
        df = parse_output(output_text)
        df['mean'] = df['total_val'] / n_runs
        variance = df['total_val_sq'] / n_runs - df['mean'] ** 2
        stderr = np.sqrt(np.clip(variance / n_runs, 0, None))
        df['rel_err_%'] = (stderr / df['mean']).replace([np.inf, -np.inf], 0).fillna(0) * 100

        # Prepare display
        display_df = df[["i", "j", "k", "total_val", "mean", "rel_err_%"]].rename(
            columns={
                "i": "Bin i", "j": "Bin j", "k": "Bin k",
                "total_val": "Total Value", "mean": "Mean",
                "rel_err_%": "Relative Error (%)"
            }
        )

        # Apply formatting and coloring
        styled = (
            display_df.style
                .format({
                    "Total Value": "{:.2e}",
                    "Mean": "{:.2e}",
                    "Relative Error (%)": "{:.2f}"
                })
                .applymap(color_error, subset=["Relative Error (%)"])
                .set_properties(**{'font-size': '24px', 'text-align': 'center'})
        )

        st.markdown("### Results Table")
        st.dataframe(styled, use_container_width=True)
else:
    st.info("Please upload both a Geant4 output file and a macro file to proceed.")
