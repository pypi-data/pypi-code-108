class KeyVaultSecret:
    def __init__(self, key: str, value: str, overwrite: bool = True):
        self.overwrite = overwrite
        self.value = value
        self.key = key # This name is inconsistent with the graph response "name"
