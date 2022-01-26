from typing import List, Optional

from camel_model.camel_model import CamelModel

from xlsx_lib.domain.shared.NewImageData import NewImageData
from xlsx_lib.domain.shared.TextLine import TextLine


class DataBlock(CamelModel):
    text_lines: Optional[List[TextLine]]
    image: Optional[NewImageData]
    upper_text: Optional[bool]

