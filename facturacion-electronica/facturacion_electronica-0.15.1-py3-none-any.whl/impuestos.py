# -*- coding: utf-8 -*-
from facturacion_electronica import clase_util as util
import math


class Impuestos(object):

    def __init__(self, vals=None):
        util.set_from_keys(self, vals)

    @property
    def CodImp(self):
        if not hasattr(self, '_cod_imp'):
            return 0
        return self._cod_imp

    @CodImp.setter
    def CodImp(self, val):
        self._cod_imp = round(val, 2)

    @property
    def mepco(self):
        if not hasattr(self, '_mepco'):
            return ''
        return self._mepco

    @mepco.setter
    def mepco(self, val):
        self._mepco = val

    @property
    def price_include(self):
        if not hasattr(self, '_price_include'):
            return False
        return self._price_include

    @price_include.setter
    def price_include(self, val):
        self._price_include = val

    @property
    def Retencion(self):
        if not hasattr(self, '_retencion'):
            return 0
        return self._retencion

    @Retencion.setter
    def Retencion(self, val):
        self._retencion = round(val, 2)

    @property
    def TasaImp(self):
        if not hasattr(self, '_tasa_imp'):
            return 0
        return self._tasa_imp

    @TasaImp.setter
    def TasaImp(self, val):
        self._tasa_imp = val

    @property
    def TpoImp(self):
        if not hasattr(self, '_tpo_imp'):
            return 0
        return self._tpo_imp

    @TpoImp.setter
    def TpoImp(self, val):
        self._tpo_imp = round(val, 2)

    @property
    def es_adicional(self):
        return self.CodImp in [15, 17, 18, 19, 24, 25, 26, 27, 271] or self.especifico

    @property
    def es_retencion(self):
        return self.CodImp in [15]

    @property
    def especifico(self):
        return self.CodImp in [28, 35]

    def calcular(self, precio, cantidad):
        monto = math.copysign(cantidad, precio)
        if self.especifico:
            return monto * self.TasaImp
        return (self.TasaImp / 100.0) * monto
