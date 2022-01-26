from typing import Callable, Any, Dict

from jinja2 import Environment, BaseLoader, Template


class UniUtilTemplate:

    def __init__(self) -> None:
        self._jinja2_env = Environment(loader=BaseLoader())
        self._templates_index: Dict[int, Template] = dict()

    def set_filter(self, name: str, filter_fn: Callable[..., str]) -> None:
        self._jinja2_env.filters[name] = filter_fn

    def template(self, definition: str, **kwargs: Any) -> str:
        if not isinstance(definition, str):
            raise TypeError(f"definition must be str. {type(definition)} given")
        i = hash(definition)
        if i not in self._templates_index:
            self._templates_index[i] = self._jinja2_env.from_string(definition)
        return self._templates_index[i] .render(**kwargs)
