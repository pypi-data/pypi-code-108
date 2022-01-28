"""Top-level objects which specific detectors should inherit from."""

from abc import ABC

import numpy as np

from ..element import ModelElement
from ..components import Node
from ..exceptions import ContextualTypeError
from ..utilities.homs import make_modes, insert_modes, remove_modes


class Detector(ABC, ModelElement):
    """Abstract representation of a component that produces a numerical output.

    User detector classes should subclass this class. The simulation will then generate a dictionary
    of output values.

    Parameters
    ----------
    name : str
        Name of newly created detector.

    node : :class:`.Node` or :class:`.Port`
        Node to read output from. If a port is given, it must have one node, so that
        is is unambiguous which node to use.

    dtype : type, optional
        The numpy datatype for which this output result will be stored in.

    unit : str, optional
        A human readable unit for the output. E.g. W, m, m/rtHz.
    """

    def __init__(
        self,
        name,
        node=None,
        dtype=np.complex128,
        shape=(),
        unit="arb.",
        label=None,
        needs_fields=True,
        needs_trace=False,
    ):
        from finesse.detectors.workspace import OutputInformation

        ModelElement.__init__(self, name)

        if not isinstance(node, (Node, type(None))):
            try:  # try and grab a node
                node = node.nodes[0]
            except Exception:
                raise ContextualTypeError("node", node, allowed_types=(Node,))

        if node:
            node.used_in_detector_output.append(self)

        self.__output_information = OutputInformation(
            name,
            type(self),
            (node,),
            dtype,
            unit,
            shape,
            label,
            needs_fields,
            needs_trace,
        )

    def _on_add(self, model):
        for node in self.__output_information.nodes:
            if node is not None and model is not node._model:
                raise Exception(
                    f"{repr(self)} is using a node {node} from a different model"
                )

    def _on_remove(self):
        self.node.used_in_detector_output.remove(self)

    @property
    def output_information(self):
        return self.__output_information

    @property
    def needs_fields(self):
        """Flag indicating whether the detector requires light fields (i.e. solving of
        the interferometer matrix)."""
        return self.__output_information.needs_fields

    @property
    def needs_trace(self):
        """Flag indicating whether the detector requires beam traces."""
        return self.__output_information.needs_trace

    @property
    def node(self):
        """The nodes this detector observes.

        :getter: Returns the detected node.
        """
        return self.__output_information.nodes[0]

    @property
    def dtype(self):
        return self.__output_information.dtype

    @property
    def dtype_shape(self):
        return self.__output_information.dtype_shape

    def _update_dtype_shape(self, shape):
        """Only to be used internally by detectors like Cameras for updating the shape
        if resolution is changed."""
        self.__output_information._update_dtype_shape(shape)

    @property
    def dtype_size(self):
        """Size of the output in terms of number of elements.

        This is typically unity as most detectors return a single
        value via their output functions.

        Equivalent to the product of :attr:`.Detector.dtype_shape`.
        """
        return int(np.prod(self.__output_information.dtype_shape))

    @property
    def unit(self):
        return self.__output_information.unit

    @property
    def label(self):
        return self.__output_information.label


class MaskedDetector(Detector, ABC):
    """An abstract class from which detector types which can have mode masks derive.

    Any detector object which calculates quantities involving loops over the modes of a
    model should inherit from this --- allowing masks to be applied to mode patterns via
    the methods of this class. Examples of detectors which should derive from
    `MaskedDetector` are power-detectors, amplitude-detectors and cameras.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # The mode indices which will be masked
        # on this detector in simulations
        self._mask = np.zeros(0, dtype=(np.intc, 2))

    @property
    def has_mask(self):
        """Whether the detector has a mask applied to it.

        Simply checks to see if the :attr:`.MaskedDetector.mask` length is non-zero.
        """
        return len(self.mask)

    @property
    def mask(self):
        """An array of HOMs to mask from the output. Any contributions from these modes
        will be zeroed when calculating the detector output.

        :getter: Returns the array of masked indices.
        :setter: Sets the masked indices. See :meth:`.MaskedDetector.select_mask` for
                 the options available.
        """
        return self._mask

    @mask.setter
    def mask(self, value):
        self.select_mask(value)

    def select_mask(self, modes=None, maxtem=None, exclude=None):
        """Select the HOM indices to include in the mask.

        The mode-selecting examples in :ref:`selecting_modes` may be referred
        to for typical patterns when using this method, as the same concepts
        apply equally to making detector masks (equivalent code under-the-hood).

        Parameters
        ----------
        modes : sequence, str, optional; default: None
            Identifier for the mode indices to generate. This can be:

            - An iterable of mode indices, where each element in the iterable must unpack to two
              integer convertible values.

            - A string identifying the type of modes to include, must be one of "even", "odd",
              "tangential" (or "x") or "sagittal" (or "y").

            By default this is None, such that, for example, this method can be used to select a
            mask of all modes up to a given `maxtem`.

        maxtem : int, optional; default: None
            Optional maximum mode order. If not specified then the maxtem used internally will be
            equal to the maximum mode order of the associated model.

            Note that this argument is ignored if `modes` is an iterable of mode indices.

        exclude : sequence, str, optional; default: None
            A mode, or iterable of modes, to exclude from the selected pattern. For example, if
            one calls ``select_mask("even", exclude="00")`` then the mask will be an array of
            all even-order HOM indices excluding the 00 mode.

        Examples
        --------
        See :ref:`selecting_modes`.
        """
        if maxtem is None:
            if self.has_model:
                maxtem = self._model.modes_setting["maxtem"]

        self._mask = make_modes(modes, maxtem)

        if exclude is not None:
            self.remove_from_mask(exclude)

    def add_to_mask(self, modes):
        """Inserts the specified mode indices into the detector mask.

        Parameters
        ----------
        modes : sequence, str
            A single mode index pair or an iterable of mode indices. Each
            element must unpack to two integer convertible values.
        """
        self._mask = insert_modes(self._mask, modes)

    def remove_from_mask(self, modes):
        """Removes the specified mode indices from the detector mask.

        Parameters
        ----------
        modes : sequence, str
            A single mode index pair or an iterable of mode indices. Each
            element must unpack to two integer convertible values.
        """
        self._mask = remove_modes(self._mask, modes)


class SymbolDetector(Detector):
    def __init__(self, name, symbol, dtype=np.complex128):
        Detector.__init__(self, name, None, dtype=dtype)
        self.symbol = symbol

    def get_output(self, *args):
        return self.dtype(self.symbol.eval())


class NoiseDetector:
    def __init__(self, noise_type):
        self.__noise_type = noise_type
        self._requested_selection_vectors = dict()
        self.__selection_vectors = {}

    @property
    def noise_type(self):
        return self.__noise_type

    def _request_selection_vector(self, name):
        self._requested_selection_vectors[name] = -1
