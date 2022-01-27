import json
import streamlit as st
import pathlib
from streamlit_vtkjs import st_vtkjs

from ladybug_geometry.geometry3d.mesh import Mesh3D
from ladybug_geometry.geometry3d.polyline import Polyline3D 
from ladybug_geometry.geometry3d.line import LineSegment3D 
from ladybug_geometry.geometry3d.pointvector import Point3D
from ladybug_geometry.geometry3d.polyface import Polyface3D

from ladybug_vtk.fromgeometry import (
    from_line3d, 
    from_mesh3d, 
    from_point3d, 
    from_polyface3d, 
    from_polyline3d
)
from ladybug_vtk.model import Model
from ladybug_vtk.model_dataset import ModelDataSet

from pollination_streamlit_io import (button,
    special)

def get_polydata(value):
    data = json.loads(value)
    polydata = []
    lbt_data = []
    for el in data:
        info = json.loads(el)
        if info['type'] == 'Mesh3D':
            mesh = Mesh3D.from_dict(info)
            print(mesh)
            polydata.append(from_mesh3d(mesh))
            lbt_data.append(mesh)
        if info['type'] == 'Polyline3D':
            pln = Polyline3D.from_dict(info)
            print(pln)
            polydata.append(from_polyline3d(pln))
            lbt_data.append(pln)
        if info['type'] == 'LineSegment3D':
            crv = LineSegment3D.from_dict(info)
            print(crv)
            polydata.append(from_line3d(crv))
            lbt_data.append(crv)
        if info['type'] == 'Point3D':
            pt = Point3D.from_dict(info)
            print(pt)
            polydata.append(from_point3d(pt))
            lbt_data.append(pt)
        if info['type'] == 'Polyface3D':
            pli = Polyface3D.from_dict(info)
            print(pli)
            polydata.extend(from_polyface3d(pli))
            lbt_data.append(pli)
    
    dataSet = ModelDataSet('test', polydata)
    model = Model(dataSet)
    test = model.to_vtkjs('.', './geometry')
    return pathlib.Path(test), lbt_data

def run_viewer(value, key):
    file, ltb_data = get_polydata(value)
    dict_data = [_.to_dict() for _ in ltb_data]
    st_vtkjs(file.read_bytes(), True, key)
    return dict_data

# get the platform from the query uri
query = st.experimental_get_query_params()
platform = query['__platform__'][0] if '__platform__' in query else 'web'

if platform == 'Rhino':
    # special controls
    st.subheader('Pollination Token for Sync')
    po_token = special.sync(key="my-po-sync")
    st.write(po_token)

    # common controls
    # first sync button.get
    st.subheader('Pollination, Get Geometry Button')
    geometry = button.get(key='0001',
        syncToken=po_token)
    if geometry:
        dict_data = run_viewer(geometry, 
            key="my-super-viewer")
    
    # second sync button.get
    st.subheader('Pollination, Get Geometry Button')
    geometry = button.get(key='0002',
        syncToken=po_token)
    if geometry:
        dict_data = run_viewer(geometry,
        key="my-super-viewer-2")


