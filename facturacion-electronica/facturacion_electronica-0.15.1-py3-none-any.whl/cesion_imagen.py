# -*- coding: utf-8 -*-
from facturacion_electronica import clase_util as util
from facturacion_electronica.clase_util import UserError


class CesionImagen(object):

    def __init__(self, vals):
        util.set_from_keys(self, vals)

    def Contenido(self):
        return self._content
