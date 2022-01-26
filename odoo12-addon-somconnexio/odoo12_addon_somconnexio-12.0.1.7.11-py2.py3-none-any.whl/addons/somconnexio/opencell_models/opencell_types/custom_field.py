from ..opencell_resource import OpenCellResource


class CustomField(OpenCellResource):
    def __init__(self, code, value):
        self.code = code
        self.value = value

    def to_dict(self):
        return {
            "code": self.code,
            "fieldType": "STRING",
            "stringValue": self.value,
        }
