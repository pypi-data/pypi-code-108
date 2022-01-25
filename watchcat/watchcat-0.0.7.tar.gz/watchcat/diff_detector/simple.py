from difflib import Differ
from watchcat.diff_detector.base import DiffDetector
from watchcat.snapshot import Snapshot


class SimpleDiffDetector(DiffDetector):
    def has_update(self, a: Snapshot, b: Snapshot) -> bool:
        assert a.timestamp < b.timestamp
        return a.content != b.content

    def diff(self, a: Snapshot, b: Snapshot):
        differ = Differ()
        diffs = differ.compare(a.content.split("\n"), b.content.split("\n"))
        return "\n".join(filter(lambda e: e.startswith("-") or e.startswith("+"), diffs))
