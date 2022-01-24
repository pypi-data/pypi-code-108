import numpy as np
from ..utils import convert_index

class Reconstructor:
    """
    Abstract base class for reconstructors.

    A `Reconstructor` is a helper to reconstruct slices in arbitrary directions
    (not only usual "horizontal slices") in parallel-beam tomography.

    Current limitations:
       - Limitation to the three main axes
       - One instance of Reconstructor can only reconstruct successive slices

    Typical scenarios examples:
       - "I want to reconstruct several slices along 'z'", where `z` is the
         vertical axis. In this case, we reconstruct "horizontal slices" in planes
         perpendicular to the rotation axis.
       - "I want to reconstruct slices along 'y'". Here `y` is an axis perpendicular
         to `z`, i.e we reconstruct "vertical slices".

    A `Reconstructor` is tied to the set of slices to reconstruct (axis
    and orientation). Once defined, it cannot be changed ; i.e another class has
    to be instantiated to reconstruct slices in other axes/indices.

    The volume geometry conventions are defined below::


                              __________
                             /         /|
                            /         / |
             z             /         /  |
             ^            /_________/   |
             |           |          |   |
             |    y      |          |   /
             |   /       |          |  /
             |  /        |          | /
             | /         |__________|/
             |/
             ---------- > x


    The axis `z` parallel to the rotation axis.
    The usual parallel-beam tomography setting reconstructs slices along `z`,
    i.e in planes parallel to (x, y).
    """

    def __init__(self, shape, indices_range, axis="z", vol_type="sinograms", slices_roi=None):
        """
        Initialize a reconstructor.

        Parameters
        -----------
        shape: tuple
            Shape of the stack of sinograms or projections.
        indices_range: tuple
            Range of indices to reconstruct, in the form (start, end).
            As the standard Python behavior, the upper bound is not included.
            For example, to reconstruct 100 slices (numbered from 0 to 99),
            then you can provide (0, 100) or (0, None). Providing (0, 99) or (0, -1)
            will omit the last slice.
        axis: str
            Axis along which the slices are reconstructed. This axis is orthogonal
            to the slices planes. This parameter can be either "x", "y", or "z".
            Default is "z" (reconstruct slices perpendicular to the rotation axis).
        vol_type: str, optional
            Whether the parameter `shape` describes a volume of sinograms or
            projections. The two are the same except that axes 0 and 1
            are swapped. Can be "sinograms" (default) or "projections".
        slices_roi: tuple, optional
            Define a Region Of Interest to reconstruct a part of each slice.
            By default, the whole slice is reconstructed for each slice index.
            This parameter is in the form `(start_u, end_u, start_v, end_v)`,
            where `u` and `v` are horizontal and vertical axes on the reconstructed
            slice respectively, regardless of its orientation.
            If one of the values is set to None, it will be replaced by
            the corresponding default value.

        Examples
        ---------
        To reconstruct the first two horizontal slices, i.e along `z`:
          `R = Reconstructor(vol_shape, [0, 1])`
        To reconstruct vertical slices 0-100 along the `y` axis:
          `R = Reconstructor(vol_shape, (0, 100), axis="y")`
        """
        self._set_shape(shape, vol_type)
        self._set_axis(axis)
        self._set_indices(indices_range)
        self._configure_geometry(slices_roi)


    def _set_shape(self, shape, vol_type):
        if "sinogram" in vol_type.lower():
            self.vol_type = "sinograms"
        elif "projection" in vol_type.lower():
            self.vol_type = "projections"
        else:
            raise ValueError("vol_type can be either 'sinograms' or 'projections'")
        if len(shape) != 3:
            raise ValueError("Expected a 3D array description, but shape does not have 3 dims")
        self.shape = shape
        if self.vol_type == "sinograms":
            n_z, n_a, n_x = shape
        else:
            n_a, n_z, n_x = shape
        self.sinos_shape = (n_z, n_a, n_x)
        self.projs_shape = (n_a, n_z, n_x)
        self.data_shape = self.sinos_shape if self.vol_type == "sinograms" else self.projs_shape
        self.n_a = n_a
        self.n_x = n_x
        self.n_y = n_x # square slice by default
        self.n_z = n_z
        self._n = {"x": self.n_x, "y": self.n_y, "z": self.n_z}


    def _set_axis(self, axis):
        if axis.lower() not in ["x", "y", "z"]:
            raise ValueError("axis can be either 'x', 'y' or 'z' (got %s)" % axis)
        self.axis = axis


    def _set_indices(self, indices_range):
        start, end = indices_range
        npix = self._n[self.axis]
        start = convert_index(start, npix, 0)
        end = convert_index(end, npix, npix)
        self.indices_range = (start, end)
        self._idx_start = start
        self._idx_end = end
        self.indices = np.arange(start, end)


    def _configure_geometry(self, slices_roi):
        self.slices_roi = slices_roi or (None, None, None, None)
        start_u, end_u, start_v, end_v = self.slices_roi
        uv_to_xyz = {
            "z": ("x", "y"), # reconstruct along z: u = x, v = y
            "y": ("y", "z"), # reconstruct along y: u = y, v = z
            "x": ("y", "z"), # reconstruct along x: u = y, v = z
        }
        rotated_axes = uv_to_xyz[self.axis]
        u_max = self._n[rotated_axes[0]]
        v_max = self._n[rotated_axes[1]]
        start_u = convert_index(start_u, u_max, 0)
        end_u = convert_index(end_u, u_max, u_max)
        start_v = convert_index(start_v, v_max, 0)
        end_v = convert_index(end_v, v_max, v_max)
        self.slices_roi = (start_u, end_u, start_v, end_v)

        if self.axis == "z":
            self.backprojector_roi = self.slices_roi
            start_z, end_z = self._idx_start, self._idx_end
        if self.axis == "y":
            self.backprojector_roi = (start_u, end_u, self._idx_start, self._idx_end)
            start_z, end_z = start_v, end_v
        if self.axis == "x":
            self.backprojector_roi = (self._idx_start, self._idx_end, start_u, end_u)
            start_z, end_z = start_v, end_v
        self._z_indices = np.arange(start_z, end_z)
        self.output_shape = (
            self._z_indices.size,
            self.backprojector_roi[3] - self.backprojector_roi[2],
            self.backprojector_roi[1] - self.backprojector_roi[0],
        )


    def _check_data(self, data):
        if data.shape != self.data_shape:
            raise ValueError(
                "Invalid data shape: expected %s shape %s, but got %s"
                % (self.vol_type, self.data_shape, data.shape)
            )
            if data.dtype != np.float32:
                raise ValueError("Expected float32 data type")


    def reconstruct(self):
        raise ValueError("Base class")


    __call__ = reconstruct
