# from __future__ import absolute_import, division, print_function

import numexpr as ne
import numpy as np
import scipy.interpolate as interpol
from matplotlib import pyplot as plt
from scipy.constants import c

import drama.utils as utls

#%%
def raised_cosine(N, alpha):
    """

    Parameters
    ----------
    N :

    alpha :


    Returns
    -------

    """
    if N == 1:
        return 1
    else:
        win = alpha + (alpha - 1) * np.cos(2 * np.pi * np.arange(N) / (N - 1))
        return win


def w2ww(n, w):
    """Makes window out of coefficient, if needed.

    Parameters
    ----------
    n :
        Number of elements
    w :
        weighting value or function

    Returns
    -------
    type
        weighting vector

    """
    ww = np.zeros(n, dtype=np.complex64)
    if np.size(w) == 1:
        # either no weighting or a hamming like
        ww[:] = raised_cosine(n, w)
        ww = ww / np.sum(ww)
    else:
        ww[:] = np.array(w)
        ww = ww.reshape((1, n)) / np.sum(np.abs(ww))
    return ww


def sinc_bp(
    sin_angle,
    L,
    f0,
    *dummy,
    field=False,
    beamwidth=None,
    sin_squint=0,
    use_ne=False,
    **kwargs,
):
    """Calculate pattern for a uniform illumination (sinc)

    Parameters
    ----------
    sin_angle :
        Sin of the angle
    L :
        Antenna length
    f0 :
        Frequency
    field :
        If true, returned values are in EM field units, else
        they are in power units (Default value = False)
    *dummy :

    beamwidth :
         (Default value = None)
    sin_squint :
         Named parameter with sin of squint angle. (Default value = 0)
    use_ne :
         (Default value = False)

    Returns
    -------

    """
    l = c / f0
    if beamwidth is None:
        La = L
    else:
        # Force antenna length to correspond to beamwidth
        # bw = l / La
        La = l / beamwidth
    if use_ne:
        K = np.pi * La / l
        pisa = K * (sin_angle - sin_squint)
        pisa = np.where(pisa == 0, 1.0e-20, pisa)
        pattern = ne.evaluate("sin(pisa)/pisa")
    else:
        pattern = np.sinc(La / l * (sin_angle - sin_squint))
    return pattern if field else pattern ** 2


def sinc_1tx_nrx(
    sin_angle, L, f0, num_chan, field=False, sin_squint=0, use_ne=False
):
    """Calculate pattern for a system with 1 TX and N RX

    Parameters
    ----------
    sin_angle :
        Sin of the angle
    L :
        Antenna length
    f0 :
        Frequency
    num_ch :
        Number of receiving channels
        :sin_squint: Named parameter with sin of squint angle.
    field :
        If true, returned values are in EM field units, else
        they are in power units (Default value = False)
    num_chan :

    sin_squint :
         (Default value = 0)
    use_ne :
         (Default value = False)

    Returns
    -------

    """

    bp_tx = sinc_bp(sin_angle - sin_squint, L, f0, field)
    bp_rx = sinc_bp(sin_angle - sin_squint, L / num_chan, f0, field)

    return bp_tx * bp_rx


def phased_array(
    sin_angle,
    L,
    f0,
    N,
    w,
    *dummy,
    field=False,
    beamwidth=None,
    sin_squint=0,
    use_ne=False,
    el_pattern=None
):
    """Calculate phased array pattern. Element pattern is assumed to be
        an ideal sinc pattern, but this could be changed in the future
        easily

    Parameters
    ----------
    sin_angle :
        Sin of the angle
    L :
        Total antenna length
    f0 :
        Frequency
    N :
        Number of receiving channels
    ww :
        complex weighting of the elements, in case one wants
        to include a tapering. Only used if it a N element
        ndarray or a list
    field :
        If true, returned values are in EM field units, else
        they are in power units
        :sin_squint: Named parameter with sin of squint angle. (Default value = False)
    w :

    *dummy :

    beamwidth :
         (Default value = None)
    sin_squint :
         (Default value = 0)
    use_ne :
         (Default value = False)

    Returns
    -------

    """

    k0 = 2 * np.pi * f0 / c
    if type(sin_angle) != np.ndarray:
        sina = np.array([sin_angle])
    else:
        sina = sin_angle  # just a copy
    try:
        ww = w2ww(N, w)
    except:
        ww = w / N
        # print("No weighting!")
    sina_s = sina - sin_squint
    shp_res = sina_s.shape
    sina_s = sina_s.reshape((sina_s.size, 1))
    if el_pattern is None:
        elpat = sinc_bp(sina, L / N, f0, field=True, use_ne=use_ne)
    else:
        elpat = el_pattern
    nkd = (k0 * (L / N * np.arange(N) - L / 2 + L / N / 2)).reshape((1, N))
    if use_ne:
        # nax = len(sina_s.shape)
        array_fact = ne.evaluate("sum(ww * exp(1j * nkd * sina_s), axis=1)")
    else:
        array_fact = np.sum(ww * np.exp(1j * nkd * sina_s), axis=-1)
    if sina.size == 1:
        pattern = (array_fact * elpat.flatten())[0]
    else:
        pattern = (array_fact * elpat.flatten()).reshape(shp_res)
    return pattern if field else np.abs(pattern) ** 2


def phased_spacedarray(
    sin_angle,
    L,
    f0,
    N,
    w,
    spacing,
    field=False,
    beamwidth=None,
    sin_squint=0,
    use_ne=False,
    el_pattern=None
):
    """Calculate phased array pattern. Element pattern is assumed to be
        an ideal sinc pattern, but this could be changed in the future
        easily

    Parameters
    ----------
    sin_angle :
        Sin of the angle
    L :
        Antenna element length
    f0 :
        Frequency
    N :
        Number of receiving channels
    w :
        complex weighting of the elements, in case one wants
        to include a tapering. Only used if it a N element
        ndarray or a list
    field :
        If true, returned values are in EM field units, else
        they are in power units (Default value = False)
    sin_squint :
        Named parameter with sin of squint angle. (Default value = 0)
    use_ne :
        use numexpr (Default value = False)
    el_pattern:
        None or element pattern, in that case user makes sure it has right dimensions,
        etc.
    spacing :

    beamwidth :
         (Default value = None)

    Returns
    -------

    """

    k0 = 2 * np.pi * f0 / c
    if type(sin_angle) != np.ndarray:
        sina = np.array([sin_angle])
    else:
        sina = sin_angle  # just a copy
    try:
        #ww = np.zeros(N, dtype=np.complex64)
        #ww[:] = np.array(w)
        #ww = ww.reshape((1, N)) # / N
        ww = w2ww(N, w)
        # print("Applied weighting")
        # print(ww)
    except:
        ww = 1 / N
        # print("No weighting!")
    sina_s = sina - sin_squint
    shp_res = sina_s.shape
    sina_s = sina_s.reshape((sina_s.size, 1))
    # sina = sina.flatten()
    if el_pattern is None:
        elpat = sinc_bp(sina, L, f0, field=True, use_ne=use_ne)
    else:
        elpat = el_pattern

    Lp = (N - 1) * spacing
    if type(elpat) == list:
        sina_s = sina_s.flatten()
        pattern = 0
        for ind in range(N):
            if type(sin_squint) == np.ndarray:
                elpat_ = elpat[ind] + np.zeros_like(sin_squint)
            else:
                elpat_ = elpat[ind]
            nkd = (k0 * spacing * ind - Lp / 2)
            ww_ = ww[0, ind]
            if use_ne:
                nax = len(sina_s.shape)
                array_fact = ne.evaluate("ww_ * exp(1j * nkd * sina_s)")
            else:
                array_fact = ww_ * np.exp(1j * nkd * sina_s)

            if sina.size == 1:
                pattern = pattern + (array_fact * elpat_.flatten())[0]
            else:
                pattern = pattern + (array_fact * elpat_.flatten()).reshape(shp_res)

    else:
        if type(sin_squint) == np.ndarray:
            elpat = elpat + np.zeros_like(sin_squint)

        nkd = (k0 * spacing * np.arange(N) - Lp / 2).reshape((1, N))
        if use_ne:
            nax = len(sina_s.shape)
            array_fact = ne.evaluate("sum(ww * exp(1j * nkd * sina_s), axis=1)")
        else:
            array_fact = np.sum(ww * np.exp(1j * nkd * sina_s), axis=-1)
        if sina.size == 1:
            pattern = (array_fact * elpat.flatten())[0]
        else:
            pattern = (array_fact * elpat.flatten()).reshape(shp_res)
    return pattern if field else np.abs(pattern) ** 2


def gaussian_bp(
    sin_angle,
    L,
    f0,
    *dummy,
    field=False,
    beamwidth=None,
    sin_squint=0,
    use_ne=False,
    **kwargs
):
    """Calculates gaussian beam pattern

    Parameters
    ----------
    sin_angle :
        Sin of the angle
    L :
        Antenna length
    f0 :
        Frequency
    field :
        If true, returned values are in EM field units, else
        they are in power units
        :sin_squint: Named parameter with sin of squint angle. (Default value = False)
    beamwidth :
        if set, this is the beamwidth, if left as None
        then the beamwidth is calculated from the L (Default value = None)
    *dummy :

    sin_squint :
         (Default value = 0)
    use_ne :
         (Default value = False)

    Returns
    -------

    """
    # exp (-(b/2)**4 / bw**2) = 0.5
    # (b/2)**2 / bw**2 = log(2)
    # bw = b/2 / sqrt(log(2)
    if beamwidth is None:
        l = c / f0
        bw = (l / L) / np.sqrt(np.log(2)) / 2
    else:
        bw = beamwidth / np.sqrt(np.log(2)) / 2

    if field:
        pattern = np.exp(-((sin_angle - sin_squint) ** 2) / (2 * bw ** 2))
    else:
        pattern = np.exp(-((sin_angle - sin_squint) ** 2) / (bw ** 2))

    return pattern


class pattern:
    """ """

    def phased_array_num(
        self, sin_angle, L, *args, sin_squint=0, field=True, **kwargs
    ):
        """

        Parameters
        ----------
        f0 :
            Frequency
        type_e :
            Function used for elevation pattern. Currently
            "sinc" or "gaussian"
        type_a :
            Function used for azimuth pattern
        La :
            Antenna length (defaults to 10 m)
        Le :
            Antenna height (defauls to 1 m)
        beamwidth_e :
            if set, this is the elevation beamwidth (deg),
            if left as None then the beamwidth is
            calculated from the L
        beamwidth_a :
            if set, this is the azimuth beamwidth (deg),
            if left as None then the beamwidth is
            calculated from the L
        squint :
            Azimuth pointing, in degree. Defaults to 9.
        el0 :
            Elevation pointing w.r.t. boresight, in degree.
            Defaults to 0.
        tilt :
            Mechanical tilt, in degree, defaults to 0.
        el_offset :
            an offset w.r.t. to nominal phase center in (m).
            This causes a linear phase in elevation.
        az_offset :
            same in azimuth
        xpol2cpol :
            we assume that cross pol patterns are identical
            to copol ones, scaled by this complex factor
        G0 :
            antenna gain, in dB
        Nel_a :
            Number of elements in azimuth, for a phased array
        Nel_e :
            Number of elements in azimuth, for a phased array
        wa :
            azimuth weighting of antenna illumination
        we :
            elevation weighting of antenna illumination
        spacing_a :
            for spaced_array type, spacing between elements in azimuth
        spacing_e :
            for spaced_array type, spacing between elements in elevation
        steering_rate :
            steering rate (deg/s) of the antenna
        Tanalysis :
            temporal processing window for target geo-history (used for LUT)
        verbosity :
            how much output on consol
        sin_angle :

        L :

        *args :

        sin_squint :
             (Default value = 0)
        field :
             (Default value = True)
        **kwargs :


        Returns
        -------

        """
        w = args[2]
        if np.size(w) > 1:
            w = w.flatten()
            # compute (1-alpha)/alpha and invert to retrieve alpha
            rc_coef = (max(np.real(w)) - min(np.real(w))) / (
                2 * np.mean(np.real(w))
            )
            w = 1 / (1 + rc_coef)
        else:
            w = np.real(w)

        # make the squint, L and w variables the same size of the sin_angle array
        sin_squint_array = sin_squint - np.zeros(sin_angle.shape)
        L_array = L - np.zeros(sin_angle.shape)
        w_array = w - np.zeros(sin_angle.shape)
        shp_res = sin_angle.shape
        pattern = self.us2pat((sin_angle, sin_squint_array, L_array, w_array))
        #        if len(sin_squint) == 1:
        #            shp_res = sin_angle.shape
        #            pattern = self.us2pat((sin_angle,sin_squint**np.ones(sin_angle.shape)))
        #        else:
        #            if sin_angle.shape == sin_squint.shape:
        #                shp_res = sin_angle.shape
        #                pattern = self.us2pat((sin_angle,sin_squint))
        #            else:
        #                sin_squint =
        #                shp_res = (sin_squint.shape[1], sin_angle.shape[0])
        #                pattern = self.us2pat((sin_angle,sin_squint))
        pattern = pattern.reshape(shp_res)
        return pattern if field else np.abs(pattern) ** 2

    # dictionary of pattern functions
    models = {
        "gaussian": gaussian_bp,
        "sinc": sinc_bp,
        "phased_array": phased_array,
        "phased_spacedarray": phased_spacedarray,
        "phased_array_num": phased_array_num,
    }

    def __init__(
        self,
        f0,
        type_a="sinc",
        type_e=None,
        element_pattern=None,
        La=10.0,
        Le=1.0,
        beamwidth_a=None,
        beamwidth_e=None,
        squint=0,
        el0=0,
        tilt=0,
        el_offset=0,
        az_offset=0,
        xpol2cpol=0,
        G0=None,
        Nel_a=8,
        Nel_e=32,
        wa=1,
        we=1,
        spacing_a=1,
        spacing_e=1,
        steering_rate=0,
        Tanalysis=1,
        verbosity=1,
    ):
        """ Initialize pattern class.

        Parameters
        ----------
        f0 : float
            Frequency
        type_e :
            Function used for elevation pattern. Currently
            "sinc", "gaussian", "phased_array", "phased_array_num", "phased_spacedarray" or "element"
        type_a :
            Function used for azimuth pattern. Currently
            "sinc", "gaussian", "phased_array", "phased_array_num" or "phased_spacedarray" or "element"
        element_pattern: Pattern class instance or list thereof
            In conjunction with phased_array or phased_spacedarray it does what the name suggests.
            Passing a list will only work correctly if we use "phased_spacedarray" in one dimension and "element"
            in the other
            Example use: to define Harmony's dual/tripple antenna system
        La :
            Antenna length (defaults to 10 m)
        Le :
            Antenna height (defauls to 1 m)
        beamwidth_e :
            if set, this is the elevation beamwidth (deg),
            if left as None then the beamwidth is
            calculated from the L
        beamwidth_a :
            if set, this is the azimuth beamwidth (deg),
            if left as None then the beamwidth is
            calculated from the L
        squint :
            Azimuth pointing, in degree. Defaults to 0.
        el0 :
            Elevation pointing w.r.t. boresight, in degree.
            Defaults to 0.
        tilt :
            Mechanical tilt, in degree, defaults to 0.
        el_offset :
            an offset w.r.t. to nominal phase center in (m).
            This causes a linear phase in elevation.
        az_offset :
            same in azimuth
        xpol2cpol :
            we assume that cross pol patterns are identical
            to copol ones, scaled by this complex factor
        G0 :
            antenna gain, in dB. Defaults to None in which case it is calculated
        Nel_a :
            Number of elements in azimuth, for a phased array
        Nel_e :
            Number of elements in azimuth, for a phased array
        wa :
            azimuth weighting of antenna illumination
        we :
            elevation weighting of antenna illumination
        spacing_a :
            for spaced_array type, spacing between elements in azimuth
        spacing_e :
            for spaced_array type, spacing between elements in elevation
        steering_rate :
            steering rate (deg/s) of the antenna
        Tanalysis :
            temporal processing window for target geo-history (used for LUT)
        verbosity :
            how much output on consol
        sin_angle :

        L :

        *args :

        sin_squint :
             (Default value = 0)
        field :
             (Default value = True)
        **kwargs :


        Returns
        -------
        """
        self.info = utls.PrInfo(verbosity, "Pattern")
        if type_e is None:
            type_e = type_a
        if type_e != "element":
            self.func_e = self.models[type_e]
        if type_a != "element":
            self.func_a = self.models[type_a]
        if type(element_pattern) == pattern:
            self.element_pattern = element_pattern
        elif type(element_pattern) == list:
            self.element_pattern = element_pattern
        else:
            self.element_pattern = None
        self.type_a = type_a
        self.type_e = type_e
        self.La = La
        self.Le = Le
        if type_a == "element":
            self.Na = 1
        else:
            self.Na = Nel_a
        if type_e == "element":
            self.Ne = 1
        else:
            self.Ne = Nel_e
        if type_a in ["phased_array", "phased_array_num", "phased_spacedarray"]:
            self.wa = w2ww(Nel_a, wa)
        else:
            self.wa = wa
        if type_e in ["phased_array", "phased_array_num", "phased_spacedarray"]:
            self.we = w2ww(Nel_e, we)
        else:
            self.we = we
        self.beamwidth_a = (
            None if (beamwidth_a is None) else np.radians(beamwidth_a)
        )
        self.beamwidth_e = (
            None if (beamwidth_e is None) else np.radians(beamwidth_e)
        )
        self.f0 = f0
        self.wavelength = c / f0
        self.k0 = 2 * np.pi / self.wavelength
        self.squint = np.radians(squint)
        self.rel0 = np.radians(el0) - np.radians(tilt)
        self.tilt = np.radians(tilt)
        self.az_offset = az_offset
        self.el_offset = el_offset
        self.xpol2cpol = xpol2cpol
        self.a_eff = self.La * self.Le
        self.spacing_a = spacing_a
        self.spacing_e = spacing_e
        # print("1")
        if G0 is None:
            # print("2")
            if (beamwidth_a is None) or (beamwidth_e is None):
                self.init_g0()

            else:
                self.g0 = np.sqrt(4 * np.pi / beamwidth_a / beamwidth_e)
        else:
            self.g0 = utls.db2lin(G0, amplitude=True)
        self.G0 = 2 * utls.db(self.g0)

        # ------ initialize the LUT ------
        # lob samples in azimuth
        Nsmp_lobe = 100
        # Max lUT samples in azimuth
        Nsmp_max_u = 10001
        # Max lUT samples in squint configuration
        Nsmp_max_s = 1001

        if type_a == "phased_array_num" or type_e == "phased_array_num":
            # --- azimuth ---
            # angle sampling interval
            du = self.wavelength / max(La, Le) / Nsmp_lobe
            # Number of samples (odd) for the u domain
            Nu = np.min([2 * np.round(1 / du) + 1, Nsmp_max_u]).astype(int)
            u = np.linspace(-1, 1, Nu).reshape(Nu, 1)
            v = u

            # --- squint ---
            # the squint range covered by the LUT is symmetric about 0.
            # the factor 2 is introduced for safety (over-coverage).
            Dsquint = np.sin(np.radians(2 * steering_rate * Tanalysis))
            # Number of samples (odd) for the squint domain
            if Dsquint == 0:
                Ns = 1
            else:
                Ns = np.min([2 * np.round(1 / Dsquint) + 1, Nsmp_max_s]).astype(
                    int
                )
            sin_s = np.linspace(-Dsquint / 2, Dsquint / 2, Ns)
            nkd_a = (
                self.k0
                * (La / Nel_a * np.arange(Nel_a) - La / 2 + La / Nel_a / 2)
            ).reshape((1, Nel_a))
            nkd_e = (
                self.k0
                * (Le / Nel_e * np.arange(Nel_e) - La / 2 + La / Nel_e / 2)
            ).reshape((1, Nel_e))
            # initialize and fill the array patterns in azimuth and elevation
            array_fact_a = np.zeros((Nu, Ns), dtype="complex")
            array_fact_e = np.zeros((Nu, Ns), dtype="complex")
            for i in range(int((Ns - 1) / 2)):
                array_fact_a[:, i] = np.sum(
                    self.wa * np.exp(1j * nkd_a * (u - sin_s[i])), axis=-1
                )
                array_fact_a[:, (Ns - 1 - i)] = np.flip(array_fact_a[:, i])
                array_fact_e[:, i] = np.sum(
                    self.we * np.exp(1j * nkd_e * (v - sin_s[i])), axis=-1
                )
                array_fact_e[:, (Ns - 1 - i)] = np.flip(array_fact_e[:, i])
            array_fact_a[:, int((Ns - 1) / 2)] = np.sum(
                self.wa * np.exp(1j * nkd_a * u), axis=-1
            )
            array_fact_e[:, int((Ns - 1) / 2)] = np.sum(
                self.we * np.exp(1j * nkd_e * v), axis=-1
            )

            # insert elevation angle with respect to boresight (if not already
            # present in the sampled squint vector sin_s)
            sin_rel = np.sin(self.rel0)
            array_fact_rel_a = np.sum(
                self.wa * np.exp(1j * nkd_a * (u - sin_rel)), axis=-1
            )
            array_fact_rel_e = np.sum(
                self.we * np.exp(1j * nkd_e * (v - sin_rel)), axis=-1
            )
            idx_rel = np.where(sin_s < sin_rel)[0]
            if len(idx_rel) == 0:
                idx_rel = np.array([-1])
            idx_rel = idx_rel[-1]
            sin_rel = np.array([sin_rel])
            if idx_rel == (Ns - 1):
                # rel larger than sampled squint angles
                sin_s = np.concatenate([sin_s, sin_rel])
                array_fact_a = np.concatenate(
                    (array_fact_a, array_fact_rel_a.reshape(Nu, 1)), axis=1
                )
                array_fact_e = np.concatenate(
                    (array_fact_e, array_fact_rel_e.reshape(Nu, 1)), axis=1
                )
            else:
                if sin_s[idx_rel + 1] != sin_rel:
                    sin_s = np.insert(sin_s, idx_rel + 1, sin_rel)
                    array_fact_a = np.insert(
                        array_fact_a, idx_rel + 1, array_fact_rel_a, axis=1
                    )
                    array_fact_e = np.insert(
                        array_fact_e, idx_rel + 1, array_fact_rel_e, axis=1
                    )
                else:
                    sin_s = np.concatenate([sin_s, sin_rel + 0.1])
                    array_fact_a = np.concatenate(
                        (array_fact_a, array_fact_rel_a.reshape(Nu, 1)), axis=1
                    )
                    array_fact_e = np.concatenate(
                        (array_fact_e, array_fact_rel_e.reshape(Nu, 1)), axis=1
                    )
            Ns = len(sin_s)
            # print("No weighting!")

            elpat_a = sinc_bp(u, La / Nel_a, f0, field=True)
            elpat_e = sinc_bp(v, Le / Nel_e, f0, field=True)
            pattern_a = array_fact_a * elpat_a
            pattern_e = array_fact_e * elpat_e

            if np.size(wa) > 1:
                # estimates alpha from raised cosine vector
                wa_0 = (wa[0] + 1) / 2
            else:
                wa_0 = wa
            if np.size(we) > 1:
                # estimates alpha from raised cosine vector
                we_0 = (we[0] + 1) / 2
            else:
                we_0 = we

            # Add 3rd and 4th LUT dimensions: antenna length and tapering factor
            if wa_0 < we_0 and La < Le:
                pattern_wa = np.dstack((pattern_a, np.zeros_like(pattern_e)))
                pattern_we = np.dstack((np.zeros_like(pattern_a), pattern_e))
                pattern_tot = np.stack(
                    (pattern_wa, pattern_wa, pattern_we, pattern_we), axis=3
                )
                L_v = np.array([La, Le])
                w_v = np.array([wa_0 - 1, wa_0, we_0, we_0 + 1])
            elif wa_0 < we_0 and La > Le:
                pattern_wa = np.dstack((np.zeros_like(pattern_e), pattern_a))
                pattern_we = np.dstack((pattern_e, np.zeros_like(pattern_a)))
                pattern_tot = np.stack(
                    (pattern_wa, pattern_wa, pattern_we, pattern_we), axis=3
                )
                L_v = np.array([Le, La])
                w_v = np.array([wa_0 - 1, wa_0, we_0, we_0 + 1])
            elif wa_0 < we_0 and La == Le:
                pattern_wa = np.dstack((pattern_a, np.zeros_like(pattern_e)))
                pattern_we = np.dstack((pattern_e, np.zeros_like(pattern_a)))
                pattern_tot = np.stack(
                    (pattern_wa, pattern_wa, pattern_we, pattern_we), axis=3
                )
                L_v = np.array([La, La + 1])
                w_v = np.array([wa_0 - 1, wa_0, we_0, we_0 + 1])
            elif wa_0 > we_0 and La < Le:
                pattern_wa = np.dstack((pattern_a, np.zeros_like(pattern_e)))
                pattern_we = np.dstack((np.zeros_like(pattern_a), pattern_e))
                pattern_tot = np.stack(
                    (pattern_we, pattern_we, pattern_wa, pattern_wa), axis=3
                )
                L_v = np.array([La, Le])
                w_v = np.array([we_0 - 1, we_0, wa_0, wa_0 + 1])
            elif wa_0 > we_0 and La > Le:
                pattern_wa = np.dstack((np.zeros_like(pattern_e), pattern_a))
                pattern_we = np.dstack((pattern_e, np.zeros_like(pattern_a)))
                pattern_tot = np.stack(
                    (pattern_we, pattern_we, pattern_wa, pattern_wa), axis=3
                )
                L_v = np.array([Le, La])
                w_v = np.array([we_0 - 1, we_0, wa_0, wa_0 + 1])
            elif wa_0 > we_0 and La == Le:
                pattern_wa = np.dstack((pattern_a, np.zeros_like(pattern_e)))
                pattern_we = np.dstack((pattern_e, np.zeros_like(pattern_a)))
                pattern_tot = np.stack(
                    (pattern_we, pattern_we, pattern_wa, pattern_wa), axis=3
                )
                L_v = np.array([La, La + 1])
                w_v = np.array([we_0 - 1, we_0, wa_0, wa_0 + 1])
            elif wa_0 == we_0 and La < Le:
                pattern_wa = np.dstack((pattern_a, pattern_e))
                pattern_we = np.zeros_like(pattern_wa)
                pattern_tot = np.stack(
                    (pattern_wa, pattern_wa, pattern_we), axis=3
                )
                L_v = np.array([La, Le])
                w_v = np.array([wa_0 - 1, wa_0, wa_0 + 1])
            elif wa_0 == we_0 and La > Le:
                pattern_wa = np.dstack((pattern_e, pattern_a))
                pattern_we = np.zeros_like(pattern_wa)
                pattern_tot = np.stack(
                    (pattern_wa, pattern_wa, pattern_we), axis=3
                )
                L_v = np.array([Le, La])
                w_v = np.array([wa_0 - 1, wa_0, wa_0 + 1])
            else:  # wa==we and La==Le
                pattern_wa = np.dstack((pattern_a, np.zeros_like(pattern_e)))
                pattern_we = np.zeros_like(pattern_wa)
                pattern_tot = np.stack(
                    (pattern_wa, pattern_wa, pattern_we), axis=3
                )
                L_v = np.array([La, La + 1])
                w_v = np.array([wa_0 - 1, wa_0, wa_0 + 1])

            self.us2pat = interpol.RegularGridInterpolator(
                points=[u.flatten(), sin_s, L_v, w_v],
                values=pattern_tot,
                method="nearest",
                bounds_error=False,
            )

            self.func_a = self.phased_array_num
            self.func_e = self.phased_array_num
        else:
            self.us2pat = []

    # FIXME: add elevation steering so that array patterns are correcty
    # computed

    def init_g0(self):
        """ """
        self.info.msg("Calculating antenna gain", 1)
        if type(self.element_pattern) == pattern:
            if type(self.wa) == np.ndarray:
                wa_ = self.wa / np.max(np.abs(self.wa))
                nae =  np.sum(wa_**2)
            else:
                nae = self.Na
            if type(self.we) == np.ndarray:
                we_ = self.we / np.max(np.abs(self.we))
                nee =  np.sum(we_**2)
            else:
                nee = self.Ne
            self.g0 = np.abs(np.sqrt(nee * nae) * self.element_pattern.g0)
            self.a_eff = np.abs(self.element_pattern.a_eff * nae / self.Na *  nee / self.Ne)
        elif type(self.element_pattern) == list:
            G0 = 0
            ap_eff = 0
            if self.Na == 1:
                ww = self.we.flatten()
            else:
                ww = self.wa.flatten()
            ww = ww / np.max(np.abs(ww))
            for ind in range(len(self.element_pattern)):
                G0 = G0 + self.element_pattern[ind].g0**2 * ww[ind]**2
                ap_eff = ap_eff + self.element_pattern[ind].a_eff * ww[ind]**2
            self.g0 = np.sqrt(np.abs(G0))
            self.a_eff = np.abs(ap_eff / np.sum(ww**2))

        else:
            if self.type_a == "phased_array":
                la = np.sum(np.abs(self.wa)) / self.Na * self.La
                la_ = np.sum(np.abs(self.wa) ** 2) / self.Na * self.La
            elif self.type_a == "phased_spacedarray":
                la = self.La * self.Na
                la_ = la
            else:
                la = self.La
                la_ = la
            if self.type_e == "phased_array":
                le = np.sum(np.abs(self.we)) / self.Ne * self.Le
                le_ = np.sum(np.abs(self.we) ** 2) / self.Ne * self.Le
            elif self.type_e == "phased_spacedarray":
                le = self.Le * self.Ne
                le_ = le
            else:
                le = self.Le
                le_ = le
            self.a_eff = la ** 2 / la_ * le ** 2 / le_
            self.g0 = np.sqrt(4 * np.pi * self.a_eff / (self.wavelength ** 2))

    def elevation(self, ang, field=True, use_ne=False, steer_rad=None):
        """Returns elevation normalized pattern

        Parameters
        ----------
        ang :
            angle in radians
        field :
            return field if True, intensity if False (Default value = True)
        use_ne :
            use numexpr to speed up (Default value = False)
        steer_rad :
            steering angle, works lie squint_rad for azimuth pattern (Default value = None)
        normalized :
            returns patter normalized (Default value = True)

        Returns
        -------

        """
        if use_ne:
            tilt = self.tilt
            sin_rang = ne.evaluate("sin(ang - tilt)")
        else:
            sin_rang = np.sin(ang - self.tilt)
        if steer_rad is None:
            sin_steer_rad = np.sin(self.rel0)
        else:
            sin_steer_rad = np.sin(steer_rad)
        we_used = self.we
        #print(type(self.element_pattern))

        if type(self.element_pattern) == pattern:
            # FIXME: we need to account for the fact that different elements have
            # different gains g0.
            el_pat = self.element_pattern.func_e(sin_rang - sin_steer_rad,
                                                 self.element_pattern.Le,
                                                 self.f0,
                                                 self.element_pattern.Ne,
                                                 self.element_pattern.we,
                                                 self.element_pattern.spacing_e,
                                                 field=field,
                                                 beamwidth=self.element_pattern.beamwidth_e,
                                                 use_ne=use_ne)
        elif (type(self.element_pattern) == list
              and self.type_e in ['phased_array' , 'phased_spacedarray']):
            el_pat = []
            we_used = w2ww(self.Ne, 1)
            for element_pattern in self.element_pattern:
                el_pat_ = element_pattern.func_e(sin_rang - sin_steer_rad,
                                                 element_pattern.Le,
                                                 self.f0,
                                                 element_pattern.Ne,
                                                 element_pattern.we,
                                                 element_pattern.spacing_e,
                                                 field=field,
                                                 beamwidth=element_pattern.beamwidth_e,
                                                 use_ne=use_ne)
                w_rel = element_pattern.g0 / self.g0 * self.we.flatten()[ind]/np.max(np.abs(self.we)) * np.sqrt(self.Ne)
                #print(w_rel)
                #print(el_pat_.max())
                el_pat.append(w_rel * el_pat_)
        elif type(self.element_pattern) == list:
                # Here we assume that the elevation patterns are al the same because
                # we do not have an array in elevation, this could change in the future
                # but this is all complicated enough
                element_pattern = self.element_pattern[0]
                el_pat = element_pattern.func_e(sin_rang - sin_steer_rad,
                                                element_pattern.Le,
                                                self.f0,
                                                element_pattern.Ne,
                                                element_pattern.we,
                                                element_pattern.spacing_e,
                                                field=field,
                                                beamwidth=element_pattern.beamwidth_e,
                                                use_ne=use_ne)
        else:
            el_pat = None

        if self.type_e == "element":
                pat = el_pat
        else:
            pat = self.func_e(
                sin_rang - sin_steer_rad,
                self.Le,
                self.f0,
                self.Ne,
                self.we,
                self.spacing_e,
                field=field,
                beamwidth=self.beamwidth_e,
                use_ne=use_ne,
                el_pattern=el_pat,
            )
        if field:
            if self.el_offset != 0:
                # Add linear phase
                # Check sign!
                phase = self.k0 * self.el_offset * sin_rang
                pat = pat * np.exp(1j * phase)
            pat = pat.astype(np.complex64)
            xpat = pat * self.xpol2cpol
        else:
            xpat = pat * np.abs(self.xpol2cpol)**2
        return pat, xpat

    def azimuth(self, ang, field=True, squint_rad=None, use_ne=False):
        """Returns azimuth normalized pattern

        Parameters
        ----------
        ang :
            angle in radians
        field :
            return field if True, intensity if False (Default value = True)
        squint_rad :
            overides init squint. If it is a vector then
            it will be combined with ang, following numpy
            rules. So, this could be sued to calculate a
            stack of patterns with different squints, or
            to compute the pattern seen by a target in
            TOPS or Spotlight mode (Default value = None)
        use_ne :
            use numexpr to speed up (Default value = False)

        Returns
        -------

        """
        if squint_rad is None:
            squint = self.squint
        else:
            squint = squint_rad
        if use_ne:
            sin_ang = ne.evaluate("sin(ang)")
        else:
            sin_ang = np.sin(ang)
        pat_norm = 1
        wa_used = self.wa
        if type(self.element_pattern) == pattern:
            el_pat = self.element_pattern.func_a(ang,
                                                 self.element_pattern.La,
                                                 self.f0,
                                                 self.element_pattern.Na,
                                                 self.element_pattern.wa,
                                                 self.element_pattern.spacing_a,
                                                 field=True,
                                                 beamwidth=self.element_pattern.beamwidth_a,
                                                 sin_squint=np.sin(squint),
                                                 use_ne=use_ne)
        elif (type(self.element_pattern) == list
              and self.type_a in ['phased_array' , 'phased_spacedarray']):
            el_pat = []
            pat_norm = 1/self.g0
            wa_used = w2ww(self.Na, 1)
            for ind in range(len(self.element_pattern)):
                element_pattern = self.element_pattern[ind]
                el_pat_ = element_pattern.func_a(ang,
                                                 element_pattern.La,
                                                 self.f0,
                                                 element_pattern.Na,
                                                 element_pattern.wa,
                                                 element_pattern.spacing_a,
                                                 field=True,
                                                 beamwidth=element_pattern.beamwidth_a,
                                                 sin_squint=np.sin(squint),
                                                 use_ne=use_ne)
                # In the case of heterogeneous elements we need to consider their different gains
                # w_rel = np.sqrt(element_pattern.g0**2 / self.g0**2 * len(self.element_pattern))
                w_rel = element_pattern.g0 / self.g0 * self.wa.flatten()[ind]/np.max(np.abs(self.wa)) * np.sqrt(self.Na)
                #print(w_rel)
                #print(el_pat_.max())
                el_pat.append(w_rel * el_pat_)
        elif type(self.element_pattern) == list:
                # Here we assume that the elevation patterns are al the same because
                # we do not have an array in elevation, this could change in the future
                # but this is all complicated enough
                element_pattern = self.element_pattern[0]
                el_pat_ = element_pattern.func_a(ang,
                                                 element_pattern.La,
                                                 self.f0,
                                                 element_pattern.Na,
                                                 element_pattern.wa,
                                                 element_pattern.spacing_a,
                                                 field=True,
                                                 beamwidth=element_pattern.beamwidth_a,
                                                 sin_squint=np.sin(squint),
                                                 use_ne=use_ne)
        else:
            el_pat = None
        if self.type_a == "element":
            if type(el_pat) == list:
                pat = np.mean(np.array(el_pat), axis=0)
            else:
                pat = el_pat
        else:
            pat = self.func_a(
                ang,
                self.La,
                self.f0,
                self.Na,
                wa_used,
                self.spacing_a,
                field=field,
                beamwidth=self.beamwidth_a,
                sin_squint=np.sin(squint),
                use_ne=use_ne,
                el_pattern=el_pat,
            )
        if field:
            if self.az_offset != 0:
                phase = self.k0 * self.az_offset * sin_ang
                pat = pat * np.exp(1j * phase)
            pat = pat.astype(np.complex64)
            xpat = pat * self.xpol2cpol
        else:
            xpat = pat * np.abs(self.xpol2cpol)**2
        return pat, xpat

    def plot_azimuth(self, ang, squint_rad=None, vmin=-40):
        """Plots the normalized azimuth pattern

        Parameters
        ----------
        ang :
            angle in radians
        squint_rad :
            overides init squint. If it is a vector then
            it will be combined with ang, following numpy
            rules. So, this could be sued to calculate a
            stack of patterns with different squints, or
            to compute the pattern seen by a target in
            TOPS or Spotlight mode (Default value = None)
        vmin :
             (Default value = -40)

        Returns
        -------

        """
        apat = self.azimuth(ang, squint_rad=squint_rad)
        plt.figure()
        apatdb = 10 * np.log10(np.abs(apat[0]) ** 2)
        plt.plot(np.degrees(ang), apatdb)
        plt.xlabel("Azimuth angle [deg]")
        plt.title("One-way azimuth pattern")
        ax = plt.gca()
        ax.set_ylim((vmin, 6))
        ax.set_xlim((np.degrees(ang).min(), np.degrees(ang).max()))
        plt.grid(True)

    def pat_2D(
        self,
        el_ang,
        az_ang,
        field=True,
        grid=True,
        squint_rad=None,
        use_ne=False,
        steer_rad=None,
    ):
        """Returns normalized pattern for (elevation, azimuth)

        Parameters
        ----------
        el_ang :
            elevation angle in radians
        az_ang :
            azimuth angle in radians
        field :
            return field if True, intensity if False (Default value = True)
        squint_rad :
            overides init squint. If it is a vector then
            it will be combined with ang, following numpy
            rules. So, this could be sued to calculate a
            stack of patterns with different squints, or
            to compute the pattern seen by a target in
            TOPS or Spotlight mode (Default value = None)
        steer_rad :
            overrides init el0, behaves like squint_rad, but in elevation.
            we want this to do SCORE and things like that (Default value = None)
        use_ne :
            use numexpr to speed up (Default value = False)
        grid :
             (Default value = True)

        Returns
        -------

        """
        az, xaz = self.azimuth(
            az_ang, field=field, squint_rad=squint_rad, use_ne=use_ne
        )
        el, xel = self.elevation(
            el_ang, field=field, use_ne=use_ne, steer_rad=steer_rad
        )
        if grid:
            pat = az.reshape((az.size, 1)) * el.reshape((1, el.size))
            xpat = xaz.reshape((az.size, 1)) * xel.reshape((1, el.size))
        else:
            if use_ne:
                pat = ne.evaluate("az * el")
                xpat = ne.evaluate("xaz * xel")
            else:
                pat = az * el
                xpat = xaz * xel
        if field:
            return pat.astype(np.complex64), xpat.astype(np.complex64)
        else:
            return pat, xpat

    def Doppler2pattern(self, la_ref, fD, ghist, az_norm=False):
        """Compute azimuth pattern as a function of Doppler, taking into
            account the geom history

        Parameters
        ----------
        la_ref :
            look angle in antenna coordiantes
        fD :
            vector of Doppler frequencies
        ghist :
            drama.geo.geo_history.GeoHistory object
        az_norm :
             (Default value = False)

        Returns
        -------

        """
        t, u, v, _, _ = ghist.Doppler2tuv(la_ref, fD, self.f0, ant_ref=True)
        pat, xpat = self.pat_2D(v.T, u.T, grid=False)

        # Now we want to normalize them with respect to elevation cut
        if az_norm:
            elpat, elxpat = self.elevation(la_ref)
            return (
                pat / elpat.reshape((elpat.size, 1)),
                xpat / elxpat.reshape((elxpat.size, 1)),
            )
        else:
            return (pat, xpat)

    def Doppler2pat_interp(self, la_ref, Dla, fD, ghist):
        """Compute coefficients for quadratic interpolator w.r.t. to look
            angle within a region given by la_ref +/- dla of the azimuth
            pattern as a function of Doppler, taking into account the geom
            history

        Parameters
        ----------
        la_ref :
            vector of reference look angles, in antenna
            coordinates
        Dla :
            vector or single value giving the look_angle deviation
            around (each) reference look angle. If it is zero, then a value of
            0.1 radians is used instead (which should be irrelevant)
        fD :
            vector of Doppler frequencies
        ghist :
            drama.geo.geo_history.GeoHistory object

        Returns
        -------

        """
        # Some initial house keeping, and make sure that there are no zeros
        dla = np.array([Dla])  # just to be sure
        if dla.size == 1:
            # Make it a non-zero scalar
            dla = 0.1 if dla[0] == 0 else np.abs(dla[0])
        else:
            # Make it non-zero everywhere
            dla = np.where(dla != 0, np.abs(dla), 0.1)
            dla = dla.reshape((1, dla.size))  # or a column vector
        # Compute patterns reference look angle and at reference angles
        # +/- dla
        t, u, v, _, _ = ghist.Doppler2tuv(la_ref, fD, self.f0, ant_ref=True)
        pat_0, xpat_0 = self.pat_2D(v.T, u.T, grid=False)
        t, u, v, _, _ = ghist.Doppler2tuv(
            la_ref - Dla, fD, self.f0, ant_ref=True
        )
        pat_m1, xpat_m1 = self.pat_2D(v.T, u.T, grid=False)
        t, u, v, _, _ = ghist.Doppler2tuv(
            la_ref + Dla, fD, self.f0, ant_ref=True
        )
        pat_p1, xpat_p1 = self.pat_2D(v.T, u.T, grid=False)
        # The patterns will be expressed as a function of la and la_ref as
        # a(la_ref, fD) + b(la_ref, fD) * (la - la_ref) +
        # c(la_ref, fD) * (la - la_ref)**2
        #
        # So now we calculate these coefficients as
        # a = pat0
        # b = (pat_p1 - pat_m1) / (2 * Dla)
        # c = (pat_p1 - 2 * pat_0 + pat_m1) / (2 * Dla**2)
        pat_a = pat_0
        pat_b = (pat_p1 - pat_m1) / (2 * dla)
        pat_c = (pat_p1 - 2 * pat_0 + pat_m1) / (2 * (dla ** 2))
        xpat_a = xpat_0
        xpat_b = (xpat_p1 - xpat_m1) / (2 * dla)
        xpat_c = (xpat_p1 - 2 * xpat_0 + xpat_m1) / (2 * (dla ** 2))
        return ((pat_a, pat_b, pat_c), (xpat_a, xpat_b, xpat_c))


# %%

if __name__ == '__main__':
    pattern0 = pattern(5.4e9,
                       type_a="phased_array",
                       type_e="phased_array",
                       element_pattern=None,
                       La=3.16,
                       Le=1.0,
                       Nel_e=20,
                       Nel_a=4)
    patternc = pattern(5.4e9,
                      type_a="phased_array",
                      type_e="phased_array",
                      element_pattern=None,
                      La=2.4,
                      Le=1.0,
                      Nel_e=20,
                      Nel_a=3)
    pattern1 = pattern(5.4e9,
                       type_a="phased_array",
                       type_e="phased_array",
                       element_pattern=None,
                       La=10.0,
                       Le=1.0,
                       Nel_e=20,
                       Nel_a=10)
    pattern2 = pattern(5.4e9,
                       type_a="phased_spacedarray",
                       type_e="element",
                       element_pattern=[pattern0, patternc, pattern0],
                       spacing_a=4.5,
                       La=5.0,
                       Le=1.0,
                       Nel_e=1,
                       Nel_a=3, wa=[0.7, 1, 0.7])

    pattern3 = pattern(5.4e9,
                       type_a="phased_spacedarray",
                       type_e="element",
                       element_pattern=pattern0,
                       spacing_a=4.5,
                       La=5.0,
                       Le=1.0,
                       Nel_e=1,
                       Nel_a=2)

#%%
    az = np.linspace(-2,2,1000)
    plt.figure()
    pattern0.plot_azimuth(np.radians(az), squint_rad=np.radians(0.25))
    # plt.figure()
    # pattern1.plot_azimuth(np.radians(az), squint_rad=np.radians(0.5))
    plt.figure()
    pattern2.plot_azimuth(np.radians(az), squint_rad=np.radians(0.25))
    #plt.figure()
    pattern3.plot_azimuth(np.radians(az), squint_rad=np.radians(0.25))
    type(pattern3.element_pattern)

#%%
    el = np.linspace(-5,5,1000)
    plt.figure()
    plt.plot(el, 10*np.log10(np.abs(pattern0.elevation(np.radians(el), field=False))[0]))
    plt.grid(True)
    plt.figure()
    plt.plot(el, 10*np.log10(pattern1.elevation(np.radians(el), field=False)[0]))
    plt.grid(True)
    plt.figure()
    plt.plot(el, 10*np.log10(pattern2.elevation(np.radians(el), field=False)[0]))
    plt.grid(True)
    plt.figure()
    plt.plot(el, 10*np.log10(pattern3.elevation(np.radians(el), field=False)[0]))
    plt.grid(True)
