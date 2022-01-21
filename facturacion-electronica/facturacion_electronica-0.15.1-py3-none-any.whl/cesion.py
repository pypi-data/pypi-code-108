# -*- coding: utf-8 -*-
from facturacion_electronica.cedente import Cedente as Ced
from facturacion_electronica.cesionario import Cesionario as Ces
from facturacion_electronica.documento import Documento
from facturacion_electronica import clase_util as util
from facturacion_electronica.clase_util import UserError
from lxml import etree
import base64
import collections
import logging
_logger = logging.getLogger(__name__)


class Cesion(Documento):

    def __init__(self, vals):
        util.set_from_keys(self, vals, priorizar=['Emisor'])

    @property
    def Cedente(self):
        if not hasattr(self, '_cedente'):
            return []
        Emisor = collections.OrderedDict()
        Emisor['RUT'] = self.Emisor.RUTEmisor
        Emisor['RazonSocial'] = self.Emisor.RznSoc
        Emisor['Direccion'] = self.Emisor.DirOrigen
        Emisor['eMail'] = self.Emisor.CorreoEmisor
        Emisor['RUTAutorizado'] = collections.OrderedDict()
        Emisor['RUTAutorizado']['RUT'] = self._cedente.RUT
        Emisor['RUTAutorizado']['Nombre'] = self._cedente.Nombre
        Emisor['DeclaracionJurada'] = self.DeclaracionJurada
        return Emisor

    @Cedente.setter
    def Cedente(self, vals):
        self._cedente = Ced(vals)

    @property
    def Cesionario(self):
        if not hasattr(self, '_cesionario'):
            return []
        Receptor = collections.OrderedDict()
        if not self._cesionario or not self._cesionario.RUT:
            raise UserError("Debe Ingresar RUT Cesionario")
        Receptor['RUT'] = self._cesionario.RUT
        Receptor['RazonSocial'] = self._cesionario.RazonSocial
        Receptor['Direccion'] = self._cesionario.Direccion
        Receptor['eMail'] = self._cesionario.eMail
        return Receptor

    @Cesionario.setter
    def Cesionario(self, vals):
        self._cesionario = Ces(vals)

    @property
    def DeclaracionJurada(self):
        if not hasattr(self, '_declaracion_jurada') or \
            not self._declaracion_jurada:
            if not hasattr(self, '_rzn_soc_receptor'):
                return False
            return  u'''Se declara bajo juramento que {0}, RUT {1} \
ha puesto a disposicion del cesionario {2}, RUT {3}, el o los documentos donde constan los recibos de las mercaderías entregadas o servicios prestados, \
entregados por parte del deudor de la factura {4}, RUT {5}, de acuerdo a lo establecido en la Ley No. 19.983'''.format(
                self.Emisor.RznSoc,
                self.Emisor.RUTEmisor,
                self.Cesionario.get('Nombre'),
                self.Cesionario.get('RUT'),
                self.RznSocReceptor,
                self.RUTReceptor,
            )
        return self._declaracion_jurada

    @DeclaracionJurada.setter
    def DeclaracionJurada(self, val):
        self._declaracion_jurada = val

    @property
    def ID(self):
        if not hasattr(self, '_id'):
            return "DocCed_%s" % str(self.Folio)
        return self._id

    @ID.setter
    def ID(self, val):
        self._id = val

    @property
    def IdDTE(self):
        if not hasattr(self, '_folio'):
            return False
        IdDoc = collections.OrderedDict()
        IdDoc['TipoDTE'] = self.TipoDTE
        IdDoc['RUTEmisor'] = self.Emisor.RUTEmisor
        if not self.RUTReceptor:
            raise UserError("Debe Ingresar RUT Receptor")
        IdDoc['RUTReceptor'] = self.RUTReceptor
        IdDoc['Folio'] = self.Folio
        IdDoc['FchEmis'] = self.FchEmis
        IdDoc['MntTotal'] = self.MntTotal
        return IdDoc

    @IdDTE.setter
    def IdDTE(self, vals):
        util.set_from_keys(self, vals)

    @property
    def ImageAR(self):
        if not hasattr(self, 'imagenes'):
            return []
        return self._imagenes

    @property
    def MontoCesion(self):
        if not hasattr(self, '_monto_cesion'):
            return 0
        return self._monto_cesion

    @MontoCesion.setter
    def MontoCesion(self, val):
        self._monto_cesion = val

    @property
    def MntTotal(self):
        if not hasattr(self, '_mnt_total'):
            return 0
        return self._mnt_total

    @MntTotal.setter
    def MntTotal(self, val):
        self._mnt_total = val

    @property
    def RUTEmisor(self):
        if not hasattr(self, '_rut_emisor'):
            return False
        return self._rut_emisor

    @RUTEmisor.setter
    def RUTEmisor(self, val):
        self._rut_emisor = val

    @property
    def RUTReceptor(self):
        if not hasattr(self, '_rut_receptor'):
            return False
        return self._rut_receptor

    @RUTReceptor.setter
    def RUTReceptor(self, val):
        self._rut_receptor = val

    @property
    def RznSocReceptor(self):
        if not hasattr(self, '_rzn_soc_receptor'):
            return False
        return self._rzn_soc_receptor

    @RznSocReceptor.setter
    def RznSocReceptor(self, val):
        self._rzn_soc_receptor = val

    @property
    def SeqCesion(self):
        if not hasattr(self, '_seq_cesion'):
            return False
        return self._seq_cesion

    @SeqCesion.setter
    def SeqCesion(self, val):
        self._seq_cesion = val

    @property
    def TipoDTE(self):
        if not hasattr(self, '_tipo_dte'):
            return False
        return self._tipo_dte

    @TipoDTE.setter
    def TipoDTE(self, val):
        self._tipo_dte = val

    @property
    def UltimoVencimiento(self):
        if not hasattr(self, '_ultimo_vencimiento'):
            return False
        return self._ultimo_vencimiento

    @UltimoVencimiento.setter
    def UltimoVencimiento(self, val):
        self._ultimo_vencimiento = val

    @property
    def xml_dte(self):
        if not hasattr(self, '_xml_dte'):
            return False
        return self._xml_dte

    @xml_dte.setter
    def xml_dte(self, val):
        self._xml_dte = val

    def doc_cedido(self, id):
        xml = '''<DocumentoDTECedido ID="{0}">
{1}
<TmstFirma>{2}</TmstFirma>
</DocumentoDTECedido>
    '''.format(
            id,
            self.xml_dte,
            util.time_stamp(),
        )
        return xml

    def _dte_cedido(self):
        id = "DocCed_" + str(self.Folio)
        doc = self.doc_cedido(id)
        xml = '''<DTECedido xmlns="http://www.sii.cl/SiiDte" version="1.0">
{}
</DTECedido>'''.format(doc)
        return xml

    def _crear_info_trans_elec_aec(self, doc):
        xml = '''<DocumentoCesion ID="CesDoc_{0}">
{1}
</DocumentoCesion>
'''.format(
            self.SeqCesion,
            doc,
        )
        return xml

    def _crear_info_cesion(self, doc):
        xml = '''<Cesion xmlns="http://www.sii.cl/SiiDte" version="1.0">
{0}
</Cesion>
'''.format(
            doc
        )
        return xml

    def xml_doc_cedido(self):
        data = collections.OrderedDict()
        data['SeqCesion'] = self.SeqCesion
        data['IdDTE'] = self.IdDTE
        data['Cedente'] = self.Cedente
        data['Cesionario'] = self.Cesionario
        data['MontoCesion'] = self.MontoCesion
        data['UltimoVencimiento'] = self.UltimoVencimiento
        data['TmstCesion'] = util.time_stamp()
        xml = self._dte_to_xml({'item': data})
        xml_pret = etree.tostring(
                xml,
                pretty_print=True, encoding="ISO-8859-1", xml_declaration=False).decode('ISO-8859-1')
        doc_cesion_xml = self._crear_info_trans_elec_aec(xml_pret)
        cesion_xml = self._crear_info_cesion(doc_cesion_xml)
        cesion = self.firmar(
            cesion_xml,
            "CesDoc_%s" % str(self.SeqCesion),
            'cesion',
        )
        return cesion.replace('<?xml version="1.0" encoding="ISO-8859-1"?>\n', '')

    def dte_cedido(self):
        xml_cedido = self._dte_cedido()
        dte_cedido = self.firmar(
            xml_cedido,
            "DocCed_" + str(self.Folio),
            'dte_cedido',
        )
        return dte_cedido
