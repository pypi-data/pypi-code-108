class CustomProperty(object):
    def __init__(self, name, type, value):
        self.name = name
        self.type = type
        self.value = value if callable(value) else lambda context: value
