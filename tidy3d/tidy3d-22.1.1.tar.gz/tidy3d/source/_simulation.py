import numpy as np
import logging

from ..constants import int_, float_, complex_, fp_eps, ETA_0, C_0, xyz_dict
from ..mode import dot_product, Mode
from ..utils.log import log_and_raise, SourceError
from .Source import VolumeSource, ModeSource, PlaneWave, PlaneSource, GaussianBeam


def _compute_modes_source(self, source, Nmodes, target_neff=None, pml_layers=(0, 0),
    bend_radius=None, bend_axis=None):

    if isinstance(source, ModeSource):
        src_data = self._src_data(source)
        # Set the Yee permittivity if not yet set
        mplane = src_data.mode_plane
        if mplane.eps_ex is None:
            mplane._set_yee_sim(self)
        # Compute the mode plane modes
        mplane.compute_modes(Nmodes, target_neff, pml_layers, bend_radius, bend_axis,
            source.angle_theta, source.angle_phi)


def _src_data(self, source):
    """Get the source data object from a source, if it is in the simulation."""
    try:
        src_data = self._source_ids[id(source)]
        return src_data
    except KeyError:
        log_and_raise("Source has not been added to Simulation!", SourceError)


def spectrum(self, source, freqs):
    """Returns the spectrum of a :class:`.Source`.

    Parameters
    ----------
    source : Source
        A source in the simulation.
    freqs : array_like
        (Hz) Array of frequencies to evaluate the spectrum over.
    """

    return source.source_time._get_spectrum(freqs, self.tmesh)


def set_mode(
    self,
    source,
    mode_ind,
    Nmodes=None,
    target_neff=None,
    pml_layers=(0, 0),
    bend_radius=None,
    bend_axis=None,
):
    """Set the index of the mode to be used by the mode source. To choose
    which mode to set use :meth:`.compute_modes` and :meth:`.viz_modes`. If
    provided as input, ``Nmodes`` number of modes with effective index closest
    to ``target_neff`` are computed, and the mode with index ``mode_ind`` is
    used. Otherwise, the modes are simply computed in order of decreasing
    effective index.
    
    Parameters
    ----------
    source : ModeSource
        A mode source in the simulation.
    mode_ind : int
        Index of the mode to use.
    Nmodes : None or int, optional
        Number of modes to compute, usually only necessary if ``target_neff``
        is also provided.
    target_neff : None or float, optional
        Look for modes with effective index closest to ``target_neff``.
    pml_layers : tuple, optional
        Number of PML layers to be added in each direction. These are added
        to the **interior** of the mode plane, i.e. the mode plane size is not
        extended. The default boundaries are PEC.
    bend_radius : float or None, optional
        A curvature radius for simulation of waveguide bends.
    bend_axis : ``'x'``, ``'y'``, ``'z'`` or ``None``, optional
        The axis normal to the plane in which the bend lies. This must be
        provided if ``bend_radius`` is not ``None``, and it must be orthogonal
        to the axis normal to the mode plane.
    """

    if isinstance(source, ModeSource):

        src_data = self._src_data(source)
        mplane = src_data.mode_plane

        src_data.mode_ind = mode_ind
        if Nmodes is None:
            src_data.Nmodes = mode_ind + 1
        else:
            src_data.Nmodes = Nmodes
        src_data.target_neff = target_neff

        src_data.pml_layers = pml_layers

        if bend_radius is not None:
            if bend_axis is None:
                raise SourceError("'bend_axis' is required if 'bend_radius is provided.") 
            if xyz_dict[bend_axis] == src_data.mode_plane.norm_ind:
                raise SourceError("'bend axis' must be normal to the mode plane axis.")
            src_data.bend_radius = bend_radius
            src_data.bend_axis = bend_axis

        logging.info("Mode set, recommend verifying using viz_modes.")

    else:
        log_and_raise("Input 0 must be an instance of a ModeSource.", SourceError)
