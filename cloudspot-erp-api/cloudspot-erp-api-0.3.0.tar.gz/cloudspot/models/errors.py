from .base import BaseModel

class Error(BaseModel):

    def __init__(self,
        message=None
    ):

        self.message = message