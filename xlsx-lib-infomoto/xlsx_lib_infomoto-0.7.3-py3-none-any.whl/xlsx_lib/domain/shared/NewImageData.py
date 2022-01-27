from camel_model.camel_model import CamelModel


class NewImageData(CamelModel):
    filename: str
    width: int
    height: int
