from pydantic.typing import List, Optional

from net_models.models.BaseModels import VendorIndependentBaseModel

class SegmentRoutingConfig(VendorIndependentBaseModel):

    sr_id: Optional[str]
    extra_config: Optional[List[str]]
