from msgraphy.data import graphdataclass


@graphdataclass
class Identity:
    display_name: str = None
    id: str = None
    thumbnails: dict = None


@graphdataclass
class IdentitySet:
    application: Identity = None
    device: Identity = None
    user: Identity = None