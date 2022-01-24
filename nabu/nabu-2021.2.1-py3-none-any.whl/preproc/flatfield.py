from bisect import bisect_left
import numpy as np
from ..io.reader import load_images_from_dataurl_dict
from ..utils import check_supported, deprecated

class FlatFieldArrays:
    """
    A class for flat-field normalization
    """

    _supported_interpolations = ["linear", "nearest"]

    def __init__(
        self,
        radios_shape: tuple,
        flats,
        darks,
        radios_indices=None,
        interpolation: str = "linear",
        distortion_correction=None,
    ):
        """
        Initialize a flat-field normalization process.

        Parameters
        ----------
        radios_shape: tuple
            A tuple describing the shape of the radios stack, in the form
            `(n_radios, n_z, n_x)`.
        flats: dict
            Dictionary where each key is the flat index, and the value is a
            numpy.ndarray of the flat image.
        darks: dict
            Dictionary where each key is the dark index, and the value is a
            numpy.ndarray of the dark image.
        radios_indices: array of int, optional
            Array containing the radios indices in the scan. `radios_indices[0]` is the index
            of the first radio, and so on.
        interpolation: str, optional
            Interpolation method for flat-field. See below for more details.
        distortion_correction: DistortionCorrection, optional
            A DistortionCorrection object. If provided, it is used to correct flat distortions based on each radio.


        Important
        ----------
        `flats` and `darks` are expected to be a dictionary with integer keys (the flats/darks indices)
        and numpy array values.
        You can use the following helper functions: `nabu.io.reader.load_images_from_dataurl_dict`
        and `nabu.io.utils.create_dict_of_indices`


        Notes
        ------
        Usually, when doing a scan, only one or a few darks/flats are acquired.
        However, the flat-field normalization has to be performed on each radio,
        although incoming beam can fluctuate between projections.
        The usual way to overcome this is to interpolate between flats.
        If interpolation="nearest", the first flat is used for the first
        radios subset, the second flat is used for the second radios subset,
        and so on.
        If interpolation="linear", the normalization is done as a linear
        function of the radio index.
        """
        self._set_parameters(radios_shape, radios_indices, interpolation)
        self._set_flats_and_darks(flats, darks)
        self.distortion_correction = distortion_correction


    def _set_flats_and_darks(self, flats, darks):
        self._check_frames(flats, "flats", 1, 9999)
        self.n_flats = len(flats)
        self.flats = flats
        self._sorted_flat_indices = sorted(self.flats.keys())
        self._flat2arrayidx = {k: v for k, v in zip(self._sorted_flat_indices, np.arange(self.n_flats))}

        self._check_frames(darks, "darks", 1, 1)
        self.darks = darks
        self.n_darks = len(darks)
        self._sorted_dark_indices = sorted(self.darks.keys())
        self._dark = None


    def _set_radios_shape(self, radios_shape):
        if len(radios_shape) == 2:
            self.radios_shape = (1,) + radios_shape
        elif len(radios_shape) == 3:
            self.radios_shape = radios_shape
        else:
            raise ValueError("Expected radios to have 2 or 3 dimensions")
        n_radios, n_z, n_x = self.radios_shape
        self.n_radios = n_radios
        self.n_angles = n_radios
        self.shape = (n_z, n_x)


    @staticmethod
    def _check_frames(frames, frames_type, min_frames_required, max_frames_supported):
        n_frames = len(frames)
        if n_frames < min_frames_required:
            raise ValueError("Need at least %d %s" % (min_frames_required, frames_type))
        if n_frames > max_frames_supported:
            raise ValueError(
                "Flat-fielding with more than %d %s is not supported"
                % (max_frames_supported, frames_type)
            )


    def _set_parameters(self, radios_shape, radios_indices, interpolation):
        self._set_radios_shape(radios_shape)
        if radios_indices is None:
            radios_indices = np.arange(0, self.n_radios, dtype=np.int32)
        else:
            radios_indices = np.array(radios_indices, dtype=np.int32)
            if radios_indices.size != self.n_radios:
                raise ValueError(
                    "Expected radios_indices to have length %s = n_radios, but got length %d"
                    % (self.n_radios, radios_indices.size)
                )
        self.radios_indices = radios_indices
        self.interpolation = interpolation
        check_supported(
            interpolation, self._supported_interpolations, "Interpolation mode"
        )

    @staticmethod
    def get_previous_next_indices(arr, idx):
        pos = bisect_left(arr, idx)
        if pos == len(arr):  # outside range
            return (arr[-1],)
        if arr[pos] == idx:
            return (idx,)
        if pos == 0:
            return (arr[0],)
        return arr[pos - 1], arr[pos]

    @staticmethod
    def get_nearest_index(arr, idx):
        pos = bisect_left(arr, idx)
        if arr[pos] == idx:
            return idx
        return arr[pos - 1] if idx - arr[pos - 1] < arr[pos] - idx else arr[pos]

    def _get_flat_linear(self, idx, dtype=np.float32):
        prev_next = self.get_previous_next_indices(self._sorted_flat_indices, idx)
        if len(prev_next) == 1:  # current index corresponds to an acquired flat
            flat_data = self.flats[prev_next[0]]
        else:  # interpolate
            prev_idx, next_idx = prev_next
            flat_data_prev = self.flats[prev_idx]
            flat_data_next = self.flats[next_idx]
            delta = next_idx - prev_idx
            w1 = 1 - (idx - prev_idx) / delta
            w2 = 1 - (next_idx - idx) / delta
            flat_data = w1 * flat_data_prev + w2 * flat_data_next
        if flat_data.dtype != dtype:
            flat_data = np.ascontiguousarray(flat_data, dtype=dtype)
        return flat_data

    def _get_flat_nearest(self, idx, dtype=np.float32):
        idx0 = self.get_nearest_index(self._sorted_flat_indices, idx)
        flat = self.flats[idx0]
        if flat.dtype != dtype:
            flat = np.ascontiguousarray(flat, dtype=dtype)
        return flat

    def get_flat(self, idx, dtype=np.float32):
        """
        Get flat file corresponding to the corresponding index.
        If no flat file was acquired at this index, an interpolated flat
        is returned.
        """
        flat = None
        if self.interpolation == "linear":
            flat = self._get_flat_linear(idx, dtype=dtype)
        elif self.interpolation == "nearest":
            flat = self._get_flat_nearest(idx, dtype=dtype)
        else:
            raise ValueError("Unsupported interpolation method %s" % self.interpolation)
        return flat

    def get_dark(self):
        if self._dark is None:
            first_dark_idx = self._sorted_dark_indices[0]
            dark = np.ascontiguousarray(self.darks[first_dark_idx], dtype=np.float32)
            self._dark = dark
        return self._dark

    def normalize_radios(self, radios):
        """
        Apply a flat-field normalization, with the current parameters, to a stack
        of radios.
        The processing is done in-place, meaning that the radios content is overwritten.

        Parameters
        -----------
        radios: numpy.ndarray
            Radios chunk
        """
        do_flats_distortion_correction = (self.distortion_correction is not None)
        dark = self.get_dark()
        for i, idx in enumerate(self.radios_indices):
            radio_data = radios[i]
            radio_data -= dark
            flat = self.get_flat(idx)
            flat = flat - dark
            if do_flats_distortion_correction:
                flat = self.distortion_correction.estimate_and_correct(flat, radio_data)
            radios[i] = radio_data / flat
        return radios


    def normalize_single_radio(self, radio, radio_idx, dtype=np.float32):
        """
        Apply a flat-field normalization to a single projection image.
        """
        dark = self.get_dark()
        radio -= dark
        flat = self.get_flat(radio_idx, dtype=dtype)
        flat = flat - dark
        if self.distortion_correction is not None:
            flat = self.distortion_correction.estimate_and_correct(flat, radio)
        radio /= flat
        return radio


FlatField = FlatFieldArrays

class FlatFieldDataUrls(FlatField):

    def __init__(
        self,
        radios_shape: tuple,
        flats: dict,
        darks: dict,
        radios_indices=None,
        interpolation: str = "linear",
        distortion_correction=None,
        **chunk_reader_kwargs
    ):
        """
        Initialize a flat-field normalization process with DataUrls.

        Parameters
        ----------
        radios_shape: tuple
            A tuple describing the shape of the radios stack, in the form
            `(n_radios, n_z, n_x)`.
        flats: dict
            Dictionary where the key is the flat index, and the value is a
            silx.io.DataUrl pointing to the flat.
        darks: dict
            Dictionary where the key is the dark index, and the value is a
            silx.io.DataUrl pointing to the dark.
        radios_indices: array, optional
            Array containing the radios indices. `radios_indices[0]` is the index
            of the first radio, and so on.
        interpolation: str, optional
            Interpolation method for flat-field. See below for more details.
        distortion_correction: DistortionCorrection, optional
            A DistortionCorrection object. If provided, it is used to


        Other Parameters
        ----------------
        The other named parameters are passed to ChunkReader(). Please read its
        documentation for more information.

        Notes
        ------
        Usually, when doing a scan, only one or a few darks/flats are acquired.
        However, the flat-field normalization has to be performed on each radio,
        although incoming beam can fluctuate between projections.
        The usual way to overcome this is to interpolate between flats.
        If interpolation="nearest", the first flat is used for the first
        radios subset, the second flat is used for the second radios subset,
        and so on.
        If interpolation="linear", the normalization is done as a linear
        function of the radio index.
        """

        flats_arrays_dict = load_images_from_dataurl_dict(flats, **chunk_reader_kwargs)
        darks_arrays_dict = load_images_from_dataurl_dict(darks, **chunk_reader_kwargs)
        super().__init__(
            radios_shape,
            flats_arrays_dict,
            darks_arrays_dict,
            radios_indices=radios_indices,
            interpolation=interpolation,
            distortion_correction=distortion_correction,
        )

