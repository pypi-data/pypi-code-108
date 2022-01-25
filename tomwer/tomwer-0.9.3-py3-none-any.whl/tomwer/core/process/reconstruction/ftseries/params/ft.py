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
__date__ = "05/03/2019"


from .base import _ReconsParam
from ....utils import _assert_cast_to_boolean, _assert_param_instance
from collections.abc import Iterable
from silx.utils.enum import Enum as _Enum
import enum
import typing
import logging

_logger = logging.getLogger(__name__)


@enum.unique
class VolSelMode(_Enum):
    total = 0
    manual = 1
    graphics = 2


@enum.unique
class FixedSliceMode(_Enum):
    middle = -1
    row_n = -3

    @classmethod
    def from_value(cls, value):
        for val in FixedSliceMode:
            if val.name == value:
                return val
        return super(FixedSliceMode, cls).from_value(value)


class FTRP(_ReconsParam):
    """Reconstruction parameters for ftseries (general parameters)"""

    _UNSPLIT_KEYS = ("FIXEDSLICE",)
    "keys that we don't want to treat in `to_unique_recons_set` function"

    def __init__(self):
        _ReconsParam.__init__(self)
        self.__show_proj = False
        self.__show_slice = True
        self.__fixed_slice = FixedSliceMode.middle
        self.__vol_out_file = False
        self.__half_acq = False
        self.__force_half_acq = False
        self.__angle_offset_value = 0.0
        self.__num_part = 4
        self.__fastomo3_version = "fastomo3 3.2"
        self.__correct_spikes_threshold = 0.04
        self.__activate_database = False
        self.__do_test_slice = True
        self.__no_test = False
        self.__zero_off_mask = True
        self.__volume_selection_mode = VolSelMode.total
        self.__record_volume_selection = False
        self.__ring_correction = False
        self.__ddf_correction = False
        self.__fix_header_size = False
        self.__head_directory_to_remove = "/lbsram"
        self.__axis_correction_file = "correct.txt"
        self.__do_axis_correction = False
        self.__force_reconstruction = False
        self.__dff_sigma = 0.0

        self._managed_params = {
            "SHOWPROJ": self.__class__.show_proj,
            "SHOWSLICE": self.__class__.show_slice,
            "FIXEDSLICE": self.__class__.fixed_slice,
            "VOLOUTFILE": self.__class__.vol_out_file,
            "HALF_ACQ": self.__class__.half_acq,
            "FORCE_HALF_ACQ": self.__class__.force_half_acq,
            "ANGLE_OFFSET_VALUE": self.__class__.angle_offset_value,
            "ANGLE_OFFSET": self.__class__.angle_offset,
            "NUM_PART": self.__class__.num_part,
            "VERSION": self.__class__.fastomo3_version,
            "CORRECT_SPIKES_THRESHOLD": self.__class__.correct_spikes_threshold,
            "DATABASE": self.__class__.activate_database,
            "DO_TEST_SLICE": self.__class__.do_test_slice,
            "NO_CHECK": self.__class__.skip_reconstruction_tests,
            "ZEROOFFMASK": self.__class__.set_mask_outside_to_zero,
            "VOLSELECT": self.__class__.volume_selection_mode,
            "VOLSELECTION_REMEMBER": self.__class__.record_volume_selection,
            "RINGSCORRECTION": self.__class__.ring_correction,
            "DFFCORRECTION": self.__class__.double_ff_correction,
            "DFF_SIGMA": self.__class__.double_ff_sigma,
            "FIXHD": self.__class__.fix_header_size,
            "RM_HEAD_DIR": self.__class__.head_directory_to_rm,
            "AXIS_CORRECTION_FILE": self.__class__.axis_correction_file,
            "DO_AXIS_CORRECTION": self.__class__.do_axis_correction,
        }

    @property
    def show_proj(self):
        """show graphical proj during reconstruction"""
        return self.__show_proj

    @show_proj.setter
    def show_proj(self, show):
        _assert_param_instance(show, (bool, int, float))
        _assert_cast_to_boolean(show)
        if self.__show_proj != bool(show):
            self.__show_proj = bool(show)
            self.changed()

    @property
    def show_slice(self):
        """ "show graphical slice during reconstruction"""
        return self.__show_slice

    @show_slice.setter
    def show_slice(self, show):
        _assert_param_instance(show, (bool, int, float))
        _assert_cast_to_boolean(show)
        if self.__show_slice != bool(show):
            self.__show_slice = bool(show)
            self.changed()

    @property
    def fixed_slice(self):
        """which slice(s) to reconstruct"""
        return self.__fixed_slice

    @fixed_slice.setter
    def fixed_slice(self, fixed):
        _assert_param_instance(fixed, (int, str, FixedSliceMode, Iterable))

        # try to see if the value is on of FixedSliceMode
        if isinstance(fixed, str):
            try:
                fixed = FixedSliceMode.from_value(fixed)
            except Exception:
                pass

        if self.__fixed_slice != fixed:
            self.__fixed_slice = fixed
            self.changed()

    def fixed_slice_as_list(self) -> typing.Union[tuple, int]:
        """Return fixed_slice as a list of int"""
        fixed_slice = self.fixed_slice
        if isinstance(fixed_slice, str):
            try:
                if fixed_slice.count(":") == 2:
                    _from, _to, _step = fixed_slice.split(":")
                    _from, _to, _step = int(_from), int(_to), int(_step)
                    if _from > _to:
                        tmp = _to
                        _to = _from
                        _from = tmp
                    res = []
                    while _from <= _to:
                        res.append(_from)
                        _from += _step
                    return tuple(res)
                else:
                    vals = fixed_slice.replace(" ", "")
                    vals = fixed_slice.replace("(", "")
                    vals = fixed_slice.replace(")", "")
                    vals = vals.replace("_", "")
                    vals = vals.replace(";", ",").split(",")
                    res = []
                    for val in vals:
                        try:
                            res.append(int(val))
                        except Exception:
                            pass
                    if len(res) == 1:
                        return res[0]
                    else:
                        return tuple(res)
            except Exception as e:
                _logger.error(e)
        else:
            return fixed_slice

    @property
    def vol_out_file(self):
        """single .vol instead of edf stack"""
        return self.__vol_out_file

    @vol_out_file.setter
    def vol_out_file(self, single_vol):
        _assert_param_instance(single_vol, (bool, int, float))
        _assert_cast_to_boolean(single_vol)
        if self.__vol_out_file != bool(single_vol):
            self.__vol_out_file = bool(single_vol)
            self.changed()

    @property
    def half_acq(self):
        """use half acquisition reconstruction"""
        return self.__half_acq

    @half_acq.setter
    def half_acq(self, half):
        _assert_param_instance(half, (bool, int, float))
        _assert_cast_to_boolean(half)
        if self.__half_acq != bool(half):
            self.__half_acq = bool(half)
            self.changed()

    @property
    def force_half_acq(self):
        """Force half acquisition even if angle is not 360 (from PyHST 2016c)"""
        return self.__force_half_acq

    @force_half_acq.setter
    def force_half_acq(self, force):
        _assert_param_instance(force, (bool, int, float))
        _assert_cast_to_boolean(force)
        self.__force_half_acq = bool(force)
        self.changed()

    @property
    def angle_offset_value(self):
        """finale image rotation angle in degrees"""
        return self.__angle_offset_value

    @angle_offset_value.setter
    def angle_offset_value(self, value):
        assert isinstance(value, (int, float))
        if self.__angle_offset_value != value:
            self.__angle_offset_value = value
            self.changed()

    @property
    def angle_offset(self):
        return self.__angle_offset_value != 0.0

    @angle_offset.setter
    def angle_offset(self, value):
        # nothing to do since it is based on the angle_offset_value. But
        # requested by the structural design choice.
        pass

    @property
    def num_part(self):
        return self.__num_part

    @num_part.setter
    def num_part(self, value):
        """length of the numerical part in the data filenames (for .edf files)"""
        _assert_param_instance(value, (int, float))
        if self.__num_part != int(value):
            self.__num_part = int(value)
            self.changed()

    @property
    def fastomo3_version(self):
        # TODO: this should be removed soon
        return self.__fastomo3_version

    @fastomo3_version.setter
    def fastomo3_version(self, version):
        if self.__fastomo3_version != version:
            self.__fastomo3_version = version
            self.changed()

    @property
    def correct_spikes_threshold(self):
        """threshold above which we have spike"""
        return self.__correct_spikes_threshold

    @correct_spikes_threshold.setter
    def correct_spikes_threshold(self, correct):
        _assert_param_instance(correct, (bool, int, float, str))
        if self.__correct_spikes_threshold != correct:
            self.__correct_spikes_threshold = correct
            self.changed()

    @property
    def activate_database(self):
        """put scan in tomoDB"""
        return self.__activate_database

    @activate_database.setter
    def activate_database(self, activate):
        _assert_param_instance(activate, (bool, int, float))
        _assert_cast_to_boolean(activate)
        if self.__activate_database != bool(activate):
            self.__activate_database = bool(activate)
            self.changed()

    @property
    def do_test_slice(self):
        """reconstruct one test slice"""
        return self.__do_test_slice

    @do_test_slice.setter
    def do_test_slice(self, test):
        _assert_param_instance(test, (bool, int, float))
        _assert_cast_to_boolean(test)
        if self.__do_test_slice != bool(test):
            self.__do_test_slice = bool(test)
            self.changed()

    @property
    def skip_reconstruction_tests(self):
        """force or not reconst of slices in ftseries"""
        return self.__no_test

    @skip_reconstruction_tests.setter
    def skip_reconstruction_tests(self, skip):
        _assert_param_instance(skip, (bool, int, float))
        _assert_cast_to_boolean(skip)
        if self.__no_test != bool(skip):
            self.__no_test = bool(skip)
            self.changed()

    @property
    def force_reconstruction(self):
        """force or not reconst of slices in ftseries"""
        return self.__force_reconstruction

    @force_reconstruction.setter
    def force_reconstruction(self, force):
        _assert_param_instance(force, (bool, int, float))
        _assert_cast_to_boolean(force)
        if self.__force_reconstruction != bool(force):
            self.__force_reconstruction = bool(force)
            self.changed()

    @property
    def set_mask_outside_to_zero(self):
        """Sets to zero the region outside the reconstruction mask"""
        return self.__zero_off_mask

    @set_mask_outside_to_zero.setter
    def set_mask_outside_to_zero(self, set_to_zero):
        _assert_param_instance(set_to_zero, (bool, int, float))
        _assert_cast_to_boolean(set_to_zero)
        if self.__zero_off_mask != set_to_zero:
            self.__zero_off_mask = set_to_zero
            self.changed()

    @property
    def volume_selection_mode(self):
        """how to select volume: total, manual or graphic"""
        return self.__volume_selection_mode

    @volume_selection_mode.setter
    def volume_selection_mode(self, mode):
        _mode = mode
        if type(mode) is str and hasattr(VolSelMode, _mode):
            _mode = getattr(VolSelMode, _mode)
        assert _mode in VolSelMode
        if self.__volume_selection_mode != _mode:
            self.__volume_selection_mode = _mode
            self.changed()

    @property
    def record_volume_selection(self):
        return self.__record_volume_selection

    @record_volume_selection.setter
    def record_volume_selection(self, record):
        _assert_param_instance(record, (bool, int, float))
        _assert_cast_to_boolean(record)
        if bool(record) != self.__record_volume_selection:
            self.__record_volume_selection = bool(record)
            self.changed()

    @property
    def ring_correction(self):
        return self.__ring_correction

    @ring_correction.setter
    def ring_correction(self, _apply):
        _assert_param_instance(_apply, (bool, int, float))
        _assert_cast_to_boolean(_apply)
        if self.__ring_correction != bool(_apply):
            self.__ring_correction = bool(_apply)
            self.changed()

    @property
    def double_ff_correction(self):
        return self.__ddf_correction

    @double_ff_correction.setter
    def double_ff_correction(self, _apply):
        _assert_param_instance(_apply, (bool, int, float))
        _assert_cast_to_boolean(_apply)
        if self.__ddf_correction != bool(_apply):
            self.__ddf_correction = bool(_apply)
            self.changed()

    @property
    def double_ff_sigma(self):
        return self.__dff_sigma

    @double_ff_sigma.setter
    def double_ff_sigma(self, sigma):
        if self.__dff_sigma != float(sigma):
            self.__dff_sigma = float(sigma)
            self.changed()

    @property
    def fix_header_size(self):
        """If true, try fixed header size determination"""
        return self.__fix_header_size

    @fix_header_size.setter
    def fix_header_size(self, fix):
        if self.__fix_header_size != fix:
            self.__fix_header_size = fix
            self.changed()

    @property
    def head_directory_to_rm(self):
        # TODO: should probably be removed, needed by octave but should be
        # managed differently later.
        return self.__head_directory_to_remove

    @head_directory_to_rm.setter
    def head_directory_to_rm(self, _dir):
        assert isinstance(_dir, str)
        if self.__head_directory_to_remove != _dir:
            self.__head_directory_to_remove = _dir
            self.changed()

    @property
    def axis_correction_file(self):
        return self.__axis_correction_file

    @axis_correction_file.setter
    def axis_correction_file(self, _file):
        assert isinstance(_file, str)
        if self.__axis_correction_file != _file:
            self.__axis_correction_file = _file
            self.changed()

    @property
    def do_axis_correction(self):
        return self.__do_axis_correction

    @do_axis_correction.setter
    def do_axis_correction(self, do):
        _assert_param_instance(do, (bool, int, float))
        _assert_cast_to_boolean(do)
        if self.__do_axis_correction != do:
            self.__do_axis_correction = do
            self.changed()

    def to_dict(self):
        _dict = {
            "SHOWPROJ": int(self.show_proj),
            "SHOWSLICE": int(self.show_slice),
            "FIXEDSLICE": self.fixed_slice.name.replace("_", " ")
            if isinstance(self.fixed_slice, FixedSliceMode)
            else str(self.fixed_slice),
            "VOLOUTFILE": int(self.vol_out_file),
            "HALF_ACQ": int(self.half_acq),
            "FORCE_HALF_ACQ": int(self.force_half_acq),
            "ANGLE_OFFSET_VALUE": float(self.angle_offset_value),
            "ANGLE_OFFSET": int(self.angle_offset),
            "NUM_PART": self.num_part,
            "VERSION": self.fastomo3_version,
            "CORRECT_SPIKES_THRESHOLD": self.correct_spikes_threshold,
            "DATABASE": int(self.activate_database),
            "DO_TEST_SLICE": int(self.do_test_slice),
            "NO_CHECK": int(self.skip_reconstruction_tests),
            "ZEROOFFMASK": int(self.set_mask_outside_to_zero),
            "VOLSELECT": self.volume_selection_mode.name,
            "VOLSELECTION_REMEMBER": int(self.record_volume_selection),
            "RINGSCORRECTION": int(self.ring_correction),
            "DFFCORRECTION": float(self.double_ff_correction),
            "DFF_SIGMA": int(self.double_ff_sigma),
            "FIXHD": int(self.fix_header_size),
            "RM_HEAD_DIR": self.head_directory_to_rm,
            "AXIS_CORRECTION_FILE": self.axis_correction_file,
            "DO_AXIS_CORRECTION": int(self.do_axis_correction),
        }
        _dict.update(self.unmanaged_params)
        return _dict

    @staticmethod
    def from_dict(_dict):
        recons_param = FTRP()
        recons_param.load_from_dict(_dict)
        return recons_param

    def load_from_dict(self, _dict):
        self._load_unmanaged_params(_dict=_dict)
        self.show_proj = _dict["SHOWPROJ"]
        self.show_slice = _dict["SHOWSLICE"]
        self.fixed_slice = _dict["FIXEDSLICE"]
        self.vol_out_file = _dict["VOLOUTFILE"]
        self.half_acq = _dict["HALF_ACQ"]
        self.force_half_acq = _dict["FORCE_HALF_ACQ"]
        self.angle_offset_value = _dict["ANGLE_OFFSET_VALUE"]
        self.num_part = _dict["NUM_PART"]
        self.correct_spikes_threshold = _dict["CORRECT_SPIKES_THRESHOLD"]
        self.activate_database = _dict["DATABASE"]
        self.do_test_slice = _dict["DO_TEST_SLICE"]
        self.skip_reconstruction_tests = _dict["NO_CHECK"]
        self.set_mask_outside_to_zero = _dict["ZEROOFFMASK"]
        self.volume_selection_mode = _dict["VOLSELECT"]
        self.record_volume_selection = _dict["VOLSELECTION_REMEMBER"]
        self.ring_correction = _dict["RINGSCORRECTION"]
        self.fix_header_size = _dict["FIXHD"]
        self.head_directory_to_rm = _dict["RM_HEAD_DIR"]
        self.axis_correction_file = _dict["AXIS_CORRECTION_FILE"]
        self.do_axis_correction = _dict["DO_AXIS_CORRECTION"]
        if "DFFCORRECTION" in _dict:
            self.double_ff_correction = _dict["DFFCORRECTION"]
        if "DFF_SIGMA" in _dict:
            self.double_ff_sigma = _dict["DFF_SIGMA"]
