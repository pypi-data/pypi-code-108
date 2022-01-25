from datetime import datetime
import streamlit as st
import pandas as pd

from puddl.db.alchemy import App

# https://deckgl.readthedocs.io/en/latest/
import pydeck as pdk
from pydeck.data_utils.viewport_helpers import compute_view

st.set_page_config(layout='wide')
app = App('exif')


def select2datetime(s: str):
    dt0_iso = app.engine.execute(s).scalar()
    return datetime.fromisoformat(dt0_iso)


dt_min = select2datetime('SELECT min(dt) as dt FROM markers')
dt_max = select2datetime('SELECT max(dt) as dt FROM markers')
# st.sidebar.text(f'dt_min={dt_min}')
# st.sidebar.text(f'dt_max={dt_max}')


dt_range = st.sidebar.date_input('select date range', [dt_min, dt_max], min_value=dt_min, max_value=dt_max)


def load_data():
    ts0 = datetime.combine(dt_range[1], datetime.min.time())
    ts1 = datetime.combine(dt_range[1], datetime.max.time())
    data = pd.read_sql(
        'SELECT * FROM markers WHERE dt_ts BETWEEN %(ts0)s AND %(ts1)s',
        app.engine,
        params={'ts0': ts0, 'ts1': ts1},
    )

    def lowercase(x):
        return str(x).lower()

    data.rename(lowercase, axis='columns', inplace=True)
    return data


data_load_state = st.sidebar.text('Loading data...')
data = load_data()
data_load_state.text("Done loading.")


def thumb2icondata(t):
    return {
        # Icon from Wikimedia, used the Creative Commons Attribution-Share Alike 3.0
        # Unported, 2.5 Generic, 2.0 Generic and 1.0 Generic licenses
        "url": t,
        "width": 242,
        "height": 242,
        "anchorY": 242,
    }


data['icon_data'] = data['thumb'].map(thumb2icondata)

# Note that there is no independent scrolling (vertical overflow for a colum with height) for columns.
# https://github.com/streamlit/streamlit/issues/2447
col1, col2 = st.columns(2)

with col1:
    layer = pdk.Layer(
        "IconLayer",
        data,
        get_position="[lng, lat]",
        get_icon="icon_data",
        get_size=4,
        size_scale=15,
        pickable=True,
    )
    # Set the viewport location
    view_state = compute_view(data[['lng', 'lat']])
    view_state.pitch = 40.5
    view_state.bearing = -27.36

    r = pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"html": '<img src="{thumb}">', "style": {"color": "white"}},
    )
    st.pydeck_chart(r)

    if st.sidebar.checkbox('show raw data'):
        st.subheader('Raw data')
        st.write(data)

with col2:
    with st.container():
        for t in data['thumb']:
            st.image(t)
