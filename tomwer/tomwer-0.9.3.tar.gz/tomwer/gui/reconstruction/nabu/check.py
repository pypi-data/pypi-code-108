# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2017 European Synchrotron Radiation Facility
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
__date__ = "02/12/2021"


from tomwer.core.scan.hdf5scan import HDF5TomoScan
from tomwer.core.utils.nxtomoutils import get_n_series
from tomoscan.esrf.hdf5scan import ImageKey
from silx.gui import qt


def check_dark_series(scan: HDF5TomoScan, logger=None, user_input: bool = True) -> bool:
    """
    check:
        - if scan has computed_dark attached. If there is more than one then ask confirmation to the user to process the dataset
        - else if the NXTomo has more than one serie of dark. Otherwise ask confirmation to the user to process the dataset

    ask confirmation for processing is done by a pop up dialog.

    :param HDF5TomoScan scan: scan to check
    :param bool user_input: if True and if n series of flat is invalid then ask the user to confirm the processing. Else print a warning and refuse processing

    :return: True if processing can be done else False
    :note: user can 'force' the processing to be done
    """
    if not isinstance(scan, HDF5TomoScan):
        raise TypeError(
            f"scan is expected to be an instance of {HDF5TomoScan} not a {type(scan)}"
        )
    try:
        image_keys = scan.image_keys
    except AttributeError:
        image_keys = scan.image_key

    n_series = get_n_series(
        image_key_values=image_keys, image_key_type=ImageKey.DARK_FIELD
    )
    if n_series != 1:
        text = f"{n_series} serie(s) of dark found when one expected. Nabu won't be able to run reconstruction (flat field will fail)."
        if n_series > 1:
            text += "\nYou can edit image_keys from the `image-key-editor` to ignore a serie (invalid all keys of series you want to ignore)."
        if user_input is False:
            text += "\n skip processing"
            if logger is not None:
                logger.error(text)
            return False
        else:
            msg = qt.QMessageBox()
            msg.setIcon(qt.QMessageBox.Warning)
            types = qt.QMessageBox.Ok | qt.QMessageBox.Cancel
            msg.setStandardButtons(types)
            text += "\nContinue ?"
            msg.setText(text)
            return msg.exec_() == qt.QMessageBox.Ok
    else:
        return True


def check_flat_series(scan: HDF5TomoScan, logger, user_input: bool = True) -> bool:
    """
    Insure the scan contains at least one serie of flat. Otherwise warn the user nabu will not be able to process
    """
    if not isinstance(scan, HDF5TomoScan):
        raise TypeError(
            f"scan is expected to be an instance of {HDF5TomoScan} not a {type(scan)}"
        )
    try:
        image_keys = scan.image_keys
    except AttributeError:
        image_keys = scan.image_key
    n_series = get_n_series(
        image_key_values=image_keys, image_key_type=ImageKey.FLAT_FIELD
    )
    if n_series == 0:
        text = "No flat found. Nabu will no be able to do the flat field correction and to reconstruct dataset."
        if user_input is False:
            if logger is not None:
                logger.error(text)
            return False
        else:
            msg = qt.QMessageBox()
            msg.setIcon(qt.QMessageBox.Warning)
            types = qt.QMessageBox.Ok | qt.QMessageBox.Cancel
            msg.setStandardButtons(types)
            text += "\nContinue ?"
            msg.setText(text)
            return msg.exec_() == qt.QMessageBox.Ok
    else:
        return True
