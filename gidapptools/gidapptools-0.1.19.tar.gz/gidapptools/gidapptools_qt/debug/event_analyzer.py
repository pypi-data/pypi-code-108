"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import json
import shutil
import inspect
from typing import Any, Union, Callable, Iterable, Optional
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# * Third Party Imports --------------------------------------------------------------------------------->
import pp

# * Qt Imports --------------------------------------------------------------------------------------->
from PySide6.QtGui import QMouseEvent, QPaintEvent, QResizeEvent, QStatusTipEvent, QPlatformSurfaceEvent, QInputMethodQueryEvent
from PySide6.QtCore import QEvent, QChildEvent, QDynamicPropertyChangeEvent

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class JsonOutputter:

    def __init__(self, target_folder: Path, file_stem_suffix: str = None) -> None:
        self.target_folder = target_folder
        self.specific_folder = self.target_folder.joinpath("event_specific_data")
        self.target_folder.mkdir(exist_ok=True, parents=True)
        if self.specific_folder.exists() is True:
            shutil.rmtree(self.specific_folder)
        self.specific_folder.mkdir(exist_ok=True, parents=True)
        self.file_stem_suffix = file_stem_suffix

    def __call__(self, data: dict):
        def _clean_event_name(_event: QEvent) -> str:
            parts = str(_event.type()).split('.')
            while parts[0].casefold() != "qevent":
                _ = parts.pop(0)
            name = '_'.join(parts)
            return name

        event = data.get("event")
        specific = {"event": data.get("event"), "specific": data.pop("specific")}
        file_name = _clean_event_name(event)
        print(file_name)
        if self.file_stem_suffix is not None:
            file_name += f"_{self.file_stem_suffix}"
        file_name += '.json'
        path = self.target_folder.joinpath(file_name)
        if path.is_file() is False:

            with path.open("w", encoding='utf-8', errors='ignore') as f:
                json.dump(data, f, default=str, sort_keys=False, indent=4)

        if specific["specific"]:
            specific_file_name = f"{path.stem}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')}.json"
            specific_path = self.specific_folder.joinpath(specific_file_name)
            with specific_path.open("w", encoding='utf-8', errors='ignore') as f:
                json.dump(specific, f, default=str, sort_keys=False, indent=4)


def _data_getter_class_name(obj: object) -> str:
    try:
        if inspect.isclass(obj):
            return obj.__name__
    except Exception as e:
        print(e)

    try:
        return obj.__class__.__name__
    except Exception as e:
        print(e)

    return "Not able to determine class Name".upper()


def _data_getter_all_subclasses(obj: object) -> tuple[type]:

    if inspect.isclass(obj):
        klass = obj
    else:
        klass = obj.__class__
    all_subclasses = []

    for subclass in klass.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(_data_getter_all_subclasses(subclass))

    return tuple(all_subclasses)


def _data_getter_all_subclasses_names(obj: object) -> tuple[str]:
    return tuple(i.__name__ for i in _data_getter_all_subclasses(obj))


def _data_getter_all_member_names(obj: object) -> tuple[str]:
    return tuple(name for name, obj in inspect.getmembers(obj))


def _data_getter_all_non_param_methods(obj: object) -> tuple[str]:
    meths = []
    for name, obj in inspect.getmembers(obj):
        try:
            if len(inspect.getfullargspec(obj)[0]) <= 1:
                meths.append(name)
        except TypeError:
            continue
    return tuple(meths)


DEFAULT_SPEC_DATA_TO_GET = {QChildEvent: ["polished"],
                            QDynamicPropertyChangeEvent: ["propertyName"],
                            QResizeEvent: ["size", "oldSize"],
                            QStatusTipEvent: ["tip"],
                            QInputMethodQueryEvent: ["queries"],
                            QPlatformSurfaceEvent: ["surfaceEventTypes"],
                            QPaintEvent: ["region", "rect"],
                            QMouseEvent: ["source", "flags"]}

DEFAULT_SPEC_DATA_TO_GET = {k.__name__: v for k, v in DEFAULT_SPEC_DATA_TO_GET.items()}


class EventAnalyzer:
    std_data_to_get: tuple[str] = ("type", "_data_getter_class_name", "_data_getter_all_non_param_methods", "_data_getter_all_subclasses_names", "_data_getter_all_member_names", "spontaneous", "isSinglePointEvent", "isPointerEvent", "isInputEvent")
    specific_data_to_get: dict[str, list] = defaultdict(list, DEFAULT_SPEC_DATA_TO_GET)
    data_getters: dict[str, Callable] = {f.__name__: f for f in [_data_getter_all_member_names, _data_getter_all_subclasses, _data_getter_class_name, _data_getter_all_subclasses_names, _data_getter_all_non_param_methods]}

    def __init__(self, output: Callable = print, output_data: bool = False, only: Iterable[str] = None, exclude: Iterable[str] = None):
        self.output = output
        self.output_data = output_data
        self.only = set(only) if only is not None else only
        self.exclude = set(exclude) if exclude is not None else set()

    def _get_event_data(self, event: QEvent) -> dict[str, Any]:
        std_data = {}
        specific_data = {}
        for to_get in self.std_data_to_get:
            if to_get.startswith("_data_getter_"):
                std_data[to_get.removeprefix("_data_getter_")] = self.data_getters[to_get](event)
            else:
                value = getattr(event, to_get)
                if callable(value):
                    value = value()
                std_data[to_get] = value
        std_data = {k: v for k, v in sorted(std_data.items(), key=lambda x: len(x[0]))}
        for spec_to_get in self.specific_data_to_get[event.__class__.__name__]:
            value = getattr(event, spec_to_get)
            if callable(value):
                value = value()
            specific_data[spec_to_get] = value
        specific_data = {k: v for k, v in sorted(specific_data.items(), key=lambda x: len(x[0]))}
        return {"event": event, "std": std_data, "specific": specific_data}

    def _render_to_string(self, data: dict[str, Any]):
        return pp.fmt(data)

    def analyze(self, event: QEvent) -> Optional[Union[str, dict]]:
        if self.only is not None and event.__class__.__name__ not in self.only:
            return
        if event.__class__.__name__ in self.exclude:

            return
        data = self._get_event_data(event)
        if self.output_data is True:
            return data
        return self._render_to_string(data)

    def __call__(self, event: QEvent) -> None:
        text_or_data = self.analyze(event)
        if text_or_data is not None:
            self.output(text_or_data)


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
