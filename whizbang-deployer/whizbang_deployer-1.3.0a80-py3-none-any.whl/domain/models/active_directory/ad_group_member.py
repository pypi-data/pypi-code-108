class AdGroupMember:
    def __init__(self, object_id: str, object_type: str, display_name: str = None):
        self.object_id = object_id
        self.display_name = display_name
        self.object_type = object_type
