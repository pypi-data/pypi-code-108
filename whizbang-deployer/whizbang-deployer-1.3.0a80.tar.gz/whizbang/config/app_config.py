
class AppConfig:
    # def __init__(self, app_config: dict):
    def __init__(self, solution_rel_path):
        self._solutions_rel_path = solution_rel_path

    @property
    def solutions_rel_path(self) -> str: return self._solutions_rel_path
