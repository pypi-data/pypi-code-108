from .capabilities import _HasExercisesMixin, _HasVideosMixin
from . import _ResourceGroup


class AppDeveloperResourceGroup(_ResourceGroup, _HasExercisesMixin, _HasVideosMixin):
    def _use_attributes(self, attributes: dict):
        super()._use_attributes(attributes)


