import streamlit as st
import polars as pl
import altair as alt

DATA_URL = "https://github.com/namtonthat/sony-fe-db/blob/main/outputs/lens.parquet"

data = pl.read_parquet('outputs/lens.parquet')

# st.write(data)
st.set_page_config(layout="wide", page_title="Lens Database", page_icon="📸")

def make_filters(option: pl.DataFrame) -> list:

    options = sorted(option.unique().to_list())

    return options

# filter pane details
apertures = make_filters(data['min_aperture'])
focal_lengths = make_filters(data['min_focal_length'])
manufacturers = make_filters(data['system'])
min_aperture = apertures[0]


with st.sidebar:
    st.header("filters")
    st.markdown("""---""")
    for manufacturer in manufacturers:
        st.checkbox(
            label=manufacturer,
            value=True,
        )

    st.select_slider(
        label="focal lengths",
        options=focal_lengths,
    )
    st.select_slider(
        label="minimum aperture (f/*)",
        options=apertures,
        value=min_aperture
    )

    st.markdown("lens type")
    prime=st.checkbox(
        label="prime"
    )

    zoom = st.checkbox(
        label="zoom"
    )


st.title('📸  Lens Database')

focal_length_vs_aperture = data.select(
    pl.col(['original_name', 'min_aperture', 'max_aperture', 'min_focal_length', 'max_focal_length'])
).with_columns(pl.col('original_name').alias('name'))

st.markdown("---")

st.subheader("focal length vs aperture")
lens_chart = alt.Chart(focal_length_vs_aperture.to_pandas()).mark_point().encode(
    x='min_focal_length:Q',
    y='min_aperture:Q',
    tooltip=["name"],
)

st.altair_chart(lens_chart, use_container_width = True)