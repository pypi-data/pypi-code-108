import typing
from typing import List as TypeList

from System.Windows.Media.Media3D import Point3D
from System import Array
from .GeometryViewer.Model.Geometry import Vertex, Edge, EdgeLoop, Face, Volume, Layer, PEdge, GeometricOrientation
from .GeometryViewer.Model import GeometryModel


GeometryModelType = typing.NewType('GeometryModel', GeometryModel)
EdgeModelType = typing.NewType('Edge', Edge)
EdgeLoopType = typing.NewType('EdgeLoop', EdgeLoop)
GeometricOrientationType = typing.NewType('GeometricOrientation', GeometricOrientation)


def create_layer(geometry_model: GeometryModelType, name: str):
    """
    Create a new layer in a geometry model
    :param geometry_model: GeometryViewer.Model.GeometryModel
    :param name: Name of the model; string
    :return: GeometryViewer.Model.Geometry.Layer
    """
    new_layer = Layer(geometry_model.Geometry, name)
    geometry_model.Geometry.Layers.Add(new_layer)
    return new_layer


def create_vertex(layer, position: typing.Iterable[float]):
    """
    Create a new vertex on a layer
    :param layer: GeometryViewer.Model.Geometry.Layer
    :param position: x, y, z position of the vertex, Iterable[float]
    :return: GeometryViewer.Model.Geometry.Vertex
    """
    return Vertex(layer, Point3D(position[0], position[1], position[2]))


def create_edge(layer, v1, v2):
    """
    Create a new edge on a layer
    :param layer: GeometryViewer.Model.Geometry.Layer
    :param v1: Vertex 1; GeometryViewer.Model.Geometry.Vertex
    :param v2: Vertex 2; GeometryViewer.Model.Geometry.Vertex
    :return: GeometryViewer.Model.Geometry.Edge
    """
    return Edge(layer, Array[Vertex]([v1, v2]))


def create_edge_loop(layer, edges: TypeList[EdgeModelType]):
    """
    Create a new edge loop on a layer
    :param layer: GeometryViewer.Model.Geometry.Layer
    :param edges: Iterable of GeometryViewer.Model.Geometry.Edges
    :return: GeometryViewer.Model.Geometry.EdgeLoop
    """
    return EdgeLoop(layer, Array[Edge](edges))


def create_face(layer, edge_loop, orientation: GeometricOrientationType, openings: TypeList[EdgeLoopType] = None):
    """
    Create a new face on a layer
    :param layer: GeometryViewer.Model.Geometry.Layer
    :param edge_loop: GeometryViewer.Model.Geometry.EdgeLoop
    :param orientation: GeometryViewer.Model.Geometry.GeometricOrientation
    :param openings: Iterable of GeometryViewer.Model.Geometry.EdgeLoop; optional
    :return: GeometryViewer.Model.Geometry.Face
    """
    if openings is None:
        openings = []

    return Face(layer, edge_loop, orientation, Array[EdgeLoop](openings))


def create_volume(layer, faces):
    """
    Create a new volume on a layer
    :param layer: GeometryViewer.Model.Geometry.Layer
    :param faces: Iterable of GeometryViewer.Model.Geometry.Face
    :return: Iterable of GeometryViewer.Model.Geometry.Volume
    """
    return Volume(layer, Array[Face](faces))
