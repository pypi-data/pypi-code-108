import json
import math
import pandas as pd
import pydeck as pdk
import requests
import streamlit as st
from dragonfly_parser import get_json_array

from pollination_streamlit_io import (button, inputs)

def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)

query = st.experimental_get_query_params()
platform = query['__platform__'][0] if '__platform__' in query else 'web'

cities = {
    'New York': [40.7495292, -73.9928448],
    'Boston': [42.361145, -71.057083],
    'Sydney': [-33.865143, 151.209900],
    'Rio De Janeiro': [-22.9094545, -43.1823189],
    'London': [51.5072, -0.1276]
}

option = st.selectbox("Samples",  cities.keys())
st.write(f"Lat: {cities[option][0]} ",
         f"Lon: {cities[option][1]}")

lat = st.number_input(
    "Latitude (deg)",
    min_value=-90.0,
    max_value=90.0,
    value=cities[option][0], step=0.1,
    format="%f")
lon = st.number_input(
    "Longitude (deg)",
    min_value=-180.0,
    max_value=180.0,
    value=cities[option][1],
    step=0.1,
    format="%f")
zoom = st.number_input(
    "Zoom (15 or 16)",
    min_value=15,
    max_value=16,
    value=15,
    step=1)

x, y = deg2num(lat, lon, zoom)
DATA_URL = f"https://data.osmbuildings.org/0.2/anonymous/tile/{zoom}/{x}/{y}.json"
print(DATA_URL)
print(lat, lon)

text_content, lbt_text_content = None, None
out_city, out_lbt_city = "city.json", "lbt_city.json"
try:
    req = requests.get(DATA_URL)
    with open(out_city, "w") as f:
        text_content = json.dumps(req.json())
except requests.exceptions.RequestException as e:
    st.error(f"{e}")
except Exception as e:
    st.error("Geojson not found.")

json_out = None
try:
    json_out = get_json_array(req.json(), lat, lon)
    with open(out_lbt_city, "w") as f:
        lbt_text_content = json_out
except Exception as e:
    st.error("Convert to LBT failed.")

if text_content:
    st.download_button(
        label='Download Geojson',
        data=text_content,
        file_name=out_city)

if lbt_text_content:
    st.download_button(
        label='Download Ladybug Json',
        data=lbt_text_content,
        file_name=out_lbt_city)


if platform == 'Rhino' and json_out:
    button.send('BakeGeometry',
        json.loads(json_out), 'my-secret-key', key='my-secret-key')
    
    inputs.send(json.loads(json_out), 
        'my-super-secret-key', 
        options={"layer":"StreamlitLayer"}, 
        key='0004')

st.pydeck_chart(pdk.Deck(map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(latitude=lat,
        longitude=lon,
        zoom=zoom,
        max_zoom=18,
        pitch=45,
        bearing=0),
    layers=[pdk.Layer('GeoJsonLayer',
            DATA_URL,
            opacity=0.5,
            stroked=False,
            filled=True,
            extruded=True,
            wireframe=True,
            get_elevation='properties.height',
            get_fill_color='[255, 0, 0]',
            get_line_color=[255, 255, 255],
            pickable=True),]))
