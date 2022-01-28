"""Gaussian beam related tools and utilities."""

import logging
import math
import numpy as np

from .env import warn
from .config import config_instance
from .symbols import Symbol, FUNCTIONS
from .utilities.misc import is_iterable
from .exceptions import ConvergenceException
from .cymath.gaussbeam import transform_q
from .cymath.complex import ceq
from .cymath.homs import HGModeWorkspace, HGModes

LOGGER = logging.getLogger(__name__)

__all__ = (
    "HGMode",
    "HGModes",
)


def transform_beam_param(ABCD, q1, nr1=1, nr2=1):
    r"""Transforms a beam parameter `q1` by the matrix `ABCD`.

    The value of the new beam parameter returned is given by the
    Kogelnik transformation,

    .. math::
        q_2 = n_{r,2} \frac{A \frac{q_1}{n_{r,1}} + B}{ C \frac{q_1}{n_{r_1}} + D},

    where :math:`A`, :math:`B`, :math:`C`, :math:`D` are the
    corresponding elements of the `ABCD` matrix, and :math:`n_{r,1}`,
    :math:`n_{r,2}` are the refractive indices of the source and target
    media respectively.

    .. note::

        The method :meth:`.Model.propagate_beam` should be preferred over this in most cases,
        as it will automatically take into account refractive indices of spaces. With that
        method, you can simply specify the input and output nodes associated with the component
        you want to transform over and get back a :class:`.PropagationSolution` instance on
        which you can find the resulting beam parameter with :meth:`.PropagationSolution.q`.

        This function is more intended for array-calculations (i.e. where `q1` is an array
        of beam parameters or complex values) and cases where `ABCD` is a manually defined
        matrix.

    Parameters
    ----------
    ABCD : :class:`numpy.ndarray`
        A 2D numpy array of shape ``(2, 2)`` containing the ABCD matrix elements. Note
        that this can be a matrix of symbolic elements or a matrix of numbers.

    q1 : complex, :class:`.BeamParam`, symbolic, array-like
        A complex number, :class:`.BeamParam` instance or complex symbolic expression,
        representing the beam parameter to be transformed by `ABCD`. This can also be
        an array of beam parameters (which in turn can be symbolic or numeric again).

    nr1 : float, symbolic
        The index of refraction of the source medium.

    nr2 : float, symbolic
        The index of refraction of the target medium.

    Returns
    -------
    out : complex, :class:`.BeamParam`, symbolic, :class:`numpy.ndarray`
        The transformed beam parameter. If `ABCD` is symbolic then a symbolic
        expression is returned. If `q1` is a :class:`.BeamParam` instance then
        a new :class:`.BeamParam` instance is returned. Note that these two
        conditions couple such that a :class:`.BeamParam` with a symbolic q
        attribute may be returned.

        If `q1` is an array of beam parameters then an array of the above types
        will be returned (dependent upon whether `q1` contains symbolic or numeric
        beam parameters).
    """
    if not isinstance(q1, (BeamParam, Symbol, np.ndarray)):
        raise ValueError("q1 should be of a type BeamParam, Symbol, or np.ndarray")

    make_bp = isinstance(q1, BeamParam)
    if make_bp:
        q1_symbolic = q1.symbolic

        wl = q1.wavelength
        q1 = q1.q
    else:
        q1_symbolic = isinstance(q1, Symbol)

    # dtype of object for ABCD indicates symbolic ABCD matrix
    if ABCD.dtype == object or q1_symbolic or isinstance(q1, np.ndarray):
        q1_factor = q1 / nr1
        A = ABCD[0][0]
        B = ABCD[0][1]
        C = ABCD[1][0]
        D = ABCD[1][1]

        q2 = nr2 * (A * q1_factor + B) / (C * q1_factor + D)
    # purely numeric so use Cython function for speed
    else:
        q2 = transform_q(ABCD, q1, nr1, nr2)

    if make_bp:
        return BeamParam(q=q2, wavelength=wl, nr=nr2)

    return q2


# TODO (sjr) Cite my thesis derivation of below equation eventually
def ws_overlap(W, S, Wp, Sp, wavelength=None):
    r"""Calculates the WS phase space overlap.

    This overlap function is computed by,

    .. math::

        O(W,S) = \frac{4}{W^2 W_P^2} \frac{1}{\left(\frac{1}{W^2} + \frac{1}{W_p^2}\right)^2 + \frac{k^2}{4}\left(S - S_P\right)^2},

    .. note::
        The equation above was derived from the work in :cite:`PhysRevD.101.102005`.

    where :math:`W` and :math:`S` are the beam size and defocus, respectively, of a gaussian beam propagated
    to the same plane as the primary mode (which has :math:`W_p`, :math:`S_p`).

    Parameters
    ----------
    W : number, array-like
        Beam size of mode [metres].

    S : number, array-like
        Defocus of mode [1/metres].

    Wp : number, array-like
        Beam size of primary mode [metres].

    Sp : number, array-like
        Defocus of primary mode [1/metres].

    wavelength : float, optional
        Wavelength of the beam. Defaults to the value in the
        loaded config file.

    Returns
    -------
    O : number, array-like
        The overlap between the mode :math:`(W,S)` and the primary mode :math:`(W_p,S_p)`.
    """
    if wavelength is None:
        wavelength = config_instance()["constants"].getfloat("lambda0")

    k = 2 * np.pi / wavelength
    A = 4 / (W ** 2 * Wp ** 2)
    B = 1 / W ** 2 + 1 / Wp ** 2
    C = (k / 2) * (S - Sp)

    return A / (B ** 2 + C ** 2)


def ws_overlap_grid(qp, woffset, soffset, wpts=200, spts=200):
    r"""Computes the WS phase space overlap with the primary beam parameter `qp`
    over a grid of W, S data.

    See :func:`.ws_overlap` for a definition of the overlap quantity.

    The :math:`W` and :math:`S` spaces are formed by creating arrays around the
    :attr:`.BeamParam.w` and :attr:`.BeamParam.S` values of `qp`, according to
    the offsets given in `woffset` and `soffset`, respectively.

    Parameters
    ----------
    qp : :class:`.BeamParam`
        The primary "mode" which overlapping modes are calculated against.

    woffset : float, sequence
        A single number, or size 2 sequence. Defines the offsets (lower, upper)
        from the primary mode beamsize to use for the W space.

    soffset : float, sequence
        A single number, or size 2 sequence. Defines the offsets (lower, upper)
        from the primary mode beamsize to use for the S space.

    wpts : int, optional; default: 200
        Number of points for the W space array.

    spts : int, optional; default: 200
        Number of points for the S space array.

    Returns
    -------
    W : :class:`numpy.ndarray`
        The W space (as a 2D grid).

    S : :class:`numpy.ndarray`
        The S space (as a 2D grid).

    OL : :class:`numpy.ndarray`
        The overlap as a function of the WS phase space (as a 2D grid).

    Examples
    --------
    In the following example, we compute the overlap to a primary mode which
    has a 6 mm beam size and a defocus of 0 m (i.e. at the waist).

    .. jupyter-execute::

        import finesse
        finesse.configure(plotting=True)

        import finesse.gaussian as gaussian
        from finesse.plotting.plot import ws_phase_space

        import matplotlib.pyplot as plt

        # Make a beam parameter with w = 6 mm, S = 0 m
        qp = gaussian.BeamParam(w=6e-3, S=0)

        # Compute the WS phase space overlap with qp, using
        # maximum offset of 1 mm in beam size and 1 cm in defocus
        W, S, OL = gaussian.ws_overlap_grid(qp, woffset=1e-3, soffset=1e-2)

        # Now plot this as contours of overlap with custom levels
        fig, ax = ws_phase_space(
            W, S, OL,
            levels=[0.6, 0.8, 0.84, 0.88, 0.92, 0.94, 0.96, 0.98, 0.995, 0.999],
        )
    """
    if not isinstance(qp, BeamParam):
        raise TypeError("Expected argument qp to be of type BeamParam.")

    if qp.symbolic:
        warn(
            "Beam parameter argument 'qp' is symbolic; evaluating this with current "
            "parameter values for use in ws_overlap_grid."
        )
        qp = qp.eval()

    # Get the beam size and defocus of the primary mode
    Wp = qp.w
    Sp = qp.S
    wavelength = qp.wavelength

    if not is_iterable(woffset):
        wlim1 = wlim2 = woffset
    else:
        wlim1, wlim2 = woffset

    if not is_iterable(soffset):
        slim1 = slim2 = soffset
    else:
        slim1, slim2 = soffset

    # Construct the w (beam size), s (defocus) spaces as
    # array offsets around primary beam parameter
    w = np.linspace(Wp - wlim1, Wp + wlim2, wpts)
    s = np.linspace(Sp - slim1, Sp + slim2, spts)

    W, S = np.meshgrid(w, s)
    OL = ws_overlap(W, S, Wp, Sp, wavelength)

    return W, S, OL


def optimise_HG00_q(e, q, homs, max_iterations=100, accuracy=1e-9, return_field=False):
    """Computes the optimal complex beam parameter to describe an optical field,
    described by a vector of HG modes. This optimisation assumes that the field to be
    optimised is approximately a HG00 beam shape.

    Parameters
    ----------
    e : array_like
        Array of complex HG mode amplitudes to be optimised
    q : [complex | :class:`finesse.BeamParam`] or tuple
        x and y complex beam parameter basis that `e` is in.
        If a singular value is given qx=qy, else (qx, qy) should
        be provided.
    homs : list(tuple(n, m))
        List of HG mode indices for each element in e
    max_iterations : int, optional
        Maximum number of iterations to try before raising a RuntimeError
    accuracy : float, optional
        level to suppress HG20 and HG02 modes to
    return_field : bool, optional
        When True the optimised array of HG modes is returned

    Returns
    -------
    qx, qy : (:class:`finesse.BeamParam`, :class:`finesse.BeamParam`)
        Optimised beam parameters
    e : ndarray
        optimised HG mode amplitude array, only when `return_field == True`

    Raises
    ------
    ConvergenceException
        If the maximum number of iterations is reached.

    Notes
    -----
    The algorithm is fairly simple: assuming an approximatly HG00
    beam described by a vector of HG modes has the wrong basis, it
    will have less HG00 amplitude and more HG20 and HG02 modes. The
    optimal basis is then finding {qx, qy} which reduces the amount
    of HG20 and HG02.

    This algorithm is iterative and takes linear steps towards the
    correct {qx, qy} using the amount of HG20 and HG02 present.
    The next q to try is given by:

    .. math::
        \\frac{-4 a Z_r}{i\\sqrt{2}} + q

    Where :math:`a` is the amplitude of the HG20 or HG02 for x
    and y optimisation in each direction. The above is reached
    by the coupling coefficient k_00->02 and determining how
    much amplitude is expected for a given mismatch, then reverting
    it.

    When using a finite number of modes to describe some mismatched
    beam some level of information is lost and not retrievable with
    this method. For large mismatches it may not be possible to optimise
    back to the true beam parameters.

    For example, consider describing a mismatched beam up to order 6 HG
    modes. A mismatched beam will scatter the 6th order modes into the 8th
    which are not included in the description of the beam, therefore the
    information is lost. When performing this inverse the 8th order mode
    information cannot be brought back to fix the 6th order mode. The result
    is that this method may not reduce higher order terms.
    """
    from finesse.knm.tools import make_scatter_matrix

    e = np.array(e, dtype=complex).copy()
    if np.squeeze(e).ndim != 1:
        raise RuntimeError("Optical field array should be 1-dimensional")
    # Remove HG00 phase otherwise this algortim fails to converge
    phase = np.angle(e[0])
    e *= np.exp(-1j * phase)
    # Try and extract the q values
    try:
        qx, qy = q
    except (ValueError, TypeError):
        qx = qy = q
    # Try and get the HG mode indices
    try:
        homs = np.asarray(homs)
        hg02_idx = np.where(np.bitwise_and.reduce(homs == np.array((0, 2)), 1))[0][0]
        hg20_idx = np.where(np.bitwise_and.reduce(homs == np.array((2, 0)), 1))[0][0]
    except IndexError:
        raise IndexError("Could not find both the HG20 and HG02 modes in homs vector")
    accuracy *= abs(e[0])  # scale relative to HG00
    i = 0
    while abs(e[hg20_idx]) > accuracy or abs(e[hg02_idx]) > accuracy:
        qx2 = -4 * e[hg20_idx] / abs(e[0]) * qx.zr / (1j * np.sqrt(2)) + qx
        qy2 = -4 * e[hg02_idx] / abs(e[0]) * qy.zr / (1j * np.sqrt(2)) + qy
        # Compute the scattering matrix, returning a KnmMatrix object
        kmat = make_scatter_matrix("bayerhelms", qx, qx2, qy, qy2, 0, 0, select=homs)
        qx = qx2  # new q
        qy = qy2  # new q
        e = kmat.data @ e  # new mode vector
        i += 1
        if i > max_iterations:
            raise ConvergenceException("Reached maximum number of iterations")
    if return_field:
        return qx, qy, e * np.exp(1j * phase)
    else:
        return qx, qy


def optimise_HG00_q_scipy(
    e,
    q,
    homs,
    accuracy=1e-6,
    return_fit_result=False,
    fix_spot_size=False,
    astigmatic=False,
):
    """Computes the optimal complex beam parameter to describe an optical field,
    described by a vector of HG modes. This optimisation assumes that the field to be
    optimised is approximately a HG00 beam shape.

    The algorithm maximises the amount of HG00 present in a beam by
    varying the x and y complex beam parameter.

    Parameters
    ----------
    e : array_like
        Array of complex HG mode amplitudes to be optimised
    q : [complex | :class:`finesse.BeamParam`] or tuple
        x and y complex beam parameter basis that `e` is in.
        If a singular value is given qx=qy, else (qx, qy) should
        be provided.
    homs : list(tuple(n, m))
        List of HG mode indices for each element in e
    accuracy : float, optional
        level to suppress HG20 and HG02 modes to
    return_fit_result : bool, optional
        When True the optimised result from Scipy minimize
        is returned.
    fix_spot_size : bool, optional
        When True a non-linear optimiser is used and keeps the spot sized fixed
        to its current value. Useful for when you expect just the curvature of a
        beam to be changing.
    astigmatic : bool, optional
        When True the x and y beam parameters will be optimised separately. If
        you know they should be equal then set this to False.

    Returns
    -------
    qx, qy : (:class:`finesse.BeamParam`, :class:`finesse.BeamParam`)
        Optimised beam parameters
    res : Scipy fit result
        optimised HG mode amplitude array, only when
        `return_fit_result == True`
    """
    from finesse.knm.tools import make_scatter_matrix
    from scipy.optimize import minimize
    import finesse

    e = np.array(e, dtype=complex).copy()
    if np.squeeze(e).ndim != 1:
        raise RuntimeError("Optical field array should be 1-dimensional")
    # Remove HG00 phase otherwise this algortim fails to converge
    e *= np.exp(-1j * np.angle(e[0]))
    # Try and extract the q values
    try:
        qx, qy = q
    except TypeError:
        qx = qy = q

    def fun(x):
        if astigmatic:
            rex, imx, rey, imy = x
        else:
            rex, imx = x
            rey = rex
            imy = imx
        # Compute the scattering matrix, returning a KnmMatrix object
        kmat = make_scatter_matrix(
            "bayerhelms", qx, rex + 1j * imx, qy, rey + 1j * imy, 0, 0, select=homs
        )
        return -abs((kmat.data @ e)[0]) ** 2

    def fun_fix_w(x):
        if not astigmatic:
            Rcx = Rcy = np.inf if x[0] == 0 else 1 / x[0]
        else:
            Rcx = np.inf if x[0] == 0 else 1 / x[0]
            Rcy = np.inf if x[1] == 0 else 1 / x[1]
        # Compute the scattering matrix, returning a KnmMatrix object
        kmat = make_scatter_matrix(
            "bayerhelms",
            qx,
            finesse.BeamParam(w=qx.w, Rc=Rcx),
            qy,
            finesse.BeamParam(w=qy.w, Rc=Rcy),
            0,
            0,
            select=homs,
        )
        return -abs((kmat.data @ e)[0]) ** 2

    if not fix_spot_size:
        if astigmatic:
            res = minimize(
                fun, (qx.z, qx.zr, qy.z, qy.zr), tol=accuracy, method="nelder-mead"
            )
            qx = finesse.BeamParam(q=res.x[0] + 1j * res.x[1])
            qy = finesse.BeamParam(q=res.x[2] + 1j * res.x[3])
        else:
            res = minimize(
                fun,
                ((qx.z + qy.z) / 2, (qx.zr + qy.zr) / 2),
                tol=accuracy,
                method="nelder-mead",
            )
            qx = finesse.BeamParam(q=res.x[0] + 1j * res.x[1])
            qy = finesse.BeamParam(q=res.x[0] + 1j * res.x[1])
    else:
        if astigmatic:
            res = minimize(
                fun_fix_w, (1 / qx.Rc, 1 / qy.Rc), tol=accuracy, method="nelder-mead"
            )
            qx = finesse.BeamParam(w=qx.w, Rc=1 / res.x[0] if res.x[0] != 0 else np.inf)
            qy = finesse.BeamParam(w=qy.w, Rc=1 / res.x[1] if res.x[1] != 0 else np.inf)
        else:
            res = minimize(
                fun_fix_w,
                (1 / qx.Rc + 1 / qy.Rc) / 2,
                tol=accuracy,
                method="nelder-mead",
            )
            qx = finesse.BeamParam(w=qx.w, Rc=1 / res.x[0] if res.x[0] != 0 else np.inf)
            qy = finesse.BeamParam(w=qy.w, Rc=1 / res.x[0] if res.x[0] != 0 else np.inf)

    if return_fit_result:
        return qx, qy, res
    else:
        return qx, qy


class BeamParam:
    r"""Gaussian beam complex parameter.

    This can be a symbolic beam parameter or numeric. For example,
    if :func:`transform_beam_param` is called using a symbolic ABCD
    matrix then a symbolic `BeamParam` instance will be created
    automatically.

    The wavelength of the laser beam defaults to the current value for
    ``lambda0`` in the config file being used, if it is not given as an
    argument during construction of a BeamParam.

    The index of refraction of the associated medium defaults to unity, if
    it is not given as an argument during construction of a BeamParam.

    The following are legal initialisations of a `BeamParam`
    object::

        q = BeamParam(w0=w0, z=z)
        q = BeamParam(z=z, zr=zr)
        q = BeamParam(w=w, rc=rc)
        q = BeamParam(w=w, S=S)
        q = BeamParam(q=c) # where c is a complex number or symbol

    Descriptions of these variables are as follows:

    - :math:`z` --- distance to the waist position (in metres). Negative
      values indicate a beam converging to the waist, positive is a beam
      diverging from the waist.
    - :math:`w_0` --- radius of the beam at the waist (in metres).
    - :math:`zr` --- Rayleigh range of the beam (in metres).
    - :math:`w` --- radius of the beam at the current position (in metres).
    - :math:`rc` --- radius of curvature of the wavefront (in metres).
    - :math:`S` --- curvature (or defocus) of the wavefront (in metres).
    - :math:`q` --- the complex beam parameter itself.

    The default wavelength and refractive index values can also be
    changed with (for example)::

        q = BeamParam(wavelength, nr, w0=w0, zr=zr)

    Note that BeamParam objects can also be symbolic by passing any value
    in `*args` or `**kwargs` as a symbolic expression.

    Parameters
    ----------
    wavelength : float, optional
        Wavelength of the beam light, defaults to the value given for
        ``lambda0`` in the config file being used.

    nr : float, optional
        Refractive index, defaults to unity.
    """

    def __init__(self, wavelength=None, nr=1, *args, **kwargs):
        if wavelength is not None:
            self.__lambda = wavelength
        else:
            self.__lambda = config_instance()["constants"].getfloat("lambda0")
        self.__nr = nr
        self.__symbolic = False

        err_msg = (
            "Expected one of:\n"
            " - q\n"
            " - w0, z\n"
            " - zr, z\n"
            " - w, Rc\n"
            " - w, S\n"
        )

        if len(args) == 1:
            if isinstance(args[0], Symbol):
                self.__q = args[0]
                self.__symbolic = True
            else:
                try:
                    self.__q = complex(args[0])
                except TypeError:
                    self.__q = np.array(args[0], dtype=complex)

        elif len(kwargs) == 1:
            if "q" in kwargs:
                if isinstance(kwargs["q"], Symbol):
                    self.__q = kwargs["q"]
                    self.__symbolic = True
                else:
                    try:
                        self.__q = complex(kwargs["q"])
                    except TypeError:
                        self.__q = np.array(kwargs["q"], dtype=complex)
            else:
                raise ValueError(err_msg)

        elif len(kwargs) == 2:
            if "w0" in kwargs and "z" in kwargs:
                q = kwargs["z"] + 1j * math.pi * kwargs["w0"] ** 2 / (
                    self.__lambda / self.__nr
                )
            elif "z" in kwargs and "zr" in kwargs:
                q = kwargs["z"] + 1j * kwargs["zr"]
            elif ("rc" in kwargs or "Rc" in kwargs) and "w" in kwargs:
                Rc = kwargs.get("Rc") or kwargs.get("rc")
                one_q = 1 / Rc - 1j * self.__lambda / (
                    math.pi * self.__nr * kwargs["w"] ** 2
                )
                q = 1 / one_q
            elif "S" in kwargs and "w" in kwargs:
                one_q = kwargs["S"] - 1j * self.__lambda / (
                    math.pi * self.__nr * kwargs["w"] ** 2
                )
                q = 1 / one_q
            else:
                raise ValueError(err_msg)

            self.__symbolic = any(isinstance(v, Symbol) for v in kwargs.values())

            self.__q = q
        else:
            raise ValueError(err_msg)

    def __repr__(self):
        return "<%s (w0=%s, w=%s, z=%s) at %s>" % (
            self.__class__.__name__,
            self.w0,
            self.w,
            self.z,
            hex(id(self)),
        )

    @property
    def symbolic(self):
        """Flag indicating whether the beam parameter is a symbolic object.

        :getter: True if symbolic, false otherwise (read-only).
        """
        return self.__symbolic

    def depends_on(self):
        """A list of the model parameters that the symbolic beam parameter depends upon.

        If this beam parameter is not symbolic, then an empty list is returned.
        """
        if not self.symbolic:
            return []

        return self.q.parameters()

    def eval(self, as_bp=True, subs=None):
        """Evaluate the symbolic beam parameter. Parameter substitutions can be
        performed via the substitution dict `subs`.

        Note that this simply returns :attr:`BeamParam.q` if this is not symbolic.

        Parameters
        ----------
        as_bp : bool, optional; default: True
            Flag indicating whether to return result as a :class:`.BeamParam` instance.

        subs : dict, optional; default: None
            Dictionary of parameter substitutions.
        """
        if not self.symbolic:
            q = self.q
        else:
            q = self.q.eval(subs=subs)
            as_bp &= not isinstance(q, np.ndarray)

        if as_bp:
            return BeamParam(wavelength=self.wavelength, q=q, nr=self.nr)

        return q

    @property
    def wavelength(self):
        """The wavelength of the beam (in metres).

        :getter: Returns the wavelength of the beam.
        :setter: Sets the wavelength of the beam.
        """
        return self.__lambda

    @wavelength.setter
    def wavelength(self, value):
        self.__lambda = value

    @property
    def nr(self):
        """The refractive index associated with the `BeamParam`.

        :getter: Returns the index of refraction.
        :setter: Sets the index of refraction.
        """
        return self.__nr

    @nr.setter
    def nr(self, value):
        self.__nr = value

    @property
    def q(self):
        """The complex beam parameter value (:math:`q`).

        :getter: Returns the complex beam parameter value.
        """
        return self.__q

    @property
    def z(self):
        """The relative distance to the waist of the beam (in metres).

        :getter: Returns the relative distance to the waist.
        :setter: Sets the relative distance to the waist.
        """
        return self.__q.real

    @z.setter
    def z(self, value):
        if self.__symbolic:
            self.__q = value + 1j * self.zr
        else:
            self.__q = complex(1j * self.zr + float(value))

    @property
    def zr(self):
        """The Rayleigh range (:math:`z_R`) of the beam (in metres).

        :getter: Returns the Rayleigh range.
        :setter: Sets the Rayleigh range.
        """
        return self.__q.imag

    @zr.setter
    def zr(self, value):
        if self.__symbolic:
            self.__q = self.z + 1j * value
        else:
            self.__q = complex(self.z + 1j * float(value))

    @property
    def w(self):
        r"""The radius of the beam, :math:`w`, in metres.

        Computed as,

        .. math::

            w = |q|\,\sqrt{\frac{\lambda}{n_r \pi z_R}},

        where :math:`q` is the complex beam parameter (given by :attr:`BeamParam.q`),
        :math:`\lambda` is the beam wavelength (given by :attr:`BeamParam.wavelength`),
        :math:`n_r` is the refractive index of the associated medium (given by
        :attr:`BeamParam.nr`) and :math:`z_R` is the Rayleigh range (given by
        :attr:`BeamParam.zr`, or :attr:`BeamParam.imag`).

        .. hint::

            Use :meth:`.BeamParam.beamsize` to compute the beam size as a function of
            any of the above dependent arguments.

        :getter: Returns the radius, often denoted as "beam-size", of the beam. Read-only.
        """
        return np.abs(self.__q) * np.sqrt(
            self.__lambda / (self.__nr * math.pi * self.zr)
        )

    @property
    def divergence(self):
        r"""Divergence of the beam.

        The divergence is defined as,

        .. math::

            d = \frac{\lambda}{w_0 \pi},

        where :math:`\lambda` is the wavelength and :math:`w_0`
        is the waist size of the beam.

        :getter: Returns the beam divergence. Read-only.
        """
        return self.wavelength / (self.w0 * np.pi)

    @property
    def w0(self):
        r"""The radius of the waist, :math:`w_0`, of the beam, in metres.

        Computed as,

        .. math::

            w_0 = \sqrt{\frac{z_R \lambda}{n_r \pi}},

        where :math:`z_R` is the Rayleigh range (given by :attr:`BeamParam.zr`,
        or :attr:`BeamParam.imag`), :math:`\lambda` is the beam wavelength (given
        by :attr:`BeamParam.wavelength`) and :math:`n_r` is the refractive index of
        the associated medium (given by :attr:`BeamParam.nr`).

        :getter: Returns the beam waist-size.
        :setter: Sets the beam waist-size.
        """
        return np.sqrt(self.zr * self.__lambda / (self.__nr * math.pi))

    @w0.setter
    def w0(self, value):
        if self.__symbolic:
            self.__q = self.z + 1j * value ** 2 * (self.__nr * math.pi) / self.__lambda
        else:
            self.__q = complex(
                self.z + 1j * value ** 2 * (self.__nr * math.pi) / self.__lambda
            )

    @property
    def Rc(self):
        r"""Radius of curvature, :math:`R_c`, of the beam, in metres.

        Computed as,

        .. math::

            R_c = z \left(1 + \left(\frac{z_R}{z}\right)^2\right),

        where :math:`z` is the distance to the waist position (given by
        :attr:`BeamParam.z`, or :attr:`BeamParam.real`) and :math:`z_R` is
        the Rayleigh range (given by :attr:`BeamParam.zr`, or :attr:`BeamParam.imag`).

        Note that if :math:`z = 0` then this will return ``np.inf``.

        .. hint::

            Use :meth:`.BeamParam.roc` to compute the radius of curvature as a
            function of any of the above dependent arguments.

        :getter: Returns the beams' radius of curvature. Read-only.
        """
        if not self.z:
            return np.inf

        return self.z * (1 + (self.zr / self.z) ** 2)

    @property
    def S(self):
        r"""Defocus (wavefront curvature), :math:`S`, of the Gaussian beam, equivalent to
        the reciprocal of :attr:`BeamParam.Rc`.

        Computed as,

        .. math::

            S = \frac{z}{z^2 + z_R^2},

        where :math:`z` is the distance to the waist position (given by
        :attr:`BeamParam.z`, or :attr:`BeamParam.real`) and :math:`z_R` is
        the Rayleigh range (given by :attr:`BeamParam.zr`, or :attr:`BeamParam.imag`).

        .. hint::

            Use :meth:`.BeamParam.curvature` to compute the curvature as a function of
            any of the above dependent arguments.

        :getter: Returns the defocus of the beam parameter. Read-only.
        """
        return self.z / (self.z * self.z + self.zr * self.zr)

    @property
    def psi(self):
        r"""Gouy phase, :math:`\psi`, of the Gaussian beam.

        Computed as,

        .. math::

            \psi = \arctan{\left(\frac{z}{z_R}\right)},

        where :math:`z` is the distance to the waist position (given by
        :attr:`BeamParam.z`, or :attr:`BeamParam.real`) and :math:`z_R` is
        the Rayleigh range (given by :attr:`BeamParam.zr`, or :attr:`BeamParam.imag`).

        .. hint::

            Use :meth:`.BeamParam.gouy` to compute the Gouy phase as a function of
            any of the above dependent arguments.

        :getter: Returns the Gouy phase (in radians) of the beam parameter. Read-only.
        """
        if self.symbolic:
            atan2 = FUNCTIONS["arctan2"]
        else:
            atan2 = np.arctan2

        return atan2(self.z, self.zr)

    def __make_q_from_args(
        self, z=None, wavelength=None, nr=None, w0=None, return_modified_args=False
    ):
        if z is None:
            z = self.z
        else:
            z = np.array(z)

        if wavelength is None:
            wavelength = self.wavelength
        else:
            wavelength = np.array(wavelength)

        if nr is None:
            nr = self.nr
        else:
            nr = np.array(nr)

        if w0 is None:
            w0 = self.w0
        else:
            w0 = np.array(w0)

        q = z + 1j * math.pi * w0 ** 2 / (wavelength / nr)

        if not return_modified_args:
            return q

        return q, z, wavelength, nr, w0

    def beamsize(self, z=None, wavelength=None, nr=None, w0=None):
        """Computes the radius of the beam as a function of any of the dependent
        arguments.

        Calling this method with no arguments is equivalent to
        accessing :attr:`BeamParam.w`.

        Parameters
        ----------
        z : float, optional
            Distance along optical axis relative to waist, defaults
            to :attr:`BeamParam.z` for this beam parameter.

        wavelength : float, optional
            Wavelength of the beam to use, defaults to :attr:`BeamParam.wavelength`
            for this beam parameter.

        nr : float, optional
            Refractive index to use, defaults to :attr:`BeamParam.nr` for
            this beam parameter.

        w0 : float, optional
            Waist-size of the beam, defaults :attr:`BeamParam.w0` for this
            beam parameter.

        Returns
        -------
        The radius of the beam using the specified properties.
        """
        q, _, wavelength, nr, _ = self.__make_q_from_args(
            z, wavelength, nr, w0, return_modified_args=True
        )

        zr_ = q.imag

        return np.abs(q) * np.sqrt(wavelength / (nr * math.pi * zr_))

    def gouy(self, z=None, wavelength=None, nr=None, w0=None):
        """Computes the Gouy-phase as a function of any of the dependent arguments.

        Parameters
        ----------
        z : float, optional
            Distance along optical axis relative to waist, defaults
            to :attr:`BeamParam.z` for this beam parameter.

        wavelength : float, optional
            Wavelength of the beam to use, defaults to :attr:`BeamParam.wavelength`
            for this beam parameter.

        nr : float, optional
            Refractive index to use, defaults to :attr:`BeamParam.nr` for
            this beam parameter.

        w0 : float, optional
            Waist-size of the beam, defaults :attr:`BeamParam.w0` for this
            beam parameter.

        Returns
        -------
        The accumulated Gouy phase using the specified properties.
        """
        q = self.__make_q_from_args(z, wavelength, nr, w0)

        if self.symbolic:
            atan2 = FUNCTIONS["arctan2"]
            z_ = q.real
            zr_ = q.imag
        else:
            atan2 = np.arctan2
            z_ = q.real
            zr_ = q.imag

        return atan2(z_, zr_)

    def roc(self, z=None, wavelength=None, nr=None, w0=None):
        """Radius of curvature of the beam as a function of any of the dependent
        arguments.

        Calling this method with no arguments is equivalent to
        accessing :attr:`BeamParam.Rc`.

        Parameters
        ----------
        z : float, optional
            Distance along optical axis relative to waist, defaults
            to :attr:`BeamParam.z` for this beam parameter.

        wavelength : float, optional
            Wavelength of the beam to use, defaults to :attr:`BeamParam.wavelength`
            for this beam parameter.

        nr : float, optional
            Refractive index to use, defaults to :attr:`BeamParam.nr` for
            this beam parameter.

        w0 : float, optional
            Waist-size of the beam, defaults :attr:`BeamParam.w0` for this
            beam parameter.

        Returns
        -------
        Radius of curvature of the beam using the specified properties.
        """
        q = self.__make_q_from_args(z, wavelength, nr, w0)
        z_ = q.real
        zr_ = q.imag

        return z_ * (1 + (zr_ / z_) ** 2)

    def curvature(self, z=None, wavelength=None, nr=None, w0=None):
        """Curvature of the beam wavefront as a function of any of the dependent
        arguments.

        Calling this method with no arguments is equivalent to
        accessing :attr:`BeamParam.S`.

        Parameters
        ----------
        z : float, optional
            Distance along optical axis relative to waist, defaults
            to :attr:`BeamParam.z` for this beam parameter.

        wavelength : float, optional
            Wavelength of the beam to use, defaults to :attr:`BeamParam.wavelength`
            for this beam parameter.

        nr : float, optional
            Refractive index to use, defaults to :attr:`BeamParam.nr` for
            this beam parameter.

        w0 : float, optional
            Waist-size of the beam, defaults :attr:`BeamParam.w0` for this
            beam parameter.

        Returns
        -------
        Curvature of the beam using the specified properties.
        """
        q = self.__make_q_from_args(z, wavelength, nr, w0)
        z_ = q.real
        zr_ = q.imag

        return z_ / (z_ * z_ + zr_ * zr_)

    @staticmethod
    def overlap(q1, q2):
        r"""
        Computes the projection from one beam parameter to another to give a measure of the
        overlap between the two beam parameters. The quantity computed is,

        .. math::
            \mathcal{O} = \frac{4|\Im{\{q_1\}}\,\Im{\{q_2\}}|}{|q_1^* - q_2|^2}.

        The return values is :math:`\mathcal{O} \in [0, 1]`, where 0 implies complete
        mode mismatch and 1 indicates full mode matching.

        This function was provided by Paul Fulda and Antonio Perreca, which came originally
        from Chris Mueller.

        Parameters
        ----------
        q1 : :class:`.BeamParam`, complex, array-like
            First beam parameter. Note that this can be a numeric or symbolic beam parameter,
            a complex number or an array of complex values.

        q2 : :class:`.BeamParam`
            Second beam parameter. Note that this can be a numeric or symbolic beam parameter,
            a complex number or an array of complex values.

        Returns
        -------
        overlap : float, array-like, :class:`.Symbol`
            The overlap between `q1` and `q2` as defined above.
        """
        if isinstance(q1, BeamParam):
            q1_q = q1.q
        else:
            q1_q = q1

        if isinstance(q2, BeamParam):
            q2_q = q2.q
        else:
            q2_q = q2

        zr1 = q1_q.imag
        zr2 = q2_q.imag

        return np.abs(4 * zr1 * zr2) / np.abs(q1_q.conjugate() - q2_q) ** 2

    @staticmethod
    def mismatch(q1, q2):
        r"""
        Computes the mode mismatch via an alternate form of :math:`1 - \mathcal{O}`, where
        :math:`\mathcal{O}` is the overlap (see :meth:`BeamParam.overlap`).

        This method is less susceptible to floating point errors than simply :math:`1 - \mathcal{O}`
        for very small mismatches. The exact form of the quantity computed is,

        .. math::
            \mathcal{M} = \frac{|q_1 - q_2|^2}{|q_1 - q_2^*|^2}.

        The return value is :math:`\mathcal{M} \in [0, 1]`, where 0 implies full mode matching
        and 1 indicates complete mode mismatch.

        Parameters
        ----------
        q1 : :class:`.BeamParam`
            First beam parameter. Note that this can be a numeric or symbolic beam parameter,
            a complex number or an array of complex values.

        q2 : :class:`.BeamParam`
            Second beam parameter. Note that this can be a numeric or symbolic beam parameter,
            a complex number or an array of complex values.

        Returns
        -------
        mismatch : float, array-like, :class:`.Symbol`
            The mismatch between `q1` and `q2` as defined above.
        """
        if isinstance(q1, BeamParam):
            q1_q = q1.q
        else:
            q1_q = q1

        if isinstance(q2, BeamParam):
            q2_q = q2.q
        else:
            q2_q = q2

        return np.abs(q1_q - q2_q) ** 2 / np.abs(q1_q - q2_q.conjugate()) ** 2

    @staticmethod
    def overlap_contour(q1, M, t):
        """This function returns a set of beam parameters that are mismatched to q1 by
        an overlap M. There are multiple beam parameters that can be X% overlapped with
        one particular q value. This function is parameterised with t from 0 to 2pi,
        which can provide all the possible beam parameters that are M% mismatched.

        q1 - reference beam parameter
        M  - Mismatch factor (1-overlap) [0 -> 1]
        t  - Selection parameter [0 -> 2pi]

        Examples
        --------
        Plots the contours of mismatch for 0.1% and 1% from some initial q value::

            import numpy as np
            import matplotlib.pyplot as plt
            import finesse

            qin = finesse.BeamParam(w0=1e-3, z=20)
            t = np.linspace(0, 2*np.pi, 100)

            # use vectorised functions to select a cerain property of the beam paramters
            vx  = np.vectorize(lambda q: q.z)
            vy  = np.vectorize(lambda q: q.w/1e-3)

            for mm in [1e-3, 2e-2]:
                mmc = finesse.BeamParam.overlap_contour(qin, mm, t)

                plt.text(vx(mmc[20]), vy(mmc[20]), "%1.1f%%" % ((mm*100)),alpha=0.5, fontsize=8)
                l, = plt.plot(vx(mmc),     vy(mmc),     ls='--', alpha=0.2, zorder=-10, c='k')

            plt.show()
        """
        M = np.asarray(M)
        if np.any(M >= 1) or np.any(M < 0):
            raise RuntimeError("Mismatch values out of bounds, 0 <= M < 1")
        from numpy import vectorize

        vbp = vectorize(lambda x: BeamParam(q1.wavelength, q1.nr, x))

        z1 = np.real(q1)
        zR1 = np.imag(q1)
        r = (2 * np.sqrt(M) * zR1) / (1 - M)
        y0 = ((M + 1) * zR1) / (1 - M)
        x0 = z1
        q2 = r * np.cos(t) + x0 + 1j * (r * np.sin(t) + y0)

        return vbp(q2)

    def conjugate(self):
        """Computes and returns the complex conjugate of the beam parameter.

        Returns
        -------
        q_conj : :class:`.BeamParam`
            The complex conjugate of this `BeamParam` instance.
        """
        return BeamParam(self.wavelength, self.nr, self.q.conjugate())

    def __abs__(self):
        return abs(self.q)

    def __complex__(self):
        return self.q

    def __str__(self):
        return (
            f"BeamParam: q = {self.q}\n"
            f"    w0 = {self.w0} m, z = {self.z} m\n"
            f"     w = {self.w} m, Rc = {self.Rc} m"
        )

    def __mul__(self, a):
        return BeamParam(self.wavelength, self.nr, q=self.__q * a)

    def __imul__(self, a):
        self.__q *= a
        return self

    __rmul__ = __mul__

    def __add__(self, a):
        return BeamParam(self.wavelength, self.nr, self.q + a)

    def __iadd__(self, a):
        self.__q += complex(a)
        return self

    __radd__ = __add__

    def __sub__(self, a):
        return BeamParam(self.wavelength, self.nr, self.q - a)

    def __isub__(self, a):
        self.__q -= a
        return self

    def __rsub__(self, a):
        return BeamParam(self.wavelength, self.nr, a - self.q)

    def __div__(self, a):
        return BeamParam(self.wavelength, self.nr, self.q / a)

    def __truediv__(self, a):
        if isinstance(a, BeamParam):
            return BeamParam(self.wavelength, self.nr, self.q / a.q)

        return BeamParam(self.wavelength, self.nr, self.q / a)

    def __idiv__(self, a):
        self.__q /= a
        return self

    def __pow__(self, q):
        return BeamParam(self.wavelength, self.nr, self.q ** q)

    def __neg__(self):
        return BeamParam(self.wavelength, self.nr, -self.q)

    def __eq__(self, q):
        if q is None:
            return False

        if self.symbolic:
            if isinstance(q, Symbol) or (isinstance(q, BeamParam) and q.symbolic):
                return np.allclose(self.eval(), q.eval())

            return ceq(complex(q), self.eval())

        return ceq(complex(q), self.q)

    @property
    def real(self):
        """The real part of the complex beam parameter, equal to the relative distance
        to the beam waist (in metres).

        :getter: Returns the real part of the beam parameter.
        :setter: Sets the real part of the beam parameter.
        """
        return self.z

    @real.setter
    def real(self, value):
        self.z = value

    @property
    def imag(self):
        """The imaginary part of the complex beam parameter, equal to the Rayleigh range
        :math:`z_R` of the beam (in metres).

        :getter: Returns the imaginary part of the beam parameter.
        :setter: Sets the imaginary part of the beam parameter.
        """
        return self.zr

    @imag.setter
    def imag(self, value):
        self.zr = value

    def reverse(self):
        """Returns the reversed beam parameter.

        This is the beam parameter with the sign of the distance to waist flipped,
        i.e. :math:`q_r = -q^*` where :math:`q_r` is the reversed beam parameter.

        Returns
        -------
        q_r : :class:`BeamParam`
            The reverse of this beam parameter.
        """
        return BeamParam(self.wavelength, self.nr, -1.0 * self.q.conjugate())


class HGMode:
    """An object representation of a Hermite-Gauss mode.

    Parameters
    ----------
    q : :class:`.BeamParam` or complex, or length two sequence of
        The beam parameter. Specify a tuple of (qx, qy) as this argument
        for an astigmatic beam.

    n : int, optional; default: 0
        Tangential mode index.

    m : int, optional; default: 0
        Sagittal mode index.
    """

    def __init__(self, q, n=0, m=0):
        if is_iterable(q):
            qx, qy = q
        else:
            qx = qy = q

        if not isinstance(qx, BeamParam):
            qx = BeamParam(q=qx)
        if not isinstance(qy, BeamParam):
            qy = BeamParam(q=qy)

        self.__qx = qx
        self.__qy = qy

        if self.qx.nr != self.qy.nr:
            raise ValueError("Refractive indices associated with qs must be equal.")
        if self.qx.wavelength != self.qy.wavelength:
            raise ValueError("Wavelengths associated with qs must be equal.")

        nr = self.qx.nr
        lambda0 = self.qx.wavelength
        self._workspace = HGModeWorkspace(
            int(n), int(m), self.qx.q, self.qy.q, nr, lambda0
        )

    @property
    def n(self):
        return self._workspace.n

    @property
    def m(self):
        return self._workspace.m

    @property
    def qx(self):
        return self.__qx

    @qx.setter
    def qx(self, value):
        if not isinstance(value, BeamParam):
            value = BeamParam(q=value)

        self.__qx = value
        self._workspace.set_values(
            qx=self.qx, nr=self.qx.nr, lambda0=self.qx.wavelength
        )

    @property
    def qy(self):
        return self.__qy

    @qy.setter
    def qy(self, value):
        if not isinstance(value, BeamParam):
            value = BeamParam(q=value)

        self.__qy = value
        self._workspace.set_values(
            qy=self.qy, nr=self.qy.nr, lambda0=self.qy.wavelength
        )

    def set_q(self, q):
        """Sets the beam parameter in both planes to the same value `q`.

        Parameters
        ----------
        q : :class:`.BeamParam` or complex
            The beam parameter.
        """
        if not isinstance(q, BeamParam):
            q = BeamParam(q=q)

        self.__qx = q
        self.__qy = q

        nr = q.nr
        lambda0 = q.wavelength
        self._workspace.set_values(qx=self.qx, qy=self.qy, nr=nr, lambda0=lambda0)

    def __check_shapes(self, a, out, direction):
        if out.shape != a.shape:
            raise ValueError(
                f"Shape of output array ({out.shape}) not equal to "
                f"shape of {direction} array ({a.shape})"
            )

    def un(self, x, out=None):
        """Compute the beam profile in the tangential plane."""

        if out is not None:
            self.__check_shapes(x, out, "x")

        return self._workspace.u_n(x, out=out)

    def um(self, y, out=None):
        """Compute the beam profile in the tangential plane."""

        if out is not None:
            self.__check_shapes(y, out, "y")

        return self._workspace.u_m(y, out=out)

    def unm(self, x, y, out=None):
        """Compute the full transverse beam profile."""

        return self._workspace.u_nm(x, y, out=out)
