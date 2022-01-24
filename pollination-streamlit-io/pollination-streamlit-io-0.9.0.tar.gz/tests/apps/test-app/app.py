import streamlit as st
import json

from pollination_streamlit_io import (button, 
    inputs,
    special)

# get the platform from the query uri
query = st.experimental_get_query_params()
platform = query['__platform__'][0] if '__platform__' in query else 'web'

if platform == 'Rhino':
    # special controls
    st.subheader('Pollination Token for Sync')
    po_token = special.sync(key="my-po-sync")
    st.write(po_token)

    st.subheader('Stremlit Token for Sync')
    st_token = st.slider(
        "streamlit token",
        min_value=1,
        max_value=10,
        value=1, 
        step=1)
    
    options = {
        'Pollination Token': po_token,
        'Streamlit Token': st_token,
    }
    selection = st.selectbox(label="Select token type: ", options=
    options.keys())

    # common controls
    st.subheader('Pollination, Get Geometry Button')
    geometry = button.get(key='0001')
    if geometry:
        st.write(json.loads(geometry))

    st.subheader('Pollination, Get Pollination Model Button Sync')
    model = button.get(isPollinationModel=True, 
        syncToken=options[selection],
        key='0002-1')
    if model:
        st.write(json.loads(model))

    st.subheader('Pollination, Get Pollination Model Button')
    model = button.get(isPollinationModel=True, key='0002-2')
    if model:
        st.write(json.loads(model))

    st.subheader('Pollination, Bake Geometry Button')

    data_to_pass = [{
            'type': 'Mesh3D',
            'vertices': [(0, 0, 0), (10, 0, 0), (0, 10, 0)],
            'faces': [(0, 1, 2)],
            'colors': [{'r': 255, 'g': 0, 'b': 0}]
        }, 
        { 
            'type': 'Polyline2D',
                'vertices': [[0, 0], [10, 0], [0, 10]] 
        }]

    option = st.selectbox(
        'What command do you want to use?',
        ('BakeGeometry', 'ClearGeometry', 'DrawGeometry', 
        'DisableDraw', 'WrongCommand'))
    command_active = button.send(option,
        data_to_pass, 'my-secret-key', 
        options={"layer":"StreamlitLayer", "units": "Feet"}, 
        key='0003')
    st.write('Command in action: %s !' % command_active)
        
    st.write(data_to_pass)

    st.subheader('Pollination, Display Checkbox')

    inputs.send(data_to_pass, 
        'my-secret-key', 
        options={"layer":"StreamlitLayer"}, 
        key='0004')

    data_model = model if model else '{}'

    command_model = button.send('BakePollinationModel',
        json.loads(data_model), 'my-secret-key', key='0005')

    st.subheader('Pollination, Command Button')

    name_input = st.text_input('Enter the command here!', value='PO_AddRooms')
    command = button.command(commandString=name_input, key='0006')
    st.write(command)
