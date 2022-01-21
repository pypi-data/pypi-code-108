# -*- coding: utf-8 -*-
from facturacion_electronica.documento import Documento as DOC
from facturacion_electronica import clase_util as util
from lxml import etree
import base64
import collections
import logging
_logger = logging.getLogger(__name__)


class UserError(Exception):
    """Clase perdida"""
    pass


class Respuesta(DOC):

    def __init__(self, vals):
        util.set_from_keys(self, vals, priorizar=['Emisor'])

    @property
    def Caratula(self):
        if self.Recibos:
            caratula = self._caratula_recep()
        else:
            caratula = self._caratula_respuesta()
        caratula_xml = util.create_xml({'Caratula': caratula})
        caratula_xml.set('version', '1.0')
        return etree.tostring(caratula_xml).decode('ISO-8859-1')

    @property
    def CodEnvio(self):
        if not hasattr(self, '_cod_envio'):
            return self.IdRespuesta
        return self._cod_envio

    @CodEnvio.setter
    def CodEnvio(self, val):
        self._cod_envio = str(val)

    @property
    def RecepEnvGlosa(self):
        if not hasattr(self, '_recep_env_glosa'):
            return 'No Procesado'
        return self._recep_env_glosa

    @RecepEnvGlosa.setter
    def RecepEnvGlosa(self, val):
        self._recep_env_glosa = val

    @property
    def EstadoRecepEnv(self):
        if not hasattr(self, '_estado_recep_env'):
            return -1
        return self._estado_recep_env

    @EstadoRecepEnv.setter
    def EstadoRecepEnv(self, val):
        self._estado_recep_env = val

    @property
    def IdRespuesta(self):
        if not hasattr(self, '_id_resp'):
            return 1
        return self._id_resp

    @IdRespuesta.setter
    def IdRespuesta(self, val):
        self._id_resp = val

    @property
    def DTEs(self):
        if not hasattr(self, '_dtes'):
            return False
        return self._dtes

    @DTEs.setter
    def DTEs(self, vals):
        _dtes = []
        if hasattr(self, '_dtes'):
            _dtes = self._dtes
        if type(vals) is list:
            for v in vals:
                if (not v['Encabezado'].get('Emisor') and \
                v['Encabezado']['Receptor']['RUTRecep'] != self._dte_emisor.RUTEmisor)\
                or (v['Encabezado'].get('Emisor') and \
                v['Encabezado']['Receptor']['RUTRecep'] != self._dte_emisor.RUTEmisor):
                    v['Encabezado']['Emisor'] = {
                            'RUTEmisor': v['Encabezado']['Receptor']['RUTRecep']
                        }
                    v['Encabezado']['Receptor']['RUTRecep'] = self._dte_emisor.RUTEmisor
                _dtes.append(DOC(v))
        else:
            _dtes.append(DOC(vals))
        self._dtes = _dtes
        self.NroDetalles = len(_dtes)

    @property
    def FonoContacto(self):
        if not hasattr(self, '_fono_contacto'):
            return ''
        return self._fono_contacto

    @FonoContacto.setter
    def FonoContacto(self, val):
        self._fono_contacto = val

    @property
    def MailContacto(self):
        if not hasattr(self, '_mail_contacto'):
            return ''
        return self._mail_contacto

    @MailContacto.setter
    def MailContacto(self, val):
        self._mail_contacto = val

    @property
    def NmbContacto(self):
        if not hasattr(self, '_nmb_contacto'):
            return ''
        return self._nmb_contacto[:40]

    @property
    def NroDetalles(self):
        if not hasattr(self, '_nro_detalles'):
            return 0
        return self._nro_detalles

    @NroDetalles.setter
    def NroDetalles(self, val):
        self._nro_detalles = val

    @NmbContacto.setter
    def NmbContacto(self, val):
        self._nmb_contacto = val

    @property
    def RecepcionEnvio(self):
        envio = self.xml_envio
        if envio.find('SetDTE/Caratula') is None:
            return True
        recep = self._receipt()
        resp_dtes = util.create_xml({"RecepcionEnvio": recep})
        return util.xml_to_string(resp_dtes)

    @property
    def Recibos(self):
        if not hasattr(self, '_recibos'):
            return ''
        return self._recibos

    @Recibos.setter
    def Recibos(self, val):
        self._recibos = "%s\n%s" % (self.Recibos, val)

    @property
    def Recinto(self):
        if not hasattr(self, '_recinto'):
            return ''
        return self._recinto[:80]

    @Recinto.setter
    def Recinto(self, val):
        self._recinto = val

    @property
    def Resultados(self):
        if not hasattr(self, '_resultados'):
            return ''
        return self._resultados

    @Resultados.setter
    def Resultados(self, val):
        self._resultados = "%s\n%s" % (self.Resultados, val)

    @property
    def RutRecibe(self):
        if not hasattr(self, '_rut_recibe'):
            return self._dte_emisor.RUTEmisor
        return self._rut_recibe

    @RutRecibe.setter
    def RutRecibe(self, val):
        self._rut_recibe = util.formatear_rut(val)

    @property
    def RutResponde(self):
        if not hasattr(self, '_rut_responde'):
            if not hasattr(self, '_receptor'):
                return False
            return self._receptor.RUTRecep
        return self._rut_responde

    @RutResponde.setter
    def RutResponde(self, val):
        self._rut_responde = util.formatear_rut(val)

    @property
    def xml_envio(self):
        if not hasattr(self, '_xml_envio'):
            return False
        return self._xml_envio

    @xml_envio.setter
    def xml_envio(self, val):
        if type(val) != bytes:
            val = val.encode()
        _xml = val
        if b'<?xml ' not in val:
            base64.decodestring(val)
            _xml = base64.b64decode(val)
        xml = _xml.decode('ISO-8859-1')\
            .replace('<?xml version="1.0" encoding="ISO-8859-1"?>', '')\
            .replace('<?xml version="1.0" encoding="ISO-8859-1" ?>', '')\
            .replace(' xmlns="http://www.sii.cl/SiiDte"', '')\
            .replace(' xmlns="http://www.w3.org/2000/09/xmldsig#"', '')
        self._xml_envio = etree.XML(xml)

    @property
    def xml_nombre(self):
        if not hasattr(self, '_xml_nombre'):
            return False
        return self._xml_nombre

    @xml_nombre.setter
    def xml_nombre(self, val):
        self._xml_nombre = val

    @property
    def xml_dte(self):
        if not hasattr(self, '_xml_dte'):
            return False
        self._xml_dte

    @xml_dte.setter
    def xml_dte(self, val):
        if type(val['xml']) != bytes:
            val['xml'] = val['xml'].encode('ISO-8859-1')
        _xml = val['xml']
        if b'<?xml ' not in val['xml'] and b'<DTE ' not in val['xml']:
            base64.decodestring(val['xml'])
            _xml = base64.b64decode(val['xml'])
        xml = _xml.replace(b' xmlns="http://www.sii.cl/SiiDte"', b'')\
            .replace(b' xmlns="http://www.w3.org/2000/09/xmldsig#"', b'')
        el = etree.XML(xml)
        dte = util.recursive_xml(el.find('Documento'))
        dte['CodEnvio'] = val['CodEnvio']
        self.DTEs = dte
        self._xml_dte = val
        self.RutRecibe = dte['Encabezado']['Emisor']['RUTEmisor']


    def _check_digest_caratula(self):
        string = etree.tostring(self.xml_envio[0])
        #mess = etree.tostring(etree.fromstring(string), method="c14n")
        #our = base64.b64encode(self.firma.digest(mess))
        #if our != xml.find("Signature/SignedInfo/Reference/DigestValue").text:
        #    self.EstadoRecepEnv = 2
        #    self.RecepEnvGlosa = 'Envio Rechazado - Error de Firma'
        self.EstadoRecepEnv = 0
        self.RecepEnvGlosa = 'Envio Ok'

    def _check_digest_dte(self, dte):
        envio = self.xml_envio.find("SetDTE")
        for e in envio.findall("DTE"):
            string = etree.tostring(e.find("Documento"))
            #mess = etree.tostring(etree.fromstring(string), method="c14n")
            #our = base64.b64encode(self.firma.digest(mess))
            #if our != e.find("Signature/SignedInfo/Reference/DigestValue").text:
            #    self.EstadoRecepEnv = 1
            #    self.RecepEnvGlosa = 'DTE No Recibido - Error de Firma'
        self.EstadoRecepDTE = 0
        self.RecepDTEGlosa = 'DTE Recibido OK'

    def _validar_caratula(self, cara):
        if cara.find('RutReceptor').text != self.RutResponde:
            self.EstadoRecepEnv = 3
            self.RecepEnvGlosa = 'Rut no corresponde a nuestra empresa'
        try:
            util.xml_validator(self._read_xml(False), 'env')
        except:
            self.EstadoRecepEnv = 1
            self.RecepEnvGlosa = 'Envio Rechazado - Error de Schema'
        self.EstadoRecepEnv = 0
        self.RecepEnvGlosa = 'Envío Ok'

    def _validar(self, doc):
        cara, glosa = self._validar_caratula(doc[0][0].find('Caratula'))
        return cara, glosa

    def _validar_dte(self, encabezado):
        res = collections.OrderedDict()
        res['TipoDTE'] = encabezado.find('IdDoc/TipoDTE').text
        res['Folio'] = encabezado.find('IdDoc/Folio').text
        res['FchEmis'] = encabezado.find('IdDoc/FchEmis').text
        res['RUTEmisor'] = encabezado.find('Emisor/RUTEmisor').text
        res['RUTRecep'] = encabezado.find('Receptor/RUTRecep').text
        res['MntTotal'] = encabezado.find('Totales/MntTotal').text
        self._check_digest_dte(encabezado)
        res['EstadoRecepDTE'] = self.EstadoRecepDTE
        res['RecepDTEGlosa'] = self.RecepDTEGlosa
        if encabezado.find('Receptor/RUTRecep').text != self.RutResponde:
            res['EstadoRecepDTE'] = 3
            res['RecepDTEGlosa'] = 'Rut no corresponde a la empresa esperada'
        return res

    def _validar_dtes(self):
        envio = self.xml_envio
        res = []
        for doc in envio.findall('SetDTE/DTE'):
            res.append({
                'RecepcionDTE': self._validar_dte(
                                    doc.find('Documento/Encabezado'))
                })
        return res

    def _receipt(self):
        envio = self.xml_envio
        resp = collections.OrderedDict()
        resp['NmbEnvio'] = util._acortar_str(self.xml_nombre, 80)
        resp['FchRecep'] = util.time_stamp()
        resp['CodEnvio'] = util._acortar_str(self.CodEnvio, 10)
        resp['EnvioDTEID'] = envio.find('SetDTE').attrib['ID']
        resp['Digest'] = envio.find(
                            "Signature/SignedInfo/Reference/DigestValue").text
        self._validar_caratula(envio.find('SetDTE/Caratula'))
        if self.EstadoRecepEnv == 0:
            self._check_digest_caratula()
        resp['RutEmisor'] = envio.find('SetDTE/Caratula/RutEmisor').text
        resp['RutReceptor'] = envio.find('SetDTE/Caratula/RutReceptor').text
        resp['EstadoRecepEnv'] = str(self.EstadoRecepEnv)
        resp['RecepEnvGlosa'] = self.RecepEnvGlosa
        NroDTE = len(envio.findall('SetDTE/DTE'))
        resp['NroDTE'] = NroDTE
        resp['item'] = self._validar_dtes()
        return resp

    def resultado(self, r):
        res = collections.OrderedDict()
        res['TipoDTE'] = r.TipoDTE
        res['Folio'] = r.Folio
        res['FchEmis'] = r.FechaEmis
        res['RUTEmisor'] = r._dte_emisor.RUTEmisor
        res['RUTRecep'] = r._receptor.RUTRecep
        res['MntTotal'] = r.MntTotal
        res['CodEnvio'] = r.CodEnvio
        res['EstadoDTE'] = r.EstadoDTE
        res['EstadoDTEGlosa'] = r.EstadoDTEGlosa
        if r.EstadoDTE == 2:
            res['CodRchDsc'] = r.CodRchDsc  # User Reject
        return res

    def recibo(self, r):
        receipt = collections.OrderedDict()
        receipt['TipoDoc'] = r.TipoDTE
        receipt['Folio'] = r.Folio
        receipt['FchEmis'] = r.FechaEmis
        receipt['RUTEmisor'] = r._dte_emisor.RUTEmisor
        receipt['RUTRecep'] = r._receptor.RUTRecep
        receipt['MntTotal'] = r.MntTotal
        receipt['Recinto'] = self.Recinto
        receipt['RutFirma'] = self.firma.rut_firmante
        receipt['Declaracion'] = r.Declaracion
        receipt['TmstFirmaRecibo'] = util.time_stamp()
        etree_receipt = util.create_xml({"item": receipt})
        return util.xml_to_string(etree_receipt)

    def _caratula_respuesta(self):
        caratula = collections.OrderedDict()
        caratula['RutResponde'] = self.RutResponde
        caratula['RutRecibe'] = self.RutRecibe
        caratula['IdRespuesta'] = self.IdRespuesta
        caratula['NroDetalles'] = self.NroDetalles
        caratula['NmbContacto'] = self.NmbContacto
        caratula['FonoContacto'] = self.FonoContacto
        caratula['MailContacto'] = self.MailContacto
        caratula['TmstFirmaResp'] = util.time_stamp()
        return caratula

    def _caratula_recep(self):
        caratula = collections.OrderedDict()
        caratula['RutResponde'] = self.RutResponde
        caratula['RutRecibe'] = self.RutRecibe
        caratula['NmbContacto'] = self.NmbContacto
        caratula['FonoContacto'] = self.FonoContacto
        caratula['MailContacto'] = self.MailContacto
        caratula['TmstFirmaEnv'] = util.time_stamp()
        return caratula

    def gen_validacion_comercial(self):
        _r = []
        for r in self.DTEs:
            _r.append({'ResultadoDTE': self.resultado(r)})
        resp_dtes = util.create_xml({'item': _r})
        self.Resultados = util.xml_to_string(resp_dtes)
