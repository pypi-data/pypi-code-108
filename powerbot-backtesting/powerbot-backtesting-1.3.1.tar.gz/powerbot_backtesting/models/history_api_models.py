from dataclasses import dataclass

@dataclass
class HistoryApiClient:
	exchange: str = "epex"
	delivery_area: str = "10YDE-RWENET---I"