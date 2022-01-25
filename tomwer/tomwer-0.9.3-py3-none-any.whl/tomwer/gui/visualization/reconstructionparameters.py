# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2017 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "31/03/2021"


from silx.gui import qt
from silx.io.url import DataUrl
from silx.io.utils import h5py_read_dataset
from tomwer.core.utils.char import BETA_CHAR, DELTA_CHAR
from tomoscan.io import HDF5File
import os


class ReconstructionParameters(qt.QWidget):
    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QFormLayout())
        # method
        self._methodQLE = qt.QLineEdit("", self)
        self.layout().addRow("method", self._methodQLE)
        # paganin
        self._paganinCB = qt.QCheckBox("", self)
        self._paganinCB.setEnabled(False)
        self.layout().addRow("Paganin", self._paganinCB)
        # delta beta
        self._deltaBetaQLE = qt.QLineEdit("", self)
        self._deltaBetaQLE.setReadOnly(True)
        self.layout().addRow(" / ".join((DELTA_CHAR, BETA_CHAR)), self._deltaBetaQLE)
        # distance
        self._distanceQLE = qt.QLineEdit("", self)
        self._distanceQLE.setReadOnly(True)
        self.layout().addRow("distance (cm)", self._distanceQLE)
        # pixel size
        self._pixelSizeQLE = qt.QLineEdit("", self)
        self._pixelSizeQLE.setReadOnly(True)
        self.layout().addRow("pixel size (cm)", self._pixelSizeQLE)
        # cor
        self._corQLE = qt.QLineEdit("", self)
        self._corQLE.setReadOnly(True)
        self.layout().addRow("cor (absolute)", self._corQLE)
        # padding type
        self._paddingTypeQLE = qt.QLineEdit("", self)
        self._paddingTypeQLE.setReadOnly(True)
        self.layout().addRow("padding type", self._paddingTypeQLE)
        # half tomo
        self._halfTomoCB = qt.QCheckBox("", self)
        self._halfTomoCB.setEnabled(False)
        self.layout().addRow("half tomo", self._halfTomoCB)
        # fbp filter type
        self._fbpFilterQLE = qt.QLineEdit("", self)
        self._fbpFilterQLE.setReadOnly(True)
        self.layout().addRow("fbp filter", self._fbpFilterQLE)
        # log min clip
        self._minLogClipQLE = qt.QLineEdit("", self)
        self._minLogClipQLE.setReadOnly(True)
        self.layout().addRow("log min clip", self._minLogClipQLE)
        # log max clip
        self._maxLogClipQLE = qt.QLineEdit("", self)
        self._maxLogClipQLE.setReadOnly(True)
        self.layout().addRow("log max clip", self._maxLogClipQLE)
        # software version
        self._softwareVersionQLE = qt.QLabel("", self)
        self.layout().addRow("software version", self._softwareVersionQLE)

    def setUrl(self, url):
        if isinstance(url, DataUrl):
            pass
        elif isinstance(url, str):
            url = DataUrl(path=url)
        else:
            raise TypeError(
                "url should be a DataUrl or a str representing"
                "an url and not {}".format(type(url))
            )
        for func in (
            self._setMethod,
            self._setPaganin,
            self._setDeltaBeta,
            self._setDistance,
            self._setPixelSize,
            self._setCor,
            self._setPaddingType,
            self._setHalfTomo,
            self._setFBPFilter,
            self._setMinLogClip,
            self._setMaxLogClip,
            self._setSoftwareVersion,
        ):
            func(url)

    @staticmethod
    def _decode_nabu_str(input):
        if hasattr(input, "decode"):
            input = input.decode("UTF-8")
        return input

    def _setMethod(self, url):
        def get_method_value():
            _NABU_METHOD_URL = "../../configuration/nabu_config/reconstruction/method"
            with HDF5File(url.file_path(), "r") as h5s:
                data_path = url.data_path()
                method_path = os.path.normpath("/".join((data_path, _NABU_METHOD_URL)))
                if method_path in h5s:
                    return h5py_read_dataset(h5s[method_path])
                else:
                    return None

        value = self._decode_nabu_str(get_method_value())
        self._methodQLE.setText(value if value is not None else "")

    def _setPaganin(self, url):
        def is_phase_defined():
            _NABU_PHASE_URL = "../../configuration/nabu_config/phase"
            with HDF5File(url.file_path(), "r") as h5s:
                data_path = url.data_path()
                phase_path = os.path.normpath("/".join((data_path, _NABU_PHASE_URL)))
                if phase_path in h5s and "method" in h5s[phase_path]:
                    method_dataset = h5py_read_dataset(h5s[phase_path]["method"])
                    return method_dataset == "paganin"
                else:
                    return False

        self._paganinCB.setChecked(is_phase_defined())

    def _setDeltaBeta(self, url):
        def get_delta_beta_value():
            _NABU_DELTA_BETA_URL = "../../configuration/nabu_config/phase/delta_beta"
            with HDF5File(url.file_path(), "r") as h5s:
                data_path = url.data_path()
                delta_beta_path = os.path.normpath(
                    "/".join((data_path, _NABU_DELTA_BETA_URL))
                )
                if delta_beta_path in h5s:
                    return h5py_read_dataset(h5s[delta_beta_path])
                else:
                    return None

        value = self._decode_nabu_str(get_delta_beta_value())
        self._deltaBetaQLE.setText(str(value) if value is not None else "")

    def _setDistance(self, url):
        def get_distance_value():
            _NABU_DISTANCE_URL = (
                "../../configuration/processing_options/phase/distance_cm"
            )
            with HDF5File(url.file_path(), "r") as h5s:
                data_path = url.data_path()
                distance_path = os.path.normpath(
                    "/".join((data_path, _NABU_DISTANCE_URL))
                )
                if distance_path in h5s:
                    return h5py_read_dataset(h5s[distance_path])
                else:
                    return None

        value = self._decode_nabu_str(get_distance_value())
        if value is not None:
            value = "{:.2}".format(float(value))
        self._distanceQLE.setText(value if value is not None else "")

    def _setPixelSize(self, url):
        def get_pixel_size_value():
            _NABU_PIXEL_SIZE_URL = (
                "../../configuration/processing_options/reconstruction/pixel_size_cm"
            )
            with HDF5File(url.file_path(), "r") as h5s:
                data_path = url.data_path()
                pixel_size_path = os.path.normpath(
                    "/".join((data_path, _NABU_PIXEL_SIZE_URL))
                )
                if pixel_size_path in h5s:
                    return h5py_read_dataset(h5s[pixel_size_path])
                else:
                    return None

        value = self._decode_nabu_str(get_pixel_size_value())
        if value is not None:
            value = "{:.8}".format(float(value))
        self._pixelSizeQLE.setText(value if value is not None else "")

    def _setCor(self, url):
        def get_cor_value():
            _NABU_COR_URL = "../../configuration/processing_options/reconstruction/rotation_axis_position"
            with HDF5File(url.file_path(), "r") as h5s:
                data_path = url.data_path()
                pixel_size_path = os.path.normpath("/".join((data_path, _NABU_COR_URL)))
                if pixel_size_path in h5s:
                    return h5py_read_dataset(h5s[pixel_size_path])
                else:
                    return None

        value = self._decode_nabu_str(get_cor_value())
        if value not in (None, "None", "none"):
            value = "{:.4f}".format(float(value))
        self._corQLE.setText(value if value is not None else "")

    def _setPaddingType(self, url):
        def get_padding_type_value():
            _NABU_PADDING_URL = (
                "../../configuration/processing_options/reconstruction/padding_type"
            )
            with HDF5File(url.file_path(), "r") as h5s:
                data_path = url.data_path()
                padding_path = os.path.normpath(
                    "/".join((data_path, _NABU_PADDING_URL))
                )
                if padding_path in h5s:
                    return h5py_read_dataset(h5s[padding_path])
                else:
                    return None

        value = self._decode_nabu_str(get_padding_type_value())
        self._paddingTypeQLE.setText(str(value) if value is not None else "")

    def _setHalfTomo(self, url):
        def get_half_tomo_value():
            _NABU_HALF_TOMO_URL = (
                "../../configuration/processing_options/reconstruction/enable_halftomo"
            )
            with HDF5File(url.file_path(), "r") as h5s:
                data_path = url.data_path()
                half_tomo_path = os.path.normpath(
                    "/".join((data_path, _NABU_HALF_TOMO_URL))
                )
                if half_tomo_path in h5s:
                    return h5py_read_dataset(h5s[half_tomo_path])
                else:
                    return False

        value = get_half_tomo_value()
        self._halfTomoCB.setChecked(value)

    def _setFBPFilter(self, url):
        def get_fbp_filter_value():
            _NABU_FBP_FILTER_URL = (
                "../../configuration/processing_options/reconstruction/fbp_filter_type"
            )
            with HDF5File(url.file_path(), "r") as h5s:
                data_path = url.data_path()
                fbp_filter_path = os.path.normpath(
                    "/".join((data_path, _NABU_FBP_FILTER_URL))
                )
                if fbp_filter_path in h5s:
                    return h5py_read_dataset(h5s[fbp_filter_path])
                else:
                    return None

        value = self._decode_nabu_str(get_fbp_filter_value())
        self._fbpFilterQLE.setText(str(value) if value is not None else "")

    def _setMinLogClip(self, url):
        def get_log_min_clip_value():
            _NABU_LOG_MIN_CLIP_URL = (
                "../../configuration/processing_options/take_log/log_min_clip"
            )
            with HDF5File(url.file_path(), "r") as h5s:
                data_path = url.data_path()
                log_min_path = os.path.normpath(
                    "/".join((data_path, _NABU_LOG_MIN_CLIP_URL))
                )
                if log_min_path in h5s:
                    return h5py_read_dataset(h5s[log_min_path])
                else:
                    return None

        value = self._decode_nabu_str(get_log_min_clip_value())
        self._minLogClipQLE.setText(str(value) if value is not None else "")

    def _setMaxLogClip(self, url):
        def get_log_max_clip_value():
            _NABU_LOG_MAX_CLIP_URL = (
                "../../configuration/processing_options/take_log/log_max_clip"
            )
            with HDF5File(url.file_path(), "r") as h5s:
                data_path = url.data_path()
                log_max_path = os.path.normpath(
                    "/".join((data_path, _NABU_LOG_MAX_CLIP_URL))
                )
                if log_max_path in h5s:
                    return h5py_read_dataset(h5s[log_max_path])
                else:
                    return None

        value = self._decode_nabu_str(get_log_max_clip_value())
        self._maxLogClipQLE.setText(str(value) if value is not None else "")

    def _setSoftwareVersion(self, url):
        _NABU_VERSION_URL = "../../version"

        def get_nabu_software_verion():
            with HDF5File(url.file_path(), "r") as h5s:
                data_path = url.data_path()
                soft_version_path = os.path.normpath(
                    "/".join((data_path, _NABU_VERSION_URL))
                )
                if soft_version_path in h5s:
                    return h5py_read_dataset(h5s[soft_version_path])
                else:
                    return None

        software = software_version = ""
        nabu_version = self._decode_nabu_str(get_nabu_software_verion())
        if nabu_version is not None:
            software = "nabu"
            software_version = nabu_version
        self._softwareVersionQLE.setText("{} ({})".format(software, software_version))
