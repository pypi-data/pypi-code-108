from watchcat.snapshot import Snapshot


class DiffDetector:
    def has_update(self, a: Snapshot, b: Snapshot) -> bool:
        raise NotImplementedError()

    def diff(self, a: Snapshot, b: Snapshot):
        raise NotImplementedError()
