#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Subpackage to define options in Pyxel."""
import typing as t
from pathlib import Path

import attr


@attr.s(
    auto_attribs=True,
    on_setattr=attr.setters.pipe(attr.setters.convert, attr.setters.validate),
)
class GlobalOptions:
    """Define a container class for all available options."""

    cache_enabled: bool = attr.ib(
        validator=attr.validators.instance_of(bool),
        default=False,
    )
    cache_folder: t.Optional[t.Union[str, Path]] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of((str, Path))),
        default=None,
    )

    def update(self, dct: t.Mapping) -> t.Mapping:
        """Apply the option(s) in this container class.

        Parameters
        ----------
        dct : Mapping
            Validated option(s) to apply.

        Returns
        -------
        Mapping
            Previous option(s).

        Examples
        --------
        >>> options = GlobalOptions()
        >>> options
        GlobalOptions(cache_enabled=False, cache_folder=None)

        >>> options.update({"cache_enabled: True"})
        {'cache_enabled': False}
        >>> options
        GlobalOptions(cache_enabled=True, cache_folder=None)
        """
        previous_params = {}
        for key, value in dct.items():
            previous_params[key] = getattr(self, key)

            setattr(self, key, value)

        return previous_params

    def validate_and_convert(self, dct: t.Mapping) -> t.Mapping:
        """Validate and convert the input 'option(s)'.

        Parameters
        ----------
        dct : Mapping
            The input option(s) to validate and to convert.

        Returns
        -------
        Mapping
            The validated and converted option(s)

        Examples
        --------
        >>> options = GlobalOptions()
        >>> options
        GlobalOptions(cache_enabled=False, cache_folder=None)

        >>> options.validate_and_convert({"cache_enabled": True})
        {'cache_enabled': True}
        >>> options.validate_and_convert({"cache_enabled": "hello"})
        TypeError(...)
        """
        valid_keys = list(attr.asdict(self, recurse=False))

        result = {}
        for key, value in dct.items():
            if key not in valid_keys:
                raise KeyError(f"Wrong option {key!r}.")

            # TODO: Check and convert types
            result[key] = value

        return result


# Create a singleton
global_options = GlobalOptions()


class SetOptions:
    """Set options for Pyxel in a controlled context.

    Currently supported options:

    * ``cache_enabled``: Enable/disable caching when reading table and data.
      Default value: False
    * ``cache_folder``: Set a folder for caching files.
      Default value: None

    Examples
    --------
    Set global options
    >>> pyxel.set_options(cache_folder="/tmp")

    Or with a context manager
    >>> with pyxel.set_options(cache_enabled=True, cache_folder="/tmp"):
    ...     print("Do something")
    ...
    """

    def __init__(self, **kwargs):
        valid_parameters = global_options.validate_and_convert(
            kwargs
        )  # type: t.Mapping

        self._previous_params = global_options.update(
            valid_parameters
        )  # type: t.Mapping

    def __enter__(self) -> "SetOptions":
        return self

    def __exit__(self, exc_type: t.Any, exc_value: t.Any, traceback: t.Any) -> None:
        _ = global_options.update(self._previous_params)
