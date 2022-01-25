from __future__ import annotations

import builtins as bltn
import dataclasses as dcls
import datetime as dttm
import json
import pickle as pckl
from pathlib import Path as path_t
from typing import Any, Dict, Optional, Sequence, Union
from collections.abc import Collection, Mapping

import matplotlib.pyplot as pypl
import numpy as nmpy
import tensorflow.keras as kras
from mpl_toolkits.mplot3d import Axes3D as axes_3d_t


array_t = nmpy.ndarray


BUILTIN_TYPES = tuple(
    _typ for _elm in dir(bltn) if isinstance((_typ := getattr(bltn, _elm)), type)
)

# The following lists are meant to be safe enough, not to serve as references
PATH_ILLEGAL_CHARACTERS_LIN = r"/"
PATH_ILLEGAL_CHARACTERS_OSX = r":"
PATH_ILLEGAL_CHARACTERS_WIN = r'|/\<>:?*"'

REPLACEMENT_CHARACTER = "_"
VERSION_SEPARATOR = "-"

PATH_ILLEGAL_CHARACTERS = "".join(
    set(
        PATH_ILLEGAL_CHARACTERS_LIN
        + PATH_ILLEGAL_CHARACTERS_OSX
        + PATH_ILLEGAL_CHARACTERS_WIN
    )
)
if (REPLACEMENT_CHARACTER in PATH_ILLEGAL_CHARACTERS) or (
    VERSION_SEPARATOR in PATH_ILLEGAL_CHARACTERS
):
    raise ValueError(
        f'The character "{REPLACEMENT_CHARACTER}" or "{VERSION_SEPARATOR}" is an illegal path character'
    )


@dcls.dataclass(repr=False, eq=False)
class archiver_t:

    folder: path_t = None

    @classmethod
    def NewForFolderAndSequence(
        cls, folder: Union[str, path_t], sequence: Union[str, path_t], /
    ) -> archiver_t:
        """
        folder: If a path_t, then it must not contain any illegal characters for the target system. Otherwise, any
        illegal character will be replaced with a legal one (a priori, "_").
        sequence: Whether a str or a path_t, only the name (with extension) will be retained, the extension ".", if any,
        will be replaced with "_", and any illegal character will be replaced with a legal one (see "folder").
        """
        if isinstance(folder, str):
            folder = path_t(_ReplacePathIllegalCharacters(folder))
        if isinstance(sequence, path_t):
            sequence = _ReplacePathIllegalCharacters(
                sequence.stem + REPLACEMENT_CHARACTER + sequence.suffix[1:]
            )
        else:
            sequence = _ReplacePathIllegalCharacters(sequence)
        for component in (sequence, None):
            if folder.exists():
                if not folder.is_dir():
                    raise ValueError(
                        f"{folder}: Not a folder; Cannot be used by {cls.__name__.upper()}"
                    )
            else:
                folder.mkdir()
            if component is not None:
                folder /= component

        original_name = _ReplacePathIllegalCharacters(_TimeStamp())
        folder /= original_name
        version = 0
        while folder.exists():
            version += 1
            folder = folder.parent / f"{original_name}{VERSION_SEPARATOR}{version}"
        folder.mkdir()

        instance = cls(folder=folder)

        return instance

    def Store(
        self, element: Any, name: str, /, *, with_time_stamp: bool = True
    ) -> None:
        """
        name: Any illegal character will be replaced with a legal one (see "folder" in NewForFolderAndSequence)
        """
        should_log = False
        should_csv = False
        if name.lower().endswith(".log"):
            should_log = isinstance(element, str)
            if not should_log:
                raise ValueError(
                    f"{type(element).__name__}: Invalid type for logging; Expected=str"
                )
        elif name.lower().endswith(".csv"):
            should_csv = isinstance(element, array_t) and (element.ndim == 2)
            if not should_csv:
                if isinstance(element, array_t):
                    raise ValueError(
                        f"{element.ndim}: Invalid number of dimensions for CSV output; Expected=2"
                    )
                else:
                    raise ValueError(
                        f"{type(element).__name__}: Invalid type for CSV output; Expected=numpy.ndarray"
                    )

        if with_time_stamp and not (should_log or should_csv):
            name += _TimeStamp()
        name = _ReplacePathIllegalCharacters(name)

        if should_log:
            with open(self.folder / name, "a") as writer:
                writer.write(_TimeStamp() + "\n")
                writer.write(element + "\n")
        elif should_csv:
            nmpy.savetxt(self.folder / name, element, delimiter=",", fmt="%f")
        elif _IsFullyBuiltin(element):
            with open(self.folder / f"{name}.json", "w") as writer:
                json.dump(element, writer, indent=4)
        elif isinstance(element, array_t):
            nmpy.savez_compressed(self.folder / f"{name}.npz", contents=element)
        elif isinstance(element, pypl.Figure):
            element.savefig(self.folder / f"{name}.png")
        elif isinstance(element, pypl.Axes) or isinstance(element, axes_3d_t):
            element.figure.savefig(self.folder / f"{name}.png")
        elif isinstance(element, kras.Model):
            element.save(self.folder / name)
        else:
            raise ValueError(
                f"{type(element).__name__}: Type of {element} unprocessable by {self.__class__.__name__.upper()}"
            )

    def StoreWithPickle(
        self,
        value: Union[Any, Sequence[Any], Dict[str, Any]],
        pickle_name: str,
        /,
        *,
        name: Union[str, Sequence[str]] = None,
        with_time_stamp: bool = True,
    ) -> None:
        """
        value: see PickleAndStoreObjects
        """
        if with_time_stamp:
            pickle_name += _TimeStamp()
        pickle_name = _ReplacePathIllegalCharacters(pickle_name)

        PickleAndStoreObjects(value, self.folder / pickle_name, name=name)


def PickleAndStoreObjects(
    value: Union[Any, Sequence[Any], Dict[str, Any]],
    where: Union[str, path_t],
    /,
    *,
    name: Union[str, Sequence[str]] = None,
) -> None:
    """
    value: Pass globals() to store all builtin-type objects
    """
    if isinstance(name, str):
        names = (name,)
        values = (value,)
    elif (name is None) and isinstance(value, dict):
        # value is normally globals()
        names = []
        values = []
        for _nme, _val in value.items():
            if isinstance(_nme, str) and _IsFullyBuiltin(_val):
                names.append(_nme)
                values.append(_val)
    elif (
        isinstance(name, Sequence)
        and ((n_names := name.__len__()) > 0)
        and all(isinstance(_elm, str) for _elm in name)
        and isinstance(value, Sequence)
        and (value.__len__() == n_names)
    ):
        names = name
        values = value
    else:
        raise ValueError(
            f"name type={type(name).__name__}/value type={type(value).__name__}: Invalid calling context. "
            f"Expected=str/Any or None/dict or Sequence[str]/Sequence[Any] w/ same length."
        )

    data = {_nme: _val for _nme, _val in zip(names, values)}
    with open(where, "wb") as accessor:
        pckl.dump(data, accessor)


def LoadPickledObjects(
    where: Union[str, path_t], /, *, context: Dict[str, Any] = None
) -> Optional[Dict[str, Any]]:
    """
    context: Use globals() typically
    """
    with open(where, "rb") as accessor:
        data = pckl.load(accessor)

    if context is None:
        return data

    for name, value in data.items():
        context[name] = value


def _TimeStamp() -> str:
    """"""
    return dttm.datetime.now().isoformat().replace(":", ".")


def _ReplacePathIllegalCharacters(
    string: str, /, *, replacement: str = REPLACEMENT_CHARACTER
) -> str:
    """"""
    translations = str.maketrans(
        PATH_ILLEGAL_CHARACTERS, PATH_ILLEGAL_CHARACTERS.__len__() * replacement
    )
    output = string.translate(translations)

    return output


def _IsFullyBuiltin(element: Any) -> bool:
    """"""
    if type(element) in BUILTIN_TYPES:
        if isinstance(element, Mapping):
            return all(
                _IsFullyBuiltin(_key) and _IsFullyBuiltin(_val)
                for _key, _val in element.items()
            )
        elif isinstance(element, Collection):
            return all(_IsFullyBuiltin(_elm) for _elm in element)

        return True

    return False
