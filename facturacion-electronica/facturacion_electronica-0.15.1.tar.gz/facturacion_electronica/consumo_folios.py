# -*- coding: utf-8 -*-
from facturacion_electronica.documento import Documento as Doc
from facturacion_electronica import clase_util as util
from datetime import datetime
import collections
import logging
_logger = logging.getLogger(__name__)


class ConsumoFolios(object):

    def __init__(self, vals):
        self._iniciar()
        util.set_from_keys(self, vals)

    def _iniciar(self):
        self.sii_message = None
        self.sii_xml_request = '<Resumen><TipoDocumento>39</TipoDocumento>\
<MntTotal>0</MntTotal><FoliosEmitidos>0</FoliosEmitidos><FoliosAnulados>0\
</FoliosAnulados><FoliosUtilizados>0</FoliosUtilizados></Resumen>'
        self.sii_xml_response = None
        self.total_boletas = 0
        self.total_neto = 0
        self.total_exento = 0
        self.total_iva = 0
        self.total = 0

    @property
    def Correlativo(self):
        if not hasattr(self, '_correlativo'):
            return 0
        return self._correlativo

    @Correlativo.setter
    def Correlativo(self, correlativo=0):
        self._correlativo = correlativo

    @property
    def Documento(self):
        if not hasattr(self, '_documentos'):
            return []
        return self._documentos

    @Documento.setter
    def Documento(self, vals):
        documentos = []
        folios = {}
        for dteDoc in vals:
            for docData in dteDoc.get("documentos", []):
                if not docData.get('sii_xml_request'):
                    docu = Doc(
                                docData,
                                resumen=self.resumen,
                                tipo_dte=dteDoc["TipoDTE"],
                            )
                    folios.setdefault(dteDoc["TipoDTE"], [])
                    if docu.Folio in folios[dteDoc["TipoDTE"]]:
                        raise util.UserError("El consumo de folios lleva folios duplicados")
                    folios[dteDoc["TipoDTE"]].append(docu.Folio)
                    documentos.append(docu)
        self._documentos = sorted(documentos, key=lambda t: t.Folio)

    @property
    def Fecha(self):
        if not hasattr(self, '_fecha'):
            return datetime.strftime(datetime.now(), '%Y-%m-%d')
        return self._fecha

    @Fecha.setter
    def Fecha(self, val):
        self._fecha = util.get_fecha(val)

    @property
    def FchFinal(self):
        if not hasattr(self, '_fch_final'):
            return self.FchInicio
        return self._fch_final

    @FchFinal.setter
    def FchFinal(self, val):
        self._fch_final = util.get_fecha(val)

    @property
    def FchInicio(self):
        if not hasattr(self, '_fch_inicio'):
            return datetime.strftime(datetime.now(), '%Y-%m-%d')
        return self._fch_inicio

    @FchInicio.setter
    def FchInicio(self, val):
        self._fch_inicio = util.get_fecha(val)

    @property
    def SecEnvio(self):
        if not hasattr(self, '_sec_envio'):
            return 0
        return self._sec_envio

    @SecEnvio.setter
    def SecEnvio(self, sec_envio=0):
        self._sec_envio = sec_envio

    @property
    def resumen(self):
        if not hasattr(self, '_resumen'):
            return True
        return self._resumen

    @resumen.setter
    def resumen(self, val):
        self._resumen = val

    def getResumen(self, rec):
        det = collections.OrderedDict()
        det['TpoDoc'] = rec.TipoDTE
        det['NroDoc'] = rec.Folio
        TasaIVA = 19
        MntIVA = rec.MntIVA
        for t in rec.impuestos:
            if t.tax_id.CodImp in [14]:
                TasaIVA = t.tax_id.TasaImp
            elif t.tax_id.es_adicional:
                MntIVA += t.MontoImp
        if rec.MntExe > 0:
            det['MntExe'] = rec.MntExe
        if MntIVA > 0:
            det['MntIVA'] = MntIVA
            det['TasaIVA'] = TasaIVA
        det['MntNeto'] = rec.MntNeto
        det['MntTotal'] = rec.MntTotal
        if rec.Anulado:
            det['Anulado'] = 'A'
        return det

    def push_item(self, folio, items=[], continuado=True):
        seted = False
        for r in items:
            if r['Inicial'] >= folio <= r['Final']:
                seted = True
                break
            elif folio == (r['Final']+1) and continuado:
                r['Final'] = folio
                seted = True
                break
            elif folio == (r['Inicial'] -1):
                r['Inicial'] = folio
                seted = True
                break
        if not seted:
            r = collections.OrderedDict()
            r['Inicial'] = folio
            r['Final'] = folio
            items.append(r)
        return items

    @property
    def item_anulados(self):
        if not hasattr( self, '_item_anulados'):
            self._item_anulados = {}
        return self._item_anulados

    @item_anulados.setter
    def item_anulados(self, vals):
        tipoDoc, folio, continuado = vals
        _item_anulados = self.item_anulados.get(tipoDoc, [])
        self._item_anulados[tipoDoc] = self.push_item(folio, _item_anulados, continuado)


    @property
    def item_utilizados(self):
        if not hasattr( self, '_item_utilizados'):
            self._item_utilizados = {}
        return self._item_utilizados

    @item_utilizados.setter
    def item_utilizados(self, vals):
        tipoDoc, folio, continuado = vals
        _item_utilizados = self.item_utilizados.get(tipoDoc, [])
        self._item_utilizados[tipoDoc] = self.push_item(folio, _item_utilizados, continuado)

    def _rangosU(self, resumen, rangos, continuado=True):
        if not rangos:
            rangos = collections.OrderedDict()
        folio = resumen['NroDoc']
        if 'Anulado' in resumen and resumen['Anulado'] == 'A':
            self.item_anulados = resumen['TpoDoc'], resumen['NroDoc'], continuado
            rangos['itemAnulados'] = self.item_anulados.get(resumen['TpoDoc'], [])
            return rangos
        #anulados = rangos['itemAnulados'] if 'itemAnulados' in rangos else []
        #rangos.setdefault('itemUtilizados', [])
        self.item_utilizados = resumen['TpoDoc'], resumen['NroDoc'], continuado
        rangos['itemUtilizados'] = self.item_utilizados.get(resumen['TpoDoc'], [])
        return rangos

    def _setResumen(self, resumen, resumenP, continuado=True):
        resumenP['TipoDocumento'] = resumen['TpoDoc']
        if 'Anulado' not in resumen:
            if 'MntNeto' in resumen and not 'MntNeto' in resumenP:
                resumenP['MntNeto'] = resumen['MntNeto']
            elif 'MntNeto' in resumen:
                resumenP['MntNeto'] += resumen['MntNeto']
            elif not 'MntNeto' in resumenP:
                resumenP['MntNeto'] = 0
            if 'MntIVA' in resumen and not 'MntIva' in resumenP:
                resumenP['MntIva'] = resumen['MntIVA']
            elif 'MntIVA' in resumen:
                resumenP['MntIva'] += resumen['MntIVA']
            elif not 'MntIva' in resumenP:
                resumenP['MntIva'] = 0
            if 'TasaIVA' in resumen and not 'TasaIVA' in resumenP:
                resumenP['TasaIVA'] = resumen['TasaIVA']
            if 'MntExe' in resumen and not 'MntExento' in resumenP:
                resumenP['MntExento'] = resumen['MntExe']
            elif 'MntExe' in resumen:
                resumenP['MntExento'] += resumen['MntExe']
            elif not resumenP.get('MntExento'):
                resumenP['MntExento'] = 0
            if not resumenP.get('MntTotal'):
                resumenP['MntTotal'] = resumen['MntTotal']
            else:
                resumenP['MntTotal'] += resumen['MntTotal']
        if 'FoliosEmitidos' in resumenP:
            resumenP['FoliosEmitidos'] +=1
        else:
            resumenP['FoliosEmitidos'] = 1
        if not resumenP.get('FoliosAnulados'):
            resumenP['FoliosAnulados'] = 0
        if resumen.get('Anulado'):
            resumenP['FoliosAnulados'] += 1
        elif 'FoliosUtilizados' in resumenP:
            resumenP['FoliosUtilizados'] += 1
        else:
            resumenP['FoliosUtilizados'] = 1
        resumenP.setdefault(('T' + str(resumen['TpoDoc'])), collections.OrderedDict())
        resumenP[('T' + str(resumen['TpoDoc']))] = self._rangosU(
                    resumen, resumenP[('T' + str(resumen['TpoDoc']))],
                    continuado)
        if 'Anulado' not in resumen:
            self.total_neto = resumenP.get('MntNeto', 0)
            self.total_iva = resumenP.get('MntIva', 0)
            self.total_exento = resumenP.get('MntExento', 0)
            self.total = resumenP['MntTotal']
        if resumen['TpoDoc'] in [39, 41]:
            self.total_boletas += 1
        return resumenP

    def get_rangos(self):
        resumenes = self._get_resumenes()
        detalles = []

        def pushItem(key_item, item, tpo_doc):
            rango = {
                'tipo_operacion': 'utilizados' if \
                key_item == 'RangoUtilizados' else 'anulados',
                'folio_inicio': item['Inicial'],
                'folio_final': item['Final'],
                'cantidad': int(item['Final']) - int(item['Inicial']) + 1,
                'tpo_doc':  tpo_doc,
            }
            detalles.append(rango)

        for r, value in resumenes.items():
            if value.get('T' + str(r)):
                Rangos = value['T' + str(r)]
                if 'itemUtilizados' in Rangos:
                    for rango in Rangos['itemUtilizados']:
                        pushItem('RangoUtilizados', rango, r)
                if 'itemAnulados' in Rangos:
                    for rango in Rangos['itemAnulados']:
                        pushItem('RangoAnulados', rango, r)
        return detalles

    def _get_resumenes(self):
        if not self.Documento:
            return {}
        resumenes = {}
        #@TODO ordenar documentos
        ant = {}
        for rec in self.Documento:
            if not rec.TipoDTE or rec.TipoDTE not in [39, 41, 61]:
                print("Por este medio solamente se pueden declarar Boletas o \
Notas de crédito Electrónicas, por favor elimine el documento %s del listado" \
% rec.name)
            if self.FchInicio == '':
                self.FchInicio = rec.FechaEmis
            if rec.FechaEmis != self.FchFinal:
                self.FchFinal = rec.FechaEmis
            resumen = self.getResumen(rec)
            TpoDoc = resumen['TpoDoc']
            if not str(TpoDoc) in ant:
                    ant[str(TpoDoc)] = 0
            if not resumenes.get(TpoDoc):
                resumenes[TpoDoc] = collections.OrderedDict()
            resumenes[TpoDoc] = self._setResumen(
                                    resumen,
                                    resumenes[TpoDoc],
                                    ((ant[str(TpoDoc)] + 1) == rec.Folio)
                                )
            ant[str(TpoDoc)] = rec.Folio
        return resumenes

    def validar(self):
        Resumen = []
        listado = ['TipoDocumento', 'MntNeto', 'MntIva', 'TasaIVA',
                   'MntExento', 'MntTotal', 'FoliosEmitidos', 'itemAnulados', 'FoliosAnulados',
                   'FoliosUtilizados', 'itemUtilizados']
        TpoDocs = []
        if self.Documento:
            resumenes = self._get_resumenes()
            for r, value in resumenes.items():
                if not str(r) in TpoDocs:
                    TpoDocs.append(str(r))
                ordered = collections.OrderedDict()
                for i in listado:
                    if i in value:
                        ordered[i] = value[i]
                    elif i == 'itemUtilizados':
                        Rangos = value['T' + str(r)]
                        folios = []
                        if 'itemUtilizados' in Rangos:
                            utilizados = []
                            for rango in Rangos['itemUtilizados']:
                                utilizados.append({'RangoUtilizados': rango})
                            folios.append({'itemUtilizados': utilizados})
                        if 'itemAnulados' in Rangos:
                            anulados = []
                            for rango in Rangos['itemAnulados']:
                                anulados.append({'RangoAnulados': rango})
                            folios.append({'itemAnulados': anulados})
                        ordered['T' + str(r)] = folios
                Resumen.append({'Resumen': ordered})
            dte = {'item': Resumen}
            etree_xml = util.create_xml(dte)
            sii_xml_request = util.xml_to_string(etree_xml)
            for TpoDoc in TpoDocs:
                sii_xml_request = sii_xml_request.replace('<T%s>' % str(TpoDoc), '')\
                .replace('</T%s>' % str(TpoDoc), '\n').replace('<T%s/>' % str(TpoDoc), '\n')
            self.sii_xml_request = sii_xml_request
        return True
