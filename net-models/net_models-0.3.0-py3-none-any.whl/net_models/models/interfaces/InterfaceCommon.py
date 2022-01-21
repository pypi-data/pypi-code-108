
from pydantic.typing import Optional

from net_models.models import VendorIndependentBaseModel
from net_models.fields import GENERIC_OBJECT_NAME, JINJA_OR_NAME, Jinja2String

class InterfaceServicePolicy(VendorIndependentBaseModel):

    input: Optional[JINJA_OR_NAME]
    output: Optional[JINJA_OR_NAME]