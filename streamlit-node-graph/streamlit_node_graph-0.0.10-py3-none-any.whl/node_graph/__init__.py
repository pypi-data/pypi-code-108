import os
import streamlit.components.v1 as components
import json 

_RELEASE = False
_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component(
        "node_graph",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    print(build_dir)
    _component_func = components.declare_component("node_graph", path=build_dir)

def node_graph(model = False, item_types = [{"title":'item_1',"color":"rgb(255,0, 192)", "port_selection" : 'both'}], key="foo") -> dict:
    try:
        assert type(model) == type(True) or type(model) == type({}) 
    except AssertionError:
        print("needs to be a bool or dict passed node_graph as model param")
        raise
    default_compoennt_value = json.dumps({'model': model, 'lastNodeSelected': None})
    if model:
        model=json.dumps(model)
    component_value = _component_func(model=model, item_types=item_types, key=key, default=default_compoennt_value)
    
    return json.loads(component_value)

if not _RELEASE:
    import streamlit as st
    item_types = [
        {"title":'Purchase',"color":"rgb(255,0, 192)", "port_selection" : 'out', "icon" : 'shopping-cart'},
        {"title":'Inventory',"color":"rgb(255, 192, 0)", "port_selection" : 'both', "icon" : 'warehouse'},
        {"title":'Conversion',"color":"rgb(0, 192, 255)", "port_selection" : 'both', "icon": "industry"},
        {"title":'Sales',"color":"rgb(0,255, 192)", "port_selection" : 'in', "icon" : 'dollar-sign'},
        
        ]

    diagram = node_graph(item_types=item_types)
    st.write(diagram)
