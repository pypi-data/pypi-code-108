from .clinvar_xml import ClinvarXMLSource
from .mitomap import MitomapFileSource
from .uniprot import UniprotFileSource
from .mtdb import MTDBFileSource

source_name_map = {
    "clinvar_xml": ClinvarXMLSource,
    "mitomap": MitomapFileSource,
    "uniprot": UniprotFileSource,
    "mtdb": MTDBFileSource,
}

__all__ = (
    "ClinvarXMLSource",
    "MitomapFileSource",
    "UniprotFileSource",
    "MTDBFileSource",
)
