from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.datastructures import Mesh

from compas_rv2.datastructures import Skeleton
from compas_rv2.datastructures import SubdMesh
from compas_rv2.datastructures import Pattern
from compas_rv2.datastructures import FormDiagram
from compas_rv2.datastructures import ForceDiagram
from compas_rv2.datastructures import ThrustDiagram

from .meshartist import MeshArtist
from .skeletonartist import SkeletonArtist
from .formartist import FormArtist
from .forceartist import ForceArtist
from .thrustartist import ThrustArtist

MeshArtist.register(Mesh, MeshArtist)
MeshArtist.register(Skeleton, SkeletonArtist)
MeshArtist.register(SubdMesh, MeshArtist)
MeshArtist.register(Pattern, MeshArtist)
MeshArtist.register(FormDiagram, FormArtist)
MeshArtist.register(ForceDiagram, ForceArtist)
MeshArtist.register(ThrustDiagram, ThrustArtist)
