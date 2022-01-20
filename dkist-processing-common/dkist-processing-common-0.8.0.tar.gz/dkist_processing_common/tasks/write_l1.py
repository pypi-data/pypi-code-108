"""
Task(s) for writing level 1 data as 214 compliant fits files
"""
import importlib
import uuid
from abc import ABC
from abc import abstractmethod
from typing import Literal

import astropy.units as u
import numpy as np
from astropy.io import fits
from astropy.time import Time
from astropy.time import TimeDelta
from dkist_fits_specifications import __version__ as spec_version
from dkist_header_validator.translator import remove_extra_axis_keys
from dkist_header_validator.translator import sanitize_to_spec214_level1
from scipy.stats import kurtosis
from scipy.stats import skew
from sunpy.coordinates import HeliocentricInertial

from dkist_processing_common._util.dkist_location import location_of_dkist
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.parsers.l0_fits_access import L0FitsAccess
from dkist_processing_common.tasks import ScienceTaskL0ToL1Base


__all__ = ["WriteL1Frame"]


class WriteL1Frame(ScienceTaskL0ToL1Base, ABC):
    """
    This task converts final calibrated science frames into spec 214 compliant level 1 frames.
    It is intended to be subclassed as the dataset header table is instrument specific.
    """

    def run(self) -> None:
        for stokes_param in self.constants.stokes_params:
            with self.apm_step(f"Get calibrated frames for stokes param {stokes_param}"):
                calibrated_fits_objects = self.fits_data_read_fits_access(
                    tags=[Tag.frame(), Tag.calibrated(), Tag.stokes(stokes_param)],
                    cls=L0FitsAccess,
                    auto_squeeze=False,
                )
            with self.apm_step("Transform frames to SPEC 214 format"):
                for calibrated_fits_object in calibrated_fits_objects:
                    # Convert the headers to L1
                    l1_header = self.convert_l0_to_l1(
                        header=calibrated_fits_object.header,
                        data=calibrated_fits_object.data,
                        hdu_size=calibrated_fits_object.size,
                        stokes_param=stokes_param,
                    )

                    # Write frame to disk - compressed
                    hdu = fits.CompImageHDU(header=l1_header, data=calibrated_fits_object.data)
                    all_tags = self.tags(calibrated_fits_object.name)
                    all_tags.remove(Tag.calibrated())
                    self.fits_data_write(
                        hdu_list=fits.HDUList([fits.PrimaryHDU(), hdu]),
                        tags=[Tag.output()] + all_tags,
                        relative_path=self.l1_filename(header=l1_header, stokes=stokes_param),
                    )

    @staticmethod
    def _replace_header_values(header: fits.Header, data: np.ndarray) -> fits.Header:
        """
        Replace the FILE_ID and DATE keywords with new values
        """
        header["FILE_ID"] = uuid.uuid4().hex
        header["DATE"] = Time.now().fits
        # DATE-END = DATE-BEG + XPOSURE
        header["DATE-END"] = (
            Time(header["DATE-BEG"], format="isot")
            + TimeDelta(float(header["XPOSURE"]) / 1000, format="sec")
        ).to_value("isot")
        # Remove BZERO and BSCALE as their value should be recalculated by astropy upon fits write
        header.pop("BZERO", None)
        header.pop("BSCALE", None)
        # Make sure that NAXIS is set to the shape of the data in case of squeezing
        header["NAXIS"] = len(data.shape)
        return header

    @staticmethod
    def _add_stats_headers(header: fits.Header, data: np.ndarray) -> fits.Header:
        """
        Fill out the spec 214 statistics header table
        """
        data = data.flatten()
        percentiles = np.nanpercentile(data, [1, 10, 25, 75, 90, 95, 98, 99])
        header["DATAMIN"] = np.nanmin(data)
        header["DATAMAX"] = np.nanmax(data)
        header["DATAMEAN"] = np.nanmean(data)
        header["DATAMEDN"] = np.nanmedian(data)
        header["DATA01"] = percentiles[0]
        header["DATA10"] = percentiles[1]
        header["DATA25"] = percentiles[2]
        header["DATA75"] = percentiles[3]
        header["DATA90"] = percentiles[4]
        header["DATA95"] = percentiles[5]
        header["DATA98"] = percentiles[6]
        header["DATA99"] = percentiles[7]
        header["DATARMS"] = np.sqrt(np.nanmean(data ** 2))
        header["DATAKURT"] = kurtosis(data, nan_policy="omit")
        header["DATASKEW"] = skew(data, nan_policy="omit")
        return header

    def _add_datacenter_headers(
        self,
        header: fits.Header,
        data: np.ndarray,
        hdu_size: float,
        stokes: Literal["I", "Q", "U", "V"],
    ) -> fits.Header:
        """
        Fill out the spec 214 datacenter header table
        """
        header["DSETID"] = self.dataset_id
        header["POINT_ID"] = self.dataset_id
        header["FRAMEVOL"] = hdu_size / 1024 / 1024
        header["PROCTYPE"] = "L1"
        header["RRUNID"] = self.recipe_run_id
        header["RECIPEID"] = self.metadata_store_recipe_id
        header["RINSTID"] = self.metadata_store_recipe_instance_id
        header["EXTNAME"] = "observation"
        header["SOLARNET"] = 1
        header["OBS_HDU"] = 1
        header["FILENAME"] = self.l1_filename(header=header, stokes=stokes)
        # Cadence keywords
        header["CADENCE"] = self.constants.average_cadence
        header["CADMIN"] = self.constants.minimum_cadence
        header["CADMAX"] = self.constants.maximum_cadence
        header["CADVAR"] = self.constants.variance_cadence
        return header

    def _add_solarnet_headers(self, header: fits.Header) -> fits.Header:
        """
        Add headers recommended by solarnet that haven't already been added
        """
        header["DATE-AVG"] = self._calculate_date_avg(header=header)
        header["TELAPSE"] = self._calculate_telapse(header=header)
        header["DATEREF"] = header["DATE-BEG"]
        itrs = location_of_dkist()
        header["OBSGEO-X"] = itrs.x.to_value(unit=u.m)
        header["OBSGEO-Y"] = itrs.y.to_value(unit=u.m)
        header["OBSGEO-Z"] = itrs.z.to_value(unit=u.m)
        header["OBS_VR"] = (
            itrs.get_gcrs(obstime=Time(header["DATE-AVG"]))
            .transform_to(HeliocentricInertial(obstime=Time(header["DATE-AVG"])))
            .d_distance.to_value(unit=u.m / u.s)
        )  # relative velocity of observer with respect to the sun in m/s
        header["SPECSYS"] = "TOPOCENT"  # no wavelength correction made due to doppler velocity
        header["VELOSYS"] = False  # no wavelength correction made due to doppler velocity

        return header

    @staticmethod
    def l1_filename(header: fits.Header, stokes: Literal["I", "Q", "U", "V"]):
        """
        Use a FITS header to derive its filename in the format:
        instrument_L1_wavelength_datetime_stokes.fits

        Example
        -------
        "VISP_L1_01080000_2020_03_13T00_00_00_000_Q.fits"
        """
        instrument = header["INSTRUME"]
        wavelength = str(round(header["LINEWAV"] * 1000)).zfill(8)
        datetime = header["DATE-BEG"].replace("-", "_").replace(":", "_").replace(".", "_")
        return f"{instrument}_L1_{wavelength}_{datetime}_{stokes}.fits"

    @staticmethod
    def _calculate_date_avg(header: fits.Header) -> str:
        """
        Given the start and end datetimes of observations, return the datetime exactly between them
        """
        start_time = Time(header["DATE-BEG"], format="isot")
        end_time = Time(header["DATE-END"], format="isot")
        time_diff = end_time - start_time
        return (start_time + (time_diff / 2)).to_value("isot")

    @staticmethod
    def _calculate_telapse(header: fits.Header) -> float:
        """
        Given the start and end time of observation, calculate the time elapsed, in seconds
        """
        start_time = Time(header["DATE-BEG"], format="isot").to_value("mjd")
        end_time = Time(header["DATE-END"], format="isot").to_value("mjd")
        return (end_time - start_time) * 86400  # seconds in a day

    def convert_l0_to_l1(
        self,
        header: fits.Header,
        data: np.ndarray,
        hdu_size: float,
        stokes_param: Literal["I", "Q", "U", "V"],
    ) -> fits.Header:
        """
        Run through the steps needed to convert a L0 header into a L1 header
        """
        # Replace header values in place
        header = self._replace_header_values(header=header, data=data)
        # Add the stats table
        header = self._add_stats_headers(header=header, data=data)
        # Add the datacenter table
        header = self._add_datacenter_headers(
            header=header, data=data, hdu_size=hdu_size, stokes=stokes_param
        )
        # Add extra headers recommended by solarnet (not all in a single table)
        header = self._add_solarnet_headers(header=header)
        # Add the documentation headers
        header = self._add_doc_headers(header=header)
        # Add the dataset headers (abstract - implement in instrument task)
        header = self.add_dataset_headers(header=header, stokes=stokes_param)
        # Remove any headers not contained in spec 214
        header = sanitize_to_spec214_level1(input_headers=header)
        # Remove any keys referring to axes that don't exist
        header = remove_extra_axis_keys(input_headers=header)
        return header

    def _add_doc_headers(self, header: fits.Header) -> fits.Header:
        """
        Add URLs to the headers that point to the correct versions of documents in our public documentation

        Values follow these rules:
            1. header['INFO_URL']:
                The main documentation site: docs.dkist.nso.edu
            2. header['HEADVERS']:
                The version of the DKIST FITS specs used for this calibration:
                dkist_fits_specifications.__version__
            3. header['HEAD_URL']:
                The URL for the documentation of this version of the DKIST fits specifications:
                docs.dkist.nso.edu/projects/data-products/en/v<version> where <version> is header['HEADVERS']
            4. header['CALVERS']:
                The version of the calibration codes used for this calibration
                dkist_processing_<instrument>.__version__
                <instrument> is available as self.constants.instrument
            5. header['CAL_URL']:
                The URL for documentation of this version of the calibration codes for the current instrument:
                docs.dkist.nso.edu/projects/<instrument>/en/v<version>
        """
        header["INFO_URL"] = self.docs_base_url
        header["HEADVERS"] = spec_version
        header["HEAD_URL"] = f"{self.docs_base_url}/projects/data-products/en/v{spec_version}"
        inst_name = self.constants.instrument.lower()
        calvers = self._get_version_from_module_name()
        header["CALVERS"] = calvers
        header["CAL_URL"] = f"{self.docs_base_url}/projects/{inst_name}/en/v{calvers}"
        return header

    def _get_version_from_module_name(self) -> str:
        """
        Get the value of __version__ from a module given its name

        Parameters
        ----------
        module_name

        Returns
        -------
        The value of __version__
        """
        package = self.__module__.split(".")[0]
        module = importlib.import_module(package)
        return module.__version__

    @abstractmethod
    def add_dataset_headers(
        self, header: fits.Header, stokes: Literal["I", "Q", "U", "V"]
    ) -> fits.Header:
        """
        This method will be written in the instrument repos. Construction of the dataset object
        is instrument, or possibly instrument mode specific.
        """
