from typing import Optional, List

from camel_model.camel_model import CamelModel

from xlsx_lib.domain.shared.NewImageData import NewImageData
from xlsx_lib.domain.shared.TextLine import TextLine


class Fault(CamelModel):
    fault_kind: List[TextLine] = []
    flash_pattern_image: Optional[NewImageData]
    flashs_number_by_time: Optional[str]
    parts_to_review: Optional[List[TextLine]]
