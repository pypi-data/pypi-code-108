from typing import List


class OlistShipment:
    seller: str
    packages: List[str]

    def __init__(self, seller: str, packages: List[str]) -> None:
        self.seller = seller
        self.packages = packages
