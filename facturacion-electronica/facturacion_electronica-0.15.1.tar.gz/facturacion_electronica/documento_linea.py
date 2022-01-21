# -*- coding: utf-8 -*-
from facturacion_electronica.impuestos import Impuestos
from facturacion_electronica import clase_util as util
import collections


class LineaDetalle(object):

    def __init__(self, vals, currency=None, valor_iva=19, NroLinDet=1):
        self._valor_iva = valor_iva
        util.set_from_keys(self, vals, priorizar=['moneda_decimales', 'PrcItem', 'QtyItem', 'DscItem'])
        if not vals.get('Impuesto'):
            self._impuestos = [Impuestos({})]
        self.uom_id = vals.get('UnmdItem', 'Unid')
        self._compute_price()

    @property
    def CodImpAdic(self):
        if not hasattr(self, '_cod_imp_adic'):
            return []
        return self._cod_imp_adic

    @CodImpAdic.setter
    def CodImpAdic(self, val):
        self._cod_imp_adic = val

    @property
    def CdgItem(self):
        if not hasattr(self, '_cdgs'):
            return []
        return self._cdgs

    @CdgItem.setter
    def CdgItem(self, cdgs):
        if not hasattr(self, '_cdgs'):
            self._cdgs = []
        if type(cdgs) is dict:
            self._cdgs.append(cdgs)
        else:
            for cdg in cdgs:
                self._cdgs.append(cdg)

    @property
    def DscItem(self):
        if not hasattr(self, '_dsc_item'):
            return False
        return self._dsc_item

    @DscItem.setter
    def DscItem(self, val):
        self._dsc_item = val

    @property
    def DctoOtrMnda(self):
        if not hasattr(self, '_dcto_otr_mnda'):
            return False
        return self._dcto_otr_mnda

    @DctoOtrMnda.setter
    def DctoOtrMnda(self, val):
        self._dcto_otr_mnda = val

    @property
    def DescuentoMonto(self):
        if not hasattr(self, '_descuento_monto'):
            return 0.0
        return self._descuento_monto

    @DescuentoMonto.setter
    def DescuentoMonto(self, val):
        if type(val) is str:
            val = val.replace(',', '.')
        mnt = util.round0(float(val))
        self._descuento_monto = mnt

    @property
    def DescuentoPct(self):
        if not hasattr(self, '_descuento_pct'):
            return 0.0
        return self._descuento_pct

    @DescuentoPct.setter
    def DescuentoPct(self, val):
        if type(val) is str:
            val = val.replace(',', '.')
        self._descuento_pct = round(float(val), 4)

    @property
    def FctConv(self):
        if not hasattr(self, '_fct_conv'):
            return False
        return self._fct_conv

    @FctConv.setter
    def FctConv(self, val):
        self._fct_conv = val

    @property
    def IndExe(self):
        if not hasattr(self, '_ind_exe'):
            return False
        return self._ind_exe

    @IndExe.setter
    def IndExe(self, val):
        self._ind_exe = val

    @property
    def Impuesto(self):
        if not hasattr(self, '_impuestos'):
            return []
        return self._impuestos

    @Impuesto.setter
    def Impuesto(self, vals):
        if self.IndExe:
            return False
        if not vals:
            return vals
        self._impuestos = []
        for tax in vals:
            if not tax.get('CodImp') or tax['CodImp'] in [14, 15]:
                tax['TasaImp'] = self._valor_iva
            if not tax.get('CodImp') and tax['TasaImp'] == self._valor_iva:
                tax['CodImp'] = 14
            impuesto = Impuestos(tax)
            if impuesto.TasaImp < 0:
                mnt_imp = impuesto.calcular(self.PrcItem, self.QtyItem) * -1
                self._dsc_item = '{0} Impuesto específico {1} negativo de {2}'.format(
                    self._dsc_item,
                    impuesto.mepco.replace('_', ' '),
                    str(mnt_imp)
                )
            self._impuestos.append(impuesto)
        self._compute_price()

    @property
    def Moneda(self):
        if not hasattr(self, '_moneda'):
            return False
        return self._moneda

    @Moneda.setter
    def Moneda(self, val):
        self._moneda = val

    @property
    def moneda_decimales(self):
        if not hasattr(self, '_moneda_decimales'):
            return 0
        return self._moneda_decimales

    @moneda_decimales.setter
    def moneda_decimales(self, val):
        self._moneda_decimales = val

    @property
    def MontoItem(self):
        if not hasattr(self, '_monto_item'):
            return 0
        return self._monto_item

    @MontoItem.setter
    def MontoItem(self, val):
        if type(val) is str:
            val = val.replace(',', '.')
        self._monto_item = util.round0(float(val))

    @property
    def MontoItemOtrMnda(self):
        if not hasattr(self, '_monto_item_otr_mnda'):
            return 0
        return self._monto_item_otr_mnda

    @MontoItemOtrMnda.setter
    def MontoItemOtrMnda(self, val):
        if type(val) is str:
            val = val.replace(',', '.')
        self._monto_item_otr_mnda = round(float(val), 4)

    @property
    def NmbItem(self):
        if not hasattr(self, '_name'):
            dsc = self.DscItem
            if not dsc:
                return ''
        else:
            dsc = self._name
        return util._acortar_str(dsc, 80)

    @NmbItem.setter
    def NmbItem(self, val):
        self._name = val

    @property
    def NroLinDet(self):
        if not hasattr(self, '_nro_lin_det'):
            return 1
        return self._nro_lin_det

    @NroLinDet.setter
    def NroLinDet(self, val):
        self._nro_lin_det = int(val)

    @property
    def OtrMnda(self):
        if not self.PrcOtrMon:
            return False
        otrmnda = collections.OrderedDict()
        otrmnda['PrcOtrMon'] = self.PrcOtrMon
        otrmnda['Moneda'] = self.Moneda
        otrmnda['FctConv'] = self.FctConv
        if self.DctoOtrMnda:
            otrmnda['DctoOtrMnda'] = self.DctoOtrMnda
        if self.RecargoOtrMnda:
            otrmnda['RecargoOtrMnda'] = self.RecargoOtrMnda
        otrmnda['MontoItemOtrMnda'] = self.MontoItemOtrMnda
        return otrmnda

    @OtrMnda.setter
    def OtrMnda(self, vals):
        util.set_from_keys(self, vals)

    @property
    def PrcItem(self):
        if not hasattr(self, '_prc_item'):
            return False
        return self._prc_item

    @PrcItem.setter
    def PrcItem(self, val):
        prc_item = val
        if type(val) is str:
            prc_item = val.replace(',', '.')
        self._prc_item = round(float(prc_item), 4)

    @property
    def PrcOtrMon(self):
        if not hasattr(self, '_prc_otr_mon'):
            return False
        return self._prc_otr_mon

    @PrcOtrMon.setter
    def PrcOtrMon(self, val):
        self._prc_otr_mon = val

    @property
    def QtyItem(self):
        if not hasattr(self, '_qty_item'):
            return 0
        return self._qty_item

    @QtyItem.setter
    def QtyItem(self, val):
        qty_item = val
        if type(val) is str:
            qty_item = val.replace(',', '.')
        self._qty_item = round(float(qty_item), 4)

    @property
    def RecargoOtrMnda(self):
        if not hasattr(self, '_recargo_otr_mnda'):
            return False
        return self._recargo_otr_mnda

    @RecargoOtrMnda.setter
    def RecargoOtrMnda(self, val):
        self._recargo_otr_mnda = val

    @property
    def RecargoMonto(self):
        if not hasattr(self, '_recargo_monto'):
            return 0.0
        return self._recargo_monto

    @RecargoMonto.setter
    def RecargoMonto(self, val):
        if type(val) is str:
            val = val.replace(',', '.')
        mnt = util.round0(float(val))
        self._recargo_monto = mnt

    @property
    def RecargoPct(self):
        if not hasattr(self, '_recargo_pct'):
            return 0.0
        return self._recargo_pct

    @RecargoPct.setter
    def RecargoPct(self, val):
        if type(val) is str:
            val = val.replace(',', '.')
        self._recargo_pct = round(float(val), 4)

    @property
    def UnmdItem(self):
        if not hasattr(self, '_unidad_item'):
            return ''
        return self._unidad_item

    @UnmdItem.setter
    def UnmdItem(self, val):
        self._unidad_item = val

    def _compute_price(self):
        total = self.QtyItem * self.PrcItem
        DescuentoMonto = self.DescuentoMonto
        RecargoMonto = self.RecargoMonto
        if self.DescuentoPct > 0 and not self.DescuentoMonto:
            DescuentoMonto = (total * ((self.DescuentoPct or 0.0) / 100.0))
            self.DescuentoMonto = DescuentoMonto
        if DescuentoMonto > 0:
            total -= DescuentoMonto
        if self.RecargoPct > 0 and not self.RecargoMonto:
            RecargoMonto = (total * ((self.RecargoPct or 0.0) / 100.0))
            self.RecargoMonto = RecargoMonto
        if RecargoMonto > 0:
            total += RecargoMonto
        if not self.MontoItem:
            self.MontoItem = total
