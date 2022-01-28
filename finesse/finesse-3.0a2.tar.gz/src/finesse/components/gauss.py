"""User-defined Gaussian beam tracing dependencies at a node."""

from itertools import chain

from ..config import config_instance
from ..parameter import float_parameter
from ..gaussian import BeamParam
from .trace_dependency import TraceDependency


@float_parameter("w0x", "Waist size (x)", units="m", validate="_validate_w0x")
@float_parameter("w0y", "Waist size (y)", units="m", validate="_validate_w0y")
@float_parameter("zx", "Distance to waist (x)", units="m", validate="_validate_zx")
@float_parameter("zy", "Distance to waist (y)", units="m", validate="_validate_zy")
class Gauss(TraceDependency):
    """Beam parameter at a specific node of a model.

    The following are legal initialisations of a `Gauss`
    object::

        # Non-astigmatic
        q = Gauss('name', node, q=q)
        q = Gauss('name', node, w0=w0, z=z) # waist size and position
        q = Gauss('name', node, zr=zr, z=z) # Rayleigh range and waist position
        q = Gauss('name', node, w=w, Rc=Rc) # beam size and RoC
        q = Gauss('name', node, w=w, S=S) # beam size and curvature

        # Astigmatic
        q = Gauss('name', node, qx=qx, qy=qy)
        q = Gauss('name', node, w0x=wx, zx=zx, w0y=wy, zy=zy)
        q = Gauss('name', node, zrx=zrx, zx=zx, zry=zry, zy=zy)
        q = Gauss('name', node, wx=wx, Rcx=Rcx, wy=wy, Rcy=Rcy)
        q = Gauss('name', node, wx=wx, Sx=Sx, wy=wy, Sy=Sy)

    See :class:`.gaussian.BeamParam` for more detailed descriptions
    of these variables.
    """

    def __init__(self, name, node, priority=0, **kwargs):
        super().__init__(name, priority)

        self.__node = node
        wl, nr = self.__get_lambda0_nr()

        # Handle q differently so that inner type of a BeamTraceSolution
        # can be used directly via this argument
        if "q" in kwargs:
            if len(kwargs) > 1:
                raise ValueError("Cannot specify both q and another parameter")

            from ..solutions.beamtrace import BeamTraceSolution

            if isinstance(kwargs["q"], BeamTraceSolution.NodeData):
                qx, qy = kwargs["q"]
            else:
                qx = qy = BeamParam(wavelength=wl, nr=nr, q=kwargs["q"])
        else:
            astig_params = [
                ("qx", "qy"),
                ("zrx", "zry", "zx", "zy"),
                ("w0x", "w0y", "zx", "zy"),
                ("Rcx", "Rcy", "wx", "wy"),
                ("Sx", "Sy", "wx", "wy"),
            ]
            # Non-astigmatic beam parameters
            if not len(set(chain.from_iterable(astig_params)) & kwargs.keys()):
                try:
                    qx = qy = BeamParam(wavelength=wl, nr=nr, **kwargs)
                except ValueError as ex:
                    raise ValueError(
                        "Invalid arguments for non-astigmatic Gauss." + str(ex)
                    )
            # Astigmatic beam parameters
            else:
                astig_params = [tuple(sorted(comb)) for comb in astig_params]
                if tuple(sorted(kwargs)) not in astig_params:
                    raise ValueError(
                        "Invalid arguments for astigmatic Gauss. Expected one of:\n - "
                        + "\n - ".join([", ".join(comb) for comb in astig_params])
                    )

                # Separate the tangential and sagittal plane arguments
                xargs = {k.split("x")[0]: v for k, v in kwargs.items() if "x" in k}
                yargs = {k.split("y")[0]: v for k, v in kwargs.items() if "y" in k}

                qx = BeamParam(wavelength=wl, nr=nr, **xargs)
                qy = BeamParam(wavelength=wl, nr=nr, **yargs)

        self.__qx = qx
        self.__qy = qy

        self._specified_params = kwargs

        self.w0x = self.__qx.w0
        self.zx = self.__qx.z
        self.w0y = self.__qy.w0
        self.zy = self.__qy.z

    # def _on_add(self, model):
    #     if model is not self.node._model:
    #         raise Exception(
    #             f"{repr(self)} is using a node {self.node} from a different model"
    #         )

    def __get_lambda0_nr(self):
        if self.__node.component.has_model:
            wl = self.__node._model.lambda0

            space = self.__node.space
            if space is not None:
                nr = space.nr.value
            else:
                nr = 1.0
        else:
            wl = config_instance()["constants"].getfloat("lambda0")
            nr = 1.0

        return wl, nr

    @property
    def qx(self):
        """Tangential plane beam parameter.

        :getter: Returns the beam parameter in the tangential plane.
        :setter: Sets the beam parameter for the tangential plane.
        """
        return self.__qx

    @qx.setter
    def qx(self, value):
        if not isinstance(value, BeamParam):
            qx = BeamParam(*self.__get_lambda0_nr(), q=value)
        else:
            qx = value

        self.__qx = qx
        self.w0x = self.__qx.w0
        self.zx = self.__qx.z

    @property
    def qy(self):
        """Sagittal plane beam parameter.

        :getter: Returns the beam parameter in the sagittal plane.
        :setter: Sets the beam parameter for the sagittal plane.
        """
        return self.__qy

    @qy.setter
    def qy(self, value):
        if not isinstance(value, BeamParam):
            qy = BeamParam(*self.__get_lambda0_nr(), q=value)
        else:
            qy = value

        self.__qy = qy
        self.w0y = self.__qy.w0
        self.zy = self.__qy.z

    @property
    def node(self):
        """The optical node associated with the `Gauss` object.

        :getter: Returns the associated :class:`.OpticalNode` instance (read-only).
        """
        return self.__node

    @property
    def is_changing(self):
        """Whether the Gauss object is changing or not.

        This is used internally when initialising simulation states.
        """
        params = (self.w0x, self.w0y, self.zx, self.zy)
        return any(p.is_changing for p in params)

    def _validate_w0x(self, value):
        if not value > 0:
            raise ValueError("Waist size must be a positive number.")

        self.__qx.w0 = value
        return value

    def _validate_w0y(self, value):
        if not value > 0:
            raise ValueError("Waist size must be a positive number.")

        self.__qy.w0 = value
        return value

    def _validate_zx(self, value):
        self.__qx.z = value
        return value

    def _validate_zy(self, value):
        self.__qy.z = value
        return value
