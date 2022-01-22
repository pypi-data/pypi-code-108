from heaobject import root


class DataElement(root.AbstractDesktopObject):

    def __init__(self):
        super().__init__()
        self.value_domain = None
        self.concept_uri = None
        self.context_uri = None
        self.workflow_status = None
