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


from .base import _ReconsParam
from .axis import AxisRP
from .beamgeo import BeamGeoRP
from .ft import FTRP
from .paganin import PaganinRP
from .pyhst import PyhstRP


class ReconsParams(_ReconsParam):
    """This class defines the reconstructions parameters to be used for
    tomography.

    Those are meant to be embeded in TomoBase class.
    They are used to tune processes like ftseries or darkref.
    They can be modify by processes (axis, darkref, ftseries).

    In the following scheme for example:

    .. image:: img/orange_data_recons_params.png

    * Data watcher will generate instance of TomoBase (alias data in Orange)
        that will have no reconstruction parameters.
    * Then dark and flat field construction will copy the currently defined 'dkrf'
        reconstruction parameters into each received TomoBase and use them to run
        dark and flat field.
    * Now TomoBase as a definition for dark and flat field and move to axis
        definition.
    * axis process will also copy it's definition of the axis the TomoBase
        reconstruction parameters and process axis process. Process result
        (position_value) will be updated in the TomoBase reconstruction paramters.
    * ftseries load reconstruction paramters of axis and dark and flat field
        (if any) and run the reconstruction.

    :param bool empty: if empty, skip reconstruction of sub parameter object
                       and set them to None instead
    """

    def __init__(self, empty=False):
        _ReconsParam.__init__(self)
        self._createSubParamsSet(empty)

        self._managed_params = {
            "FT": self.__class__.ft,
            "PYHSTEXE": self.__class__.pyhst,
            "FTAXIS": self.__class__.axis,
            "PAGANIN": self.__class__.paganin,
            "BEAMGEO": self.__class__.beam_geo,
            "DKRF": self.__class__.dkrf,
        }

    def _createSubParamsSet(self, empty):
        self._ft = None if empty else FTRP()
        self._pyhst = None if empty else PyhstRP()
        self._axis = None if empty else AxisRP()
        self._paganin = None if empty else PaganinRP()
        self._beam_geo = None if empty else BeamGeoRP()
        from tomwer.core.process.reconstruction.darkref.params import DKRFRP

        self._dkrf = None if empty else DKRFRP()

    def unmanaged_params_tree(self):
        """

        :return: unmanged paramters of the Reconsparams and the one
                 of his 'childrens': FTRP, PyhstRP...
        :rtype: dict
        """
        this_node_unmanged = self.unmanaged_params
        for managed_key in self._managed_params:
            unmanaged = self._managed_params[managed_key].fget(self).unmanaged_params
            if len(unmanaged) > 0:
                if managed_key not in this_node_unmanged:
                    this_node_unmanged[managed_key] = {}
                this_node_unmanged[managed_key].update(unmanaged)
        return this_node_unmanged

    @property
    def ft(self):
        """set of general reconstruction parameters

        :rtype: :class:`.FTRP`
        """
        return self._ft

    @ft.setter
    def ft(self, ft):
        self._ft = ft
        self.changed()

    @property
    def pyhst(self):
        """set of reconstruction parameters regarding pyhst option (version...)

        :rtype: :class:`.PyhstRP`
        """
        return self._pyhst

    @pyhst.setter
    def pyhst(self, pyhst):
        self._pyhst = pyhst
        self.changed()

    @property
    def axis(self):
        """reconstruction parameters regarding the center of rotation

        :rtype: :class:`.AxisRP`
        """
        return self._axis

    @axis.setter
    def axis(self, axis):
        self._axis = axis
        self.changed()

    @property
    def paganin(self):
        """set of paramrters regarding Paganin mode

        :rtype: :class:`.PaganinRP`
        """
        return self._paganin

    @paganin.setter
    def paganin(self, paganin):
        self._paganin = paganin
        self.changed()

    @property
    def beam_geo(self):
        """set of parameters regarding the beam geometry

        :rtype: :class:`.BeamGeoRP`
        """
        return self._beam_geo

    @beam_geo.setter
    def beam_geo(self, beam_geo):
        self._beam_geo = beam_geo
        self.changed()

    @property
    def dkrf(self):
        """set of parameters regarding the dark and flat field correction

        :rtype: :class:`.DKRFRP`
        """
        return self._dkrf

    @dkrf.setter
    def dkrf(self, dkrf):
        self._dkrf = dkrf
        self.changed()

    def to_dict(self):
        _dict = {
            "FT": self.ft.to_dict() if self.ft else None,
            "PYHSTEXE": self.pyhst.to_dict() if self.pyhst else None,
            "FTAXIS": self.axis.to_dict() if self.axis else None,
            "PAGANIN": self.paganin.to_dict() if self.paganin else None,
            "BEAMGEO": self.beam_geo.to_dict() if self.beam_geo else None,
            "DKRF": self.dkrf.to_dict() if self.dkrf else None,
        }
        _dict.update(self.unmanaged_params)
        return _dict

    to_dict.__doc__ = _ReconsParam.to_dict.__doc__

    @staticmethod
    def from_dict(_dict):
        recons_params = ReconsParams()
        recons_params.load_from_dict(_dict)
        return recons_params

    from_dict.__doc__ = _ReconsParam.from_dict.__doc__

    def load_from_dict(self, _dict):
        self._load_unmanaged_params(_dict=_dict)
        if _dict["FT"] is None:
            self._ft = None
        else:
            self._ft.load_from_dict(_dict["FT"])
        if _dict["PYHSTEXE"] is None:
            self._pyhst = None
        else:
            self._pyhst.load_from_dict(_dict["PYHSTEXE"])
        if _dict["FTAXIS"] is None:
            self._axis = None
        else:
            self._axis.load_from_dict(_dict["FTAXIS"])
        if _dict["PAGANIN"] is None:
            self._paganin = None
        else:
            self._paganin.load_from_dict(_dict["PAGANIN"])
        if _dict["BEAMGEO"] is None:
            self._beam_geo = None
        else:
            self._beam_geo.load_from_dict(_dict["BEAMGEO"])
        if _dict["DKRF"] is None:
            self._dkrf = None
        else:
            self._dkrf.load_from_dict(_dict["DKRF"])

    load_from_dict.__doc__ = _ReconsParam.load_from_dict.__doc__

    def __iter__(self):
        yield self.ft
        yield self.pyhst
        yield self.axis
        yield self.paganin
        yield self.beam_geo
        yield self.dkrf

    def copy(self, other_rp):
        """
        copy parameters value from other_rp

        :param _ReconsParam: reconsparam to copy
        :param Union[list, None] parameters: parameters names that we want to
                                             copy
        """
        if other_rp is None:
            return

        def copy_all_recons_params():
            """function called if other_rp is an instance of ReconsParams"""
            assert isinstance(other_rp, ReconsParams)
            other_sub_rps = (
                other_rp.ft,
                other_rp.pyhst,
                other_rp.axis,
                other_rp.paganin,
                other_rp.beam_geo,
                other_rp.dkrf,
            )
            for other_sub_rp in other_sub_rps:
                self.copy(other_sub_rp)
            self._set_unmanaged_params(other_rp.unmanaged_params)

        from tomwer.core.process.reconstruction.darkref.params import (
            DKRFRP,
        )  # avoid cyclic import. DKRF should be specific to dark and flat field and not in relation with ftserie

        if isinstance(other_rp, ReconsParams):
            copy_all_recons_params()
        elif isinstance(other_rp, FTRP):
            self._copy_ft_rp(other_rp)
        elif isinstance(other_rp, PyhstRP):
            self._copy_pyhst_rp(other_rp)
        elif isinstance(other_rp, AxisRP):
            self._copy_axis_rp(other_rp)
        elif isinstance(other_rp, PaganinRP):
            self._copy_paganin_rp(other_rp)
        elif isinstance(other_rp, BeamGeoRP):
            self._copy_beam_geo_rp(other_rp)
        elif isinstance(other_rp, DKRFRP):
            self._copy_dkrf_rp(other_rp)
        else:
            raise TypeError(
                "Cannot copy %s, because type %s is not recognized"
                "" % (other_rp, type(other_rp))
            )

    def _copy_ft_rp(self, other_rp):
        # note: we cannot pass by the deep copy function, fail with the
        # properties
        if self.ft is None:
            self.ft = other_rp.__class__()
        self.ft.copy(other_rp)

    def _copy_pyhst_rp(self, other_rp):
        if self.pyhst is None:
            self.pyhst = other_rp.__class__()
        self.pyhst.copy(other_rp)

    def _copy_axis_rp(self, other_rp):
        if self.axis is None:
            self.axis = other_rp.__class__()
        self.axis.copy(other_rp)

    def _copy_paganin_rp(self, other_rp):
        if self.paganin is None:
            self.paganin = other_rp.__class__()
        self.paganin.copy(other_rp)

    def _copy_beam_geo_rp(self, other_rp):
        if self.beam_geo is None:
            self.beam_geo = other_rp.__class__()
        self.beam_geo.copy(other_rp)

    def _copy_dkrf_rp(self, other_rp):
        if self.dkrf is None:
            self.dkrf = other_rp.__class__()
        self.dkrf.copy(other_rp)

    def _reset_unmanaged_params(self):
        _ReconsParam._reset_unmanaged_params(self)
        for sub_rp in self:
            sub_rp._reset_unmanaged_params()
