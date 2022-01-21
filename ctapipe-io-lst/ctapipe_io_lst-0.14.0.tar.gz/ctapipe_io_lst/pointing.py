from ctapipe.core import TelescopeComponent
from ctapipe.core.traits import Path, TelescopeParameter
from astropy.table import Table
from astropy import units as u
from scipy.interpolate import interp1d
from ctapipe.containers import TelescopePointingContainer
import numpy as np


__all__ = [
    'PointingSource'
]

NAN_ANGLE = np.nan * u.deg


class PointingSource(TelescopeComponent):
    """Provides access to pointing information stored in LST drive reports."""
    drive_report_path = TelescopeParameter(
        trait=Path(exists=True, directory_ok=False, allow_none=True),
        help='Path to the LST drive report file',
        default_value=None,
    ).tag(config=True)

    def __init__(self, subarray, config=None, parent=None, **kwargs):
        '''Initialize PointingSource'''

        super().__init__(subarray, config=config, parent=parent, **kwargs)
        self.drive_report = {}
        self.interp_az = {}
        self.interp_alt = {}
        self.interp_ra = {}
        self.interp_dec = {}

    @staticmethod
    def _read_drive_report(path):
        """
        Read a drive report into an astropy table

        Parameters:
        -----------
        str: drive report file

        Returns:
        data:`~astropy.table.Table`
             A table of drive reports

        """
        data = Table.read(
            path, format='ascii', delimiter=' ',
            header_start=None,
            data_start=0,
            names=[
                'weekday', 'month', 'day', 'time', 'year', 'unix_time',
                'Az', 'azimuth_avg', 'azimuth_min', 'azimuth_max', 'azimuth_std',
                'El', 'zenith_avg', 'zenith_min', 'zenith_max', 'zenith_std',
                'Ra', 'target_ra', 'Dec', 'target_dec',
            ]
        )
        return data

    def _read_drive_report_for_tel(self, tel_id):
        path = self.drive_report_path.tel[tel_id]
        if path is None:
            raise ValueError(f'No drive report given for telescope {tel_id}')

        self.log.info(f'Loading drive report "{path}" for tel_id={tel_id}')
        self.drive_report[tel_id] = self._read_drive_report(path)

        self.interp_az[tel_id] = interp1d(
            self.drive_report[tel_id]['unix_time'],
            self.drive_report[tel_id]['azimuth_avg'],
        )
        self.interp_alt[tel_id] = interp1d(
            self.drive_report[tel_id]['unix_time'],
            90 - self.drive_report[tel_id]['zenith_avg'],
        )

        self.interp_ra[tel_id] = interp1d(
            self.drive_report[tel_id]['unix_time'],
            self.drive_report[tel_id]['target_ra'],
        )
        self.interp_dec[tel_id] = interp1d(
            self.drive_report[tel_id]['unix_time'],
            self.drive_report[tel_id]['target_dec'],
        )

    def get_pointing_position_altaz(self, tel_id, time):
        """
        Calculating pointing positions by interpolation

        Parameters:
        -----------
        time: array
            times from events

        Drivereport: Container
            a container filled with drive information
        """
        if tel_id not in self.drive_report:
            self._read_drive_report_for_tel(tel_id)

        alt = u.Quantity(self.interp_alt[tel_id](time.unix), u.deg)
        az = u.Quantity(self.interp_az[tel_id](time.unix), u.deg)

        return TelescopePointingContainer(
            altitude=alt.to(u.rad),
            azimuth=az.to(u.rad),
        )

    def get_pointing_position_icrs(self, tel_id, time):
        if tel_id not in self.drive_report:
            self._read_drive_report_for_tel(tel_id)

        ra = u.Quantity(self.interp_ra[tel_id](time.unix), u.deg)
        dec = u.Quantity(self.interp_dec[tel_id](time.unix), u.deg)

        # drive reports contain 0 / 0 if not tracking ICRS coordinates
        # TODO: hope we never really observe ra=0°, dec=0°
        if ra != 0.0 and dec != 0.0:
            return ra, dec

        return NAN_ANGLE, NAN_ANGLE
