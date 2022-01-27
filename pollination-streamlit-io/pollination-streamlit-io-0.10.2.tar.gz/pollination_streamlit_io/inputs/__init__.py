import os
import streamlit.components.v1 as components

__all__ = ['send']

_RELEASE = True

if not _RELEASE:
    _component_func_send = components.declare_component(
        "set",
        url="http://localhost:3004",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "send")
    _component_func_send = components.declare_component("send", path=build_dir)

def send(data: dict, 
    uniqueId: str, 
    options: dict = {},
    key=None) -> str:
    """Create a new instance of "button.send".

    Parameters
    ----------
    data: dict
        A Python dictionary. When you run Pollination command it MUST be Pollination model
        Otherwise it MUST be ladybug geometry dictionary (see. to_dict).
    uniqueId: str
        A key to recognize what geometries come from streamlit on Rhino. It becomes 
        a userString inside Rhino.
    options: dict
        A Python dictionary to specify options to use for baking geometry.
        If you use BakePollinationModel you do not need layer options.
        .. code-block:: python
            {
                "layer": "My-Custom-Layer",
                "units': "Meters"
            }
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    """
    component_value = _component_func_send(
        data=data,
        uniqueId=uniqueId,
        options=options,
        key=key, 
        default="NAN")

    return component_value

if not _RELEASE:
    import streamlit as st
    import json

    st.subheader("Magic Checkbox")

    data_to_pass = [{
            "type": "Mesh3D",
            "vertices": [(0, 0, 0), (10, 0, 0), (0, 10, 0)],
            "faces": [(0, 1, 2)],
            "colors": [{"r": 255, "g": 0, "b": 0}]
        }, 
        { 
            'type': 'Polyline2D',
             'vertices': [[0, 0], [10, 0], [0, 10]] 
        }]

    send(
        data=data_to_pass, 
        uniqueId="my-secret-key", 
        options={
            "layer": "MyCustomLayer", 
            "units": "Feet"
            },
        key="secret-key-1")

