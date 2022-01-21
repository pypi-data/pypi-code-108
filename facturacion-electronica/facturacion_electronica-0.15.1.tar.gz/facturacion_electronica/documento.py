# -*- coding: utf-8 -*-
from facturacion_electronica.dte import DTE
from facturacion_electronica.documento_exportacion import Exportacion
from facturacion_electronica.documento_linea import LineaDetalle
from facturacion_electronica.documento_referencias import Referencia
from facturacion_electronica.linea_impuesto import LineaImpuesto
from facturacion_electronica.receptor import Recep
from facturacion_electronica.clase_util import UserError
from facturacion_electronica.impuestos import Impuestos
from facturacion_electronica.global_descuento_recargo import GlobalDescuentoRecargo as GDR
from facturacion_electronica import clase_util as util
from datetime import datetime
import collections
import re
import decimal
decimal.getcontext().rounding = decimal.ROUND_HALF_UP
import logging
_logger = logging.getLogger(__name__)


class Documento(DTE):

    def __init__(self, vals, emisor=False, resumen=False, tipo_dte=33):
        if emisor:
            self._dte_emisor = emisor
        self.TipoDTE = tipo_dte
        self.resumen = resumen
        priorizar = ['Emisor', 'moneda_decimales', 'TasaIVA', 'MntIVA', 'IVA']
        util.set_from_keys(self, vals, priorizar=priorizar)
        if 'codigo_vendedor' in vals:
            self.CodVndor = vals['codigo_vendedor']
        if 'codigo_caja' in vals:
            self.CodCaja = vals['codigo_caja']
        if vals.get('ticket'):
            self.TpoImpresion = 'T'
        #if self.es_boleta(False):
        #    if not self._resumen and (not self.CodCaja or not self.CodVndor):
        #        print("Debe Ingresar código de vendedor  y de caja")

    @property
    def Anulado(self):
        if not hasattr(self, '_anulado'):
            return False
        return self._anulado

    @Anulado.setter
    def Anulado(self, val):
        self._anulado = val

    @property
    def Aduana(self):
        if not hasattr(self, '_aduana'):
            return False
        Aduana = collections.OrderedDict()
        aduana = self._aduana
        if self.IndServicio in [3,4,5]:
            aduana.CodModVenta = 1
        if aduana.CodModVenta:
            Aduana['CodModVenta'] = aduana.CodModVenta
        elif not self.es_nc_exportacion:
            raise UserError("Debe Ingresar Modalidad de Venta")
        if aduana.CodClauVenta and not aduana.CodModVenta:
            raise UserError("Debe Ingresar un Término de Pago")
        if aduana.CodClauVenta:
            Aduana['CodClauVenta'] = aduana.CodClauVenta
        if aduana.TotClauVenta and aduana.CodClauVenta != 32:
            Aduana['TotClauVenta'] = aduana.TotClauVenta
        if aduana.CodViaTransp:
            Aduana['CodViaTransp'] = aduana.CodViaTransp
        if aduana.NombreTransp:
            Aduana['NombreTransp'] = aduana.NombreTransp
        if aduana.RUTCiaTransp:
            Aduana['RUTCiaTransp'] = aduana.RUTCiaTransp
        if aduana.NomCiaTransp:
            Aduana['NomCiaTransp'] = aduana.NomCiaTransp
        #Aduana['IdAdicTransp'] = self.indicador_adicional
        if aduana.CodPtoEmbarque:
            Aduana['CodPtoEmbarque'] = aduana.CodPtoEmbarque
        #Aduana['IdAdicPtoEmb'] = expo.ind_puerto_embarque
        if aduana.CodPtoDesemb:
            Aduana['CodPtoDesemb'] = aduana.CodPtoDesemb
        #Aduana['IdAdicPtoDesemb'] = expo.ind_puerto_desembarque
        if aduana.Tara:
            Aduana['Tara'] = aduana.Tara
        if aduana.CodUnidMedTara:
            Aduana['CodUnidMedTara'] = aduana.CodUnidMedTara
        if aduana.PesoBruto:
            Aduana['PesoBruto'] = aduana.PesoBruto
        if aduana.CodUnidPesoBruto:
            Aduana['CodUnidPesoBruto'] = aduana.CodUnidPesoBruto
        if aduana.PesoNeto:
            Aduana['PesoNeto'] = aduana.PesoNeto
        if aduana.CodUnidPesoNeto:
            Aduana['CodUnidPesoNeto'] = aduana.CodUnidPesoNeto
        if aduana.TotItems:
            Aduana['TotItems'] = aduana.TotItems
        if aduana.TotBultos:
            bultos = []
            for b in aduana.Bultos:
                bulto = collections.OrderedDict()
                bulto['CodTpoBultos'] = b.CodTpoBultos
                bulto['CantBultos'] = b.CantBultos
                if b.Marcas:
                    bulto['Marcas'] = b.Marcas
                if b.IdContainer:
                    bulto['IdContainer'] = b.IdContainer
                    bulto['Sello'] = b.Sello
                    bulto['EmisorSello'] = b.EmisorSello
                bultos.append(bulto)
            Aduana['TotBultos'] = aduana.TotBultos
            Aduana['TipoBultos'] = bultos
        #Aduana['Marcas'] =
        #Solo si es contenedor
        #Aduana['IdContainer'] =
        #Aduana['Sello'] =
        #Aduana['EmisorSello'] =
        if aduana.MntFlete:
            Aduana['MntFlete'] = aduana.MntFlete
        if aduana.MntSeguro:
            Aduana['MntSeguro'] = aduana.MntSeguro
        if aduana.CodPaisRecep:
            Aduana['CodPaisRecep'] = aduana.CodPaisRecep
        if aduana.CodPaisDestin:
            Aduana['CodPaisDestin'] = aduana.CodPaisDestin
        return Aduana

    @Aduana.setter
    def Aduana(self, vals):
        self._aduana = Exportacion(vals)

    @property
    def CiudadDest(self):
        if not hasattr(self, '_ciudad_dest'):
            return False
        return self._ciudad_dest

    @CiudadDest.setter
    def CiudadDest(self, val):
        self._ciudad_dest = val

    @property
    def Chofer(self):
        if not hasattr(self, '_chofer'):
            return False
        return self._nombre_chofer

    @Chofer.setter
    def Chofer(self, vals):
        util.set_from_keys(self, vals)

    @property
    def CodCaja(self):
        if not hasattr(self, '_cod_caja'):
            return False
        return self._cod_caja

    @CodCaja.setter
    def CodCaja(self, val):
        self._cod_caja = val

    @property
    def CodEnvio(self):
        if not hasattr(self, '_cod_envio'):
            return 0
        return self._cod_envio

    @CodEnvio.setter
    def CodEnvio(self, val):
        self._cod_envio = val

    @property
    def CodIVANoRec(self):
        if not hasattr(self, '_no_rec_code'):
            return False
        return self._no_rec_code

    @CodIVANoRec.setter
    def CodIVANoRec(self, val):
        '''
            Integer con una de las opciones
            [
                ('1','Compras destinadas a IVA a generar operaciones no gravados o exentas.'),
                ('2','Facturas de proveedores registrados fuera de plazo.'),
                ('3','Gastos rechazados.'),
                ('4','Entregas gratuitas (premios, bonificaciones, etc.) recibidos.'),
                ('9','Otros.')
            ]
        '''
        self._no_rec_code = val

    @property
    def CodOtroImp(self):
        return self._otroImp

    @CodOtroImp.setter
    def CodOtroImp(self, vals):
        if type(vals) is dict:
            vals = [vals]
        for val in vals:
            tax = {
                    'TasaImp': val['TasaOtroImp'],
                    'CodImp': val['CodOtroImp'],
                    'no_rec': True if val['MontoOtroImpNoRec'] and val['MontoOtroImpNoRec'] > 0 else False,
                    'Retencion': val.get('Retencion')

            }
            otroImp = Impuestos(tax)
            impuesto = LineaImpuesto({
                            'tax_id': otroImp,
                            'base': self.neto,
                            'MontoImp': vals.get('MontoOtroImp', 19),
                            'moneda_decimales': self.moneda_decimales,
                            })
            self.impuestos = impuesto

    @property
    def CodRchDsc(self):
        if not hasattr(self, '_cod_rch_dsc'):
            return -1
        return self._cod_rch_dsc

    @CodRchDsc.setter
    def CodRchDsc(self, val):
        self._cod_rch_dsc = val

    @property
    def CodVndor(self):
        if not hasattr(self, '_cod_vndor'):
            return False
        return self._cod_vndor

    @CodVndor.setter
    def CodVndor(self, val):
        self._cod_vndor = val

    @property
    def CmnaDest(self):
        if not hasattr(self, '_cmna_dest'):
            return False
        return self._cmna_dest

    @CmnaDest.setter
    def CmnaDest(self, val):
        self._cmna_dest = val

    @property
    def CredEC(self):
        if not hasattr(self, '_credec'):
            return False
        return self._credec

    @CredEC.setter
    def CredEC(self, val):
        self._credec = val

    @property
    def Declaracion(self):
        if not hasattr(self, '_declaracion'):
            return 'El acuse de recibo que se declara en\
 este acto, de acuerdo a lo dispuesto en la letra b) del Art. 4, y la letra c)\
 del Art. 5 de la Ley 19.983, acredita que la entrega de mercaderias\
 o servicio(s) prestado(s) ha(n) sido recibido(s).'
        return self._declaracion

    @Declaracion.setter
    def Declaracion(self, val):
        self._declaracion = val

    @property
    def Detalle(self):
        if not hasattr(self, '_lineas_detalle'):
            return []
        line_number = 1
        invoice_lines = []
        for line in self._lineas_detalle:
            lines = collections.OrderedDict()
            lines['NroLinDet'] = line_number
            if line.CdgItem:
                cdg_items = []
                for cdg in line.CdgItem:
                    if cdg.get('VlrCodigo') == 'NO_PRODUCT':
                        no_product = True
                    else:
                        cdg_line = collections.OrderedDict()
                        cdg_line['TpoCodigo'] = cdg.get('TpoCodigo', 'INT1')
                        cdg_line['VlrCodigo'] = cdg.get('VlrCodigo', False)
                        cdg_items.append({'CdgItem': cdg_line})
                lines['cdg_items'] = cdg_items
            for t in line.Impuesto:
                taxInclude = t.price_include
            if line.IndExe:
                lines['IndExe'] = 1
            #if line.product_id.type == 'events':
            #   lines['ItemEspectaculo'] =
#            if self.es_boleta():
#                lines['RUTMandante']
            lines['NmbItem'] = line.NmbItem
            lines['DscItem'] = line.DscItem #descripción más extenza
            if line.CdgItem:
                lines['NmbItem'] = line.NmbItem
            #lines['InfoTicket']
            if line.QtyItem > 0:
                lines['QtyItem'] = line.QtyItem
                lines['UnmdItem'] = line.uom_id[:4]
            elif line.QtyItem < 0:
                raise UserError("NO puede ser menor que 0")
            if line.PrcItem:
                lines['PrcItem'] = line.PrcItem
            if line.OtrMnda:
                lines['OtrMnda'] = line.OtrMnda
            if line.DescuentoMonto > 0:
                if line.DescuentoPct:
                    lines['DescuentoPct'] = line.DescuentoPct
                lines['DescuentoMonto'] = line.DescuentoMonto
            if line.RecargoMonto > 0:
                if line.RecargoPct:
                    lines['RecargoPct'] = line.RecargoPct
                lines['RecargoMonto'] = line.RecargoMonto
            if not self.es_boleta():
                if line.CodImpAdic:
                    lines['CodImpAdic'] = line.CodImpAdic
                else:
                    for imp in line.Impuesto:
                        if imp.es_adicional:
                            lines['CodImpAdic'] = imp.CodImp
            lines['MontoItem'] = line.MontoItem
            line_number += 1
            invoice_lines.append({'Detalle': lines})
            if line.IndExe and not self.es_boleta():
                self.MntBruto = False
        return invoice_lines

    @Detalle.setter
    def Detalle(self, vals=[]):
        if type(vals) is dict:
            vals = [vals]
        NroLinDet = 0
        recs = []
        for d in vals:
            NroLinDet += 1
            NroLinDet = d.get('NroLinDet', NroLinDet)
            valor_iva = self.TasaIVA
            d['moneda_decimales'] = self.moneda_decimales
            linea = LineaDetalle(
                            d,
                            self.TpoMoneda,
                            valor_iva=valor_iva,
                            NroLinDet=NroLinDet
                        )
            self.impuestos = linea
            recs.append(linea)
        self._lineas_detalle = sorted(recs, key=lambda l: l.NroLinDet)

    @property
    def DirDest(self):
        if not hasattr(self, '_dir_dest'):
            return False
        return self._dir_dest

    @DirDest.setter
    def DirDest(self, val):
        self._dir_dest = val

    @property
    def DscRcgGlobal(self):
        if not hasattr(self, '_gdrs'):
            return []
        result = []
        lin_dr = 1
        for dr in self._gdrs:
            dr_line = collections.OrderedDict()
            dr_line['NroLinDR'] = dr.NroLinDR
            dr_line['TpoMov'] = dr.TpoMov
            if dr.GlosaDR:
                dr_line['GlosaDR'] = dr.GlosaDR
            dr_line['TpoValor'] = dr.TpoValor
            dr_line['ValorDR'] = dr.ValorDR
            if dr.ValorDROtrMnda:
                dr_line['ValorDROtrMnda'] = dr.ValorDROtrMnda
            if self.TipoDTE in [34] and (
                    self.Referencia and \
                    self._referencias[0].TpoDocRef == '34'):
                dr_line['IndExeDR'] = 1
            result.append({'DscRcgGlobal': dr_line})
            lin_dr += 1
        return result

    @DscRcgGlobal.setter
    def DscRcgGlobal(self, vals=[]):
        """
            "DscRcgGlobal": [
                    {
                        "valor": 500,
                        "tipo": "monto", # monto o porcentaje
                        "glosa": "descripción descuento"
                    },
                ]
        """
        gdrs = []
        for r in vals:
            gdr = GDR(r)
            gdrs.append(gdr)
        self._gdrs = gdrs

    @property
    def Encabezado(self):
        if not self.IdDoc:
            return False
        encabezado = collections.OrderedDict()
        encabezado['IdDoc'] = self.IdDoc
        encabezado['Emisor'] = self.Emisor
        encabezado['Receptor'] = self.Receptor
        if self.Transporte:
            encabezado['Transporte'] = self.Transporte
        encabezado['Totales'] = self.Totales
        if self.OtraMoneda or self.es_exportacion:
            encabezado['OtraMoneda'] = self.OtraMoneda
        return encabezado

    @Encabezado.setter
    def Encabezado(self, vals={}):
        util.set_from_keys(self, vals)

    @property
    def es_exportacion(self):
        return self.TipoDTE in [110] or self.es_nc_exportacion

    @property
    def es_guia(self):
        return self.TipoDTE in [52]

    @property
    def es_nc_exportacion(self):
        return self.TipoDTE in [111, 112]

    @property
    def EstadoDTE(self):
        if not hasattr(self, '_estado_dte'):
            return 0
        return self._estado_dte

    @EstadoDTE.setter
    def EstadoDTE(self, val):
        self._estado_dte = val

    @property
    def EstadoDTEGlosa(self):
        if not hasattr(self, '_estado_dte_glosa'):
            return ''
        return self._estado_dte_glosa

    @EstadoDTEGlosa.setter
    def EstadoDTEGlosa(self, val):
        self._estado_dte_glosa = val

    @property
    def FchVenc(self):
        if not hasattr(self, '_fch_venc'):
            return datetime.strftime(datetime.now(), '%Y-%m-%d')
        return self._fch_venc

    @FchVenc.setter
    def FchVenc(self, val):
        self._fch_venc = util.get_fecha(val)

    @property
    def FchEmis(self):
        if not hasattr(self, '_fch_emis'):
            return datetime.strftime(datetime.now(), '%Y-%m-%d')
        return self._fch_emis

    @FchEmis.setter
    def FchEmis(self, val):
        self._fch_emis = util.get_fecha(val)

    @property
    def FechaEmis(self):
        return self.FchEmis

    @FechaEmis.setter
    def FechaEmis(self, val):
        self.FchEmis = val

    @property
    def FechaVenc(self):
        return self.FchVenc

    @FechaVenc.setter
    def FechaVenc(self, val):
        self.FchVenc = val

    @property
    def FmaPago(self):
        if not hasattr(self, '_fma_pago'):
            return 1
        return self._fma_pago

    @FmaPago.setter
    def FmaPago(self, val):
        '''
            [
                ('1','Contado'),
                ('2','Crédito'),
                ('3','Gratuito')
            ]
        '''
        self._fma_pago = val

    @property
    def FmaPagExp(self):
        if not hasattr(self, '_fma_pago_exp'):
            return False
        return self._fma_pago_exp

    @FmaPagExp.setter
    def FmaPagExp(self, val):
        self._fma_pago_exp = val

    @property
    def Folio(self):
        if not hasattr(self, '_folio'):
            return 0
        return self._folio

    @Folio.setter
    def Folio(self, val):
        self._folio = int(val)

    @property
    def IdDoc(self):
        IdDoc = collections.OrderedDict()
        if not hasattr(self, '_tpo_dte'):
            return False
        IdDoc['TipoDTE'] = self.TipoDTE
        IdDoc['Folio'] = self.Folio
        IdDoc['FchEmis'] = self.FechaEmis
        if self.IndServicio:
            IdDoc['IndServicio'] = self.IndServicio
        if self.TipoDespacho:
            IdDoc['TipoDespacho'] = self.TipoDespacho
        if self.IndTraslado:
            IdDoc['IndTraslado'] = self.IndTraslado
        if self.TpoImpresion:
            IdDoc['TpoImpresion'] = self.TpoImpresion
        #if self.tipo_servicio:
        #    Encabezado['IdDoc']['IndServicio'] = 1,2,3,4
        # todo: forma de pago y fecha de vencimiento - opcional
        if self.MntBruto and self.MntExe == 0 and not self.es_boleta():
            IdDoc['MntBruto'] = 1
        if not self.es_boleta() and not self.es_guia:
            if not self.es_exportacion:
                IdDoc['FmaPago'] = self.FmaPago
            if self.FmaPagExp:
                IdDoc['FmaPagExp'] = self.FmaPagExp
        if self.IndMntNeto:
            IdDoc['IndMntNeto'] = 2
        #if self.es_boleta():
            #Servicios periódicos
        #    IdDoc['PeriodoDesde'] =
        #    IdDoc['PeriodoHasta'] =
        if not self.es_boleta() and self.FmaPago == 2:
            IdDoc['FchVenc'] = self.FchVenc
        return IdDoc

    @IdDoc.setter
    def IdDoc(self, vals={}):
        util.set_from_keys(self, vals)

    @property
    def impuestos(self):
        _impuestos = []
        if not hasattr(self, '_impuestos'):
            return _impuestos
        for k, v in self._impuestos.items():
            _impuestos.append(v)
        return _impuestos

    @impuestos.setter
    def impuestos(self, linea):
        if not linea:
            return
        if not hasattr(self, '_impuestos'):
            self._impuestos = {}

        def set_impuesto(val, base=0, cantidad=0):
            imp = False
            if not isinstance(val, LineaImpuesto):
                imp = self._impuestos.get(str(val.CodImp), False)
            if not imp:
                if isinstance(val, LineaImpuesto):
                    imp = val
                else:
                    imp = LineaImpuesto({
                                'tax_id': val,
                                'base': 0,
                                'MontoImp': 0,
                                'moneda_decimales': self.moneda_decimales,
                                }
                            )
                    if val.especifico:
                        imp.cantidad = cantidad
            imp.base += base
            imp._compute_tax()
            if imp.tax_id.es_retencion:
                self._imp_reten = True
            self._impuestos[str(imp.tax_id.CodImp)] = imp
        if isinstance(linea, LineaImpuesto):
            set_impuesto(linea)
        elif type(linea) is list:
            for l in linea:
                for i in l.Impuesto:
                    set_impuesto(i, l.MontoItem, l.QtyItem)
        else:
            for i in linea.Impuesto:
                set_impuesto(i, linea.MontoItem, linea.QtyItem)

    @property
    def impuesto_incluido(self):
        return self.MntBruto

    @property
    def ImptoReten(self):
        if not hasattr(self, '_imp_reten'):
            self._imp_reten = 0
            for li in self.impuestos:
                if li.tax_id.es_adicional:
                    self._imp_reten += li.MontoImp
            self._imp_reten = self._aplicar_dsc_rcg(self._imp_reten)
        return self._imp_reten

    @ImptoReten.setter
    def ImptoReten(self, vals):
        otros_imp = 0
        for val in vals:
            tax = {
                 'TasaImp': val.get('TasaImp', self.TasaImp),
                 'CodImp': val.get('TipoImp', 15),
                 'Retencion': val.get('Retencion', 0),
                 'moneda_decimales': self.moneda_decimales,
            }
            iva = Impuestos(tax)
            impuesto = LineaImpuesto({
                                    'tax_id': iva,
                                    'MontoImp': val.get('MontoImpt', 0),
                                    'moneda_decimales': self.moneda_decimales,
                                })
            self.impuestos = impuesto
            otros_imp += impuesto.MontoImp
        if not hasattr(self, '_imp_reten'):
            otros_imp = self._aplicar_dsc_rcg(otros_imp)
        self._imp_reten = otros_imp

    @property
    def ImptoRetenOtrMnda(self):
        if not hasattr(self, '_imp_reten_otr_mnda'):
            return 0
        return self._imp_reten_otr_mnda

    @ImptoRetenOtrMnda.setter
    def ImptoRetenOtrMnda(self, val):
        self._imp_reten_otr_mnda = val

    @property
    def IndMntNeto(self):
        if not hasattr(self, '_ind_mnt_neto'):
            return False
        self._ind_mnt_neto

    @IndMntNeto.setter
    def IndMntNeto(self, val):
        self._ind_mnt_neto = val

    @property
    def IndTraslado(self):
        if not hasattr(self, '_ind_traslado'):
            return False
        return self._ind_traslado

    @IndTraslado.setter
    def IndTraslado(self, val):
        self._ind_traslado = int(val)

    @property
    def IndServicio(self):
        if not hasattr(self, '_ind_servicio'):
            return False
        return self._ind_servicio

    @IndServicio.setter
    def IndServicio(self, val):
        self._ind_servicio = val

    @property
    def IVA(self):
        return self.MntIVA

    @IVA.setter
    def IVA(self, val):
        self.MntIVA = val

    @property
    def IVAOtrMnda(self):
        if not hasattr(self, '_iva_otr_mnda'):
            return 0
        return self._iva_otr_mnda

    @IVAOtrMnda.setter
    def IVAOtrMnda(self, val):
        self._iva_otr_mnda = val

    @property
    def IVAUsoComun(self):
        if not hasattr(self, '_iva_uso_comun'):
            return 0
        return self.MntIVA

    @IVAUsoComun.setter
    def IVAUsoComun(self, val):
        if not val:
            return
        self._iva_uso_comun = val

    @property
    def MntActivoFijo(self):
        if not hasattr(self, '_activo_fijo'):
            return 0
        return self._activo_fijo

    @MntActivoFijo.setter
    def MntActivoFijo(self, val):
        tax = {
             'TasaImp': val.get('TasaImp', 19),
             'CodImp': val.get('CodImp', 14),
             'TpoImp': val.get('TpoImp', 1),
        }
        iva = Impuestos(tax)
        impuesto = LineaImpuesto({
                                'tax_id': iva,
                                'base': val,
                                'ActivoFijo': True,
                                'moneda_decimales': self.moneda_decimales,
                                })
        impuesto._compute_tax()
        self.MntIVAActivoFijo = impuesto.MontoImp
        self.impuesto = impuesto
        self.activo_fijo = val

    @property
    def MntBruto(self):
        if not hasattr(self, '_mnt_bruto'):
            return False
        return self._mnt_bruto

    @MntBruto.setter
    def MntBruto(self, val):
        self._mnt_bruto = val

    @property
    def MntExe(self):
        if not hasattr(self, '_mnt_exe'):
            self._mnt_exe = 0
            for li in self.impuestos:
                if li.tax_id.TasaImp == 0:
                    self._mnt_exe += li.MontoImp
            self._mnt_exe = self._aplicar_dsc_rcg(self._mnt_exe, False, True)
        return self._mnt_exe

    @MntExe.setter
    def MntExe(self, val):
        val = float(val)
        if val == 0:
            return 0
        tax = {
                'TasaImp': 0,
                'CodImp': 0,
            }
        '''
        exento = Impuestos(tax)
        impuesto = LineaImpuesto({
                        'tax_id': exento,
                        'base': val,
                        'MontoImp': val,
                        })
        self.impuestos = impuesto'''
        val = round(val, self.moneda_decimales)
        decimal.getcontext().rounding = decimal.ROUND_HALF_UP
        self._mnt_exe = int(decimal.Decimal(val).to_integral_value())

    @property
    def MntExeOtrMnda(self):
        if not hasattr(self, '_mnt_exe_otr_mnda'):
            return 0
        return self._mnt_exe_otr_mnda

    @MntExeOtrMnda.setter
    def MntExeOtrMnda(self, val):
        val = float(val)
        self._mnt_exe_otr_mnda = round(val)

    @property
    def MntFaeCarneOtrMnda(self):
        if not hasattr(self, '_mnt_fae_carne_otr_mnda'):
            return 0
        return self._mnt_fae_carne_otr_mnda

    @MntFaeCarneOtrMnda.setter
    def MntFaeCarneOtrMnda(self, val):
        return self._mnt_fae_carne_otr_mnda

    @property
    def MntIVA(self):
        if not hasattr(self, '_mnt_iva'):
            self._mnt_iva = 0
            for li in self.impuestos:
                if li.tax_id.TasaImp == self.TasaIVA:
                    if li.base == 0 and self.resumen:
                        li.base = self.MntNeto
                    li._compute_tax()
                    self._mnt_iva += li.MontoImp
            self._mnt_iva = self._aplicar_dsc_rcg(self._mnt_iva)
        return self._mnt_iva

    @MntIVA.setter
    def MntIVA(self, val):
        val = float(val)
        val = round(val, self.moneda_decimales)
        if self.moneda_decimales == 0:
            val = int(val)
        self._mnt_iva = val

    @property
    def MntIVAActivoFijo(self):
        if not hasattr(self, '_iva_activo_fijo'):
            return 0
        return self._iva_activo_fijo

    @MntIVAActivoFijo.setter
    def MntIVAActivoFijo(self, val):
        self._iva_activo_fijo = val

    @property
    def MntIVANoRec(self):
        if not hasattr(self, '_iva_no_rec'):
            if self.CodIVANoRec:
                return self.IVA
            return 0
        return self._iva_no_rec

    @MntIVANoRec.setter
    def MntIVANoRec(self, val):
        self._iva_no_rec = val

    @property
    def MntNeto(self):
        if not hasattr(self, '_mnt_neto'):
            self._mnt_neto = 0
            for li in self.impuestos:
                if li.tax_id.TasaImp == self.TasaIVA:
                    self._mnt_neto += li.base
            self._mnt_neto = self._aplicar_dsc_rcg(self._mnt_neto)
        return self._mnt_neto

    @MntNeto.setter
    def MntNeto(self, val):
        val = float(val)
        if self.resumen and self.MntIVA == 0:
            tax = {
                'TasaImp': 19,
                'CodImp': 14,
                'TpoImp': 1
            }
            iva = Impuestos(tax)
            impuesto = LineaImpuesto({
                                'tax_id': iva,
                                'base': val,
                                'moneda_decimales': self.moneda_decimales,
                                })
            self.impuestos = impuesto
        decimal.getcontext().rounding = decimal.ROUND_HALF_UP
        self._mnt_neto = int(decimal.Decimal(val).to_integral_value())

    @property
    def MontoOtroImpNoRec(self):
        return

    @property
    def MntTotal(self):
        if not hasattr(self, '_mnt_total'):
            self._mnt_total = self.MntExe + self.MntNeto + self.MntIVA + self.ImptoReten
        return self._mnt_total

    @MntTotal.setter
    def MntTotal(self, val):
        val = float(val)
        decimal.getcontext().rounding = decimal.ROUND_HALF_UP
        monto_total = int(decimal.Decimal(val).to_integral_value())
        if self.no_product:
            monto_total = 0
        self._mnt_total = monto_total

    @property
    def MntNetoOtrMnda(self):
        if not hasattr(self, '_mnt_neto_otr_mnda'):
            return 0
        return self._mnt_neto_otr_mnda

    @MntNetoOtrMnda.setter
    def MntNetoOtrMnda(self, val):
        self._mnt_neto_otr_mnda = val

    @property
    def MntTotOtrMnda(self):
        if not hasattr(self, '_mnt_total_otr_mnda'):
            self._mnt_total_otr_mnda = self.MntExeOtrMnda + self.MntNetoOtrMnda + self.IVAOtrMnda + self.ImptoRetenOtrMnda
        return self._mnt_total_otr_mnda

    @MntTotOtrMnda.setter
    def MntTotOtrMnda(self, val):
        val = float(val)
        monto_total = val
        if self.no_product:
            monto_total = 0
        self._mnt_total_otr_mnda = monto_total

    @property
    def moneda_decimales(self):
        if not hasattr(self, '_moneda_decimales'):
            return 0
        return self._moneda_decimales

    @moneda_decimales.setter
    def moneda_decimales(self, val):
        self._moneda_decimales = val

    @MontoOtroImpNoRec.setter
    def MontoOtroImpNoRec(self, vals):
        tax = {
                'TasaImp': -1,
                'CodImp': -1,
                'no_rec': True,
            }
        no_rec = Impuestos(tax)
        impuesto = LineaImpuesto({
                        'tax_id': no_rec,
                        'base': 1,
                        'MontoImp': vals['MontoOtroImpNoRec'],
                        'moneda_decimales': self.moneda_decimales,
                        })
        self.impuestos = impuesto

    @property
    def no_product(self):
        if not hasattr(self, '_no_product'):
            return False
        return self._no_product

    @no_product.setter
    def no_product(self, val):
        self._no_product = val

    @property
    def NombreChofer(self):
        if not hasattr(self, '_nombre_chofer'):
            return False
        return self._nombre_chofer

    @NombreChofer.setter
    def NombreChofer(self, val):
        self._nombre_chofer = val

    @property
    def NroDTE(self):
        if not hasattr(self, '_nro_dte'):
            return 1
        return self._nro_dte

    @NroDTE.setter
    def NroDTE(self, val):
        self._nro_dte = int(val)

    @property
    def Patente(self):
        if not hasattr(self, '_patente'):
            return False
        return self._patente

    @property
    def OtraMoneda(self):
        if not self.TpoCambio:
            return False
        Totales = collections.OrderedDict()
        Totales['TpoMoneda'] = self.TpoMonedaOtr
        Totales['TpoCambio'] = self.TpoCambio
        if self.FmaPagExp == '21':
            Totales['MntExeOtrMnda'] = '0.0'
            Totales['MntTotOtrMnda'] = '0.0'
            return Totales
        if self.MntNetoOtrMnda:
            Totales['MntNetoOtrMnda'] = self.MntNetoOtrMnda
        if self.MntExeOtrMnda:
            Totales['MntExeOtrMnda'] = self.MntExeOtrMnda
        if self.MntFaeCarneOtrMnda:
            Totales['MntFaeCarneOtrMnda'] = self.MntFaeCarneOtrMnda
        if self.IVAOtrMnda:
            Totales['IVAOtrMnda'] = self.IVAOtrMnda
        Totales['MntTotOtrMnda'] = self.MntTotOtrMnda
        #Totales['MontoNF']
        #Totales['TotalPeriodo']
        #Totales['SaldoAnterior']
        #Totales['VlrPagar']
        return Totales

    @OtraMoneda.setter
    def OtraMoneda(self, vals):
        if vals.get('TpoMoneda'):
            vals['TpoMonedaOtr'] = vals['TpoMoneda']
            del vals['TpoMoneda']
        util.set_from_keys(self, vals)

    @Patente.setter
    def Patente(self, val):
        self._patente = val

    @property
    def Receptor(self):
        if not hasattr(self, '_receptor'):
            self.Receptor = {}
        Receptor = collections.OrderedDict()
        #if self.es_boleta():
        #    Receptor['CdgIntRecep']
        Receptor['RUTRecep'] = '55555555-5' if self.es_exportacion else self._receptor.RUTRecep
        Receptor['RznSocRecep'] = self._receptor.RznSocRecep
        if self._receptor.Nacionalidad:
            Receptor['Extranjero'] = collections.OrderedDict()
            Receptor['Extranjero']['Nacionalidad'] = self._receptor.Nacionalidad
        if not self.es_boleta() and not self.es_exportacion:
            Receptor['GiroRecep'] = self._receptor.GiroRecep
        if self._receptor.Contacto:
            Receptor['Contacto'] = self._receptor.Contacto
        if self._receptor.CorreoRecep and not self.es_boleta():
            Receptor['CorreoRecep'] = self._receptor.CorreoRecep
        if self._receptor.DirRecep:
            Receptor['DirRecep'] = self._receptor.DirRecep
        if not self.es_exportacion:
            Receptor['CmnaRecep'] = self._receptor.CmnaRecep
        Receptor['CiudadRecep'] = self._receptor.CiudadRecep
        return Receptor

    @Receptor.setter
    def Receptor(self, vals):
        if not hasattr(self, '_receptor'):
            self._receptor = Recep()
        util.set_from_keys(self._receptor, vals)

    @property
    def Referencia(self):
        if not hasattr(self, '_referencias') or not self._referencias:
            return False
        lin_ref = 1
        ref_lines = []
        for ref in self._referencias:
                ref_line = collections.OrderedDict()
                ref_line['NroLinRef'] = ref.NroLinRef or lin_ref
                if not self.es_boleta():
                    if ref.TpoDocRef:
                        ref_line['TpoDocRef'] = ref.TpoDocRef
                        ref_line['FolioRef'] = ref.FolioRef
                    ref_line['FchRef'] = ref.FchRef or datetime.strftime(
                                            datetime.now(), '%Y-%m-%d')
                if ref.CodRef:
                    ref_line['CodRef'] = ref.CodRef
                    if ref.CodRef == 2:
                        dice = re.compile(r'DICE:(.*)DEBE DECIR:')
                        if len(dice.findall(ref.RazonRef.upper())) == 0:
                            raise UserError('Modificación de texto debe \
llevar estrictamente las palabras Dice: y debe decir:')
                if ref.RazonRef:
                    ref_line['RazonRef'] = ref.RazonRef
                if self.es_boleta():
                    if self.CodVndor:
                        ref_line['CodVndor'] = self.CodVndor
                    if self.CodCaja:
                        ref_line['CodCaja'] = self.CodCaja
                ref_lines.append({'Referencia': ref_line})
                lin_ref += 1
        return ref_lines

    @Referencia.setter
    def Referencia(self, vals=[]):
        self._referencias = []
        for ref in vals:
            self._referencias.append(Referencia(ref))

    @property
    def resumen(self):
        if not hasattr(self, '_resumen'):
            return False
        return self._resumen

    @resumen.setter
    def resumen(self, val):
        self._resumen = val

    @property
    def RUTChofer(self):
        if not hasattr(self, '_rut_chofer'):
            return False
        return self._rut_chofer

    @RUTChofer.setter
    def RUTChofer(self, val):
        self._rut_chofer = util.formatear_rut(val)

    @property
    def RUTTrans(self):
        if not hasattr(self, '_rut_trans'):
            return self.Emisor.RUTEmisor
        return self._rut_trans

    @RUTTrans.setter
    def RUTTrans(self, val):
        self._rut_trans = util.formatear_rut(val)

    @property
    def sii_barcode_img(self):
        if not hasattr(self, '_sii_barcode_img'):
            return False
        return self._sii_barcode_img

    @sii_barcode_img.setter
    def sii_barcode_img(self, val):
        self._sii_barcode_img = val.decode()

    @property
    def TasaImp(self):
        return self.TasaIVA

    @TasaImp.setter
    def TasaImp(self, val):
        self.TasaIVA = round(val, 2)

    @property
    def TasaIVA(self):
        if not hasattr(self, '_tasa_iva'):
            return 19
        return self._tasa_iva

    @TasaIVA.setter
    def TasaIVA(self, val):
        val = float(val)
        self._tasa_iva = round(val, 2)

    @property
    def TermPagoCdg(self):
        if not hasattr(self, '_term_pago_cod'):
            return False
        return self._term_pago_cod

    @TermPagoCdg.setter
    def TermPagoCdg(self, val):
        self._term_pago_cod = val


    @property
    def TipoDespacho(self):
        if not hasattr(self, '_tipo_despacho'):
            return False
        return self._tipo_despacho

    @TipoDespacho.setter
    def TipoDespacho(self, val):
        self._tipo_despacho = int(val)

    @property
    def TipoDTE(self):
        if not hasattr(self, '_tpo_dte'):
            return 33
        return self._tpo_dte

    @TipoDTE.setter
    def TipoDTE(self, val):
        self._tpo_dte = val

    @property
    def Totales(self):
        Totales = collections.OrderedDict()
        if not self.MntTotal or self.no_product:
            Totales['MntTotal'] = 0
            return Totales
        if not self.es_exportacion:
            Totales['MntNeto'] = self.MntNeto
        if self.TpoMoneda:
            Totales['TpoMoneda'] = self.TpoMoneda
        if self.MntExe:
            Totales['MntExe'] = self.MntExe
        if not self.es_exportacion:
            if self.MntIVA:
                if not self.es_boleta():
                    Totales['TasaIVA'] = self.TasaIVA
                Totales['IVA'] = self.MntIVA
            for i in self.impuestos:
                if i.tax_id.es_adicional:
                    Totales['ImptoReten'] = collections.OrderedDict()
                    Totales['ImptoReten']['TipoImp'] = i.tax_id.CodImp
                    Totales['ImptoReten']['TasaImp'] = 1 if i.tax_id.especifico else round(i.tax_id.TasaImp, 2)
                    decimal.getcontext().rounding = decimal.ROUND_HALF_UP
                    mnt_imp = int(decimal.Decimal(i.MontoImp).to_integral_value())
                    Totales['ImptoReten']['MontoImp'] = 1 if mnt_imp < 0 else mnt_imp
        elif self.es_exportacion and self.MntIVA:
            raise UserError("Todos los productos deben ser Exentos")
        if self.CredEC:
            Totales['CredEC'] = self.CredEC
        Totales['MntTotal'] = self.MntTotal
        #Totales['MontoNF']
        #Totales['TotalPeriodo']
        #Totales['SaldoAnterior']
        #Totales['VlrPagar']
        return Totales

    @Totales.setter
    def Totales(self, vals={}):
        util.set_from_keys(self, vals)

    @property
    def TpoImpresion(self):
        if not hasattr(self, '_tpo_impresion'):
            return False
        return self._tpo_impresion

    @TpoImpresion.setter
    def TpoImpresion(self, val):
        self._tpo_impresion = val

    @property
    def TpoCambio(self):
        if not hasattr(self, '_tpo_cambio'):
            return False
        return self._tpo_cambio

    @TpoCambio.setter
    def TpoCambio(self, val):
        self._tpo_cambio = round(float(val), 10)

    @property
    def TpoMoneda(self):
        if not hasattr(self, '_tpo_moneda'):
            return False
        return self._tpo_moneda

    @TpoMoneda.setter
    def TpoMoneda(self, val):
        self._tpo_moneda = val

    @property
    def TpoMonedaOtr(self):
        if not hasattr(self, '_tpo_moneda_otr'):
            return False
        return self._tpo_moneda_otr

    @TpoMonedaOtr.setter
    def TpoMonedaOtr(self, val):
        self._tpo_moneda_otr = val

    @property
    def TpoTranCompra(self):
        if not hasattr(self, '_tpo_tran_compra'):
            return False
        return self._tpo_tran_compra

    @TpoTranCompra.setter
    def TpoTranCompra(self, val):
        self._tpo_tran_compra = val

    @property
    def TpoTranVenta(self):
        if not hasattr(self, '_tpo_tran_venta'):
            return False
        return self._tpo_tran_venta

    @TpoTranVenta.setter
    def TpoTranVenta(self, val):
        self._tpo_tran_venta = val

    @property
    def Transporte(self):
        if not self.IndTraslado and not self.Aduana and not self.es_exportacion:
            return False
        Transporte = collections.OrderedDict()
        if self.Patente:
            Transporte['Patente'] = self.Patente[:8]
        if self.TipoDespacho in [2, 3]:
            if self.TipoDespacho == 2:
                Transporte['RUTTrans'] = self.RUTTrans
            elif self.TipoDespacho == 3:
                if not hasattr(self, '_rut_trans'):
                    raise UserError("Debe especificar el RUT del transportista\
, en su ficha de receptor")
                Transporte['RUTTrans'] = self.RUTTrans
            if self.RUTChofer:
                Transporte['Chofer'] = collections.OrderedDict()
                Transporte['Chofer']['RUTChofer'] = self.RUTChofer
                Transporte['Chofer']['NombreChofer'] = self.NombreChofer[:30]
        if self.IndTraslado:
            Transporte['DirDest'] = self.DirDest
            if self.CmnaDest:
                Transporte['CmnaDest'] = self.CmnaDest[:20]
            Transporte['CiudadDest'] = self.CiudadDest
        if self.Aduana or self.es_exportacion:
            Transporte['Aduana'] = self.Aduana or ''
        return Transporte

    @Transporte.setter
    def Transporte(self, vals):
        util.set_from_keys(self, vals)

    def es_nc_boleta(self):
        boletas = [35, 38, 39, 41, 70, 71]
        return (hasattr(self, '_referencias') and\
                self._referencias and \
                self._referencias[0].TpoDocRef in boletas)

    def es_boleta(self):
        boletas = [35, 38, 39, 41, 70, 71]
        return self.TipoDTE in boletas

    def get_agrupados(self, monto, Afectos=True, Exentos=False):
        result = {'D': 0.00, 'R': 0.00}
        for gdr in self._gdrs:
            if (Afectos and gdr.Afectos) or (Exentos and gdr.Exentos):
                result[gdr.TpoMov] += gdr.get_monto(monto)
        return result

    def _aplicar_dsc_rcg(self, monto, Afectos=True, Exentos=False):
        if not hasattr(self, '_gdrs') or monto == 0:
            return monto
        agrupados = self.get_agrupados(monto, Afectos, Exentos)
        monto_gdr = agrupados['R'] - agrupados['D']
        mn = round(monto + monto_gdr, self.moneda_decimales)
        if self.moneda_decimales == 0:
            return int(mn)
        return mn

    def _es_nota(self):
        return self.TipoDTE in [55, 56, 60, 61, 111, 112]
