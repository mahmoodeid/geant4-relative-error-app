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
st.title("🎯 Geant4 Relative Error Calculator")

# Sidebar for file uploads
st.sidebar.header("Upload Files")
output_file = st.sidebar.file_uploader(
    "Geant4 Output File",
    type=["txt", "csv"],
    help="File containing lines of i,j,k,total_val,total_val_sq,entries"
)
macro_file = st.sidebar.file_uploader(
    "Macro File",
    type=["mac", "txt"],
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
    # Read whitespace-delimited with first column as CSV
    df_raw = pd.read_csv(
        StringIO(output_content),
        delim_whitespace=True,
        header=None,
        comment='#',
        engine='python'
    )
    # Split first column by commas
    df_split = df_raw[0].str.split(",", expand=True)
    df_split.columns = ["i", "j", "k", "total_val", "total_val_sq", "entries"]
    # Convert to numeric
    df_split[["total_val", "total_val_sq", "entries"]] = df_split[["total_val", "total_val_sq", "entries"]].astype(float)
    return df_split

# Display table when both files are uploaded
if output_file and macro_file:
    # Read contents
    macro_text = StringIO(macro_file.getvalue().decode("utf-8")).read()
    output_text = output_file.getvalue().decode("utf-8")

    # Extract number of runs
    n_runs = get_number_of_runs(macro_text)
    if n_runs is None:
        st.error("No '/run/beamOn' command found in macro file.")
    else:
        st.success(f"Number of runs (beamOn): {n_runs:,}")

        # Parse output data
        df = parse_output(output_text)

        # Compute mean, variance, standard error, and relative error
        df['mean'] = df['total_val'] / n_runs
        variance = df['total_val_sq'] / n_runs - df['mean']**2
        stderr = np.sqrt(np.clip(variance / n_runs, 0, None))
        df['rel_err_%'] = (stderr / df['mean']).replace([np.inf, -np.inf], 0).fillna(0) * 100

        # Select columns to display
        display_df = df[["i", "j", "k", "total_val", "mean", "rel_err_%"]]
        display_df = display_df.rename(columns={
            "i": "Bin i",
            "j": "Bin j",
            "k": "Bin k",
            "total_val": "Total Value",
            "mean": "Mean",
            "rel_err_%": "Relative Error (%)"
        })

        # Styling for large font
        st.markdown(
            "<style>
            .dataframe td { font-size: 18px; }
            .dataframe th { font-size: 20px; }
            </style>",
            unsafe_allow_html=True
        )

        st.markdown("### Results Table", unsafe_allow_html=True)
        st.dataframe(display_df, use_container_width=True)
else:
    st.info("Please upload both a Geant4 output file and a macro file to proceed.")
import pandas as pd
import numpy as np
from io import StringIO

# Page configuration
st.set_page_config(
    page_title="Geant4 Relative Error Calculator",
    layout="wide",
)

# Title
st.title("🎯 Geant4 Relative Error Calculator")

# Sidebar for file uploads
st.sidebar.header("Upload Files")
output_file = st.sidebar.file_uploader(
    "Geant4 Output File",
    type=["txt", "csv"],
    help="File containing lines of i,j,k,total_val,total_val_sq,entries"
)
macro_file = st.sidebar.file_uploader(
    "Macro File",
    type=["mac", "txt"],
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
    # Read whitespace-delimited with first column as CSV
    df_raw = pd.read_csv(
        StringIO(output_content),
        delim_whitespace=True,
        header=None,
        comment='#',
        engine='python'
    )
    # Split first column by commas
    df_split = df_raw[0].str.split(",", expand=True)
    df_split.columns = ["i", "j", "k", "total_val", "total_val_sq", "entries"]
    # Convert to numeric
    df_split[["total_val", "total_val_sq", "entries"]] = df_split[["total_val", "total_val_sq", "entries"]].astype(float)
    return df_split

# Display table when both files are uploaded
if output_file and macro_file:
    # Read contents
    macro_text = StringIO(macro_file.getvalue().decode("utf-8")).read()
    output_text = output_file.getvalue().decode("utf-8")

    # Extract number of runs
    n_runs = get_number_of_runs(macro_text)
    if n_runs is None:
        st.error("No '/run/beamOn' command found in macro file.")
    else:
        st.success(f"Number of runs (beamOn): {n_runs:,}")

        # Parse output data
        df = parse_output(output_text)

        # Compute mean, variance, standard error, and relative error
        df['mean'] = df['total_val'] / n_runs
        variance = df['total_val_sq'] / n_runs - df['mean']**2
        stderr = np.sqrt(np.clip(variance / n_runs, 0, None))
        df['rel_err_%'] = (stderr / df['mean']).replace([np.inf, -np.inf], 0).fillna(0) * 100

        # Select columns to display
        display_df = df[["i", "j", "k", "total_val", "mean", "rel_err_%"]]
        display_df = display_df.rename(columns={
            "i": "Bin i",
            "j": "Bin j",
            "k": "Bin k",
            "total_val": "Total Value",
            "mean": "Mean",
            "rel_err_%": "Relative Error (%)"
        })

        # Styling for large font
        st.markdown(
            "<style>
            .dataframe td { font-size: 18px; }
            .dataframe th { font-size: 20px; }
            </style>",
            unsafe_allow_html=True
        )

        st.markdown("### Results Table", unsafe_allow_html=True)
        st.dataframe(display_df, use_container_width=True)
else:
    st.info("Please upload both a Geant4 output file and a macro file to proceed.")
