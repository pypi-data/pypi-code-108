from cnvrgv2.modules.base.dynamic_attributes import DynamicAttributes


class Folder(DynamicAttributes):

    available_attributes = {
        "name": str,
        "fullpath": str,
        "created_at": str,
        "updated_at": str,
        "object_path": str
    }

    def __init__(self, context=None, slug=None, attributes=None):
        self._attributes = attributes or {}
