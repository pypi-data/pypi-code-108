import time
import warnings
import numpy as np
from astropy.io import fits as pyfits
from astropy.time import Time
import scipy.interpolate as spi
from scipy.spatial.qhull import QhullError
from dkist_processing_pac import Data, generic
from dkist_processing_pac.tag import tag

warnings.simplefilter('always', UserWarning)
ATOL = 1e-6
RTOL = 1e-6


class TelescopeModel():
    """Build up the Mueller matrix of the full "Telescope Model" for use in PA&C analysis. As detailed in the DKIST
    PolCal Plan this model is parametrized by 3 mirror groups (M12, M34, M56) and the rotation matrices between them.
    The mirror Mueller matrices are calculated in real time from the parameters x (the ration of reflectivity between
    light parallel and perpendicular to the plane of incidence) and \tau (the retardance). The rotation matrices are
    also calculated in real time based on the (alt, az, coude_table) angles of DKIST.

    Each of the matrices in the Telescope Model are individually accessible as properties of the class
    (e.g. TelescopeModel.M34) and the full model exists in the .TM property. Note that the Telescope Model does NOT
    include the M12 group, but that group's Mueller matrix is still included in this object.

    Because each component of the model is recomputed each time it is queried this class lends itself well to iterative
    fitting.

    Attributes
    (only those you might need)
    ----------
    TM : numpy.ndarray
        Set of Mueller matrices for the entire telescope model. Shape (N, 4, 4)

    M12 : numpy.ndarray
        Mueller matrix of the M12 group. Shape (4, 4)

    R23 : numpy.ndarray
        Mueller matrix for rotation between M2 and M3. Shape (4, 4)

    M34 : numpy.ndarray
        Mueller matrix of the M34 group. Shape (4, 4)

    R45 : numpy.ndarray
        Mueller matrix for rotation between M4 and M5. Shape (N, 4, 4)

    M56 : numpy.ndarray
        Mueller matrix of the M56 group. Shape (4, 4)

    numsteps : int
        Number of steps in a Calibration Sequence (N)
    """

    def __init__(self, azimuth, elevation, table_angle):
        """Initialize the class with a sequence of telescope geometries.

        If the inputs are array-like then each entry is assumed to correspond to an individual step in the calibration
        sequence.

        Parameters
        ----------
        azimuth : float or array-like
            Telescope azimuth angle (in degrees)

        elevation : float or array-like
            Telescope elevation angle (in degrees)

        table_angle : float or array-like
            Angle (in degrees) of coude table
        """
        self.x12 = 1.07
        self.t12 = np.pi
        self.x34 = 1.07
        self.t34 = np.pi
        self.x56 = 1.07
        self.t56 = np.pi
        self.elevation = np.atleast_1d(elevation) * np.pi / 180
        self.azimuth = np.atleast_1d(azimuth) * np.pi / 180
        self.table_angle = np.atleast_1d(table_angle) * np.pi / 180

        if self.elevation.shape != self.azimuth.shape or self.elevation.shape != self.table_angle.shape:
            raise ValueError('Telescope geometry vectors do not have the same shape')

        self.numsteps = self.elevation.size

        self.wavelength = None
        self.obstime = None

    def __add__(self, other):
        """Concatenate two Telescope Models together.

        Returns
        -------
        TelescopeModel
            A new TelescopeModel object
        """
        output = TelescopeModel(np.append(self.azimuth, other.azimuth) * 180 / np.pi,
                                np.append(self.elevation, other.elevation) * 180 / np.pi,
                                np.append(self.table_angle, other.table_angle) * 180 / np.pi)

        return output

    def load_from_database(self, db_file, obstime, obswave, method='linear'):
        """Update (x, t) mirror parameters based on a database of previous measurements.

        Given a date and wavelength, the closest set of parameters is found via interpolation. The default is to use
        linear interpolation, but cubic interpolation can be requested via the `method` parameter.

        If the supplied time or wavelength is outside of the parameter space covered by the database then the values
        are set to the closest (time, wave) coordinate rather than extrapolating.

        Parameters
        ----------
        db_file : str
            The path to the database file (see Notes)

        obstime : float
            The time at which to interpolate the parameters. Format is MJD.

        obswave : float
            The wavelength at which to interpolate the parameters (nm)

        method : str
            The interpolation method to use. Can be either 'nearest', 'linear' (default), or 'cubic'

        Notes
        -----
        Currently the database is simply a space-delimited text file with the following columns:

            MJD wavelength x12 t12 x34 t34 x56 t56

        """
        times, wave, x12, t12, x34, t34, x56, t56 = np.loadtxt(db_file, unpack=True)
        print(f"{tag()}: Loading database parameters from {db_file} for {obswave} at {Time(obstime, format='mjd').fits}")

        for source, target in zip([x12, t12, x34, t34, x56, t56],
                                  ['x12', 't12', 'x34', 't34', 'x56', 't56']):

            try:
                value = float(spi.griddata((times, wave), source, (obstime, obswave), method=method))
            except QhullError:
                warnings.warn('Telescope database lacks diversity along either time or wavelength axis. '
                              'Reverting to nearest neighbor interpolation.')
                value = float(spi.griddata((times, wave), source, (obstime, obswave), method='nearest'))


            # griddata returns NaN if out of range
            if np.isnan(value):
                warnings.warn(
                        'Requested time/wavelength is outside of the Telescope Database range, using the nearest '
                        'in-bounds value')
                value = float(spi.griddata((times, wave), source, (obstime, obswave), method='nearest'))

            setattr(self, target, value)
            
        self.wavelength = obswave
        self.obstime = obstime
        print('{:}: loaded (x12, t12, x34, t34, x56, t56) = ({:.5f}, {:.5f}, {:.5f}, {:.5f}, {:.5f}, {:.5f}) at {:} nm'.format(tag(),
                                                                                                                               self.x12,
                                                                                                                               self.t12,
                                                                                                                               self.x34,
                                                                                                                               self.t34,
                                                                                                                               self.x56,
                                                                                                                               self.t56,
                                                                                                                               self.wavelength))

    def save_to_database(self, db_file, obstime=None, obswave=None):
        """Update the telescope database with the current class telescope mirror parameters.

        If the wavelength and time are not set in the class they must be passed explicitly.

        Parameters
        ----------
        db_file : str
            Path to parameter database. See notes for load_from_database for information on the format of this file.

        obstime : float
            The time of the current observation, in MJD. Can also be 'now' to use the current system time.

        obswave : float
            The wavelength (nm) of the current observation.
        """
        if obstime == 'now':
            new_time = Time(time.time(), format='unix').mjd
        elif obstime is None:
            if self.obstime is None:
                raise ValueError('Obstime was not set in the Telescope Model nor specified explicitly')
            else:
                new_time = self.obstime
        else:
            new_time = obstime

        if obswave is None:
            if self.wavelength is None:
                raise ValueError('Wavelength was not set in the Telescope Model nor specified explicitly')
            else:
                new_wave = self.wavelength
        else:
            new_wave = obswave

        with open(db_file, 'a') as f:
            f.write(str('{:15.6f}' + '{:8.2f}' + '{:7.3f}' * 6 + '\n').format(new_time,
                                                                              new_wave,
                                                                              self.x12,
                                                                              self.t12,
                                                                              self.x34,
                                                                              self.t34,
                                                                              self.x56,
                                                                              self.t56))

    def save_FITS(self, outputfile, overwrite=False):
        """Save a FITS file with the M3 - M7 Mueller matrix and M12 Muller matrix as separate HDUs.

        It's not immediately obvious why this method is useful. Wouldn't it make more sense to just load the object
        itself and use the associated properties? You're going to need to load the object anyway to enter the correct
        telescope geometry.
        """

        if self.numsteps > 1:
            warnings.warn('Multiple telescope geometries found. Only using the first configuration')

        primary = pyfits.PrimaryHDU()
        primary.header['TAZIMUTH'] = self.azimuth[0]
        primary.header['TELEVATN'] = self.elevation[0]
        primary.header['TTBLANGL'] = self.table_angle[0]
        primary.header['X12'] = self.x12
        primary.header['T12'] = self.t12
        primary.header['X34'] = self.x34
        primary.header['T34'] = self.t34
        primary.header['X56'] = self.x56
        primary.header['T56'] = self.t56

        tm = pyfits.ImageHDU(self.TM[0, :, :])
        tm.header['NAME'] = ('TM', 'Mueller matrix for mirrors 3-6')

        m12 = pyfits.ImageHDU(self.M12)
        m12.header['NAME'] = ('M12', 'Mueller matrix for M12 group')

        pyfits.HDUList([primary, tm, m12]).writeto(outputfile, overwrite=overwrite)

    def generate_inverse_telescope_model(self, M12=True, include_parallactic=True):
        """Produce the inverse of the full Telescope Model's Mueller matrix.

        The user can choose to include M12 as part of the Telescope Model, in which case the inverse will capture all
        polarization effects between the DKIST entrance aperture and M7.

        If, for whatever reason, the generated inverse does not satisfy T int(T) = inv(T) T = Identity then an error
        will be raised.

        Parameters
        ----------
        M12 : bool
            If True then include M12 in the Telescope Model

        include_parallactic : bool
            If True then the final rotation from DKIST to Solar reference frame will be included in the output matrix

        Returns
        -------
        numpy.ndarray
            The (4, 4) inverse Mueller matrix of the Telescope Model.
        """
        full_model = self.TM

        if M12:
            full_model = full_model @ self.M12

        if full_model.shape[0] > 1:
            warnings.warn('Multiple telescope geometries found. Only using the first configuration')

        inverse = np.linalg.inv(full_model[0, :, :])

        if not (np.allclose(np.diag(np.ones(4)), inverse @ full_model[0], rtol=RTOL, atol=ATOL) and
                np.allclose(np.diag(np.ones(4)), full_model[0] @ inverse, rtol=RTOL, atol=ATOL)):
            raise ArithmeticError('The generated inverse is not mathematically valid')

        if include_parallactic:
            time = Time(self.obstime, format='mjd')
            p_rot = Data.rotation(-1 * generic.compute_parallactic_angle(time))
            inverse = p_rot @ inverse

        return inverse

    @property
    def M12(self):
        """The M12 mirror Mueller matrix"""
        return Data.mirror(self.x12, self.t12)

    @property
    def M34(self):
        """The M34 mirror Mueller matrix"""
        return Data.mirror(self.x34, self.t34)

    @property
    def M56(self):
        """The M56 mirror Mueller matrix"""
        return Data.mirror(self.x56, self.t56)

    @property
    def R23(self):
        """The rotation matrix between M2 and M3. This is always the same, so it doesn't have a step dimension

        Returns
        -------
        numpy.ndarray
            Array of shape (4, 4)
        """
        return Data.rotation(-np.pi / 2.)

    @property
    def R45(self):
        """The rotation matrix between M4 and M5

        Returns
        -------
        numpy.ndarray
            Array of shape (N, 4, 4)
        """

        Rarr = np.empty((self.numsteps, 4, 4), dtype=np.float64)
        for i in range(self.numsteps):
            Rarr[i, :, :] = Data.rotation(-1 * self.elevation[i])

        return Rarr

    @property
    def R67(self):
        """The rotation matrix between M6 and M7

        Returns
        -------
        numpy.ndarray
            Array of shape (N, 4, 4)
        """

        Rarr = np.empty((self.numsteps, 4, 4), dtype=np.float64)
        for i in range(self.numsteps):
            theta = self.azimuth[i] - self.table_angle[i] + np.pi / 2.
            Rarr[i, :, :] = Data.rotation(theta)

        return Rarr

    @property
    def TM(self):
        """The completed Telescope Model

        Returns
        -------
        numpy.ndarray
            Array of shape (N, 4, 4)
        """
        return self.R67 @ self.M56 @ self.R45 @ self.M34 @ self.R23
