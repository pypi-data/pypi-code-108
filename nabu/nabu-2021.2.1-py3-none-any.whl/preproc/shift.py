from math import floor
import numpy as np

class VerticalShift:
    def __init__(self, radios_shape, shifts):
        """
        This class is used when a vertical translation (along the tomography
        rotation axis) occurred.

        These translations are meant "per projection" and can be due either to
        mechanical errors, or can be applied purposefully with known motor movements
        to smear rings artefacts.

        The object is initialised with an array of shifts: one shift for each projection.
        A positive shifts means that the axis has moved in the positive Z direction.
        The interpolation is done taking for a pixel (y,x) the pixel found at (y+shft,x)
        in the recorded images.

        The method apply_vertical_shifts performs the correctionson the radios.

        Parameters
        ----------
        radios_shape: tuple
            Shape of the radios chunk, in the form (n_radios, n_y, n_x)
        shifts: sequence of floats
            one shift for each projection

        Notes
        ------
        During the acquisition, there might be other translations, each of them
        orthogonal to the rotation axis.
          - A "horizontal" translation in the detector plane: this is handled
            directly in the Backprojection operation.
          - A translation along the beam direction: this one is of no concern
            for parallel-beam geometry
        """
        self.radios_shape = radios_shape
        self.shifts = shifts
        self._init_interp_coefficients()

    def _init_interp_coefficients(self):
        self.interp_infos = []
        for s in self.shifts:
            s0 = int(floor(s))
            f = s - s0
            self.interp_infos.append([s0, f])


    def _check(self, radios, iangles):
        assert np.min(iangles) >= 0
        assert np.max(iangles) < len(self.interp_infos)
        assert len(iangles) == radios.shape[0]


    def apply_vertical_shifts(self, radios, iangles, output=None):
        """
        Parameters
        ----------
        radios: a sequence of np.array
            The input radios. If the optional parameter is not given, they are modified in-place
        iangles:  a sequence of integers
            Must have the same lenght as radios.
            It contains the index at which the shift is found in `self.shifts`
            given by `shifts` argument in the initialisation of the object.
        output: a sequence of np.array, optional
            If given, it will be modified to contain the shifted radios.
            Must be of the same shape of `radios`.
        """
        self._check(radios, iangles)

        newradio = np.zeros_like(radios[0])
        for radio, ia in zip(radios, iangles):
            newradio[:] = 0
            S0, f = self.interp_infos[ia]
            s0 = S0

            if s0 > 0:
                newradio[:-s0] = radio[s0:] * (1 - f)
            elif s0 == 0:
                newradio[:] = radio[s0:] * (1 - f)
            else:
                newradio[-s0:] = radio[:s0] * (1 - f)

            s0 = S0 + 1

            if s0 > 0:
                newradio[:-s0] += radio[s0:] * f
            elif s0 == 0:
                newradio[:] += radio[s0:] * f
            else:
                newradio[-s0:] += radio[:s0] * f

            if output is None:
                radios[ia] = newradio
            else:
                output[ia] = newradio
