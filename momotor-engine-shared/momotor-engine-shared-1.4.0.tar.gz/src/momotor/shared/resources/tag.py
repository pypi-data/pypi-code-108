from .item import ResourceItem


class Tag(ResourceItem):
    def __init__(self, value: str):
        if value.startswith('?'):
            value = value[1:]
            required, excluded = False, False
        elif value.startswith('~'):
            value = value[1:]
            required, excluded = False, True
        else:
            required, excluded = True, False

        super().__init__(value, required, excluded)

    def comparable(self, worker: ResourceItem) -> bool:
        return super().comparable(worker) and self.value == worker.value
