from heaobject import root


class DataModel(root.AbstractDesktopObject):
    def __init__(self):
        super().__init__()


class RelationalDataModel(DataModel):
    def __init__(self):
        super().__init__()
        self.entities = []


class FlatDataModel(DataModel):
    def __init__(self):
        super().__init__()
        self.row = None
        self.columns = []


class DelimitedDataModel(FlatDataModel):
    def __init__(self):
        super().__init__()


class FixedWidthDataModel(FlatDataModel):
    def __init__(self):
        super().__init__()


class Row(root.AbstractMemberObject):
    def __init__(self):
        super().__init__()


class Column(root.AbstractMemberObject):
    def __init__(self):
        super().__init__()
        self.data_element_uri = None


class DynamicWidthColumn(Column):
    def __init__(self):
        super().__init__()
        self.start = 0
        self.max_width = 0


class FixedWidthColumn(Column):
    def __init__(self):
        super().__init__()
        self.start = 0
        self.width = 0


class Entity(root.AbstractMemberObject):
    def __init__(self):
        super().__init__()
        self.attributes = []
        self.associations = []


class Attribute(root.AbstractMemberObject):
    def __init__(self):
        super().__init__()
        self.data_element_uri = None


class Association(root.AbstractMemberObject):
    def __init__(self):
        super().__init__()
        self.lhs = None  # An entity
        self.rhs = None  # Another entity


