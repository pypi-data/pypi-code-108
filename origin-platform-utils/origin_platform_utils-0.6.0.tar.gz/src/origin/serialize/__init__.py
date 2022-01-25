from .serializer import Serializer, Serializable  # noqa: F401
from .serpyco import SerpycoSimpleSerializer, SerpycoJsonSerializer


simple_serializer = SerpycoSimpleSerializer()

json_serializer = SerpycoJsonSerializer()
