from io import BytesIO

from camel_model.camel_model import CamelModel


class NewImageFile(CamelModel):
    filename: str
    file: BytesIO
