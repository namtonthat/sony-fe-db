import streamlit as st
import polars as pl

DATA_URL = "https://git@github.com:namtonthat/sony-fe-db.git"

data = pl.read_parquet('outputs/lens.parquet')

# st.write(data)
st.set_page_config(layout="wide", page_title="Lens Database", page_icon="📸")

# filter pane details
apertures = data.select('min_aperture').unique()
st.write(data.select('min_aperture').unique())

with st.sidebar:
    st.header("filters")
    st.markdown("""---""")
    # st.select_slider(
    #     label="min aperture",
    #     options = apertures
    # )


st.title('📸  Lens Database')

