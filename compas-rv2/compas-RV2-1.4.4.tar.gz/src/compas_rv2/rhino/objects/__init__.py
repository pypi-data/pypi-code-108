from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas_rv2.datastructures import Skeleton
from compas_rv2.datastructures import SubdMesh
from compas_rv2.datastructures import Pattern
from compas_rv2.datastructures import FormDiagram
from compas_rv2.datastructures import ForceDiagram
from compas_rv2.datastructures import ThrustDiagram

from .meshobject import MeshObject
from .skeletonobject import SkeletonObject
from .patternobject import PatternObject
from .formobject import FormObject
from .forceobject import ForceObject
from .thrustobject import ThrustObject
from .subdobject import SubdObject

MeshObject.register(Skeleton, SkeletonObject)
MeshObject.register(SubdMesh, SubdObject)
MeshObject.register(Pattern, PatternObject)
MeshObject.register(FormDiagram, FormObject)
MeshObject.register(ForceDiagram, ForceObject)
MeshObject.register(ThrustDiagram, ThrustObject)
