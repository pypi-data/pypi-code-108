class TargetGroupRepository:
    def __init__(self):
        self.target_groups = []

    def set_target_groups(self, target_groups):
        self.target_groups = target_groups

    def get_target_group(self, id):
        return next((g for g in self.target_groups if g.id == id), None)
