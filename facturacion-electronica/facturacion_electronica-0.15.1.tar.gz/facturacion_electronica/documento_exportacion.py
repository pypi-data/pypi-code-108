# -*- coding: utf-8 -*-
from facturacion_electronica import clase_util as util


class Exportacion(object):

    def __init__(self, vals):
        util.set_from_keys(self, vals)

    @property
    def CodModVenta(self):
        if not hasattr(self, '_cod_mod_venta'):
            return False
        return self._cod_mod_venta

    @CodModVenta.setter
    def CodModVenta(self, val):
        self._cod_mod_venta = int(val)

    @property
    def TotClauVenta(self):
        if not hasattr(self, '_tot_clau_venta'):
            return False
        return self._tot_clau_venta

    @TotClauVenta.setter
    def TotClauVenta(self, val):
        self._tot_clau_venta = round(val, 2)

    @property
    def CodClauVenta(self):
        if not hasattr(self, '_cod_clau_venta'):
            return False
        return self._cod_clau_venta

    @CodClauVenta.setter
    def CodClauVenta(self, val):
        self._cod_clau_venta = val

    @property
    def CodViaTransp(self):
        if not hasattr(self, '_cod_via_transp'):
            return False
        return self._cod_via_transp

    @CodViaTransp.setter
    def CodViaTransp(self, val):
        self._cod_via_transp = int(val)

    @property
    def NombreTransp(self):
        if not hasattr(self, '_nombre_transp'):
            return False
        return self._nombre_transp

    @NombreTransp.setter
    def NombreTransp(self, val):
         self._nombre_transp = val

    @property
    def RUTCiaTransp(self):
        if not hasattr(self, '_rut_cia_transp'):
            return False
        return self._rut_cia_transp

    @RUTCiaTransp.setter
    def RUTCiaTransp(self, val):
         self._rut_cia_transp = util.format_vat(val)

    @property
    def NomCiaTransp(self):
        if not hasattr(self, '_nom_cia_transp'):
            return False
        return self._nom_cia_transp

    @NomCiaTransp.setter
    def NomCiaTransp(self, val):
        self._nom_cia_transp = val
    #def IdAdicTransp(self): = self.indicador_adicional

    @property
    def CodPtoEmbarque(self):
        if not hasattr(self, '_cod_pto_embarque'):
            return False
        return self._cod_pto_embarque

    @CodPtoEmbarque.setter
    def CodPtoEmbarque(self, val):
        self._cod_pto_embarque = val
    #def IdAdicPtoEmb(self):

    @property
    def CodPtoDesemb(self):
        if not hasattr(self, '_cod_pto_desemb'):
            return False
        return self._cod_pto_desemb

    @CodPtoDesemb.setter
    def CodPtoDesemb(self, val):
        self._cod_pto_desemb = val
    #def IdAdicPtoDesemb(self): = expo.ind_puerto_desembarque

    @property
    def Tara(self):
        if not hasattr(self, '_tara'):
            return False
        return self._tara

    @Tara.setter
    def Tara(self, val):
        self._tara = val

    @property
    def CodUnidMedTara(self):
        if not hasattr(self, '_cod_unid_med_tara'):
            return False
        return self._cod_unid_med_tara

    @CodUnidMedTara.setter
    def CodUnidMedTara(self, val):
        self._cod_unid_med_tara = val

    @property
    def PesoBruto(self):
        if not hasattr(self, '_peso_bruto'):
            return False
        return self._peso_bruto

    @PesoBruto.setter
    def PesoBruto(self, val):
        self._peso_bruto = round(val, 2)

    @property
    def CodUnidPesoBruto(self):
        if not hasattr(self, '_cod_unid_peso_bruto'):
            return False
        return self._cod_unid_peso_bruto

    @CodUnidPesoBruto.setter
    def CodUnidPesoBruto(self, val):
        self._cod_unid_peso_bruto = val

    @property
    def PesoNeto(self):
        if not hasattr(self, '_peso_neto'):
            return False
        return self._peso_neto

    @PesoNeto.setter
    def PesoNeto(self, val):
        self._peso_neto = round(val, 2)

    @property
    def CodUnidPesoNeto(self):
        if not hasattr(self, '_cod_unid_peso_neto'):
            return False
        return self._cod_unid_peso_neto

    @CodUnidPesoNeto.setter
    def CodUnidPesoNeto(self, val):
        self._cod_unid_peso_neto = val

    @property
    def TotItems(self):
        if not hasattr(self, '_tot_items'):
            return False
        return self._tot_items

    @TotItems.setter
    def TotItems(self, val):
        self._tot_items = val

    @property
    def TotBultos(self):
        if not hasattr(self, '_tot_bultos'):
            return False
        return self._tot_bultos

    @TotBultos.setter
    def TotBultos(self, val):
        self._tot_bultos = val

    @property
    def Bultos(self):
        if not hasattr(self, '_bultos'):
            return False
        return self._bultos

    @Bultos.setter
    def Bultos(self, vals):
        _bultos = []
        for v in vals:
            _bultos.append(Bulto(v))
        self._bultos = _bultos
    #def Marcas(self): =
    #Solo si es contenedor
    #def IdContainer(self): =
    #def Sello(self): =
    #def EmisorSello(self): =

    @property
    def MntFlete(self):
        if not hasattr(self, '_mnt_flete'):
            return False
        return self._mnt_flete

    @MntFlete.setter
    def MntFlete(self, val):
        self._mnt_flete = val

    @property
    def MntSeguro(self):
        if not hasattr(self, '_mnt_seguro'):
            return False
        return self._mnt_seguro

    @MntSeguro.setter
    def MntSeguro(self, val):
        self._mnt_seguro = val

    @property
    def CodPaisRecep(self):
        if not hasattr(self, '_cod_pais_recep'):
            return False
        return self._cod_pais_recep

    @CodPaisRecep.setter
    def CodPaisRecep(self, val):
        self._cod_pais_recep = val

    @property
    def CodPaisDestin(self):
        if not hasattr(self, '_cod_pais_destin'):
            return False
        return self._cod_pais_destin

    @CodPaisDestin.setter
    def CodPaisDestin(self, val):
        self._cod_pais_destin = val


class Bulto(object):

    def __init__(self, vals):
        util.set_from_keys(self, vals)

    @property
    def CodTpoBultos(self):
        if not hasattr(self, '_cod_tpo_bultos'):
            return False
        return self._cod_tpo_bultos

    @CodTpoBultos.setter
    def CodTpoBultos(self, val):
        self._cod_tpo_bultos = val

    @property
    def CantBultos(self):
        if not hasattr(self, '_cant_bultos'):
            return False
        return self._cant_bultos

    @CantBultos.setter
    def CantBultos(self, val):
        self._cant_bultos = val

    @property
    def EmisorSello(self):
        if not hasattr(self, '_emisor_sello'):
            return False
        return self._emisor_sello

    @EmisorSello.setter
    def EmisorSello(self, val):
        self._emisor_sello = val

    @property
    def IdContainer(self):
        if not hasattr(self, '_id_container'):
            return False
        return self._id_container

    @IdContainer.setter
    def IdContainer(self, val):
        self._id_container = val

    @property
    def Marcas(self):
        if not hasattr(self, '_marcas'):
            return False
        return self._marcas

    @Marcas.setter
    def Marcas(self, val):
        self._marcas = val

    @property
    def Sello(self):
        if not hasattr(self, '_sello'):
            return False
        return self._sello

    @Sello.setter
    def Sello(self, val):
        self._sello = val
