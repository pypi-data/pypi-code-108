from enum import Enum
from dataclasses 	import dataclass

class HubChannelType(Enum):
    IN = "IN"
    OUT = "OUT"

class HubChannelStatusIntegration(Enum):
    SENT_CHANNEL_OUT      = "SENT_TO_CHANNEL_OUT"
    CHANNEL_OUT_APPROVED  = "CHANNEL_OUT_APPROVED"
    CHANNEL_OUT_ERROR     = "CHANNEL_OUT_ERROR"

@dataclass
class HubChannelStatus:
	external_id : str
	status	    : HubChannelStatusIntegration
	message     : str

@dataclass
class HubSellerChannelSyncProduct:
	date : str
	quantity_created : int
	quantity_updated : int
	quantity_discarted : int
	quantity_failed : int


@dataclass
class HubSellerChannelSyncPriceAndStock:
	date : str
	quantity_updated : int
	quantity_discarted : int
	quantity_failed : int
