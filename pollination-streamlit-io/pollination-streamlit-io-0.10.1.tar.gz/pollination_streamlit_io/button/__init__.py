import os
import streamlit.components.v1 as components

__all__ = ['command', 'get', 'send']

_RELEASE = True

if not _RELEASE:
    _component_func_command = components.declare_component(
        "command",
        url="http://localhost:3001",
    )
    _component_func_get = components.declare_component(
        "get",
        url="http://localhost:3002",
    )
    _component_func_send = components.declare_component(
        "set",
        url="http://localhost:3003",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "command")
    _component_func_command = components.declare_component("command", path=build_dir)
    build_dir = os.path.join(parent_dir, "get")
    _component_func_get = components.declare_component("get", path=build_dir)
    build_dir = os.path.join(parent_dir, "send")
    _component_func_send = components.declare_component("send", path=build_dir)

def command(commandString: str, 
    commandOptions: str = "", 
    key: str = None) -> str:
    """Create a new instance of "button.command".

    Parameters
    ----------
    commandString: str
        Name of the command or a command macro. E.g. 'PO_AddRooms' OR '_Line 0,0,0 2,2,2'.
    commandOptions: str
        WIP.
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.

    Returns
    -------
    str
        If the command run successfully it is the name of the command.

    """
    component_value = _component_func_command(commandString=commandString, 
        commandOptions=commandOptions,
        key=key, 
        default=None)
    return component_value

def get(isPollinationModel: bool = False, 
    syncToken: str = "",
    key : str = None) -> str:
    """Create a new instance of "button.get".

    Parameters
    ----------
    isPollinationModel: bool
        True if you want to send a HBJson. False if you send geometries.
    syncToken: str
        A special string that enable the auto-refresh of the component. 
        Connect the return of the special.sync component.
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.

    Returns
    -------
    string
        Ladybug geometry JSON array string which comes from Rhino.
    """
    component_value = _component_func_get(isPollinationModel=isPollinationModel, 
        syncToken=syncToken,
        key=key, 
        default=None)

    return component_value

def send(action: str, 
    data: dict, 
    uniqueId: str, 
    options: dict = {},
    key=None) -> str:
    """Create a new instance of "button.send".

    Parameters
    ----------
    action: str
        The name of the command to run. Available commands are
        - BakeGeometry
        - ClearGeometry
        - DrawGeometry
        - DisableDraw
        - BakePollinationModel
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

    Returns
    -------
    str
        If the command run successfully it is the name of the command.

    """
    component_value = _component_func_send(action=action, 
        data=data,
        uniqueId=uniqueId,
        options=options,
        key=key, 
        default="NAN")

    return component_value

if not _RELEASE:
    import streamlit as st
    import json

    st.subheader("Component with constant args")

    name_input = st.text_input("Enter the command here!", value="PO_AddRooms")
    c_btn_value = command(commandString=name_input, key="secret-key-1")
    st.write(c_btn_value)

    st.subheader("Pollination, Bake Geometry Button")

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

    option = st.selectbox(
     "What command do you want to use?",
     ("BakeGeometry", "ClearGeometry", "DrawGeometry", 
        "DisableDraw"))
    
    command_active = send(
        action=option,
        data=data_to_pass, 
        uniqueId="my-secret-key", 
        options={
            "layer": "MyCustomLayer", 
            "units": "Feet"
            },
        key="secret-key-2")
    
    st.write("Command in action: %s !" % command_active)
    
    st.write(data_to_pass)

    command_model = send("BakePollinationModel",
        {}, "my-secret-key", key="secret-key-3")

    
    st.subheader("Pollination, Get Geometry Button")
    geometry = get(key="secret-key-4")
    st.write(geometry)

    st.subheader("Pollination, Get Pollination Model Button")
    model = get(isPollinationModel=True, key="secret-key-4")
    st.write(model)


    