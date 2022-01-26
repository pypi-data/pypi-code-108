from weakref import WeakSet
import colorlog
from tqdm import tqdm
from .utils import classproperty
from .geo_default_types import create_geo_classes


logger = colorlog.getLogger('PySimultan')


class GeometryModel(object):

    _cls_instances = WeakSet()      # weak set with all created objects
    _create_all = False             # if true all properties are evaluated to create python objects when initialized

    @classproperty
    def _cls_instances_dict(cls):
        return dict(zip([x.id for x in cls._cls_instances], [x() for x in cls._cls_instances]))

    @classproperty
    def cls_instances(cls):
        return list(cls._cls_instances)

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        if "_cls_instances" not in cls.__dict__:
            cls._cls_instances = WeakSet()
        try:
            cls._cls_instances.add(instance)
        except Exception as e:
            logger.error(f'Error adding instance {instance} to _cls_instances: {e}')

        return instance

    def __init__(self, *args, **kwargs):
        self._wrapped_obj = kwargs.get('wrapped_obj', None)
        self.template_parser = kwargs.get('template_parser', None)

        self._vertices = kwargs.get('vertices', None)
        self._edges = kwargs.get('edges', None)
        self._edge_loops = kwargs.get('edge_loops', None)
        self._faces = kwargs.get('faces', None)
        self._volumes = kwargs.get('volumes', None)
        self._layers = kwargs.get('layers', None)

        self._geo_types = kwargs.get('geo_types', None)

        self.GeoBaseClass, self.LayerCls, self.VertexCls, self.EdgeCls, self.EdgeLoopCls, self.FaceCls, self.VolumeCls = create_geo_classes(self._geo_types)

        self.loaded = False

        # self.load_all()

    @property
    def id(self):
        return self._wrapped_obj.Id

    @property
    def filename(self):
        return self._wrapped_obj.File.Name

    @property
    def name(self):
        if self._wrapped_obj is not None:
            return self._wrapped_obj.Name

    @name.setter
    def name(self, value):
        if self._wrapped_obj is not None:
            self._wrapped_obj.Name = value

    @property
    def layers(self):
        if not self.loaded:
            self.load_all()
        if self._layers is None:
            self._layers = self.get_layers()
        return self._layers

    @property
    def vertices(self):
        if not self.loaded:
            self.load_all()

        if self._vertices is None:
            self._vertices = self.get_vertices()
        return self._vertices

    @property
    def edges(self):
        if not self.loaded:
            self.load_all()
        if self._edges is None:
            self._edges = self.get_edges()
        return self._edges

    @property
    def edge_loops(self):
        if not self.loaded:
            self.load_all()
        if self._edge_loops is None:
            self._edge_loops = self.get_edge_loops()
        return self._edge_loops

    @property
    def faces(self):
        if not self.loaded:
            self.load_all()
        if self._faces is None:
            self._faces = self.get_faces()
        return self._faces

    @property
    def volumes(self):
        if not self.loaded:
            self.load_all()
        if self._volumes is None:
            self._volumes = self.get_volumes()
        return self._volumes

    def __getattribute__(self, attr):
        try:
            return object.__getattribute__(self, attr)
        except KeyError:
            wrapped = object.__getattribute__(self, '_wrapped_obj')
            if wrapped is not None:
                return object.__getattribute__(wrapped, attr)
            else:
                raise KeyError

    def __setattr__(self, attr, value):

        if hasattr(self, '_wrapped_obj'):

            if hasattr(self._wrapped_obj, attr) and (self._wrapped_obj is not None):
                object.__setattr__(self._wrapped_obj, attr, value)
            else:
                object.__setattr__(self, attr, value)
        else:
            object.__setattr__(self, attr, value)

    def get_vertices(self):
        return [self.VertexCls(wrapped_obj=x, geometry_model=self) for x in tqdm(self._wrapped_obj.Geometry.Vertices.Items)]

    def get_edges(self):
        return [self.EdgeCls(wrapped_obj=x, geometry_model=self) for x in tqdm(self._wrapped_obj.Geometry.Edges.Items)]

    def get_edge_loops(self):
        return [self.EdgeLoopCls(wrapped_obj=x, geometry_model=self) for x in tqdm(self._wrapped_obj.Geometry.EdgeLoops.Items)]

    def get_faces(self):
        return [self.FaceCls(wrapped_obj=x, geometry_model=self) for x in tqdm(self._wrapped_obj.Geometry.Faces.Items)]

    def get_volumes(self):
        return [self.VolumeCls(wrapped_obj=x, geometry_model=self) for x in tqdm(self._wrapped_obj.Geometry.Volumes.Items)]

    def get_layers(self):
        return [self.LayerCls(wrapped_obj=x, geometry_model=self) for x in tqdm(self._wrapped_obj.Geometry.Layers.Items)]

    def get_face_by_id(self, id):

        face = self.FaceCls.get_obj_by_id(id)
        if face is None:
            _ = self.faces
        face = self.FaceCls.get_obj_by_id(id)
        return face

    def get_zone_by_id(self, id):

        zone = self.VolumeCls.get_obj_by_id(id)
        if zone is None:
            _ = self.volumes
        zone = self.VolumeCls.get_obj_by_id(id)
        return zone

    def load_all(self):

        self.loaded = True

        logger.info(f'Geometry model: {self.name}: loading vertices')
        _ = self.vertices
        logger.info(f'Geometry model: {self.name}: loading edges')
        _ = self.edges
        logger.info(f'Geometry model: {self.name}: loading edge loops')
        _ = self.edge_loops
        logger.info(f'Geometry model: {self.name}: loading faces')
        _ = self.faces
        logger.info(f'Geometry model: {self.name}: loading volumes')
        _ = self.volumes

        logger.info(f'\n\nGeometry model import info:\n----------------------------------------------')
        logger.info(f'Geometry model: {self.name}')
        logger.info(f'Number vertices: {self.vertices.__len__()}')
        logger.info(f'Number edges: {self.edges.__len__()}')
        logger.info(f'Number edge_loops: {self.edge_loops.__len__()}')
        logger.info(f'Number faces: {self.faces.__len__()}')
        logger.info(f'Number volumes: {self.volumes.__len__()}\n\n')

        self.loaded = True

    def get_geo_components(self, geo):
        """
        Get the simultan components linked to the geometric instance
        :param geo: geometry instance of type BaseGeoBaseClass
        :return: simultan components
        """
        return self.template_parser.get_geo_components(geo)

    def get_py_geo_components(self, geo, template_name=None):
        """

        :param geo: geometry instance of type BaseGeoBaseClass
        :param template_name: name of the template which should be used to create the component; if None suiting template is found automatically; default: None
        :return: python typed components
        """
        return self.template_parser.get_py_geo_components(geo, template_name=template_name)

    def create_layer(self, name, layer=None, **kwags):
        new_layer = self.LayerCls.create_new(self._wrapped_obj, name, layer=layer, **kwags)
        if self._layers is None:
            self._layers = []
        return new_layer

    def create_vertex(self, position, layer=None, **kwags):
        """
        Creates a new vertex in this geometry model
        :param position: np.array, tuple or list with three float; example: [0, 1, 12.25], np.array([0, 1, 12.25]), (0, 1, 12.25)
        :param layer: Instance of PySimultan.geo_default_types.BaseGeometricLayer
        :return: Instance of PySimultan.geo_default_types.BaseGeometricVertex
        """
        new_vertex = self.VertexCls.create_new(self._wrapped_obj, position, layer, **kwags)
        if self._vertices is None:
            self._vertices = []
        self._vertices.append(new_vertex)
        return new_vertex

    def create_edge(self, v1, v2, layer=None, **kwags):
        """
        Creates a new edge in this geometry model
        :param v1: Vertex 1; Instance of PySimultan.geo_default_types.BaseGeometricVertex
        :param v2: Vertex 2; Instance of PySimultan.geo_default_types.BaseGeometricVertex
        :param layer: Instance of PySimultan.geo_default_types.BaseGeometricLayer
        :return: Instance of PySimultan.geo_default_types.BaseGeometricEdge
        """
        new_edge = self.EdgeCls.create_new(self._wrapped_obj, v1, v2, layer, **kwags)
        if self._edges is None:
            self._edges = []

        self._edges.append(new_edge)
        return new_edge

    def create_edge_loop(self, edges, layer=None, **kwags):
        """
        Creates a new edge_loop in this geometry model
        :param edges: List, tuple or np.array with Instance of PySimultan.geo_default_types.BaseGeometricEdge
        :param layer: Instance of PySimultan.geo_default_types.BaseGeometricLayer
        :return: Instance of PySimultan.geo_default_types.BaseGeometriceEdgeLoop
        """
        new_edge_loop = self.EdgeLoopCls.create_new(self._wrapped_obj, edges, layer, **kwags)
        if self._edge_loops is None:
            self._edge_loops = []
        self._edge_loops.append(new_edge_loop)
        return new_edge_loop

    def create_face(self, edge_loop, orientation='forward', openings=None, layer=None, **kwags):
        """
        Creates a new face in this geometry model
        :param edge_loop: Instance of PySimultan.geo_default_types.BaseGeometriceEdgeLoop
        :param orientation: Orientation of the face; default is 'forward'; Valid values: 'forward', 'backward', 'undefined'
        GeometricOrientation.Backward, GeometricOrientation.Undefined
        :param openings: List, array or tuple with PySimultan.geo_default_types.BaseGeometriceEdgeLoop
        :param layer: Instance of PySimultan.geo_default_types.BaseGeometriceEdgeLoop
        :return: Instance of PySimultan.geo_default_types.BaseGeometriceFace
        """
        # if orientation == 'forward':
        #     orientation = GeometricOrientation.Forward
        # elif orientation == 'backward':
        #     orientation = GeometricOrientation.Backward
        # else:
        #     orientation = GeometricOrientation.Undefined

        new_face = self.FaceCls.create_new(self._wrapped_obj, edge_loop, orientation, openings, layer, **kwags)
        if self._faces is None:
            self._faces = []
        self._faces.append(new_face)
        return new_face

    def create_volume(self, faces, layer=None, **kwags):
        new_volume = self.VolumeCls.create_new(self._wrapped_obj, faces, layer, **kwags)
        if self._volumes is None:
            self._volumes = []
        self._volumes.append(new_volume)
        return new_volume

    def associate_face_with_component(self, component, face):
        """
        Associate a face with a component
        :param component: Instance of PySimultan.default_types.SimultanObject, PySimultan.default_types.List, PySimultan.default_types.ReferenceList
        :param face: Instance of PySimultan.geo_default_types.BaseGeometriceFace
        """
        face.associate_with_component(component, exch=self.template_parser.current_data_model.exch)

    def associate_volume_with_component(self, component, volume):
        """

        :param component:
        :param volume:
        """
        volume.associate_with_component(component, exch=self.template_parser.current_data_model.exch)
