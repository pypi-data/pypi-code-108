import os
import meshio
import pathlib
import numpy as np
import pandas as pd
from copy import deepcopy

from .logger import logger
from PySimultan import TemplateParser, DataModel
from PySimultan.default_types import SimMultiValueBigTable
from .geometry.utils import generate_mesh

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 importlib_resources.
    import importlib_resources as pkg_resources


from . import resources

with pkg_resources.path(resources, 'mesh_template.yml') as r_path:
    template_filename = str(r_path)


class ProjectLoader(object):

    def __init__(self, *args, **kwargs):

        self.user_name = kwargs.get('user_name', 'admin')
        self.password = kwargs.get('password', 'admin')

        self.project_filename = kwargs.get('project_filename')
        self.template_filename = kwargs.get('template_filename', template_filename)

        self.template_parser = None
        self.data_model = None
        self.typed_data = None

        self.setup_components = []
        self.app = kwargs.get('app', None)

        self.loaded = False

    def load_project(self):

        logger.setLevel('INFO')
        self.template_parser = TemplateParser(template_filepath=self.template_filename)

        logger.info(f'Loading SIMULTAN Project: {self.project_filename}')
        self.data_model = DataModel(project_path=self.project_filename,
                                    user_name=self.user_name,
                                    password=self.password)
        logger.info(f'SIMULTAN Project loaded successfully')

        logger.info(f'Creating typed data model...')
        self.typed_data = self.data_model.get_typed_data(template_parser=self.template_parser, create_all=True)
        logger.info(f'Typed data model created successfully')

        # logger.info(f'Searching active ShadingAnalysis components...')
        # self.setup_components = [x for x in self.template_parser.template_classes['ShadingAnalysis']._cls_instances if bool(x.Active)]
        # logger.info(f'Found {self.setup_components.__len__()} active Shading Analyses')

        self.loaded = True

    def run(self, *args, **kwargs):

        self.loaded = True
        geo_model = kwargs.get('geo_model', None)

        typed_geo_model = next((x for x in self.template_parser.typed_geo_models.values() if x.id == geo_model.Id), None)
        if typed_geo_model is None:
            logger.error(f'Could not find geometry model {geo_model.Name} {geo_model.File} in typed_geo_models')

        mesh_export = MeshExport(geo_model=typed_geo_model,
                                 tables=kwargs.get('tables', None),
                                 mesh_filename=kwargs.get('mesh_filename', None),
                                 mesh_format=kwargs.get('mesh_format', None),
                                 template_parser=self.template_parser)
        mesh_export.create_mesh()

    def close_project(self):
        if self.loaded:
            self.typed_data = None
            self.setup_components = None
            self.loaded = False
            if self.data_model is not None:
                self.data_model.cleanup()
            self.data_model = None
            logger.info(f'Project closed')

    def save_project(self):
        self.data_model.save()


class MeshExport(object):

    def __init__(self, *args, **kwargs):

        self.geo_model = kwargs.get('geo_model', None)
        self.tables = kwargs.get('tables', None)
        self.mesh_filename = kwargs.get('mesh_filename', None)
        self.mesh_format = kwargs.get('mesh_format', None)
        self.template_parser = kwargs.get('template_parser', None)

    def create_mesh(self):

        vertices = self.geo_model.vertices
        edges = self.geo_model.edges
        edge_loops = self.geo_model.edge_loops
        faces = set(self.geo_model.faces)

        logger.info('Creating mesh....')

        # Fläche 84 2D: 1076741842
        # local_ids = [x.components[0].id.LocalId for x in faces]

        mesh = generate_mesh(vertices=vertices,
                             edges=edges,
                             edge_loops=edge_loops,
                             faces=faces,
                             volumes=[],
                             model_name=str(self.geo_model.id),
                             lc=999999,
                             min_size=0.1,
                             max_size=9999999,
                             dim=2,
                             mesh_size_from_faces=False,
                             id_getter=lambda x: x.components[0].id.LocalId)

        logger.info('Mesh created successfully')

        if not self.tables:
            filepath = pathlib.Path(self.mesh_filename)
            mesh_filename = os.path.join(str(filepath.parent), str(filepath.stem) + '.vtk')
            mesh.write(mesh_filename)
        else:

            mesh_data = {}

            for table in self.tables:
                logger.debug(f'adding data from table {table} to mesh')

                if not isinstance(table, SimMultiValueBigTable):
                    logger.error(f'Value file is not SimMultiValueBigTable but {type(table).__name__}')
                    continue

                py_table = self.template_parser.create_python_object(table, template_name='ValueField')
                values = np.zeros((mesh.cells_dict['triangle'].shape[0], py_table.shape[0]))

                for i, column in enumerate(py_table.columns):
                    if column in mesh.cell_sets.keys():
                        values[mesh.cell_sets[column][1], :] = py_table[column].values

                mesh_data[table.Name] = (py_table.index, values)

            if self.mesh_format == '.vtk':
                write_vtks(mesh, mesh_data, self.mesh_filename)
            elif self.mesh_format == '.xdmf':
                logger.warning('Attention: xdmf format contains errors.')
                write_xdmf(mesh, mesh_data, self.mesh_filename)


def write_vtks(mesh, mesh_data, filename):

    vtk_mesh = deepcopy(mesh)
    vtk_mesh.cell_data = {}
    vtk_mesh.cells = [mesh.cells[1]]

    # get max number of timesteps:
    shapes = [x[1].shape[1] for x in mesh_data.values()]
    max_shapes = max(shapes)

    for i in range(max_shapes):
        filepath = pathlib.Path(filename)
        cur_filename = os.path.join(str(filepath.parent), str(filepath.stem) + f'_{i}.vtk')
        vtk_mesh.cell_data = {}
        for key in mesh_data.keys():
            if (mesh_data[key][1].shape[1] - 1) >= i:
                vtk_mesh.cell_data[key] = [mesh_data[key][1][:, i]]
        meshio.vtk.write(cur_filename, vtk_mesh, binary=True)
        logger.info(f'Written mesh file {i} of {max_shapes-1}')


def write_xdmf(mesh, values, filename):
    vtk_mesh = deepcopy(mesh)
    vtk_mesh.cell_data = {}
    vtk_mesh.cells = [mesh.cells[1]]

    filepath = pathlib.Path(filename)
    xdmf_filename = os.path.join(str(filepath.parent), str(filepath.stem) + '.xdmf')

    try:
        with meshio.xdmf.TimeSeriesWriter(xdmf_filename) as writer:
            writer.write_points_cells(mesh.points, {'triangle': mesh.cells_dict['triangle']})

            writer.write_data(i, cell_data={table.Name: [values[:, i]]})
    except Exception as e:
        logger.error(f'Error writing data to mesh\n {e}')
    mesh.write(self.mesh_filename)
