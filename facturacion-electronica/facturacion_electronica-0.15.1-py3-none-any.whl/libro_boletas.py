# -*- coding: utf-8 -*-
from facturacion_electronica.documento import Documento
from facturacion_electronica.impuestos import Impuestos
from facturacion_electronica.linea_impuesto import LineaImpuesto


class Boletas(Documento):

    @property
    def MntExento(self):
        return self.MntExe

    @MntExento.setter
    def MntExento(self, val):
        self.MntExe = val

    @property
    def rango_inicial(self):
        if not hasattr(self, '_rango_inicial'):
            return 0
        return self._rango_inicial

    @rango_inicial.setter
    def rango_inicial(self, val):
        self._rango_inicial = val

    @property
    def rango_final(self):
        if not hasattr(self, '_rango_final'):
            return 0
        return self._rango_final

    @rango_final.setter
    def rango_final(self, val):
        self._rango_final = val

    def get_cantidad(self):
        if not self.rango_inicial or not self.rango_final:
            return
        if self.rango_final < self.rango_inicial:
            raise UserError("¡El rango Final no puede ser menor al inicial")
        self.cantidad_boletas = self.rango_final - self.rango_inicial +1
