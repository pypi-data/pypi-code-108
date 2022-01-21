# -*- coding: utf-8 -*-
from facturacion_electronica.libro_boletas import Boletas
from facturacion_electronica.documento import Documento as Doc
from facturacion_electronica.dte import DTE
from facturacion_electronica.emisor import Emisor
from facturacion_electronica.receptor import Recep
from facturacion_electronica import clase_util as util
from datetime import datetime
import collections
import logging
_logger = logging.getLogger(__name__)


class Libro(object):

    def __init__(self, vals=False):
        if not vals:
            return
        self._iniciar()
        util.set_from_keys(self, vals, priorizar=['TipoOperacion'])

    @property
    def boletas(self):
        if not hasattr(self, '_boletas'):
            return False
        return self._boletas

    @boletas.setter
    def boletas(self, vals):
        _boletas = []
        for b in vals:
            _boletas.append(Boletas(b))
        self._boletas = _boletas

    @property
    def CodigoRectificacion(self):
        if not hasattr(self, '_codigo_rectificacion'):
            return False
        return self._codigo_rectificacion

    @CodigoRectificacion.setter
    def CodigoRectificacion(self, val):
        self._codigo_rectificacion = val

    @property
    def Documento(self):
        if not hasattr(self, '_documentos'):
            return []
        return self._documentos

    @Documento.setter
    def Documento(self, vals):
        documentos = []
        for dteDoc in vals:
            for docData in dteDoc.get("documentos", []):
                if not docData.get('sii_xml_request'):
                    if self.TipoOperacion == 'COMPRA' and \
                    (not docData['Encabezado'].get('Emisor') or \
                     docData['Encabezado']['Receptor']['RUTRecep'] == self.Emisor.RUTEmisor):
                        if docData['Encabezado']['Receptor']['RUTRecep'] == self.Emisor.RUTEmisor:
                            docData['Encabezado']['Receptor'] = {
                                'RUTRecep': docData['Encabezado']['Emisor']['RUTEmisor'],
                                'RznSocRecep': docData['Encabezado']['Emisor']['RznSoc'],
                            }
                        docData['Encabezado']['Emisor'] = {
                            'RUTEmisor': self.Emisor.RUTEmisor,
                            'RznSoc': self.Emisor.RznSoc,
                            'CdgSIISucur': self.Emisor.CdgSIISucur,
                        }

                    docu = Doc(
                                docData,
                                resumen=True,
                                tipo_dte=dteDoc["TipoDTE"],
                            )
                    documentos.append(docu)
        self._documentos = documentos

    @property
    def Emisor(self):
        if not hasattr(self, '_dte_emisor'):
            self._dte_emisor = Emis()
        return self._dte_emisor

    @Emisor.setter
    def Emisor(self, vals):
        if not hasattr(self, '_dte_emisor'):
            self._dte_emisor = Emis()
        self._dte_emisor.set_from_keys(vals)

    @property
    def Fecha(self):
        if not hasattr(self, '_fecha'):
            return datetime.strftime(datetime.now(), '%Y-%m-%d')
        return self._fecha

    @Fecha.setter
    def Fecha(self, val):
        self._fecha = val

    @property
    def FolioNotificacion(self):
        if not hasattr(self, '_folio_notificacion'):
            return 0
        return self._folio_notificacion

    @FolioNotificacion.setter
    def FolioNotificacion(self, val):
        self._folio_notificacion = val

    @property
    def NroSegmento(self):
        if not hasattr(self, '_nro_segmento'):
            return False
        return self._nro_segmento

    @NroSegmento.setter
    def NroSegmento(self, val):
        self._nro_segmento = val

    @property
    def FctProp(self):
        if not hasattr(self, '_fct_prop'):
            return False
        return self._fct_prop

    @FctProp.setter
    def FctProp(self, val):
        self._fct_prop = val

    @property
    def PeriodoTributario(self):
        if not hasattr(self, '_periodo_tributario'):
            return False
        return self._periodo_tributario

    @PeriodoTributario.setter
    def PeriodoTributario(self, val):
        self._periodo_tributario = val

    @property
    def ResumenPeriodo(self):
        if not hasattr(self, '_resumen_periodo'):
            return False
        return self._resumen_periodo

    @property
    def TipoOperacion(self):
        if not hasattr(self, '_tipo_operacion'):
            return 'VENTA'
        return self._tipo_operacion

    @TipoOperacion.setter
    def TipoOperacion(self, val):
        '''
            [
                ('COMPRA', 'Compras'),
                ('VENTA', 'Ventas'),
                ('BOLETA', 'Boleta'),
            ]
        '''
        self._tipo_operacion = val

    @property
    def TipoLibro(self):
        if not hasattr(self, '_tipo_libro'):
            return 'MENSUAL'
        return self._tipo_libro

    @TipoLibro.setter
    def TipoLibro(self, val):
        '''
            [
                ('ESPECIAL','Especial'),
                ('MENSUAL','Mensual'),
                ('RECTIFICA','Rectifica')
            ]
        '''
        self._tipo_libro = val

    @property
    def TipoEnvio(self):
        if not hasattr(self, '_tipo_envio'):
            return 'TOTAL'
        return self._tipo_envio

    @TipoEnvio.setter
    def TipoEnvio(self, val):
        '''
            [
                ('AJUSTE', 'Ajuste'),
                ('TOTAL', 'Total'),
                ('PARCIAL', 'Parcial'),
            ]
        '''
        self._tipo_envio = val

    def _iniciar(self):
        self.sii_message = None
        self.sii_xml_request = None
        self.sii_xml_response = None
        self.sii_send_ident = None

    def _TpoImp(self, imp=1):
        #if imp.CodImp in [14, 1]:
        return 1
        #if imp.CodImp in []: determinar cuando es 18.211 // zona franca
        #    return 2

    def getResumen(self, rec):
        det = collections.OrderedDict()
        det['TpoDoc'] = rec.TipoDTE
        #det['Emisor']
        #det['IndFactCompra']
        det['NroDoc'] = rec.Folio
        if rec.Anulado:
            det['Anulado'] = 'A'
        #det['Operacion']
        if rec.IndTraslado:
            det['TpoOper'] = rec.IndTraslado
        #det['TotalesServicio']
        MntTotal = rec.MntTotal
        if rec.impuestos and rec.IVA:
            for imp in rec.impuestos:
                if imp.tax_id.CodImp not in [14, 15]:
                    continue
                det['TpoImp'] = self._TpoImp()
                det['TasaImp'] = round(imp.tax_id.TasaImp, 2)
                break
        #det['IndServicio']
        #det['IndSinCosto']
        det['FchDoc'] = rec.FechaEmis
        if rec.Emisor.CdgSIISucur:
            det['CdgSIISucur'] = rec.Emisor.CdgSIISucur
        det['RUTDoc'] = rec._receptor.RUTRecep
        det['RznSoc'] = rec._receptor.RznSocRecep[:50]
        if rec.Referencia:
            det['TpoDocRef'] = rec._referencias[0].TpoDocRef
            det['FolioDocRef'] = rec._referencias[0].FolioRef
        if rec.MntExe > 0:
            det['MntExe'] = rec.MntExe
        elif self.TipoOperacion in ['VENTA'] and not rec.MntNeto > 0:
            det['MntExe'] = 0
        if rec.MntNeto > 0:
            det['MntNeto'] = rec.MntNeto
        if rec.MntIVA > 0 and not rec.IVAUsoComun and not rec.CodIVANoRec:
            det['MntIVA'] = rec.MntIVA
        if rec.MntActivoFijo > 0:
            det['MntActivoFijo'] = rec.MntActivoFijo
            det['MntIVAActivoFijo'] = rec.MntIVAActivoFijo
        if rec.CodIVANoRec:
            det['IVANoRec'] = collections.OrderedDict()
            det['IVANoRec']['CodIVANoRec'] = rec.CodIVANoRec
            det['IVANoRec']['MntIVANoRec'] = rec.MntIVANoRec
        if rec.IVAUsoComun:
            det['IVAUsoComun'] = rec.IVAUsoComun
        if rec.ImptoReten:
            otros_imp = []
            for imp in rec.impuestos:
                if imp.tax_id.CodImp in [14]:
                    continue
                otro = collections.OrderedDict()
                if rec.CodIVANoRec:
                    otro['MntSinCred'] = imp.MontoImp
                else:
                    otro['CodImp'] = str(imp.tax_id.CodImp)
                    otro['TasaImp'] = imp.tax_id.TasaImp
                    otro['MntImp'] = imp.MontoImp
                otros_imp.append({'OtrosImp': otro})
            det['itemOtrosImp'] = otros_imp
            if det.get('MntIVA', False):
                for imp in rec.impuestos:
                    if imp.tax_id.Retencion:
                        if imp.tax_id.Retencion == imp.tax_id.TasaImp:
                            det['IVARetTotal'] = imp.MontoImp
                            det['MntIVA'] -= det['IVARetTotal']
                        else:
                            det['IVARetParcial'] = int(round(
                                self.MntNeto * (imp.tax_id.Retencion / 100)))
                            det['IVANoRetenido'] = int(round(imp.MontoNoRet))
                            det['MntIVA'] -= det['IVARetParcial']
        det['MntTotal'] = MntTotal
        return det

    def getResumenGuia(self, rec):
        det = collections.OrderedDict()
        det['Folio'] = rec.Folio
        if rec.Anulado:
            det['Anulado'] = rec.Anulado
        #det['Operacion']
        if rec.IndTraslado:
            det['TpoOper'] = rec.IndTraslado
        #det['TotalesServicio']
        #det['IndServicio']
        #det['IndSinCosto']
        det['FchDoc'] = rec.FechaEmis
        det['RUTDoc'] = rec._receptor.RUTRecep
        det['RznSoc'] = rec._receptor.RznSocRecep[:50]
        if rec.Referencia:
            det['TpoDocRef'] = rec._referencias[0].TpoDocRef
            det['FolioDocRef'] = rec._referencias[0].FolioRef
        if rec.IndTraslado not in [5]:
            if rec.MntNeto > 0:
                det['MntNeto'] = rec.MntNeto
            det['TasaImp'] = 19.0
            if rec.impuestos:
                for imp in rec.impuestos:
                    if imp.tax_id.CodImp not in [14]:
                        continue
                    det['TasaImp'] = round(imp.tax_id.TasaImp, 2)
                    break
            if rec.MntIVA > 0:
                det['IVA'] = rec.MntIVA
            det['MntTotal'] = rec.MntTotal
        return det

    def _setResumenBoletas(self, rec):
        det = collections.OrderedDict()
        det['TpoDoc'] = rec.TipoDTE
        det['TotDoc'] = det['NroDoc'] = rec.Folio
        if rec.impuesto.TasaImp > 0:
            det['TpoImp'] = self._TpoImp(rec.impuesto)
            det['TasaImp'] = rec.TasaImp.TasaImp
            det['MntNeto'] = rec.MntNeto
            det['MntIVA'] = rec.MntIVA
        else:
            det['MntExe'] = rec.MntExento
        det['MntTotal'] = rec.MntTotal
        return det

    def _process_imps(self, tax_line_id, totales=0, currency=None, Neto=0,
                      TaxMnt=0, MntExe=0, ivas={}, imp={}):
        mnt = tax_line_id.compute_all(totales,  currency, 1)['taxes'][0]
        if mnt['monto'] < 0:
            mnt['monto'] *= -1
            mnt['base'] *= -1
        if tax_line_id.CodImp in [14, 15, 17, 18, 19, 30, 31, 32, 33, 34,
                                  36, 37, 38, 39, 41, 47, 48]:
            ivas.setdefault(tax_line_id.id, [tax_line_id, 0])
            ivas[tax_line_id.id][1] += mnt['monto']
            TaxMnt += mnt['monto']
            Neto += mnt['base']
        else:
            imp.setdefault(tax_line_id.id, [tax_line_id, 0])
            imp[tax_line_id.id][1] += mnt['monto']
            if tax_line_id.MntImp == 0:
                MntExe += mnt['base']
        return Neto, TaxMnt, MntExe, ivas, imp

    def getResumenBoleta(self, rec):
        det = collections.OrderedDict()
        det['TpoDoc'] = rec.TipoDTE
        det['FolioDoc'] = rec.Folio
        det['TpoServ'] = 3
        det['FchEmiDoc'] = rec.FechaEmis
        if rec.FechaVenc:
            det['FchVencDoc'] = rec.FechaVenc
        #det['PeriodoDesde']
        #det['PeriodoHasta']
        #det['CdgSIISucur']
        det['RUTCliente'] = rec._receptor.RUTRecep
        det['MntExe'] = rec.MntExe
        if rec.MntNeto > 0:
            det['MntNeto'] = rec.MntNeto
        det['TasaIVA'] = 19.0
        if rec.impuestos:
            for imp in rec.impuestos:
                if imp.tax_id.CodImp not in [14]:
                    continue
                det['TasaIVA'] = round(imp.tax_id.TasaImp, 2)
                break
        if rec.MntIVA > 0:
            det['MntIVA'] = rec.MntIVA
        det['MntTotal'] = rec.MntTotal
        #det['IndServicio']
        #det['IndSinCosto']
        return det

    def _procesar_otros_imp(self, resumen, resumenP):
        no_rec = 0 if 'TotImpSinCredito' not in resumenP else resumenP['TotImpSinCredito']
        if not 'itemOtrosImp' in resumenP :
            tots = []
            for o in resumen['itemOtrosImp']:
                tot = {}
                if 'MntSinCred' not in o:
                    cod = o['OtrosImp']['CodImp']
                    tot['TotOtrosImp'] = collections.OrderedDict()
                    tot['TotOtrosImp']['CodImp']  = cod
                    tot['TotOtrosImp']['TotMntImp']  = o['OtrosImp']['MntImp']
                    #tot['FctImpAdic']
                    tot['TotOtrosImp']['TotCredImp']  = o['OtrosImp']['MntImp']
                    tots.append(tot)
                else:
                    no_rec += o['MntSinCred']
            if tots:
                resumenP['itemOtrosImp'] = tots
            if no_rec > 0:
                resumenP['TotImpSinCredito'] = no_rec
            return resumenP
        seted = False
        itemOtrosImp = []
        for r in resumen['itemOtrosImp']:
            cod = r['OtrosImp']['CodImp'].replace('_no_rec','')
            for o in resumenP['itemOtrosImp']:
                if o['TotOtrosImp']['CodImp'] == cod:
                    o['TotOtrosImp']['TotMntImp'] += r['OtrosImp']['MntImp']
                    if cod == r['OtrosImp']['CodImp'] and not 'TotCredImp' in o['TotOtrosImp']:
                        o['TotOtrosImp']['TotCredImp'] = r['OtrosImp']['MntImp']
                    elif cod == r['OtrosImp']['CodImp']:
                        o['TotOtrosImp']['TotCredImp'] += r['OtrosImp']['MntImp']
                    seted = True
                    itemOtrosImp.append(o)
                else:
                    no_rec += o['OtrosImp']['MntImp']
        if not seted:
                if cod == o['OtrosImp']['CodImp']:
                    tot = {}
                    tot['TotOtrosImp'] = collections.OrderedDict()
                    tot['TotOtrosImp']['CodImp'] = cod
                    tot['TotOtrosImp']['TotMntImp'] = r['OtrosImp']['MntImp']
                #tot['FctImpAdic']
                    tot['TotOtrosImp']['TotCredImp'] += o['OtrosImp']['MntImp']
                    itemOtrosImp.append(tot)
                else:
                    no_rec += o['OtrosImp']['MntImp']

        resumenP['itemOtrosImp'] = itemOtrosImp
        if not 'TotImpSinCredito' in resumenP and no_rec > 0:
            resumenP['TotImpSinCredito'] += no_rec
        elif no_rec:
            resumenP['TotImpSinCredito'] = no_rec
        return resumenP

    def _setResumenPeriodo(self, resumen, resumenP):
        resumenP['TpoDoc'] = resumen['TpoDoc']
        if 'TpoImp' in resumen:
            resumenP['TpoImp'] = resumen['TpoImp'] or 1
        if not resumenP.get('TotDoc'):
            resumenP['TotDoc'] = 1
            if 'TotDoc' in resumen:
                resumenP['TotDoc'] = resumen['TotDoc']
        else:
            resumenP['TotDoc'] += 1
        if 'TotAnulado' in resumenP and 'Anulado' in resumen:
            resumenP['TotAnulado'] += 1
            return resumenP
        elif 'Anulado' in resumen:
            resumenP['TotAnulado'] = 1
            return resumenP
        if 'MntExe' in resumen and not resumenP.get('TotMntExe'):
            resumenP['TotMntExe'] = resumen['MntExe']
        elif 'MntExe' in resumen:
            resumenP['TotMntExe'] += resumen['MntExe']
        elif not resumenP.get('TotMntExe'):
            resumenP['TotMntExe'] = 0
        if 'MntNeto' in resumen and not resumenP.get('TotMntNeto'):
            resumenP['TotMntNeto'] = resumen['MntNeto']
        elif 'MntNeto' in resumen:
            resumenP['TotMntNeto'] += resumen['MntNeto']
        elif not resumenP.get('TotMntNeto'):
            resumenP['TotMntNeto'] = 0
        if 'TotOpIVARec' in resumen:
            resumenP['TotOpIVARec'] = resumen['OpIVARec']
        if 'MntIVA' in resumen and not resumenP.get('TotMntIVA'):
            resumenP['TotMntIVA'] = resumen['MntIVA']
        elif 'MntIVA' in resumen:
            resumenP['TotMntIVA'] += resumen['MntIVA']
        elif not resumenP.get('TotMntIVA'):
            resumenP['TotMntIVA'] = 0
        if 'MntActivoFijo' in resumen and not 'TotOpActivoFijo'in resumenP:
            resumenP['TotOpActivoFijo'] = 1
            resumenP['TotMntActivoFijo'] = resumen['MntActivoFijo']
            resumenP['TotMntIVAActivoFijo'] = resumen['MntIVAActivoFijo']
        elif 'MntActivoFijo' in resumen:
            resumenP['TotOpActivoFijo'] += 1
            resumenP['TotMntActivoFijo'] += resumen['MntActivoFijo']
            resumenP['TotMntIVAActivoFijo'] += resumen['MntIVAActivoFijo']
        if 'IVANoRec' in resumen and not resumenP.get('TotIVANoRec'):
            tot = collections.OrderedDict()
            tot['CodIVANoRec'] = resumen['IVANoRec']['CodIVANoRec']
            tot['TotOpIVANoRec'] = 1
            tot['TotMntIVANoRec'] = resumen['IVANoRec']['MntIVANoRec']
            resumenP['TotIVANoRec'] = [tot]
        elif 'IVANoRec' in resumen:
            seted = False
            itemNoRec = []
            for r in resumenP.get('TotIVANoRec', []):
                if r['CodIVANoRec'] == resumen['IVANoRec']['CodIVANoRec']:
                    r['TotOpIVANoRec'] += 1
                    r['TotMntIVANoRec'] += resumen['IVANoRec']['MntIVANoRec']
                    seted = True
                itemNoRec.extend([r])
            if not seted:
                tot = collections.OrderedDict()
                tot['CodIVANoRec'] = resumen['IVANoRec']['CodIVANoRec']
                tot['TotOpIVANoRec'] = 1
                tot['TotMntIVANoRec'] = resumen['IVANoRec']['MntIVANoRec']
                itemNoRec.extend([tot])
            resumenP['TotIVANoRec'] = itemNoRec
        if resumen.get('IVAUsoComun') and not resumenP.get('TotOpIVAUsoComun', False):
            resumenP['TotOpIVAUsoComun'] = 1
            resumenP['TotIVAUsoComun'] = resumen['IVAUsoComun']
            if not self.FctProp:
                raise util.UserError("Debe Ingresar Factor de proporcionlaidad")
            resumenP['FctProp'] = self.FctProp
            resumenP['TotCredIVAUsoComun'] = int(round((
                            resumen['IVAUsoComun'] * self.FctProp)))
        elif resumen.get('IVAUsoComun'):
            resumenP['TotOpIVAUsoComun'] += 1
            resumenP['TotIVAUsoComun'] += resumen['IVAUsoComun']
            resumenP['TotCredIVAUsoComun'] += int(round((
                            resumen['IVAUsoComun'] * self.FctProp)))
        if resumen.get('itemOtrosImp'):
            resumenP = self._procesar_otros_imp(resumen, resumenP)
        if 'IVARetTotal' in resumen and not resumenP.get('TotOpIVARetTotal'):
            resumenP['TotIVARetTotal'] = resumen['IVARetTotal']
        elif 'IVARetTotal' in resumen:
            resumenP['TotIVARetTotal'] += resumen['IVARetTotal']
        if 'IVARetParcial' in resumen and not resumenP.get('TotOpIVARetParcial'):
            resumenP['TotIVARetParcial'] = resumen['IVARetParcial']
            resumenP['TotIVANoRetenido'] = resumen['IVANoRetenido']
        elif 'IVARetParcial' in resumen:
            resumenP['TotIVARetParcial'] += resumen['IVARetParcial']
            resumenP['TotIVANoRetenido'] += resumen['IVANoRetenido']
        #@TODO otros tipos IVA
        if not resumenP.get('TotMntTotal'):
            resumenP['TotMntTotal'] = resumen['MntTotal']
        else:
            resumenP['TotMntTotal'] += resumen['MntTotal']
        return resumenP

    def _setResumenPeriodoBoleta(self, resumen, resumenP):
        resumenP['TpoDoc'] = resumen['TpoDoc']
        if 'Anulado' in resumen and 'TotAnulado' in resumenP:
            resumenP['TotAnulado'] += 1
            return resumenP
        elif 'Anulado' in resumen:
            resumenP['TotAnulado'] = 1
            return resumenP
        if 'TotalesServicio' not in resumenP:
            resumenP['TotalesServicio'] = collections.OrderedDict()
            resumenP['TotalesServicio']['TpoServ'] = resumen['TpoServ']#@TODO separar por tipo de servicio
            resumenP['TotalesServicio']['TotDoc'] = 0
        resumenP['TotalesServicio']['TotDoc'] += 1
        if 'MntExe' in resumen and not 'TotMntExe' in resumenP['TotalesServicio']:
            resumenP['TotalesServicio']['TotMntExe'] = resumen['MntExe']
        elif 'MntExe' in resumen:
            resumenP['TotalesServicio']['TotMntExe'] += resumen['MntExe']
        elif not resumenP['TotalesServicio'].get('TotMntExe'):
            resumenP['TotalesServicio']['TotMntExe'] = 0
        if 'MntNeto' in resumen and not resumenP['TotalesServicio'].get('TotMntNeto'):
            resumenP['TotalesServicio']['TotMntNeto'] = resumen['MntNeto']
        elif 'MntNeto' in resumen:
            resumenP['TotalesServicio']['TotMntNeto'] += resumen['MntNeto']
        elif not resumenP['TotalesServicio'].get('TotMntNeto'):
            resumenP['TotalesServicio']['TotMntNeto'] = 0
        if 'MntIVA' in resumen:
            resumenP['TotalesServicio']['TasaIVA'] = resumen['TasaIVA']
        if 'MntIVA' in resumen and not 'TotMntIVA' in resumenP['TotalesServicio']:
            resumenP['TotalesServicio']['TotMntIVA'] = resumen['MntIVA']
        elif 'MntIVA' in resumen:
            resumenP['TotalesServicio']['TotMntIVA'] += resumen['MntIVA']
        elif not 'TotMntIVA' in resumenP['TotalesServicio']:
            resumenP['TotalesServicio']['TotMntIVA'] = 0
        if not 'TotMntTotal' in resumenP['TotalesServicio']:
            resumenP['TotalesServicio']['TotMntTotal'] = resumen['MntTotal']
        else:
            resumenP['TotalesServicio']['TotMntTotal'] += resumen['MntTotal']
        return resumenP

    def _setResumenPeriodoGuias(self, resumen, resumenP):
        if 'TotFolAnulado' not in resumenP and 'Anulado' in resumen:
            if resumen['Anulado'] == 1:
                resumenP['TotFolAnulado'] = 1
            else:
                resumenP['TotGuiaAnulada'] = 1
            return resumenP
        elif 'Anulado' in resumen:
            if resumen['Anulado'] == 1 and 'TotFolAnulado':
                resumenP['TotFolAnulado'] += 1
            elif resumen['Anulado'] == '1':
                resumenP['TotFolAnulado'] = 1
            elif 'TotGuiaAnulada' in resumenP:
                resumenP['TotGuiaAnulada'] += 1
            else:
                resumenP['TotGuiaAnulada'] = 1
            return resumenP
        if 'TotGuiaVenta' not in resumenP:
            resumenP['TotGuiaVenta'] = 0
            resumenP['TotMntGuiaVta'] = 0
        if resumen['TpoOper'] in [1, 2]:
            resumenP['TotGuiaVenta'] += 1
            resumenP['TotMntGuiaVta'] += resumen.get('MntTotal', 0)
        else:
            TotTraslado = []
            if 'itemTraslado' not in resumenP:
                tras = collections.OrderedDict()
                tras['TpoTraslado'] = resumen['TpoOper']
                tras['CantGuia'] = 1
                tras['MntGuia'] = resumen.get('MntTotal', 0)
                TotTraslado.extend([{'TotTraslado': tras}])
                resumenP['itemTraslado'] = TotTraslado
            else:
                new = []
                seted = False
                for tpo in resumenP['itemTraslado']:
                    if resumen['TpoOper'] == tpo['TotTraslado']['TpoTraslado']:
                        tpo['TotTraslado']['CantGuia'] += 1
                        tpo['TotTraslado']['MntGuia'] += resumen.get('MntTotal', 0)
                        seted = True
                    new.extend([tpo])
                if not seted:
                    tras = collections.OrderedDict()
                    tras['TpoTraslado'] = resumen['TpoOper']
                    tras['CantGuia'] = 1
                    tras['MntGuia'] = resumen.get('MntTotal', 0)
                    new.extend([{'TotTraslado': tras}])
                resumenP['itemTraslado'] = new
        return resumenP

    def validar(self):
        resumenes = []
        resumenesPeriodo = {}
        resumenPeriodo = {}
        for rec in self.Documento:
            rec.sended = True
            TpoDoc = rec.TipoDTE
            if TpoDoc not in resumenesPeriodo and self.TipoOperacion != 'GUIA':
                resumenesPeriodo[TpoDoc] = {}
            if self.TipoOperacion == 'BOLETA':
                resumen = self.getResumenBoleta(rec)
                resumenesPeriodo[TpoDoc] = self._setResumenPeriodoBoleta(
                                    resumen, resumenesPeriodo[TpoDoc])
                del(resumen['MntNeto'])
                del(resumen['MntIVA'])
                del(resumen['TasaIVA'])
            elif self.TipoOperacion == 'GUIA':
                resumen = self.getResumenGuia(rec)
                resumenPeriodo = self._setResumenPeriodoGuias(
                                    resumen, resumenPeriodo)
            else:
                resumen = self.getResumen(rec)
            resumenes.append({'Detalle': resumen})
            if self.TipoOperacion not in ['BOLETA', 'GUIA']:
                resumenesPeriodo[TpoDoc] = self._setResumenPeriodo(
                                    resumen, resumenesPeriodo[TpoDoc])
        if self.boletas:  # no es el libro de boletas especial
            for boletas in self.boletas:
                resumenesPeriodo[boletas.TipoDTE] = {}
                resumen = self._setResumenBoletas(boletas)
                del(resumen['TotDoc'])
                resumenesPeriodo[boletas.TipoDTE] = self._setResumenPeriodo(
                                    resumen, resumenesPeriodo[boletas.TipoDTE])
                # resumenes.extend([{'Detalle':resumen}])
        lista = ['TpoDoc', 'TpoImp', 'TotDoc', 'TotAnulado', 'TotMntExe',
                 'TotMntNeto', 'TotalesServicio', 'TotOpIVARec',
                 'TotMntIVA', 'TotMntIVA', 'TotOpActivoFijo',
                 'TotMntActivoFijo', 'TotMntIVAActivoFijo', 'TotIVANoRec',
                 'TotOpIVAUsoComun', 'TotIVAUsoComun', 'FctProp',
                 'TotCredIVAUsoComun', 'itemOtrosImp', 'TotImpSinCredito',
                 'TotIVARetTotal', 'TotIVARetParcial', 'TotMntTotal',
                 'TotIVANoRetenido', 'TotTabPuros', 'TotTabCigarrillos',
                 'TotTabElaborado', 'TotImpVehiculo', 'TotFolAnulado',
                 'TotGuiaAnulada', 'TotGuiaVenta', 'TotMntGuiaVta',
                 'TotMntModificado', 'itemTraslado']
        ResumenPeriodo = []
        dte = collections.OrderedDict()
        for r, value in resumenesPeriodo.items():
            total = collections.OrderedDict()
            for v in lista:
                if v in value:
                    total[v] = value[v]
            ResumenPeriodo.extend([{'TotalesPeriodo': total}])
            #dte['ResumenPeriodo'] = ResumenPeriodo
            #dte_etree = util.create_xml({'item': dte})
            #util.create_xml(resumenes, dte_etree)
        if self.TipoOperacion == 'GUIA':
            ResumenPeriodo = collections.OrderedDict()
            for f in lista:
                if f in resumenPeriodo:
                    ResumenPeriodo[f] = resumenPeriodo[f]
        dte['ResumenPeriodo'] = ResumenPeriodo
        dte['item'] = resumenes
        dte['TmstFirma'] = util.time_stamp()
        dte_etree = util.create_xml({'item': dte})
        self.sii_xml_request = util.xml_to_string(dte_etree)
        return True
