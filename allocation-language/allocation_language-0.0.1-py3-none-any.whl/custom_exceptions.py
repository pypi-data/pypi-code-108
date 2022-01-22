class FieldNotInDataError(Exception):
    """
    Exception raised for error when field is not in the dataset
    given to the objects here
    """
    def __init__(self, data: dict, field_name: str):
        self.data = data
        self.field_name = field_name
        super().__init__(f"{self.field_name} not in {self.data}")
