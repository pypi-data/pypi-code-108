# -*- coding: utf-8 -*-
from facturacion_electronica import clase_util as util


class LineaImpuesto(object):

    def __init__(self, vals):
        self._iniciar()
        util.set_from_keys(vals, priorizar=['moneda_decimales'])
        self.tax_id = vals['tax_id']
        self._compute_tax()

    @property
    def ActivoFijo(self):
        if not hasattr(self, '_activo_fijo'):
            return False
        return self._activo_fijo

    @ActivoFijo.setter
    def ActivoFijo(self, val):
        self._activo_fijo = val

    @property
    def base(self):
        if not hasattr(self, '_base'):
            return 0
        if self.tax_id and self.tax_id.price_include and self.tax_id.TasaImp != 0:
            return self._base / (1 + (self.tax_id.TasaImp / 100.0))
        return self._base

    @base.setter
    def base(self, val):
        self._base = int(round(val))

    @property
    def cantidad(self):
        if not hasattr(self, '_cantidad'):
            return 0
        return self._cantidad

    @cantidad.setter
    def cantidad(self, val):
        self._cantidad = val

    @property
    def moneda_decimales(self):
        if not hasattr(self, '_moneda_decimales'):
            return 0
        self._moneda_decimales

    @moneda_decimales.setter
    def moneda_decimales(self, val):
        self._moneda_decimales = 0

    @property
    def MontoImp(self):
        if not hasattr(self, '_monto'):
            return 0
        return self._monto

    @MontoImp.setter
    def MontoImp(self, val):
        mnt = round(val, self.moneda_decimales)
        if self.moneda_decimales == 0:
            mnt = int(mnt)
        self._monto = mnt

    def _iniciar(self):
        self.tax_id = None

    def monto_fijo(self):
        return self.tax_id.TasaImp * self.cantidad

    def _compute_tax(self):
        if self.tax_id.especifico:
            monto = self.monto_fijo()
        else:
            if not self.tax_id or self.tax_id.TasaImp == 0:
                return 0.0
            monto = (self.base * (self.tax_id.TasaImp / 100.0))
        self.MontoImp = monto

    def get_tax_monto(self, moneda_decimales=0):
        self._compute_tax()
        return self.MontoImp
