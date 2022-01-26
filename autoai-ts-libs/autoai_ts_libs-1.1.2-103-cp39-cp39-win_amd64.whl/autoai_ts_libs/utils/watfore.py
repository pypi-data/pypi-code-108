# ************* Begin Copyright - Do not add comments here **************
#   Licensed Materials - Property of IBM
#
#   (C) Copyright IBM Corp. 2019, 2020, All Rights Reserved
#
# The source code for this program is not published or other-
# wise divested of its trade secrets, irrespective of what has
# been deposited with the U.S. Copyright Office.
# **************************** End Copyright ***************************
"""
@author: Syed Yousaf Shah (syshah@us.ibm.com)
Available transforms, interpolators and forecasters.

"""
class Transforms:
    def _watfore_transform(func):
        return func()

    @_watfore_transform
    def difference(self=None):
        return "difference"
    @_watfore_transform
    def fill_na(self=None):
        return "fill_na"
    @_watfore_transform
    def shift(self=None):
        return "shift"
    @_watfore_transform
    def awgn_noise(self=None):
        return "awgn_noise"
    @_watfore_transform
    def mwgn_noise(self=None):
        return "mwgn_noise"
    @_watfore_transform
    def z_score(self=None):
        return "z_score"


class Forecasters:
    def _watfore_forecasters(func):
        return func()

    @_watfore_forecasters
    def bats(self=None):
        return "bats"

    @_watfore_forecasters
    def arima(self=None):
        return "arima"

    @_watfore_forecasters
    def arma(self=None):
        return "arma"

    @_watfore_forecasters
    def hw(self=None):
        return "hw"

    @_watfore_forecasters
    def autoforecaster(self=None):
        return "autoforecaster"

class Interpolators:
    def _watfore_interpolators(func):
        return func()

    @_watfore_interpolators
    def linear(self=None):
        return "linear"

    @_watfore_interpolators
    def cubic(self=None):
        return "cubic"

    @_watfore_interpolators
    def nearest(self=None):
        return "nearest"

    @_watfore_interpolators
    def prev(self=None):
        return "prev"

    @_watfore_interpolators
    def next(self=None):
        return "next"

    @_watfore_interpolators
    def fill(self=None):
        return "fill"
class Accessors:
    WATFORE_FILENAME_APPEND ='_AITSPYWF'

    @classmethod
    def make_watfore_save_filename(cls,file_name):

        if file_name.lower().endswith(('.pkl', '.pickle')):
            # Use replace for case filename full path start with '.', such as "./repository/output/model/"
            onlyname = file_name.replace('.pkl', '').replace('.pickle', '')
            ext = file_name.split('.')[-1]
            return onlyname + Accessors.WATFORE_FILENAME_APPEND + "." + ext
        else:
            return file_name + Accessors.WATFORE_FILENAME_APPEND
