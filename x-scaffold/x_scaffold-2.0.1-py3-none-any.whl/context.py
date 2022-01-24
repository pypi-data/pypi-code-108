from typing import Dict, List


class ScaffoldContext(dict):
    notes: List[str]
    todos: List[str]
    environ: Dict[str, str]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.notes = []
        self.todos = []
        self.environ = {}
