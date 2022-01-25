class DatabricksLibrary:
    def __init__(self, library_dict: dict, install_all: bool = False):
        self.install_all: bool = install_all
        self.library_dict = library_dict
