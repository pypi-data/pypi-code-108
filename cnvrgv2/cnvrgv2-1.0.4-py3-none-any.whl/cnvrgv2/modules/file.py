from cnvrgv2.modules.base.dynamic_attributes import DynamicAttributes


class File(DynamicAttributes):

    available_attributes = {
        "sha1": str,
        "fullpath": str,
        "created_at": str,
        "updated_at": str,
        "path": str,
        "file_name": str,
        "file_size": str,
        "content_type": str,
        "object_path": str
    }

    def __init__(self, context=None, slug=None, attributes=None):
        self._attributes = attributes or {}
