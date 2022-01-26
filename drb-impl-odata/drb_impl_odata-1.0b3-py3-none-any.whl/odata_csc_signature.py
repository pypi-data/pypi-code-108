import uuid

from drb import DrbNode
from drb.exceptions import DrbException
from drb.factory import DrbSignature, DrbFactory, DrbSignatureType
from .factory import OdataCscFactory
from .odata_utils import is_csc_odata_svc


class OdataCscSignature(DrbSignature):
    csc_factory = OdataCscFactory()

    @property
    def uuid(self) -> uuid.UUID:
        return uuid.UUID('a32c5d56-409e-11ec-973a-0242ac130003')

    @property
    def label(self) -> str:
        return 'OData Copernicus Space Component'

    @property
    def category(self) -> DrbSignatureType:
        return DrbSignatureType.CONTAINER

    @property
    def factory(self) -> DrbFactory:
        return self.csc_factory

    def match(self, node: DrbNode) -> bool:
        try:
            node.get_attribute('odata-version')
            return is_csc_odata_svc(node.path.name)
        except DrbException:
            return False
