# -*- coding: utf-8 -*-
from facturacion_electronica import clase_util as util
from facturacion_electronica.clase_util import UserError


class Cedente(object):

    def __init__(self, vals):
        util.set_from_keys(self, vals)

    @property
    def Nombre(self):
        if not hasattr(self, '_nombre'):
            return False
        return self._nombre

    @Nombre.setter
    def Nombre(self, val):
        self._nombre = val

    @property
    def Phono(self):
        if not hasattr(self, '_phono'):
            return False
        return self._phono

    @Phono.setter
    def Phono(self, val):
        self._phono = val

    @property
    def RUT(self):
        if not hasattr(self, '_rut'):
            return False
        return self._rut

    @RUT.setter
    def RUT(self, val):
        self._rut = val

    @property
    def eMail(self):
        if not hasattr(self, '_email'):
            return False
        return self._email

    @eMail.setter
    def eMail(self, val):
        self._email = val
