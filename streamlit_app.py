import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO

# Page config
st.set_page_config(page_title="Geant4 Relative Error Calculator", layout="wide")

st.markdown("# 🎯 Geant4 Relative Error Calculator")

# --- Sidebar uploads ---
st.sidebar.header("Upload Files")
output_file = st.sidebar.file_uploader(
    "Geant4 Output File", type=["txt","csv"],
    help="Lines: i,j,k,total_val,total_val_sq,entries"
)
macro_file = st.sidebar.file_uploader(
    "Macro File", type=["mac","txt"],
    help="Must contain a '/run/beamOn N' line"
)

@st.cache_data
def get_number_of_runs(macro_text: str) -> int:
    lines = macro_text.splitlines()
    beamons = [L for L in lines if "/run/beamOn" in L]
    if not beamons:
        return None
    return int(beamons[-1].split()[-1])

@st.cache_data
def parse_output(txt: str) -> pd.DataFrame:
    df_raw = pd.read_csv(
        StringIO(txt),
        delim_whitespace=True, header=None,
        comment="#", engine="python"
    )
    cols = df_raw[0].str.split(",", expand=True)
    cols.columns = ["i","j","k","total_val","total_val_sq","entries"]
    cols[["total_val","total_val_sq","entries"]] = cols[["total_val","total_val_sq","entries"]].astype(float)
    return cols

def color_error(val):
    if val < 15:
        return "background-color:#a8e6a3"   # green
    if val < 30:
        return "background-color:#ffd59e"   # orange
    return "background-color:#f28c8c"       # red

# --- Main logic ---
if output_file and macro_file:
    macro_text  = StringIO(macro_file.getvalue().decode()).read()
    output_text = output_file.getvalue().decode()

    n_runs = get_number_of_runs(macro_text)
    if n_runs is None:
        st.error("❌ Could not find any `/run/beamOn N` in your macro file.")
    else:
        st.success(f"Runs (beamOn): **{n_runs:,}**")

        df = parse_output(output_text)
        df["mean"]     = df["total_val"]   / n_runs
        var            = df["total_val_sq"]/n_runs - df["mean"]**2
        stderr         = np.sqrt(np.clip(var/n_runs, 0, None))
        df["rel_err_%"]= (stderr/df["mean"]).replace([np.inf,-np.inf],0).fillna(0)*100

        display_df = df[["i","j","k","total_val","mean","rel_err_%"]].rename(
            columns={
                "i":"Bin i","j":"Bin j","k":"Bin k",
                "total_val":"Total Value","mean":"Mean",
                "rel_err_%":"Relative Error (%)"
            }
        )

        # Style it
        styled = (
            display_df.style
                .format({
                    "Total Value":"{:.2e}",
                    "Mean":"{:.2e}",
                    "Relative Error (%)":"{:.2f}"
                })
                .applymap(color_error, subset=["Relative Error (%)"])
                .set_properties(**{"font-size":"28px","text-align":"center"})
        )

        # Render raw HTML
        st.markdown("### Results Table", unsafe_allow_html=True)
        html = styled.to_html()
        st.write(html, unsafe_allow_html=True)

else:
    st.info("⚠️ Please upload both the Geant4 output and the macro file.")
