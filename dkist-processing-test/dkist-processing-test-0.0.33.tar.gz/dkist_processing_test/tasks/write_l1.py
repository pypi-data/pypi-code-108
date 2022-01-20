from typing import Literal

from astropy.io import fits
from dkist_processing_common.tasks.write_l1 import WriteL1Frame


class WriteL1Data(WriteL1Frame):
    def add_dataset_headers(
        self, header: fits.Header, stokes: Literal["I", "Q", "U", "V"]
    ) -> fits.Header:
        header["DAAXES"] = 2
        header["DEAXES"] = 1
        header["DNAXIS"] = 3
        header["LEVEL"] = 1
        header["WAVEMAX"] = 124
        header["WAVEMIN"] = 123
        header["WAVEREF"] = "Air"
        header["WAVEUNIT"] = -9
        header["DINDEX3"] = 3
        header["DNAXIS1"] = header["NAXIS1"]
        header["DNAXIS2"] = header["NAXIS2"]
        header["DNAXIS3"] = 10
        header["DPNAME1"] = "spatial x"
        header["DPNAME2"] = "spatial y"
        header["DPNAME3"] = "frame number"
        header["DTYPE1"] = "SPATIAL"
        header["DTYPE2"] = "SPATIAL"
        header["DTYPE3"] = "TEMPORAL"
        header["DUNIT1"] = "arcsec"
        header["DUNIT2"] = "arcsec"
        header["DUNIT3"] = "s"
        header["DWNAME1"] = "helioprojective longitude"
        header["DWNAME2"] = "helioprojective latitude"
        header["DWNAME3"] = "time"
        header["NBIN"] = 1
        for i in range(1, header["NAXIS"] + 1):
            header[f"NBIN{i}"] = 1

        return header
