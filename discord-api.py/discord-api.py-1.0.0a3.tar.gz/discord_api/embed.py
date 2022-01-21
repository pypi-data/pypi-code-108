class Embed:
    """This can create a embed
    
    Parameters
    ----------
    title : Optional[str]
        title of embed
    description : Optional[str]
        description of embed
        
    Attributes
    ----------
    title : Optional[str]
        title of embed
    description : Optional[str]
        description of embed
    """
    def __init__(self, title:str = None, description:str = None):
        self.title = title
        self.description = description
        self.fields = []

    def add_field(self, name:str, value:str):
        """This can add field to embed
        
        Parameters
        ----------
        name : str
            This is name for embed field.
        value : str
            This is value for embed field.
        """
        self.fields.appends({"name": name, "value": "value"})

    def to_dict(self) -> dict:
        payload = {}
        if self.title is not None:
            payload["title"] = self.title
        if self.description is not None:
            payload["description"] = self.description
        if len(self.fields) != 0:
            payload["fields"] = [i for i in self.fields]
        return payload
