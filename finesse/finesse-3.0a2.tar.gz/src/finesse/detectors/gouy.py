"""Accumulated Gouy phase detector."""

import logging

import numpy as np

from .general import Detector
from .compute.gaussian import GouyDetectorWorkspace
from ..env import warn

LOGGER = logging.getLogger(__name__)


class Gouy(Detector):
    """Detector to measure the accumulated gouy phase across a sequence of spaces.

    This detector can operate in one of two modes, depending upon args given:

      * automatically determine the spaces through an arbitrary path by specifying the
        `from_node` and `to_node` arguments,
      * OR provide a pre-determined sequence of spaces (or their names) as positional
        arguments.

    Whichever option is chosen, this detector will compute the same fundamental quantity;
    that is the sum of the Gouy phases accumulated over each space (in degrees).

    Parameters
    ----------
    name : str
        Name of newly created gouy detector.

    *args : sequence
        A sequence of spaces or space names.

    from_node : node-like
        An :class:`.OpticalNode` instance, or a data type which can be converted
        to an optical node.

    to_node : node-like
        An :class:`.OpticalNode` instance, or a data type which can be converted
        to an optical node.

    via_node : node-like
        An :class:`.OpticalNode` instance, or a data type which can be converted
        to an optical node.

    direction : str
        Plane to detect in - 'x' for tangential, 'y' for sagittal. Defaults to 'x'.
    """

    def __init__(
        self, name, *args, from_node=None, to_node=None, via_node=None, direction="x"
    ):
        Detector.__init__(
            self, name, dtype=np.float64, unit="degrees", label="Gouy phase"
        )

        nodes = from_node, to_node, via_node
        if args and any(node is not None for node in nodes):
            raise ValueError(
                f"Error in Gouy detector {self.name}:\n"
                "    Cannot specify both a sequence of spaces and a node path."
            )

        if not args and all(node is None for node in nodes):
            raise ValueError(
                f"Error in Gouy detector {self.name}:\n"
                "    Must specify EITHER a sequence of spaces or a node path."
            )

        self.direction = direction
        self.__spaces = list(args)
        self.__from_node = from_node
        self.__to_node = to_node
        self.__via_node = via_node

    @property
    def needs_fields(self):
        return False

    @property
    def needs_trace(self):
        return True

    @property
    def spaces(self):
        """The spaces that this detector will calculated the accumulated Gouy phase
        over."""
        return self.__spaces.copy()

    def _lookup_spaces(self):
        from finesse.components import Space

        if not self.has_model:
            raise RuntimeError(f"Bug detected! No model associated with {self.name}")

        for i, item in enumerate(
            self.__spaces
        ):  # sequence of spaces / space names given
            if isinstance(item, Space):
                continue

            if not isinstance(item, str):
                raise TypeError(
                    f"Error in Gouy detector {self.name}:\n"
                    "    Unexpected type in iterable of spaces. Expected a "
                    f"Space or str, but got type: {type(item)}"
                )

            space = self._model.elements.get(item, None)
            if space is None:
                raise LookupError(
                    f"Error in Gouy detector {self.name}:\n"
                    f"    No space of name {item} in model."
                )
            if not isinstance(space, Space):
                raise TypeError(
                    f"Error in Gouy detector {self.name}:\n"
                    f"    Element of name {item} is not a Space."
                )

            self.__spaces[i] = space

        # node path source, target given
        if self.__from_node is not None and self.__to_node is not None:
            path = self._model.path(self.__from_node, self.__to_node, self.__via_node)
            self.__spaces = list(path.spaces)

        if self.__spaces:
            LOGGER.info(
                "Gouy detector %s using spaces: %s",
                self.name,
                self.__spaces,
            )
        else:
            warn(
                f"Gouy detector {repr(self.name)} not using any spaces! This will "
                f"always return values of zero in a simulation."
            )

    def _get_workspace(self, sim):
        ws = GouyDetectorWorkspace(self, sim)
        return ws
