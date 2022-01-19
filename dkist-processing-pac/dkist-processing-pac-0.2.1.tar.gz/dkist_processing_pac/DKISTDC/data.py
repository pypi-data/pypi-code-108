import numpy as np
from astropy.time import Time

from dkist_processing_pac.Data import Drawer
from dkist_processing_common.parsers.l0_fits_access import L0FitsAccess
from typing import List, Dict

from dkist_processing_pac.data import CONSTANTS
from dkist_processing_pac.tag import tag


class DCDrawer(Drawer):

    def __init__(self, fits_access_dict, skip_darks=True, remove_I_trend=True):
        super().__init__(data_dir=None, suffix='', remove_I_trend=False)
        self.fits_access_dict = dict()
        self.load_from_dict_of_objects(fits_access_dict, skip_darks=skip_darks)
        if remove_I_trend:
            self.find_clears()
            self.fit_intensity_trend()
        self.data_list = self.fits_access_dict

    def load_from_dict_of_objects(self, raw_fits_access: Dict[int, List[L0FitsAccess]],
                                  skip_darks=True):
        """Load all images found in a given directory. Data are stored as a list of astropy.io.fits HDUList objects.

        In addition to loading the actual data, header values are also inspected to create vectors of the polarizer and
        retarder angles, telescope geometry, and observation times.

        skip_darks : bool
            If True (default) then don't load any dark steps from the CS
        """
        inst_set = set()
        nummod_set = set()
        wave_set = set()
        ip_start_set = set()
        ip_end_set = set()
        final_step_num = 0
        for cs_step in sorted(raw_fits_access.keys()):
            meta_obj = raw_fits_access[cs_step][0]
            if meta_obj.gos_level0_status == 'DarkShutter' and skip_darks:
                continue

            inst_set.add(meta_obj.instrument)
            wave_set.add(meta_obj.wavelength)
            ip_start_set.add(meta_obj.ip_start_time)
            ip_end_set.add(meta_obj.ip_end_time)

            self.azimuth = np.append(self.azimuth, meta_obj.azimuth)
            self.elevation = np.append(self.elevation, meta_obj.elevation)
            self.table_angle = np.append(self.table_angle, meta_obj.table_angle)

            self.theta_pol_steps = np.append(self.theta_pol_steps, float(meta_obj.gos_polarizer_angle))
            self.theta_ret_steps = np.append(self.theta_ret_steps, float(meta_obj.gos_retarder_angle))
            self.pol_in = np.append(self.pol_in, meta_obj.gos_polarizer_status not in ['undefined', 'clear', False])
            self.ret_in = np.append(self.ret_in, meta_obj.gos_retarder_status not in ['undefined', 'clear', False])
            self.dark_in = np.append(self.dark_in, meta_obj.gos_level0_status == 'DarkShutter')

            self.timeobs = np.append(self.timeobs, Time(meta_obj.time_obs).mjd)
            nummod_set.add(meta_obj.number_of_modulator_states)
            self.fits_access_dict[final_step_num] = raw_fits_access[cs_step]  # So the index is still correct after skipping darks
            final_step_num += 1

        if len(nummod_set) > 1:
            raise ValueError('Not all input files have the same number of modulator states')
        self.nummod = nummod_set.pop()

        if len(inst_set) > 1:
            raise ValueError('Data belong to more than one instrument')
        self.instrument = inst_set.pop()

        if len(wave_set) > 1:
            raise ValueError('Data have more than one wavelength')
        self.wavelength = wave_set.pop()

        if len(ip_start_set) > 1 or len(ip_end_set) > 1:
            raise ValueError("Data don't all have the same IP start/end times")
        self.date_bgn = Time(ip_start_set.pop(), format='fits').mjd
        self.date_end = Time(ip_end_set.pop(), format="fits").mjd

        # TODO: Make this match Data (probably by changing Data???)
        # noise_floor_dict = CONSTANTS['Fallback_noise_floors']
        self.RN = 0.0

        self.numsteps = len(self.fits_access_dict.keys())

    def __getitem__(self, item):
        """This builtin method provides the mechanism by which the object can be sliced to provided a single SoCC.

        The slice must have two elements (x, y, l). E.g.:

        >>> I = DRWR[x, y, l]

        Parameters
        ----------
        item : tuple
            The (x, y, l) position tuple. Don't worry, python's slicing syntax will take care of this for you.

        Returns
        -------
        numpy.ndarray
            A 2D array of shape (M, N) where M is the number of modulator states and N is the number of steps in the
            Calibration Sequence.

        """
        if type(item) is not tuple or len(item) != 3:
            raise IndexError('Drawer must be indexed by exactly three values')

        xpos, ypos, lpos = item

        if not np.issubdtype(type(xpos), np.integer) \
                or not np.issubdtype(type(ypos), np.integer) \
                or not np.issubdtype(type(lpos), np.integer):
            raise IndexError('Only integers are allowed as valid indices')

        result = np.zeros((self.nummod, self.numsteps), dtype=np.float64)

        for n in range(self.numsteps):
            obj_list = self.fits_access_dict[n]
            modnum_list = [h.modulator_state for h in self.fits_access_dict[n]]
            for m in range(self.nummod):
                idx = modnum_list.index(m + 1)
                result[m, n] = obj_list[idx].data[xpos, ypos, lpos] / self.norm_func(self.timeobs[n])

        return result

    @property
    def shape(self):
        """The shape of this objects 'data'.

        This is useful for those who will be using the slicing functionality and expect to be able to see the shape of
        these data.
        """
        data = self.fits_access_dict[0][0].data

        return data.shape

    def find_clears(self):
        """Identify which HDUList objects contain clear observations and populate self.clear_objs

        A clear frame is defined as one in which both the polarizer and retarder were out of the light path.
        """
        clear_objs = []
        clear_times = np.array([])
        for n in range(self.numsteps):
            if not self.pol_in[n] and not self.ret_in[n] and not self.dark_in[n]:
                clear_objs.append(self.fits_access_dict[n])
                clear_times = np.append(clear_times, self.timeobs[n])

        self.clear_objs = clear_objs
        self.clear_times = clear_times

    def fit_intensity_trend(self):
        """Use clear frames to fit and remove any global intensity trends.

        The flux in each clear is averaged over all modulation states and the set of all clears is used to fit a linear
        trend of flux vs time. This line is then divided from all data, including clears.

        Note that because the absolute offset (i.e., intercept) is also fit the overall intensity is normalized by
        something very close to the flux in the first clear measurement.
        """
        try:
            avg_clear_flux = np.zeros(len(self.clear_objs))
        except AttributeError:
            print('{}: WARNING: clear frames have not yet been identified. Use .find_clears() to do so'.format(tag()))
            return
        if len(self.clear_objs) == 0:
            print('{}: WARNING: this Drawer does not contain any clear measurements. No correction is possible.'.format(tag()))
            return

        # First, get the linear trend in clear intensity
        for n in range(len(self.clear_objs)):
            tmp = 0.
            for j in range(self.nummod):
                tmp += np.nanmean(self.clear_objs[n][j].data)
            avg_clear_flux[n] = tmp / self.nummod

        self.I_clear = np.mean(avg_clear_flux)
        print('{}: Average flux in clear measurements (I_clear): {:<10.3f}'.format(tag(), self.I_clear))
        if self.I_clear < CONSTANTS['min_clear_flux']:
            raise ValueError('Flux in Clear measurements is too low ({:.2f} < {:.2f})'.format(self.I_clear,
                                                                                              CONSTANTS['min_clear_flux']))
        fit = np.poly1d(np.polyfit(self.clear_times, avg_clear_flux, 1)) / self.I_clear
        self.norm_func = fit
