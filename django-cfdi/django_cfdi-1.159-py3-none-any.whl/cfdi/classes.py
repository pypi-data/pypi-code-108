import re
import time
import base64
import requests
import json
import hashlib
from django.conf import settings
from .functions import to_decimal, get_field, escape, unescape, \
    chunkstring
from .settings import (
    TMP_DIR, DFACTURE_AUTH, PRODIGIA_AUTH, NTLINK_AUTH, XSLT_PATH_CFDI,
    XSLT_PATH_TFD, STO_AUTH,
)
from .constants import PACS
import datetime, io, pytz
from django.utils import timezone
from .complementos import ComplementoPago


class Object:
    pass
    #def __str__(self) :
    #    return 

class CFDI:
    """
    Clase para manejar comprobantes
    """

    def __init__(self, *args, **kwargs):
        self.Version = "3.3"
        self.id = ""
        self.pem_path = ""
        self.TIMBRADO_PRUEBAS = None
        self.cfdi_uuid = None
        self.key = None
        self.csd_pass = None

        self.recuperar_xml = False
        self.cfdi_status = ""
        self.xml = ""
        self.Serie = ""
        self.Folio = ""
        self.Fecha = ""
        self.NoCertificado = ""
        self.Certificado  = ""
        self.SubTotal = ""
        self.Moneda = ""
        self.Total = ""
        self.TipoDeComprobante = ""
        self.FormaPago = ""
        self.MetodoPago = ""
        self.CondicionesDePago = ""
        self.Descuento = ""
        self.TipoCambio = ""
        self.LugarExpedicion = ""
        self.traslados = []
        self.retenciones = []
        self.TotalImpuestosRetenidos = ""
        self.TotalImpuestosTrasladados = ""
        self.CfdiRelacionados = {}
        self.TipoCambio = ""
        self.Moneda = ""

        self.total = ""
        self.LugarExpedicion = ""
        self.sello = ""
        self.certificado = ""
        #Emisor
        self.emisor_rfc = ""
        self.emisor_nombre = ""

        #Receptor
        self.receptor_rfc = ""
        self.receptor_nombre = ""

        self.conceptos = []
        self.retenciones = []

        self.error_conexion = ""

        self.total_retenciones_locales = 0
        self.total_traslados_locales = 0
        self.traslados_locales = []
        self.retenciones_locales = []

        self.inicio_timbrado = None
        self.fin_timbrado = None
        self.inicio_conexion_pac = None
        self.fin_conexion_pac = None

        #Complemento de servicios parciales para construcción
        self.construccion_licencia = ""
        self.construccion_calle = ""
        self.construccion_no_exterior = ""
        self.construccion_no_interior = ""
        self.construccion_colonia = ""
        self.construccion_localidad = ""
        self.construccion_referencia = ""
        self.construccion_municipio = ""
        self.construccion_estado = ""
        self.construccion_codigo_postal = ""

        #Complemento INE
        self.ine = None

        #Complemento IEDU
        self.iedu = None

        #Complemento Detallista
        self.detallista = None

        #Complemento Nómina
        self.nomina = None

        #Comercio exterior:
        self.comercio_exterior = None
        
        #Complemento Recepción de pagos
        self.recepcion_pago = None
        self.pagos = []
        #tmp
        self.tmp_path = TMP_DIR


        #Complemento leyendasFiscales
        self.leyendasFiscales = []

        self.complementos = []

        self.motivo_cancelacion = ""
        self.uuid_relacionado_cancelacion = ""

        #Prodigia
        try:
            #self.prodigia_url = "https://timbrado.pade.mx/servicio/Timbrado3.3?WSDL"
            self.prodigia_url = "https://timbrado.pade.mx/PadeServ/IntegracionCfdi?WSDL"

            self.prodigia_contrato = PRODIGIA_AUTH["prod"]["contrato"]
            self.prodigia_usuario = PRODIGIA_AUTH["prod"]["usuario"]
            self.prodigia_password = PRODIGIA_AUTH["prod"]["password"]
        except AttributeError:
            self.prodigia_url = ""
            self.prodigia_contrato = ""
            self.prodigia_usuario = ""
            self.prodigia_password = ""

        self.openssl_algo_hash = "-sha1"
        self.timezone = settings.TIME_ZONE        

        self.VERIFICAR_SERIE_FOLIO = False


    def get_full_tmp_path(self, file_name):
        fecha = datetime.datetime.today().strftime("%d%m%y%H%M%S")
        if self.tmp_path.endswith("/"):
            self.tmp_path = self.tmp_path[:-1]

        return "{}/{}_{}_{}".format(
            self.tmp_path,
            str(self.Emisor.get("Rfc")),
            fecha,
            file_name,
        )

    def iso_date(self, fecha):
        """
        Recibe la fecha y la cambia a la zona horaria establecida.
        """
        
        if settings.USE_TZ:
            import pytz
            timezoneLocal = pytz.timezone(self.timezone)
            return fecha.astimezone(timezoneLocal).strftime('%Y-%m-%dT%H:%M:%S')

        else:
            iso_tuple = (
                fecha.year, fecha.month, fecha.day,
                fecha.hour, fecha.minute, fecha.second,
                0,0,0,
            )
            return time.strftime('%Y-%m-%dT%H:%M:%S', iso_tuple)

    def generar_xml(self):
        return self.generar_xml_v33()
        
    def generar_xml_v33(self):

        xml = u'<?xml version="1.0" encoding="UTF-8"?>'
        xml += "<cfdi:Comprobante "
        xml += 'xmlns:cfdi="http://www.sat.gob.mx/cfd/3" '
        xml += 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        xml += 'xsi:schemaLocation="http://www.sat.gob.mx/cfd/3 http://www.sat.gob.mx/sitio_internet/cfd/3/cfdv33.xsd'

        for complemento in self.complementos:
            if getattr(complemento, "schemaLocation", None):
                xml += ' {}'.format(complemento.schemaLocation)

        if self.Receptor.get("Rfc", "") == "MTE440316E54":
            xml += ' http://www.fact.com.mx/schema/mte http://www.mysuitemex.com/fact/schema/mte_2013.xsd'

        if self.retenciones_locales or self.traslados_locales: 
            xml += ' http://www.sat.gob.mx/implocal http://www.sat.gob.mx/sitio_internet/cfd/implocal/implocal.xsd'

        if self.nomina:
            xml += ' http://www.sat.gob.mx/nomina12 http://www.sat.gob.mx/sitio_internet/cfd/nomina/nomina12.xsd'

        if self.pagos:
            xml += ' http://www.sat.gob.mx/Pagos http://www.sat.gob.mx/sitio_internet/cfd/Pagos/Pagos10.xsd'

        if self.construccion_licencia:
            xml += ' http://www.sat.gob.mx/servicioparcialconstruccion http://www.sat.gob.mx/sitio_internet/cfd/servicioparcialconstruccion/servicioparcialconstruccion.xsd'

        if self.ine:
            xml += ' http://www.sat.gob.mx/ine http://www.sat.gob.mx/sitio_internet/cfd/ine/ine11.xsd'

        if self.iedu:
            xml += ' http://www.sat.gob.mx/iedu http://www.sat.gob.mx/sitio_internet/cfd/iedu/iedu.xsd'

        if self.comercio_exterior:
            xml += ' http://www.sat.gob.mx/ComercioExterior11 http://www.sat.gob.mx/sitio_internet/cfd/ComercioExterior11/ComercioExterior11.xsd'

        xml += '" '

        for complemento in self.complementos:
            for xmlns in complemento.xmlns_list:
                xml += '\n{} '.format(xmlns)

        if self.Receptor.get("Rfc", "") == "MTE440316E54":
           xml += 'xmlns:mte="http://www.fact.com.mx/schema/mte" '

        if self.retenciones_locales or self.traslados_locales: 
            xml += '\nxmlns:implocal="http://www.sat.gob.mx/implocal" '

        if self.nomina:
            xml += '\nxmlns:nomina12="http://www.sat.gob.mx/nomina12" '
            xml += '\nxmlns:catNomina="http://www.sat.gob.mx/sitio_internet/cfd/catalogos/Nomina" '
            xml += '\nxmlns:tdCFDI="http://www.sat.gob.mx/sitio_internet/cfd/tipoDatos/tdCFDI" '
            xml += '\nxmlns:catCFDI="http://www.sat.gob.mx/sitio_internet/cfd/catalogos" '

        if self.pagos:
            #xml += '\nxmlns:pago10="http://www.sat.gob.mx/sitio_internet/cfd/Pagos" '
            xml += '\nxmlns:pago10="http://www.sat.gob.mx/Pagos" '


        if self.construccion_licencia:
            xml += 'xmlns:servicioparcial="http://www.sat.gob.mx/servicioparcialconstruccion" '

        if self.ine:
            xml += 'xmlns:ine="http://www.sat.gob.mx/ine" '

        if self.iedu:
            xml += 'xmlns:iedu="http://www.sat.gob.mx/iedu" '

        if self.comercio_exterior:
            xml += 'xmlns:cce11="http://www.sat.gob.mx/ComercioExterior11" '


        xml += get_field("Version", self.Version)
        xml += get_field("Serie", self.Serie)
        xml += get_field("Folio", self.Folio)
        xml += get_field("Fecha", self.iso_date(self.Fecha))
        xml += get_field("NoCertificado", self.NoCertificado)
        if self.sello:
            xml += get_field("Sello", self.sello)
            
        xml += get_field("Certificado", self.Certificado )

        xml += get_field("SubTotal", self.SubTotal)
        xml += get_field("Moneda", self.Moneda)
        xml += get_field("Total", self.Total)
        xml += get_field("TipoDeComprobante", self.TipoDeComprobante)
        xml += get_field("FormaPago", self.FormaPago)
        xml += get_field("MetodoPago", self.MetodoPago)
        xml += get_field("CondicionesDePago", self.CondicionesDePago)
        xml += get_field("Descuento", self.Descuento)
        xml += get_field("TipoCambio", self.TipoCambio)
        xml += get_field("LugarExpedicion", self.LugarExpedicion)
        xml += ">"

        if self.CfdiRelacionados.get("documentos"):
            xml += '<cfdi:CfdiRelacionados TipoRelacion="%s">' % self.CfdiRelacionados["TipoRelacion"]
            for uuid in self.CfdiRelacionados["documentos"]:
                xml += '<cfdi:CfdiRelacionado UUID="%s" />' % uuid
            xml += "</cfdi:CfdiRelacionados>"
            
        #Emisor
        xml += "<cfdi:Emisor "
        xml += get_field("Rfc", self.Emisor.get("Rfc"))
        xml += get_field("Nombre", self.Emisor.get("Nombre"))
        #xml += get_field("Curp", self.Emisor.get("Curp"))
        xml += get_field("RegimenFiscal", self.Emisor.get("RegimenFiscal"))
        xml += "/>"
        #Receptor
        xml += "<cfdi:Receptor "
        xml += get_field("Rfc", self.Receptor.get("Rfc"))
        xml += get_field("Nombre", self.Receptor.get("Nombre"))
        xml += get_field("Curp", self.Receptor.get("Curp"))
        xml += get_field("ResidenciaFiscal", self.Receptor.get("ResidenciaFiscal"))
        xml += get_field("NumRegIdTrib", self.Receptor.get("NumRegIdTrib"))
        xml += get_field("UsoCFDI", self.Receptor.get("UsoCFDI"))
        xml += "/>"

        xml += "<cfdi:Conceptos>"
        for concepto in self.conceptos:
            xml += "<cfdi:Concepto "
            xml += get_field("NoIdentificacion", concepto.get("NoIdentificacion"))
            xml += get_field("ClaveUnidad", concepto.get("ClaveUnidad"))
            xml += get_field("Cantidad", concepto.get("Cantidad"))
            xml += get_field("Unidad", concepto.get("Unidad"))
            xml += get_field("Descripcion", concepto.get("Descripcion")[:900] )
            xml += get_field("ValorUnitario", concepto.get("ValorUnitario"))
            xml += get_field("Importe", concepto.get("Importe"))
            xml += get_field("ClaveProdServ", concepto.get("ClaveProdServ"))
            xml += get_field("Descuento", concepto.get("Descuento"))

            if concepto.get("traslados") or concepto.get("retenciones") or concepto.get("CuentaPredial", {}):
                xml += ">"
                if concepto.get("traslados") or concepto.get("retenciones"):
                    xml += "<cfdi:Impuestos> "
                    if concepto.get("traslados"):
                        xml += "<cfdi:Traslados> "
                        for traslado in concepto.get("traslados"):
                            xml += '<cfdi:Traslado '
                            xml += get_field("Base", traslado.get("Base"))
                            xml += get_field("Impuesto", traslado["Impuesto"])
                            xml += get_field("TipoFactor", traslado["TipoFactor"])
                            xml += get_field("TasaOCuota", traslado.get("TasaOCuota", ""))
                            xml += get_field("Importe", traslado.get("Importe", ""))
                            xml += "/>"
                        xml += "</cfdi:Traslados>"

                    if concepto["retenciones"]:
                        xml += "<cfdi:Retenciones> "
                        for retencion in concepto["retenciones"]:
                            xml += '<cfdi:Retencion '
                            xml += get_field("Base", retencion["Base"])
                            xml += get_field("Impuesto", retencion["Impuesto"])
                            xml += get_field("TipoFactor", retencion["TipoFactor"])
                            xml += get_field("TasaOCuota", retencion["TasaOCuota"])
                            xml += get_field("Importe", retencion["Importe"])
                            xml += "/>"
                        xml += "</cfdi:Retenciones>"
                    xml += "</cfdi:Impuestos> "

                if not self.comercio_exterior:
                    for p in concepto.get("pedimentos", []):
                        np = p.get("numero", "").replace(" ", "")
                        numero_pedimento = "%s  %s  %s  %s" % (np[:2], np[2:4], np[4:8], np[8:])
                        xml += '<cfdi:InformacionAduanera NumeroPedimento="%s"/>' % numero_pedimento

                if concepto.get("CuentaPredial", {}):
                    xml += "<cfdi:CuentaPredial "
                    xml += get_field("Numero", concepto.get("CuentaPredial", {}).get("Numero"))
                    xml += "/>"
                
                xml += "</cfdi:Concepto>"
            else:
                xml += "/>"

        xml += "</cfdi:Conceptos>"

        if self.traslados or self.retenciones:
            xml += "<cfdi:Impuestos "
            if self.TotalImpuestosRetenidos:
                xml += get_field("TotalImpuestosRetenidos", self.TotalImpuestosRetenidos)
            
            xml += get_field("TotalImpuestosTrasladados", self.TotalImpuestosTrasladados)
            xml += ">"
            
            if self.retenciones:
                xml += "<cfdi:Retenciones>"
                for retencion in self.retenciones:
                    xml += '<cfdi:Retencion '
                    xml += get_field("Impuesto", retencion["Impuesto"])
                    xml += get_field("Importe", retencion["Importe"])
                    xml += "/>"
                xml += "</cfdi:Retenciones>"

            if self.traslados:
                xml += "<cfdi:Traslados>"
                for traslado in self.traslados:
                    xml += '<cfdi:Traslado '
                    xml += get_field("Impuesto", traslado["Impuesto"])
                    xml += get_field("TipoFactor", traslado["TipoFactor"])
                    xml += get_field("TasaOCuota", traslado["TasaOCuota"])
                    xml += get_field("Importe", traslado["Importe"])
                    xml += "/>"
                xml += "</cfdi:Traslados>"  

            xml += "</cfdi:Impuestos>"

        elif (self.TipoDeComprobante == "E" or self.TipoDeComprobante == "I" or self.TipoDeComprobante == "N") and (self.TotalImpuestosRetenidos or self.TotalImpuestosTrasladados):
            xml += "<cfdi:Impuestos "
            xml += get_field("TotalImpuestosRetenidos", self.TotalImpuestosRetenidos)
            xml += get_field("TotalImpuestosTrasladados", self.TotalImpuestosTrasladados)
            xml += "/>"
          

        xml = self.generar_xml_complementos(xml)
        xml += "</cfdi:Comprobante>"
        self.xml = ''.join(c for c in xml if c.isprintable())

        try:
            assert self.suprimir_caracteres_especiales 
        except:
            pass
        else:
            caracteres_permitidos = [chr(i) for i in range(128)] + list("ñÑáÁéÉíÍóÓúÚüÜ")
            self.xml = ''.join(c for c in xml if c in caracteres_permitidos)


    def generar_xml_complementos(self, xml):
        """
        Se genera el nodo Complemento de acuerdo
        a los complementos que trae el comprobante
        """
        if self.nomina or \
           self.retenciones_locales or \
           self.traslados_locales or \
           self.construccion_licencia or \
           self.ine or \
           self.iedu or \
           self.detallista or \
           self.comercio_exterior or \
           self.pagos or \
           self.leyendasFiscales or \
           self.complementos:
            
            xml += '<cfdi:Complemento>'
            for complemento in self.complementos:
                complemento.timezone = self.timezone
                xml += complemento.get_xml_string()

            if self.ine:
                xml += '<ine:INE xmlns:implocal="http://www.sat.gob.mx/ine" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                xml += 'xsi:schemaLocation="http://www.sat.gob.mx/ine http://www.sat.gob.mx/sitio_internet/cfd/ine/ine11.xsd" Version="1.1" '
                if self.ine["tipo_proceso"] == "Ordinario":
                    xml += 'TipoComite="%s" ' % ( escape(self.ine["tipo_comite"]) )
               
                xml += 'TipoProceso="%s">' % escape(self.ine["tipo_proceso"]) 
                if self.ine.get("clave_entidad"):
                    xml += '<ine:Entidad '

                    if self.ine["tipo_proceso"] != "Ordinario":
                        if "estatal" in escape(self.ine["tipo_comite"]).lower():
                            xml += 'Ambito="Local" '
                        else:
                            xml += 'Ambito="Federal" '

                    xml += 'ClaveEntidad="%s">' % escape(self.ine["clave_entidad"])
                    xml += '<ine:Contabilidad IdContabilidad="%s" />' % escape(self.ine["id_contabilidad"])
                    xml += '</ine:Entidad>'

                xml += '</ine:INE>'

            if self.iedu:
                xml += '<iedu:instEducativas version="1.0" '
                xml += 'nombreAlumno="%s" ' % escape(self.iedu["nombreAlumno"])
                xml += 'CURP="%s" ' % escape(self.iedu["CURP"])
                xml += 'nivelEducativo="%s" ' % escape(self.iedu["nivelEducativo"])
                xml += 'autRVOE="%s" ' % escape(self.iedu["autRVOE"])
                
                rfcPago = escape(self.iedu["rfcPago"])
                if rfcPago:
                    xml += 'rfcPago="%s" ' % rfcPago

                xml += '/>'

            if self.detallista and self.TipoDeComprobante == "I":
                xml += '''<detallista:detallista 
    type="SimpleInvoiceType" 
    contentVersion="1.3.1" 
    documentStructureVersion="AMC8.1" 
    documentStatus="%s" 
    xmlns:detallista="http://www.sat.gob.mx/detallista">''' % (self.detallista["documentStatus"])

                xml += '''<detallista:requestForPaymentIdentification>
        <detallista:entityType>%s</detallista:entityType>
    </detallista:requestForPaymentIdentification>''' % self.detallista["entityType"]

                xml += '''<detallista:specialInstruction code="%s">''' % self.detallista["code"]
                xml += '''<detallista:text>%s</detallista:text>
    </detallista:specialInstruction>''' % (self.detallista["cantidad_letra"])
                xml += '''<detallista:orderIdentification>
        <detallista:referenceIdentification type="ON">%s</detallista:referenceIdentification>
        <detallista:ReferenceDate>%s</detallista:ReferenceDate>
    </detallista:orderIdentification>''' % (self.detallista["referenceIdentification"], self.detallista["fecha_oc"] )

                xml += '''<detallista:AdditionalInformation>
        <detallista:referenceIdentification type="ACE">1</detallista:referenceIdentification>
    </detallista:AdditionalInformation>'''

                xml += '''<detallista:DeliveryNote>
        <detallista:referenceIdentification>%s</detallista:referenceIdentification>
        <detallista:ReferenceDate>%s</detallista:ReferenceDate>
    </detallista:DeliveryNote>''' % (self.detallista["deliveryNote"], self.detallista["fecha_referencia"])

                xml +='''<detallista:buyer>
        <detallista:gln>%s</detallista:gln>
        <detallista:contactInformation>
            <detallista:personOrDepartmentName>
                <detallista:text>%s</detallista:text>
            </detallista:personOrDepartmentName>
        </detallista:contactInformation>
    </detallista:buyer>''' % (self.detallista["buyerGLN"], self.detallista["personDepartament"])
                
                xml += '''<detallista:seller>
        <detallista:gln>%.013d</detallista:gln>
        <detallista:alternatePartyIdentification type="SELLER_ASSIGNED_IDENTIFIER_FOR_A_PARTY">%s</detallista:alternatePartyIdentification>
    </detallista:seller>''' % (int(self.detallista["sellerGLN"]), self.detallista["sellerGLN"])

                xml += '''<detallista:allowanceCharge allowanceChargeType="ALLOWANCE_GLOBAL" settlementType="OFF_INVOICE">
        <detallista:specialServicesType>AJ</detallista:specialServicesType>
        <detallista:monetaryAmountOrPercentage>
            <detallista:rate base="INVOICE_VALUE">
                <detallista:percentage>0</detallista:percentage>
            </detallista:rate>
        </detallista:monetaryAmountOrPercentage>
    </detallista:allowanceCharge>
    <detallista:lineItem number="1">
        <detallista:tradeItemIdentification>
            <detallista:gtin>2050081295008</detallista:gtin>
        </detallista:tradeItemIdentification>
        <detallista:alternateTradeItemIdentification type="BUYER_ASSIGNED">2050081295008</detallista:alternateTradeItemIdentification>
        <detallista:tradeItemDescriptionInformation language="ES">
            <detallista:longText>IREEMO 2 BLANCO</detallista:longText>
        </detallista:tradeItemDescriptionInformation>
        <detallista:invoicedQuantity unitOfMeasure="PIEZA">252</detallista:invoicedQuantity>
        <detallista:grossPrice>
            <detallista:Amount>782.145</detallista:Amount>
        </detallista:grossPrice>
        <detallista:netPrice>
            <detallista:Amount>782.145</detallista:Amount>
        </detallista:netPrice>
        <detallista:totalLineAmount>
            <detallista:grossAmount>
                <detallista:Amount>197100.540</detallista:Amount>
            </detallista:grossAmount>
            <detallista:netAmount>
                <detallista:Amount>197100.540</detallista:Amount>
            </detallista:netAmount>
        </detallista:totalLineAmount>
    </detallista:lineItem>
    <detallista:totalAmount>
        <detallista:Amount>228636.63</detallista:Amount>
    </detallista:totalAmount>
    <detallista:TotalAllowanceCharge allowanceOrChargeType="ALLOWANCE">
        <detallista:specialServicesType>AA</detallista:specialServicesType>
        <detallista:Amount>0</detallista:Amount>
    </detallista:TotalAllowanceCharge>
</detallista:detallista>'''
            
            if self.nomina:
            
                xml += '<nomina12:Nomina '
                
                #xml += 'xmlns:nomina12="http://www.sat.gob.mx/nomina12" '

                #xml += 'xsi:schemaLocation="http://www.sat.gob.mx/nomina12 '
                #xml += 'http://www.sat.gob.mx/informacion_fiscal/factura_electronica/Documents/Complementoscfdi/nomina12.xsd" '

                xml += 'Version="1.2" '
                xml += 'TipoNomina="%s" ' % self.nomina["TipoNomina"]
                xml += 'FechaPago="%s" ' % self.nomina["FechaPago"]
                xml += 'FechaInicialPago="%s" ' % self.nomina["FechaInicialPago"]
                xml += 'FechaFinalPago="%s" ' % self.nomina["FechaFinalPago"]
                xml += 'NumDiasPagados="%s" ' % self.nomina["NumDiasPagados"]
                
                if self.nomina.get("TotalPercepciones"):
                    xml += 'TotalPercepciones="%s" ' % self.nomina["TotalPercepciones"]
                
                if self.nomina.get("TotalDeducciones"):
                    xml += 'TotalDeducciones="%s" ' % self.nomina["TotalDeducciones"]

                if self.nomina.get("TotalOtrosPagos"):
                    xml += 'TotalOtrosPagos="%s" ' % self.nomina["TotalOtrosPagos"]

                xml += '>'

                xml += '<nomina12:Emisor '
                
                if self.nomina["Emisor"].get("Curp"):
                    xml += 'Curp="%s" ' % self.nomina["Emisor"]["Curp"]

                if self.nomina["Emisor"].get("RegistroPatronal"):
                    xml += 'RegistroPatronal="%s" ' % self.nomina["Emisor"]["RegistroPatronal"]
                
                if self.nomina["Emisor"].get("RfcPatronOrigen"):
                    xml += 'RfcPatronOrigen="%s" ' % self.nomina["Emisor"]["RfcPatronOrigen"]
                xml += '>'
                
                if self.nomina["Emisor"].get("EntidadSNCF"):
                    xml += '<nomina12:EntidadSNCF '
                    xml +='OrigenRecurso="%s" ' % self.nomina["Emisor"]["EntidadSNCF"]["OrigenRecurso"]
                    if self.nomina["Emisor"]["EntidadSNCF"]["MontoRecursoPropio"]:
                        xml += 'MontoRecursoPropio="%s" ' % self.nomina["Emisor"]["EntidadSNCF"]["MontoRecursoPropio"]
                    xml += '/>'

                xml += '</nomina12:Emisor>'

                xml += '<nomina12:Receptor '
                xml += 'Curp="%s" ' % self.nomina["Receptor"]["Curp"]
                if self.nomina["Receptor"].get("NumSeguridadSocial"):
                    xml += 'NumSeguridadSocial="%s" ' % self.nomina["Receptor"]["NumSeguridadSocial"]

                if self.nomina["Receptor"].get("FechaInicioRelLaboral"):
                    xml += 'FechaInicioRelLaboral="%s" ' % self.nomina["Receptor"]["FechaInicioRelLaboral"]
                
                if self.nomina["Receptor"].get(u"Antigüedad"):
                    xml += u'Antigüedad="%s" ' % self.nomina["Receptor"][u"Antigüedad"]
                
                if self.nomina["Receptor"].get("TipoContrato"):
                    xml += 'TipoContrato="%s" ' % self.nomina["Receptor"]["TipoContrato"]
                
                if self.nomina["Receptor"].get("Sindicalizado"):
                    xml += u'Sindicalizado="%s" ' % self.nomina["Receptor"]["Sindicalizado"]
                
                if self.nomina["Receptor"].get("TipoJornada"):
                    xml += 'TipoJornada="%s" ' % self.nomina["Receptor"]["TipoJornada"]
                
                if self.nomina["Receptor"].get("TipoRegimen"):
                    xml += 'TipoRegimen="%s" ' % self.nomina["Receptor"]["TipoRegimen"]
                
                if self.nomina["Receptor"].get("NumEmpleado"):
                    xml += 'NumEmpleado="%s" ' % self.nomina["Receptor"]["NumEmpleado"]
                
                if self.nomina["Receptor"].get("Departamento"):
                    xml += 'Departamento="%s" ' % self.nomina["Receptor"]["Departamento"]
                
                if self.nomina["Receptor"].get("Puesto"):
                    xml += 'Puesto="%s" ' % escape(self.nomina["Receptor"]["Puesto"])
                
                if self.nomina["Receptor"].get("RiesgoPuesto"):
                    xml += 'RiesgoPuesto="%s" ' % self.nomina["Receptor"]["RiesgoPuesto"]
                
                if self.nomina["Receptor"].get("PeriodicidadPago"):
                    xml += 'PeriodicidadPago="%s" ' % self.nomina["Receptor"]["PeriodicidadPago"]
                
                if self.nomina["Receptor"].get("Banco"):
                    xml += 'Banco="%s" ' % self.nomina["Receptor"]["Banco"]
                
                if self.nomina["Receptor"].get("CuentaBancaria"):
                    xml += 'CuentaBancaria="%s" ' % self.nomina["Receptor"]["CuentaBancaria"]
                
                if self.nomina["Receptor"].get("SalarioBaseCotApor"):
                    xml += 'SalarioBaseCotApor="%s" ' % self.nomina["Receptor"]["SalarioBaseCotApor"]
                
                if self.nomina["Receptor"].get("SalarioDiarioIntegrado"):
                    xml += 'SalarioDiarioIntegrado="%s" ' % self.nomina["Receptor"]["SalarioDiarioIntegrado"]
                
                if self.nomina["Receptor"].get("ClaveEntFed"):
                    xml += 'ClaveEntFed="%s" ' % self.nomina["Receptor"]["ClaveEntFed"]
                xml += '>'

                if self.nomina["Receptor"].get("SubContratacion"):
                    xml += '<nomina12:SubContratacion RfcLabora="%s" PorcentajeTiempo="%s" />' % (
                        self.nomina["Receptor"]["SubContratacion"]["RfcLabora"],
                        self.nomina["Receptor"]["SubContratacion"]["PorcentajeTiempo"],
                )
                xml += '</nomina12:Receptor>'

                if self.nomina.get("Percepciones"):
                    xml += '\n<nomina12:Percepciones '
                    
                    if self.nomina["Percepciones"]["TotalSueldos"]:
                        xml += '\nTotalSueldos="%s" ' % self.nomina["Percepciones"]["TotalSueldos"]
                    if self.nomina["Percepciones"]["TotalSeparacionIndemnizacion"]:
                        xml += '\nTotalSeparacionIndemnizacion="%s" ' % self.nomina["Percepciones"]["TotalSeparacionIndemnizacion"]
                    if self.nomina["Percepciones"]["TotalJubilacionPensionRetiro"]:
                        xml += '\nTotalJubilacionPensionRetiro="%s" ' % self.nomina["Percepciones"]["TotalJubilacionPensionRetiro"]
                    xml += '\nTotalGravado="%s" ' % self.nomina["Percepciones"]["TotalGravado"]
                    xml += '\nTotalExento="%s" ' % self.nomina["Percepciones"]["TotalExento"]
                    xml += '>'

                    for percepcion in self.nomina["Percepciones"]["percepciones"]:
                        xml += '\n<nomina12:Percepcion '
                        xml += '\nTipoPercepcion="%s" ' % percepcion["TipoPercepcion"]
                        xml += '\nClave="%s" ' % percepcion["Clave"]
                        xml += '\nConcepto="%s" ' % percepcion["Concepto"]
                        xml += '\nImporteGravado="%s" ' % percepcion["ImporteGravado"]
                        xml += '\nImporteExento="%s" ' % percepcion["ImporteExento"]
                        if percepcion.get("AccionesOTitulos") or percepcion.get("HorasExtra"):
                            xml += '>'
                            if percepcion.get("AccionesOTitulos"):
                                xml += '<AccionesOTitulos ValorMercado="%s" PrecioAlOtorgarse="%s" />' % (
                                    percepcion["AccionesOTitulos"]["ValorMercado"], 
                                    percepcion["AccionesOTitulos"]["PrecioAlOtorgarse"],
                                )

                            if percepcion.get("HorasExtra"):
                                for he in percepcion.get("HorasExtra"):
                                    xml += '<nomina12:HorasExtra Dias="%s" TipoHoras="%s" HorasExtra="%s" ImportePagado="%s"/>' % (
                                        he["Dias"], 
                                        he["TipoHoras"],
                                        he["HorasExtra"],
                                        he["ImportePagado"],
                                    )
                            xml += '</nomina12:Percepcion>'
                        else:
                            xml += '/>'

                    if self.nomina["Percepciones"].get("JubilacionPensionRetiro"):
                        xml += '<nomina12:JubilacionPensionRetiro '
                        xml += 'TotalUnaExhibicion="%s" ' % self.nomina["Percepciones"]["JubilacionPensionRetiro"]["TotalUnaExhibicion"]
                        xml += 'TotalParcialidad="%s" ' % self.nomina["Percepciones"]["JubilacionPensionRetiro"]["TotalParcialidad"]
                        xml += 'MontoDiario="%s" '% self.nomina["Percepciones"]["JubilacionPensionRetiro"]["MontoDiario"]
                        xml += 'IngresoAcumulable="%s"' % self.nomina["Percepciones"]["JubilacionPensionRetiro"]["IngresoAcumulable"]
                        xml += 'IngresoNoAcumulable="%s"' % self.nomina["Percepciones"]["JubilacionPensionRetiro"]["IngresoNoAcumulable"]

                    if self.nomina["Percepciones"].get("SeparacionIndemnizacion"):
                        xml += '<nomina12:SeparacionIndemnizacion '
                        xml += 'TotalPagado="%.2f" ' % self.nomina["Percepciones"]["SeparacionIndemnizacion"]["TotalPagado"]
                        xml += u'NumAñosServicio="%s" ' % self.nomina["Percepciones"]["SeparacionIndemnizacion"][u"NumAñosServicio"]
                        xml += 'IngresoAcumulable="%.2f" '% self.nomina["Percepciones"]["SeparacionIndemnizacion"]["IngresoAcumulable"]
                        xml += 'IngresoNoAcumulable="%.2f" ' % self.nomina["Percepciones"]["SeparacionIndemnizacion"]["IngresoNoAcumulable"]
                        xml += 'UltimoSueldoMensOrd="%.2f" ' % self.nomina["Percepciones"]["SeparacionIndemnizacion"]["UltimoSueldoMensOrd"]
                        xml += "/>"
                    xml += '</nomina12:Percepciones>'


                if self.nomina.get("Deducciones"):
                    xml += '<nomina12:Deducciones '

                    if self.nomina["Deducciones"]["TotalOtrasDeducciones"]:
                        xml += 'TotalOtrasDeducciones="%s" ' % self.nomina["Deducciones"]["TotalOtrasDeducciones"]

                    if self.nomina["Deducciones"]["TotalImpuestosRetenidos"]:
                        xml += 'TotalImpuestosRetenidos="%s" ' % self.nomina["Deducciones"]["TotalImpuestosRetenidos"]
                    xml += '>'

                    for deduccion in self.nomina["Deducciones"]["deducciones"]:
                        xml += '<nomina12:Deduccion '
                        xml += 'TipoDeduccion="%s" ' % deduccion["TipoDeduccion"]
                        xml += 'Clave="%s" ' % deduccion["Clave"]
                        xml += 'Concepto="%s" ' % deduccion["Concepto"]
                        xml += 'Importe="%s" ' % deduccion["Importe"]
                        xml += '/>'

                    xml += '</nomina12:Deducciones>'

                if self.nomina.get("OtrosPagos"):
                    xml += '<nomina12:OtrosPagos>'
                    for otropago in self.nomina["OtrosPagos"]["otrospagos"]:
                        xml += '<nomina12:OtroPago '
                        xml += 'TipoOtroPago="%s" ' % otropago["TipoOtroPago"]
                        xml += 'Clave="%s" ' % otropago["Clave"]
                        xml += 'Concepto="%s" ' % otropago["Concepto"]
                        xml += 'Importe="%s" ' % otropago["Importe"]
                        xml += ">"
                        if otropago.get("SubsidioAlEmpleo"):
                            xml += '<nomina12:SubsidioAlEmpleo SubsidioCausado="%s" />' % otropago["SubsidioAlEmpleo"]["SubsidioCausado"]

                        if otropago.get("CompensacionSaldosAFavor"):
                            xml += '<nomina12:CompensacionSaldosAFavor SaldoAFavor="%s" Año="%s" RemanenteSalFav="%s"/>' % (
                                otropago["CompensacionSaldosAFavor"]["SaldoAFavor"],
                                otropago["CompensacionSaldosAFavor"]["Año"],
                                otropago["CompensacionSaldosAFavor"]["RemanenteSalFav"],
                            )

                        xml += '</nomina12:OtroPago>'
                    xml += '</nomina12:OtrosPagos>'

                if self.nomina.get("Incapacidades"):
                    xml += '<nomina12:Incapacidades>'
                    for incapacidad in self.nomina["Incapacidades"]["incapacidades"]:
                        xml += '<nomina12:Incapacidad DiasIncapacidad="%s" TipoIncapacidad="%s" ImporteMonetario="%s" />' % (
                            incapacidad["DiasIncapacidad"],
                            incapacidad["TipoIncapacidad"],
                            incapacidad["ImporteMonetario"],
                        )
                    xml += '</nomina12:Incapacidades>'
                xml += '</nomina12:Nomina>'

            if self.retenciones_locales or self.traslados_locales:
                xml += '<implocal:ImpuestosLocales xmlns:implocal="http://www.sat.gob.mx/implocal" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                xml += 'xsi:schemaLocation="http://www.sat.gob.mx/implocal http://www.sat.gob.mx/sitio_internet/cfd/implocal/implocal.xsd" version="1.0" '
                xml += 'TotaldeRetenciones="%s" TotaldeTraslados="%s">' % (self.total_retenciones_locales, self.total_traslados_locales)
                for r in self.retenciones_locales:
                    xml += '<implocal:RetencionesLocales ImpLocRetenido="%s" TasadeRetencion="%.2f" Importe="%.2f"/>' % (
                        r["nombre"],
                        r["tasa"],
                        r["monto"]
                    )

                for t in self.traslados_locales:
                    xml += '<implocal:TrasladosLocales ImpLocTrasladado="%s" TasadeTraslado="%.2f" Importe="%.2f"/>' % (
                        t["nombre"],
                        t["tasa"],
                        t["monto"]
                    )

                xml += '</implocal:ImpuestosLocales>'

            if self.pagos:
                #xml += '<pago10:Pagos Version="1.0"  xmlns:pago10="http://www.sat.gob.mx/Pagos" xsi:schemaLocation="http://www.sat.gob.mx/Pagos http://www.sat.gob.mx/sitio_internet/cfd/Pagos/Pagos10.xsd">'
                xml += '<pago10:Pagos Version="1.0">'
                for pago in self.pagos:
                    xml += '<pago10:Pago FechaPago="%s" ' % self.iso_date(pago["FechaPago"]) 
                    xml += 'FormaDePagoP="%s" ' % pago["FormaDePagoP"] 
                    xml += 'MonedaP="%s" ' % pago["MonedaP"]
                    if pago["MonedaP"] != "MXN" and pago.get("TipoCambioP"):
                        xml += 'TipoCambioP="%s" ' % pago["TipoCambioP"] 
                    
                    xml += 'Monto="%s" ' % pago["Monto"] 
                    if pago.get("NumOperacion"):
                        xml += 'NumOperacion="%s" ' % pago["NumOperacion"] 
                    if pago.get("NomBancoOrdExt"):
                        xml += 'NomBancoOrdExt="%s" ' % pago["NomBancoOrdExt"] 
                    if pago.get("CtaOrdenante"):
                        xml += 'CtaOrdenante="%s" ' % pago["CtaOrdenante"]
                    if pago.get("RfcEmisorCtaOrd"):
                        xml += 'RfcEmisorCtaOrd="%s" ' % pago["RfcEmisorCtaOrd"]
                    if pago.get("RfcEmisorCtaBen"):
                        xml += 'RfcEmisorCtaBen="%s" ' % pago["RfcEmisorCtaBen"]
                    if pago.get("CtaBeneficiario"):
                        xml += 'CtaBeneficiario="%s" ' % pago["CtaBeneficiario"]
                    
                    if pago.get("TipoCadPago"):
                        xml += 'TipoCadPago="%s" ' % pago["TipoCadPago"]
                    
                    if pago.get("CertPago"):
                        xml += 'CertPago="%s" ' % pago["CertPago"]
                    
                    if pago.get("CadPago"):
                        xml += 'CadPago="%s" ' % pago["CadPago"]
                    
                    if pago.get("SelloPago"):
                        xml += 'SelloPago="%s" ' % pago["SelloPago"]
                    xml += '>'

                    for docto in pago["DoctoRelacionado_set"]:
                        xml += '<pago10:DoctoRelacionado '
                        xml += 'IdDocumento="%s" ' % docto["IdDocumento"]
                        if docto["Serie"]:
                            xml += 'Serie="%s" ' % docto["Serie"]
                        
                        if docto["Folio"]:
                            xml += 'Folio="%s" ' % docto["Folio"]

                        if docto["MonedaDR"]:
                            xml += 'MonedaDR="%s" ' % docto["MonedaDR"]
                        
                        if docto["TipoCambioDR"]:
                            xml += 'TipoCambioDR="%s" ' % docto["TipoCambioDR"]
                        
                        xml += 'MetodoDePagoDR="%s" ' % docto["MetodoDePagoDR"]
                        xml += 'NumParcialidad="%s" ' % docto["NumParcialidad"]
                        xml += 'ImpSaldoAnt="%s" ' % docto["ImpSaldoAnt"]
                        xml += 'ImpPagado="%s" ' % docto["ImpPagado"]
                        xml += 'ImpSaldoInsoluto="%s" ' % docto["ImpSaldoInsoluto"]
                        xml += '/>'

                    xml += '</pago10:Pago>'
                xml += '</pago10:Pagos>'

            if  self.comercio_exterior:
                xml += '<cce11:ComercioExterior Version="1.1" '
                xml += get_field('CertificadoOrigen', self.comercio_exterior["CertificadoOrigen"]) 
                xml += get_field('ClaveDePedimento', self.comercio_exterior["ClaveDePedimento"])
                xml += get_field('NumCertificadoOrigen', self.comercio_exterior["NumCertificadoOrigen"])
                xml += get_field('NumeroExportadorConfiable', self.comercio_exterior["NumeroExportadorConfiable"])
                xml += get_field('Incoterm', self.comercio_exterior["Incoterm"])
                xml += get_field('Observaciones', self.comercio_exterior["Observaciones"])
                xml += get_field('Subdivision', self.comercio_exterior["Subdivision"])
                xml += get_field('TipoCambioUSD', self.comercio_exterior["TipoCambioUSD"])
                xml += get_field('TipoOperacion', self.comercio_exterior["TipoOperacion"])
                xml += get_field('TotalUSD', self.comercio_exterior["TotalUSD"])
                xml += get_field('MotivoTraslado', self.comercio_exterior.get("MotivoTraslado"))
                xml += 'xmlns:cce11="http://www.sat.gob.mx/ComercioExterior11">'
                

                nodo = self.comercio_exterior["Emisor"]
                #xml += '<cce11:Emisor><cce11:Domicilio '
                xml += '<cce11:Emisor %s><cce11:Domicilio ' % get_field('Curp', self.comercio_exterior["Emisor"].get("Curp"))
                xml += get_field('Calle', nodo.get("Calle"))
                xml += get_field('NumeroExterior', nodo.get("NumeroExterior"))
                xml += get_field('NumeroInterior', nodo.get("NumeroInterior"))
                xml += get_field('Colonia', nodo.get("Colonia"))
                xml += get_field('Localidad', nodo.get("Localidad"))
                xml += get_field('Referencia', nodo.get("Referencia"))
                xml += get_field('Municipio', nodo.get("Municipio"))
                xml += get_field('Estado', nodo.get("Estado"))
                xml += get_field('Pais', nodo.get("Pais"))
                xml += get_field('CodigoPostal', nodo.get("CodigoPostal"))
                xml += ' /></cce11:Emisor>'

                if self.comercio_exterior.get("Propietario"):
                    nodo = self.comercio_exterior["Propietario"]
                    xml += '<cce11:Propietario '
                    xml += get_field('NumRegIdTrib', nodo.get("NumRegIdTrib"))
                    xml += get_field('ResidenciaFiscal', nodo.get("ResidenciaFiscal"))
                    xml += ' />'


                nodo = self.comercio_exterior["Receptor"]
                xml += '<cce11:Receptor><cce11:Domicilio '
                xml += get_field('Calle', nodo.get("Calle"))
                xml += get_field('NumeroExterior', nodo.get("NumeroExterior"))
                xml += get_field('NumeroInterior', nodo.get("NumeroInterior"))
                xml += get_field('Colonia', nodo.get("Colonia"))
                xml += get_field('Localidad', nodo.get("Localidad"))
                xml += get_field('Referencia', nodo.get("Referencia"))
                xml += get_field('Municipio', nodo.get("Municipio"))
                xml += get_field('Estado', nodo.get("Estado"))
                xml += get_field('Pais', nodo.get("Pais"))
                xml += get_field('CodigoPostal', nodo.get("CodigoPostal"))
                xml += ' /></cce11:Receptor>'


                nodo = self.comercio_exterior.get("Destinatario")
                if nodo:
                    xml += f'<cce11:Destinatario NumRegIdTrib="{nodo["NumRegIdTrib"]}" Nombre="{nodo["Nombre"]}"><cce11:Domicilio '
                    xml += get_field('Calle', nodo.get("Calle"))
                    xml += get_field('NumeroExterior', nodo.get("NumeroExterior"))
                    xml += get_field('NumeroInterior', nodo.get("NumeroInterior"))
                    xml += get_field('Colonia', nodo.get("Colonia"))
                    xml += get_field('Localidad', nodo.get("Localidad"))
                    xml += get_field('Referencia', nodo.get("Referencia"))
                    xml += get_field('Municipio', nodo.get("Municipio"))
                    xml += get_field('Estado', nodo.get("Estado"))
                    xml += get_field('Pais', nodo.get("Pais"))
                    xml += get_field('CodigoPostal', nodo.get("CodigoPostal"))
                    xml += ' /></cce11:Destinatario>'

                xml += '<cce11:Mercancias>' 
                for mercancia in self.comercio_exterior["Mercancias"]:
                    xml += '<cce11:Mercancia '
                    xml += get_field('CantidadAduana', mercancia.get("CantidadAduana"))
                    xml += get_field('FraccionArancelaria', mercancia.get("FraccionArancelaria"))
                    xml += get_field('UnidadAduana', mercancia.get("UnidadAduana"))
                    xml += get_field('NoIdentificacion', mercancia.get("NoIdentificacion"))
                    xml += get_field('ValorUnitarioAduana', mercancia.get("ValorUnitarioAduana"))
                    xml += get_field('ValorDolares', mercancia.get("ValorDolares"))
                    
                    descripciones_especificas = mercancia.get("DescripcionesEspecificas")
                    if descripciones_especificas:
                        xml += '>'
                        for descesp in descripciones_especificas:
                            xml += '<cce11:DescripcionesEspecificas ' 
                            xml += get_field('Marca', descesp["Marca"])
                            xml += get_field('Modelo', descesp.get("Modelo"))
                            xml += get_field('SubModelo', descesp.get("SubModelo"))
                            xml += get_field('NumeroSerie', descesp.get("NumeroSerie"))
                            xml += '/>'
                        xml += '</cce11:Mercancia>'
                    else:
                        xml += '/>'

                xml += '</cce11:Mercancias>'
                
                xml += '</cce11:ComercioExterior>'

            if self.construccion_licencia:
                xml += '<servicioparcial:parcialesconstruccion Version="1.0" NumPerLicoAut="%s" ' % escape(self.construccion_licencia)
                xml += 'xmlns:servicioparcial="http://www.sat.gob.mx/servicioparcialconstruccion" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                xml += 'xsi:schemaLocation="http://www.sat.gob.mx/servicioparcialconstruccion http://www.sat.gob.mx/sitio_internet/cfd/servicioparcialconstruccion/servicioparcialconstruccion.xsd">'
                xml += '<servicioparcial:Inmueble Calle="%s" ' % escape(self.construccion_calle)
                if self.construccion_no_exterior:
                    xml += 'NoExterior="%s" ' % escape(self.construccion_no_exterior)

                if self.construccion_no_interior:
                    xml += 'NoInterior="%s" ' % escape(self.construccion_no_interior)

                if self.construccion_colonia:
                    xml += 'Colonia="%s" ' % escape(self.construccion_colonia)

                if self.construccion_localidad:
                    xml += 'Localidad="%s" ' % escape(self.construccion_localidad)

                if self.construccion_referencia:
                    xml += 'Referencia="%s" ' % escape(self.construccion_referencia)

                xml +=  'Municipio="%s" Estado="%s" CodigoPostal="%s" />' % (
                    escape(self.construccion_municipio), 
                    escape(self.construccion_estado), 
                    escape(self.construccion_codigo_postal)
                )
                xml += '</servicioparcial:parcialesconstruccion>'



            if self.leyendasFiscales:
                xml += (
                    '<leyendasFisc:LeyendasFiscales xmlns:leyendasFisc="http://www.sat.gob.mx/leyendasFiscales" '
                    'version="1.0" xsi:schemaLocation="http://www.sat.gob.mx/leyendasFiscales '
                    'http://www.sat.gob.mx/sitio_internet/cfd/leyendasFiscales/leyendasFisc.xsd">'
                )
                for leyenda_fisc in self.leyendasFiscales:
                    xml += '<leyendasFisc:Leyenda disposicionFiscal="{}" norma="{}" textoLeyenda="{}" />'.format(
                        leyenda_fisc["disposicionFiscal"],
                        leyenda_fisc["norma"],
                        leyenda_fisc["textoLeyenda"],
                    )
                xml += '</leyendasFisc:LeyendasFiscales>'

            xml += '</cfdi:Complemento>'
        return xml
        

    def generar_sello(self):
        from lxml import etree
        from subprocess import Popen, PIPE
        import os

        xslt_path = XSLT_PATH_CFDI
        co_path = self.get_full_tmp_path("co.txt")
        xml_path = self.get_full_tmp_path("xml.xml")
        styledoc = etree.parse(xslt_path)
        transform = etree.XSLT(styledoc)
        f = io.open(xml_path, 'w', encoding='utf-8')
        f.write(self.xml)
        f.close()
        
        try:
            doc = etree.parse(xml_path)
        except etree.XMLSyntaxError as ex:
            return (
                "No se pudo generar el XML del comprobante, "
                "probablemente haya algún caracter no soportado "
                f"-- Mensaje de error del sistema: {ex}"
            )

        result_tree = transform(doc)
        f = io.open(co_path, 'w', encoding='utf-8')
        f.write(str(result_tree))
        f.close()

        pem_path = self.pem_path or ""
        if getattr(self, "pem", None):
            pem_path = self.get_full_tmp_path("pem.pem")
            self.pem_path = pem_path
            f = open(pem_path, 'w', encoding='utf-8')
            f.write(self.pem)
            f.close()

        #elif not self.pem_path:
        #    self.pem_path = self.cf.pem_path()

        cmd_dgst = ["openssl", "dgst", self.openssl_algo_hash, "-sign", pem_path, co_path,]
        cmd_enc = ["openssl", "enc", "-base64", "-A"]
        if self.pem_path:

            p_dgst = Popen(cmd_dgst, stdout=PIPE)
            p_enc =  Popen(cmd_enc, stdin=p_dgst.stdout, stdout=PIPE)
            self.sello = p_enc.communicate()[0].decode("utf-8")
        
        try:
            os.remove(co_path)
            os.remove(xml_path)
            
            if pem_path:
                os.remove(pem_path)
        except:
            pass

        if not self.TIMBRADO_PRUEBAS and not self.sello:
            return (
                "No se pudo generar el sello del comprobante, "
                "corrobore que su certificado de sello digital "
                "se encuentre correctamente cargado: "
                "%s | %s" % (" ".join(cmd_dgst), " ".join(cmd_enc))
            )



    def sellar_xml(self):
        import re
        self.xml = re.sub(r' Sello=".+?"', '', self.xml)
        if self.Version == "3.3":
            self.xml = self.xml.replace(' Certificado="', ' Sello="%s" Certificado="' % self.sello)
        elif self.Version == "R":
            self.xml = self.xml.replace(' Cert="', ' Sello="%s" Cert="' % self.sello)

    def incrustar_tfd(self, tfd):
        pass

    def timbrar_xml(self, *args, **kwargs):

        if self.PAC == PACS["PRODIGIA"] or self.PAC is None:
            return self._timbrar_prodigia(*args, **kwargs)    
        
        elif self.PAC == PACS["STOCONSULTING"]:
            return self._timbrar_stoconsulting(*args, **kwargs)

        elif self.PAC == PACS["FINKOK"]:
            return self._timbrar_finkok(*args, **kwargs)

        elif self.PAC == PACS["PRUEBA"]:
            return self._timbrar_prueba(*args, **kwargs)

        elif self.PAC == PACS["DFACTURE"]:
            return self._timbrar_dfacture(*args, **kwargs)
        else:
            return self._timbrar_prodigia(*args, **kwargs)

    def set_post_timbrado(self):

        if self.Version == "3.3":
            timbre_xml = self.xml_timbrado.split("<cfdi:Complemento>")[1].split("</cfdi:Complemento>")[0]
            self.cfdi_uuid = timbre_xml.split('UUID="')[1].split('"')[0]
            fecha_cfdi = timbre_xml.split('FechaTimbrado="')[1].split('"')[0]
            self.cfdi_fecha_timbrado = datetime.datetime.strptime(fecha_cfdi , "%Y-%m-%dT%H:%M:%S")
            
            self.cfdi_sello_digital = timbre_xml.split('SelloCFD="')[1].split('"')[0]
            self.cfdi_no_certificado_sat = timbre_xml.split('NoCertificadoSAT="')[1].split('"')[0]
            self.cfdi_sello_sat = timbre_xml.split('SelloSAT="')[1].split('"')[0]


            #self.cfdi_qrcode = u"?re=%s&rr=%s&tt=%s&id=%s" % (
            #    self.emisor_rfc,
            #    self.receptor_rfc,
            #    self.total,
            #    self.cfdi_uuid,
            #)

            try:
                rfc_emisor = self.Emisor.get("Rfc")
                if not rfc_emisor:
                    rfc_emisor = self.xml.strip('<cfdi:Emisor Rfc="')[1].strip('"')[0]
            except:
                rfc_emisor = ""

            try:
                rfc_receptor = self.Receptor.get("Rfc")
                if not rfc_receptor:
                    rfc_receptor = self.xml.strip('<cfdi:Receptor Rfc="')[1].strip('"')[0]
            except:
                rfc_receptor = ""

            self.cfdi_qrcode = 'https://' + \
                'verificacfdi.facturaelectronica.sat.gob.mx' + \
                '/default.aspx?&id=%s&re=%s&rr=%s&tt=%s&fe=%s' % (
                self.cfdi_uuid, 
                rfc_emisor,
                rfc_receptor,
                self.Total, 
                self.cfdi_sello_digital[-8:],
            )

            self.cadena_original_complemento = "||1.1|%s|%s|%s|%s||" % (
                self.cfdi_uuid,
                fecha_cfdi,
                self.cfdi_sello_digital,
                self.cfdi_no_certificado_sat,
            )

        else:
            if self.Version == "R":
                ns = "retenciones"
            else:
                ns = "cfdi"
            timbre_xml = self.xml_timbrado.split("<cfdi:Complemento>")[1].split("</cfdi:Complemento>")[0]
            self.cfdi_uuid = timbre_xml.split('UUID="')[1].split('"')[0]
            fecha_cfdi = timbre_xml.split('FechaTimbrado="')[1].split('"')[0]
            self.cfdi_fecha_timbrado = datetime.strptime( fecha_cfdi , "%Y-%m-%dT%H:%M:%S" )
            self.cfdi_sello_digital = timbre_xml.split('selloCFD="')[1].split('"')[0]
            self.cfdi_no_certificado_sat = timbre_xml.split('noCertificadoSAT="')[1].split('"')[0]
            self.cfdi_sello_sat = timbre_xml.split('selloSAT="')[1].split('"')[0]


            self.cfdi_qrcode = u"?re=%s&rr=%s&tt=%s&id=%s" % (
                self.emisor_rfc,
                self.receptor_rfc,
                self.total,
                self.cfdi_uuid,
            )
            self.cadena_original_complemento = "||1.0|%s|%s|%s|%s||" % (
                self.cfdi_uuid,
                fecha_cfdi,
                self.cfdi_sello_digital,
                self.cfdi_no_certificado_sat,
            )

        if settings.USE_TZ:
            #Se guarda específicamente con la hora de CDMX 
            #porque así se lo requiere el SAT a los proveedores de timbrado.
            self.cfdi_fecha_timbrado = self.cfdi_fecha_timbrado.replace(
                tzinfo=pytz.timezone("America/Mexico_City"))

        try:
            self._post_timbrar_callback()
        except Exception as error:
            self._error_callback(error)


    def registrar_emisor_ntlink(self):
        c  = Object()
        c.razon_social = self.Emisor.get("Nombre")
        c.regimen_fiscal = self.Emisor.get("RegimenFiscal")
        c.rfc = self.Emisor.get("Rfc")
        from .functions import registrar_ntlink
        error = registrar_ntlink(c)
        if error:
            return False
        return self._timbrar_ntlink(registrar=False)


    def _timbrar_ntlink(self, registrar=True):
        from suds.client import Client
        from xml.sax import saxutils
        self.cfdi_uuid = ""

        if self.TIMBRADO_PRUEBAS:
            url = self.ntlink_pruebas_url
            usuario = self.ntlink_pruebas_usuario
            password = self.ntlink_pruebas_password
        else:
            url = self.ntlink_url 
            usuario = self.ntlink_usuario 
            password= self.ntlink_password 


        try:
            xml = self.xml.decode('utf-8')
        except:
            xml = self.xml

        self.xml = xml
        self.inicio_conexion_pac = timezone.now()
        try:
            client = Client(url)
        except Exception as e:
            self.cfdi_status = u"Error al intentar conectar con el PAC: %s -ntlink %s" % (repr(e), self.TIMBRADO_PRUEBAS)
            return False

        self.fin_conexion_pac = timezone.now()
        escaped_xml = saxutils.escape(xml)
        fn = client.service.TimbraCfdi
        self.inicio_timbrado = timezone.now()
        try:
            respuesta_timbrado = fn(usuario, password, escaped_xml)
        except Exception as e: #except (SAXParseException, URLError) as e:
            self.cfdi_status = u"Respuesta inesperada del PAC: %s -ntlink %s" % (repr(e), self.TIMBRADO_PRUEBAS)
            return False
        
        self.fin_timbrado = timezone.now()
        xml_timbrado =""
        from bs4 import BeautifulStoneSoup
        if "<tfd:TimbreFiscalDigital" in respuesta_timbrado:
            complemento = respuesta_timbrado.split("\n")[1]
            #self.cfdi_timbre = respuesta_timbrado
            xml_timbrado = str(self.xml.replace("</cfdi:Complemento>", ""))
            xml_timbrado = xml_timbrado.replace("</cfdi:Comprobante>", "")
            if not "<cfdi:Complemento>" in xml_timbrado:
                xml_timbrado += "<cfdi:Complemento>"
            xml_timbrado += complemento
            xml_timbrado += "</cfdi:Complemento></cfdi:Comprobante>"
            xml_timbrado = " ".join(xml_timbrado.split())
            self.cfdi_xml = xml_timbrado
            self.xml_timbrado = xml_timbrado

        if not xml_timbrado:
            self.cfdi_status = u"%s -ntlink %s" % (respuesta_timbrado, self.TIMBRADO_PRUEBAS)
            if registrar:
                if "No encontrado en la base de datos de emisores" in respuesta_timbrado:
                    return self.registrar_emisor_ntlink()
            return False


        self.cfdi_uuid = complemento.split('UUID="')[1].split('"')[0]
        fecha_cfdi = complemento.split('FechaTimbrado="')[1].split('"')[0]

        self.cfdi_status = ""
        self.cfdi_fecha_timbrado = datetime.strptime(fecha_cfdi , "%Y-%m-%dT%H:%M:%S" )
        self.cfdi_sello_digital = complemento.split('selloCFD="')[1].split('"')[0].decode('utf-8')
        self.cfdi_no_certificado_sat = complemento.split('noCertificadoSAT="')[1].split('"')[0]
        self.cfdi_sello_sat = complemento.split('selloSAT="')[1].split('"')[0]

        self.cfdi_qrcode = u"?re=%s&rr=%s&tt=%s&id=%s" % (
            self.emisor_rfc,
            self.receptor_rfc,
        self.total,
            self.cfdi_uuid,
        )

        self.cadena_original_complemento = "||1.0|%s|%s|%s|%s||" % (
            self.cfdi_uuid,
            self.cfdi_fecha_timbrado,
            self.cfdi_sello_digital,
            self.cfdi_no_certificado_sat,
        )


        #xml_f = open("%s/%s.xml" % (settings.XML_FOLDER, self.cfdi_uuid), 'w')
        #xml_f.write(self.cfdi_xml.encode('utf-8'))
        #xml_f.close()
        return True

    def _timbrar_facturadigital(self):
        from suds.client import Client
        import base64
        
        try:
            xml = self.xml.encode('utf-8')
        except:
            xml = self.xml

        self.xml = xml
        self.inicio_conexion_pac = timezone.now()
        
        if self.TIMBRADO_PRUEBAS:
            rfc = "DPI1211065H7"
            username = "DPI1211065H7"
            password = "'http://prueba.digitalfactura.com:81/facturacion/wsdl/timbrev33.php?wsdl'"
            url_timbrado = 'http://prueba.digitalfactura.com:81/facturacion/wsdl/timbrev33.php?wsdl'

        else:
            pass

        try:
            client = Client(url_timbrado)
        except Exception as e:
            self.cfdi_status = u"Error al intentar conectar con el PAC: %s -facturadigital" % (repr(e))
            return False

        self.fin_conexion_pac = timezone.now()
        self.inicio_timbrado = timezone.now()
        
        try:
            request_auth_token = str(client.service.fnIniciaSesion(rfc, username, password))
            token = request_auth_token.split("1|")[1]
            respuesta_timbrado = client.service.Generartimbre(self.xml, token)

        except Exception as e: #except (SAXParseException, URLError) as e:
            self.cfdi_status = u"Respuesta inesperada del PAC: %s -facturadigital" % (repr(e))
            return False
        self.fin_timbrado = timezone.now()
                
        if respuesta_timbrado:
            self.cfdi_xml = respuesta.xml
            self.xml_timbrado = respuesta.xml
            self.set_post_timbrado()
            return True
        
        return False
            
    def _timbrar_finkok(self, registrar=True):
        
        from suds.client import Client
        import base64
        
        try:
            #Convertir de unicode a str
            xml = self.xml.encode('utf-8')
        except:
            xml = self.xml

        self.xml = xml
        self.inicio_conexion_pac = timezone.now()
        
        if self.TIMBRADO_PRUEBAS:
            finkok_username = "juanefren@admintotal.com"
            finkok_password = "T3nedor!"
            if self.Version == "R":
                stamp_url = "http://demo-facturacion.finkok.com/servicios/soap/retentions.wsdl"
            else: 
                stamp_url = "http://demo-facturacion.finkok.com/servicios/soap/stamp.wsdl"
            
            registration_url = "http://demo-facturacion.finkok.com/servicios/soap/registration.wsdl"

        else:
            finkok_username = settings.FINKOK_USERNAME
            finkok_password = settings.FINKOK_PASSWORD
            if self.Version == "R":
                stamp_url = "http://facturacion.finkok.com/servicios/soap/retentions.wsdl"
            else:
                stamp_url = "http://facturacion.finkok.com/servicios/soap/stamp.wsdl"
            
            registration_url = "http://facturacion.finkok.com/servicios/soap/registration.wsdl"

        try:
            client = Client(stamp_url)
        except Exception as e:
            self.cfdi_status = u"Error al intentar conectar con el PAC: %s -finkok" % (repr(e))
            return False

        self.fin_conexion_pac = timezone.now()
        self.inicio_timbrado = timezone.now()

        try:
            respuesta = client.service.stamp(base64.b64encode(xml).decode(), finkok_username, finkok_password)

        except Exception as e: #except (SAXParseException, URLError) as e:
            self.cfdi_status = u"Respuesta inesperada del PAC: %s -finkok" % (repr(e))
            return False
        self.fin_timbrado = timezone.now()
        
        
        if respuesta.xml:
            respuesta_xml = str(respuesta.xml)
            self.cfdi_xml = respuesta_xml
            self.xml_timbrado = respuesta_xml
            self.set_post_timbrado()

        else:
            self.cfdi_status = u"%s -finkok" % (respuesta)
            if registrar and respuesta.Incidencias: 
                txt_incidencias = str(respuesta.Incidencias)
                if u"Socio de Negocios Inv" in txt_incidencias or u"Sorry there was an error when validating the reseller and user" in txt_incidencias: 
                    cliente = Client(registration_url)
                    cliente.service.add(finkok_username, finkok_password, self.Emisor["Rfc"])
                    return self._timbrar_finkok(registrar=False)

            return False
            
        return True

    def _timbrar_dfacture(self):
        try:
            xml = self.xml.decode('utf-8')
        except:
            xml = self.xml

        self.inicio_conexion_pac = timezone.now()

        if self.TIMBRADO_PRUEBAS:
            url = "http://timbrado.demodfacture.com/api/TimbrarCFDI33"
            usuario = DFACTURE_AUTH["dev"]["usuario"]
            password = DFACTURE_AUTH["dev"]["password"]
        else:
            url = "https://timbradobalancer.dfacture.com/api/timbrarCFDI33"
            usuario = DFACTURE_AUTH["prod"]["usuario"]
            password = DFACTURE_AUTH["prod"]["password"]


        self.inicio_timbrado = timezone.now()
        self.inicio_conexion_pac = self.inicio_timbrado
        
        data = {
            "xml":base64.b64encode(xml.encode("utf-8")).decode(),
            "user":usuario,
            "password":password,
        }

        try:
            respuesta_timbrado = requests.post(url, data=data, verify=False, timeout=120)
        except Exception as e:
            self.cfdi_status = "Hubo un error inesperado del PAC: %s -dfacture" % (e)
            return False        

        self.fin_timbrado = timezone.now()
        self.fin_conexion_pac = self.inicio_conexion_pac
        
        try:
            respuesta_json = json.loads(respuesta_timbrado.text)
        except Exception as e:
            self.cfdi_status = u"Error al paresear respuesta en JSON %s : %s -dfacture" % (respuesta_timbrado.text, e)
            return False


        if respuesta_json.get("xml"):
            self.xml_timbrado = base64.b64decode(respuesta_json["xml"]).decode("utf-8")
            self.cfdi_xml = self.xml_timbrado
            self.set_post_timbrado()
        else:
            self.cfdi_status = u"No se detectó XML en la respuesta: %s -dfacture" % (respuesta_json)
            return False

        return True

    
    def get_headers_prodigia(self):
        concatenated_pass = PRODIGIA_AUTH["prod"]["usuario"] + ":" + PRODIGIA_AUTH["prod"]["password"]
        userpass64 = base64.b64encode(concatenated_pass.encode()).decode()
        
        return {
            "Authorization":"Basic %s" % userpass64, 
            "Content-Type":"application/xml"
        }

    def _timbrar_prodigia(self, test=False):
        try:
            xml = self.xml.decode('utf-8')
        except:
            xml = self.xml

        self.inicio_conexion_pac = timezone.now()

        if test:
            url = "https://pruebas.pade.mx/servicio/Timbrado3.3?contrato=%s" % PRODIGIA_AUTH["prod"]["contrato"]
            verify = False
        else:
            verify = True
            if self.TIMBRADO_PRUEBAS:
                url = "https://timbrado.pade.mx/servicio/rest/timbradoPrueba?contrato=%s" % PRODIGIA_AUTH["prod"]["contrato"]
            else:
                url = "https://timbrado.pade.mx/servicio/rest/timbrado?contrato=%s" % PRODIGIA_AUTH["prod"]["contrato"]


        #if self.recuperar_xml:
        url += '&opciones=REGRESAR_CON_ERROR_307_XML'

        if self.VERIFICAR_SERIE_FOLIO:
            url += '&opciones=VERIFICAR_SERIE_FOLIO'

        self.inicio_timbrado = timezone.now()
        self.inicio_conexion_pac = self.inicio_timbrado
        
        try:
            respuesta_timbrado = requests.post(
                url, 
                data=xml.encode("utf-8"), 
                headers=self.get_headers_prodigia(), 
                verify=verify, 
                timeout=120
            )
        except Exception as e:
            self.cfdi_status = "Hubo un error inesperado del PAC: %s -prodigia" % (e)
            return False        

        self.fin_timbrado = timezone.now()
        self.fin_conexion_pac = self.inicio_conexion_pac
        if not respuesta_timbrado.status_code in [200, 202] and not self.recuperar_xml and not '<codigo>307</codigo>' in respuesta_timbrado.text:
            self.cfdi_status = respuesta_timbrado.text
            self.cfdi_status = "%s -prodigia %s" % (self.cfdi_status, self.TIMBRADO_PRUEBAS)
            return False

        
        respuesta_timbrado_content = respuesta_timbrado.text
        if "<xmlBase64>" in respuesta_timbrado_content:

            self.xml_timbrado = base64.b64decode(respuesta_timbrado_content.split("<xmlBase64>")[1].split("</xmlBase64>")[0]).decode("utf-8")
            self.cfdi_xml = self.xml_timbrado
            self.set_post_timbrado()
        else:
            self.cfdi_status = respuesta_timbrado.text
            self.cfdi_status = "%s -prodigia %s" % (self.cfdi_status, self.TIMBRADO_PRUEBAS)
            return False
            #raise Exception("Respuesta inesperada %s" % respuesta_timbrado_content)

        return True

    def _timbrar_stoconsulting(self):
        try:
            xml = self.xml.decode('utf-8')
        except:
            xml = self.xml

        self.inicio_conexion_pac = timezone.now()

        if self.TIMBRADO_PRUEBAS:
            url = "https://pac-test.stofactura.com/pac-sto-rest/rest/cfdi33/timbrarCfdi/"
            usuario = STO_AUTH["dev"]["usuario"] #"TESTUSERSTO"
            password = STO_AUTH["dev"]["password"] # "TESTPASSSTO"
        else:
            url = "https://pac.stofactura.com/pac-sto-rest/rest/cfdi33/timbrarCfdi/"
            usuario =  STO_AUTH["prod"]["usuario"]
            password = STO_AUTH["prod"]["password"]

        
        md5pass = hashlib.md5(password.encode()).hexdigest()
        #if self.recuperar_xml:
        #    url += '&opciones=REGRESAR_CON_ERROR_307_XML'

        
        

        cfdi_byte_array = bytearray()
        cfdi_byte_array.extend(xml.encode("utf-8"))
        
        data = {
            "usuario":usuario,
            "password":md5pass,
            "cfdi": list(cfdi_byte_array),
        }

        self.inicio_timbrado = timezone.now()
        self.inicio_conexion_pac = self.inicio_timbrado

        try:
            respuesta_timbrado = requests.post(url, json=data, timeout=120)
        except Exception as e:
            self.cfdi_status = "Hubo un error inesperado del PAC: %s -STO" % (e)
            return False 


        
        self.fin_timbrado = timezone.now()
        self.fin_conexion_pac = self.inicio_conexion_pac
        
        if not respuesta_timbrado.status_code in [200, 202]:
            self.cfdi_status = respuesta_timbrado.text
            #self.cfdi_status = respuesta_timbrado.text
            self.cfdi_status = "%s -stoconsulting %s" % (self.cfdi_status, self.TIMBRADO_PRUEBAS)
            return False

        respuesta_json = json.loads(respuesta_timbrado.content.decode("utf-8"))
        if respuesta_json.get("estatus") == "10":
            self.xml_timbrado = respuesta_json["cfdi"]
            self.cfdi_xml = self.xml_timbrado
            self.set_post_timbrado()
        elif respuesta_json.get("mensaje"):
            self.cfdi_status = respuesta_json.get("mensaje")
            return False
        else:

            raise Exception("Respuesta inesperada %s -stoconsultint" % respuesta_json)
        return True

    def _timbrar_prueba(self):
        from xml.sax import saxutils

        try:
            xml = self.xml.decode("utf-8")
        except:
            xml = self.xml
    
        if not self.TIMBRADO_PRUEBAS:
            raise Exception("No se puede timbrar recibos reales usando el PAC para pruebas.")

        self.inicio_timbrado = timezone.now()
        self.inicio_conexion_pac = self.inicio_timbrado

        try:
            if settings.TIMBRADO_PRUEBA_DELAY:
                print(f"Delay de {settings.TIMBRADO_PRUEBA_DELAY}")
                time.sleep(settings.TIMBRADO_PRUEBA_DELAY)
        except:
            pass
            

        self.fin_timbrado = timezone.now()
        self.fin_conexion_pac = self.fin_timbrado = self.fin_timbrado

        respuesta_timbrado_content = self.get_tfd()

        if "<tfd:TimbreFiscalDigital" in respuesta_timbrado_content:
            self.agregar_complemento(respuesta_timbrado_content)
            self.set_post_timbrado()
            return True
        return False

        

    def get_tfd(self):
        import uuid
        cfdi_uuid = str(uuid.uuid4()).upper()
        fecha_timbrado = timezone.now().strftime("%Y-%m-%dT%H:%M:%S")
        tfd_txt = """<tfd:TimbreFiscalDigital 
            xmlns:tfd="http://www.sat.gob.mx/TimbreFiscalDigital" 
            FechaTimbrado="%s" 
            UUID="%s"
            NoCertificadoSAT="00000000000000000000" 
            SelloCFD="%s"
            SelloSAT="Timbrado de prueba, sin validez fiscal."
            version="1.1" 
            xsi:schemaLocation="
                http://www.sat.gob.mx/TimbreFiscalDigital 
                http://www.sat.gob.mx/sitio_internet/timbrefiscaldigital/TimbreFiscalDigital.xsd"
            />""" % (fecha_timbrado, cfdi_uuid, self.sello)
        return tfd_txt

    def get_rfc_receptor_from_xml(self):
        try:
            return "%s" % unescape(
                self.cfdi_xml.split("<cfdi:Receptor ")[1]\
                .split('Rfc="')[1].split('"')[0])
        except:
            return ""


    def get_total_from_xml(self):
        try:
            return self.cfdi_xml.split(' Total="')[1].split('"')[0]

        except:
            return ""

    def cancelar_cfdi(self, dfacture=False, prodigia=False):
        
        rfc_pac = self.cfdi_xml.split('RfcProvCertif="')[1].split('"')[0] if 'RfcProvCertif' in self.cfdi_xml else ""
        if 'oCertificadoSAT="200' in self.cfdi_xml or \
            'NoCertificadoSAT="00000000000000000000' in self.cfdi_xml:
            
            self.acuse_cancelacion = "Acuse para timbre de pruebas"
            return [True, "CFDI de prueba, acuse de cancelación de prueba."]


        if self.TIMBRADO_PRUEBAS:
            return [
                False, 
                "Los ambientes en modo de pruebas solo pueden obtener acuses "
                "de cancelación de facturas hechas en modo de prueba."
            ]
        

        self.rfc_receptor = self.get_rfc_receptor_from_xml()
        self.total = self.get_total_from_xml()
        if dfacture:
            return self.cancelar_dfacture()

        if prodigia:
            return self.cancelar_prodigia()

        if rfc_pac:
            fncancel = {
                #'FIN1203015JA':self.cancelar_finkok,
                'PPD101129EA3':self.cancelar_prodigia,
                #'STO020301G28':self.cancelar_stoconsulting,
                'STO020301G28':self.cancelar_prodigia,
                #'FEL100622S88':self.cancelar_dfacture,
                #'LSO1306189R5':self.cancelar_dfacture,
                'CCF1011111K9':self.cancelar_dfacture,
            }

            fn = fncancel.get(rfc_pac)
            if fn:
                return fn()
            else:
                #return self.cancelar_prodigia()
                return self.cancelar_dfacture()

        return [False, "noCertificadoSAT no reconocido"]


    def cancelar_timbre(self, rfc, uuid, certificado, key, csd_pass):
        return self.cancelar_cfdi()


    def cancelar_ntlink(self):
        self.acuse_cancelacion = ""
        from suds.client import Client
        if self.TIMBRADO_PRUEBAS:
            url = self.ntlink_pruebas_url
            usuario = self.ntlink_pruebas_usuario
            password = self.ntlink_pruebas_password
        else:
            url = self.ntlink_url
            usuario = self.ntlink_usuario
            password = self.ntlink_password

        #xml = self.xml.decode('utf-8')
        client = Client(url)
        try:
            respuesta_timbrado = client.service.CancelaCfdi(usuario, password, self.cfdi_uuid, self.rfc)
        except Exception as e:
            return [False, str(e)]

        cancelado = False
        if "<Acuse xmlns:" in respuesta_timbrado:
            self.acuse_cancelacion = respuesta_timbrado
            cancelado = True

        return [cancelado, respuesta_timbrado]

    def prodigia_recuperar_cfdi(self):
        from suds.client import Client
        #from urllib2 import URLError
        client = Client(self.prodigia_url)

        try:
            msg = client.service.cfdiPorUUID(
                self.prodigia_contrato, 
                self.prodigia_usuario, 
                self.prodigia_password, 
                self.cfdi_uuid
            )
            return [True, msg]

        except Exception as e:
            self.error_conexion = "Hubo un error al conectarse con el PAC %s" % e
            return [False, cfdi.error_conexion]

    def cancelar_prodigia(self):
        self.acuse_cancelacion = ""
        url = "https://timbrado.pade.mx/servicio/rest/cancelacion/cancelar"
        url += f'?contrato={PRODIGIA_AUTH["prod"]["contrato"]}'
        url += f"&rfcEmisor={requests.utils.quote(self.rfc)}"
        url += f"&certBase64={requests.utils.quote(self.certificado)}"
        url += f"&keyBase64={requests.utils.quote(self.key)}"
        url += f"&keyPass={requests.utils.quote(self.csd_pass)}"
        url += f"&arregloUUID={self.cfdi_uuid}"
        url += f"|{requests.utils.quote(self.rfc_receptor)}"
        url += f"|{requests.utils.quote(self.rfc)}"
        url += f"|{self.total}"

        if self.motivo_cancelacion:
            url += f"|{self.motivo_cancelacion}"
            if self.motivo_cancelacion == "01" and self.uuid_relacionado_cancelacion:
                url += f"|{self.uuid_relacionado_cancelacion}"


        respuesta = requests.post(
            url, 
            headers=self.get_headers_prodigia(), 
            timeout=120
        ).text

        if "<codigo>" in respuesta and "<uuid>" in respuesta:
            respuesta_chunk = respuesta.split("<uuid>")[1]
            codigo = respuesta_chunk.split("<codigo>")[1].split("</codigo>")[0]
            if codigo in ["91", "98", "201", "202"]:
                self.acuse_cancelacion = respuesta
                return [True, respuesta]
            else:
                return [False, respuesta]
        else:
            self.error_conexion = (
                "Respuesta inesperada del pac" 
                f"{respuesta} -prodigia"
            )
            return [False, self.error_conexion]


    def cancelar_dfacture(self):
        return self.dfactura_consulta_cfdi(tipo_consulta=2)

    def consultar_estatus_dfacture(self):
        return self.dfactura_consulta_cfdi(tipo_consulta=3)

    def consultar_relacionados_dfacture(self):
        return self.dfactura_consulta_cfdi(tipo_consulta=4)

    def consultar_pendientes_dfacture(self):
        return self.dfactura_consulta_cfdi(tipo_consulta=5)

    def aceptacion_rechazo_dfacture(self):
        return self.dfactura_consulta_cfdi(tipo_consulta=6)


    def consultar_estatus_prodigia(self):
        self.rfc_receptor = self.get_rfc_receptor_from_xml()
        self.total = self.get_total_from_xml()

        url = "https://timbrado.pade.mx/servicio/rest/cancelacion/consultarEstatusComprobante"
        url += f'?contrato={PRODIGIA_AUTH["prod"]["contrato"]}'
        url += f"&rfcEmisor={requests.utils.quote(self.rfc)}"
        url += f"&rfcReceptor={requests.utils.quote(self.rfc_receptor)}"
        url += f"&uuid={self.cfdi_uuid}"
        url += f"&total={self.total}"

        respuesta = requests.post(
            url, 
            headers=self.get_headers_prodigia(), 
            timeout=120
        ).text


        if "<codigo>" in respuesta and "<uuid>" in respuesta:
            respuesta_chunk = respuesta.split("<uuid>")[1]
            codigo = respuesta_chunk.split("<codigo>")[1].split("</codigo>")[0]
            if codigo in ["91", "98", "201", "202"]:
                self.acuse_cancelacion = respuesta
                return [True, respuesta]
            else:
                return [False, respuesta]
        else:
            self.error_conexion = (
                "Respuesta inesperada del pac" 
                f"{respuesta} -prodigia"
            )
            return [False, self.error_conexion]



    def dfactura_consulta_cfdi(self, tipo_consulta):
        self.acuse_cancelacion = ""

        if tipo_consulta == 1:
            webservice = "XXXXXX"
        elif tipo_consulta == 2:
            webservice = "CancelarCFDI"
        elif tipo_consulta == 3:
            webservice = "ConsultarEstatusCFDI"
        elif tipo_consulta == 4:
            webservice = "ConsultarRelacionadosCFDI"                
        elif tipo_consulta == 5:
            webservice = "ConsultarPendientesCFDI"
        elif tipo_consulta == 6:
            webservice = "AceptacionRechazoCFDI"
               

        if self.TIMBRADO_PRUEBAS:
            url = "http://cancelacion.demodfacture.com/api/%s" % webservice
            usuario = DFACTURE_AUTH["dev"]["usuario"]
            password = DFACTURE_AUTH["dev"]["password"]
        else:
            url = "http://cancelacion.dfacture.com/api/%s" % webservice
            #url = "https://cancelacion.dfacture.com/api/CancelarCFDI"
            usuario = DFACTURE_AUTH["prod"]["usuario"]
            password = DFACTURE_AUTH["prod"]["password"]

        if tipo_consulta == 5:
            data = {
                "user":usuario,
                "password":password,
                "rfcReceptor":self.rfc,
            }

        elif tipo_consulta == 4:
            data = {
                "user":usuario,
                "password":password,
                "uuid":self.cfdi_uuid,
                "rfc":self.rfc,
                "certificado":self.certificado,
                "llave":self.key,
                "password_llave":self.csd_pass,
            }

        else:

            data = {
                "user":usuario,
                "password":password,
                "rfc":self.rfc,
                "rfcEmisor":self.rfc,
                "uuid":self.cfdi_uuid,
                "certificado":self.certificado,
                "llave":self.key,
                "password_llave":self.csd_pass,
                "rfcReceptor":self.rfc_receptor,
                "total":self.total,
                #"motivo":"",
                #"uuidRelacionado":"",
            }

            if self.motivo_cancelacion:
                data["motivo"] = self.motivo_cancelacion
                if self.motivo_cancelacion == "01" and self.uuid_relacionado_cancelacion:
                    data["uuidRelacionado"] = self.uuid_relacionado_cancelacion
        
        try:
            respuesta = requests.post(url, data=data, verify=False, timeout=120).text
        except Exception as e:
            self.error_conexion = "Hubo un error al intentar conectarse con el PAC: %s" % e
            return [False, self.error_conexion]

        try:
            respuesta_json = json.loads(respuesta)
        except Exception as e:
            self.error_conexion = "Hubo un error al intentar parsear el JSON: %s - %s dfacture" % (respuesta, e)
            return [False, self.error_conexion]

        if tipo_consulta == 2 and respuesta_json["codigo"] in [201, 202, "201", "202"]:
            self.acuse_cancelacion = respuesta_json["mensaje"]
            return [True, self.acuse_cancelacion]

        return [False, "%s" % respuesta_json]

    def cancelar_finkok(self):
        self.acuse_cancelacion = ""
        from suds.client import Client
        import base64

        client = Client("http://facturacion.finkok.com/servicios/soap/cancel.wsdl")
        

        lista_uuids = client.factory.create("UUIDS")
        lista_uuids.uuids.string = [self.cfdi_uuid, ]
        key = base64.b64encode(open(self.pem_path, "rb").read()).decode()
        ###certificado = """"""
        
        
        
        #openssl enc -base64 -in /tmp/cer64 
        
        
        try:
            respuesta = client.service.cancel(
                lista_uuids, 
                settings.FINKOK_USERNAME, 
                settings.FINKOK_PASSWORD, 
                self.rfc, 
                self.cer64_finkok, 
                key,
            )

        except Exception as e:
            self.error_conexion = "Hubo un error al intentar conectarse con el PAC: %s" % e
            return [False, self.error_conexion]

        try:
            self.acuse_cancelacion = str(respuesta.Acuse)
            return [True, self.acuse_cancelacion]
        except AttributeError:
            return [False, str(respuesta)]

    def cancelar_stoconsulting(self):

        self.acuse_cancelacion = ""
        if self.TIMBRADO_PRUEBAS:
            url = "https://pac-test.stofactura.com/pac-sto-rest/rest/cfdi33/cancelarCfdiPorUuid/"
            usuario = "TESTUSERSTO"
            password = "TESTPASSSTO"
        else:
            url = "https://pac.stofactura.com/pac-sto-rest/rest/cfdi33/cancelarCfdiPorUuid/"
            usuario =  settings.LOGIN_STCOCONSULTING[0]
            password = settings.LOGIN_STCOCONSULTING[1]
        
        
        pfx = bytearray()
        if getattr(self, "pfx", None):
            pfx.extend(self.pfx)
        else:
            with open(self.pem_path.rsplit('.pem', 1)[0] + ".pfx", "rb") as pfx_file:
                pfx.extend(pfx_file.read())

        data = {
            "usuario":usuario,
            "password":hashlib.md5(password.encode()).hexdigest(),
            "uuid": self.cfdi_uuid,
            "rfcEmisor": self.rfc,
            "pfx":list(pfx),
            "passwordPfx": self.csd_pass,
        }

        respuesta = requests.post(url, json=data, timeout=120)

        if respuesta.status_code == 200:
            json_response = json.loads(respuesta.text)
            
            if json_response.get("estatus") in ["200", "201", "202"]:
                self.acuse_cancelacion = str(respuesta.text)
                return [True, self.acuse_cancelacion]
        
        return [False, str(respuesta.text)]

    def cancelar_diverza(self):

        if self.TIMBRADO_PRUEBAS:           
            url = "https://staging.diverza.com/stamp/cancel/%s/%s/" % (self.rfc, self.cfdi_uuid)
            x_auth_token = "ABCD1234"
        else:
            url = "https://rest.timbrefiscal.mx/stamp/cancel/%s/%s/" % (self.rfc, self.cfdi_uuid)
            #if self.emisor_rfc == "DDE9907137SA":
            x_auth_token = "HQozba9IKZsRS/JAjMyB6NaOAraxOCPl9JZg0EO7UkM="
            #else:
            #    raise Exception("Emisor no configurado para timbrar con Diverza")
            
        respuesta = requests.post(url, headers={ "x-auth-token":x_auth_token, }, timeout=120)
        msg = respuesta.text
        if not respuesta.status_code == 200:
            cancelado = False
        else:
            cancelado = True

        return [cancelado, msg.decode("utf-8")]

    def agregar_complemento(self, complemento):
        if self.PAC == "ntlink":
            complemento = complemento.split("\n")[1]

        if self.Version == "R":
            ns = "retenciones"
        else:
            ns = "cfdi"
        xml_timbrado = str(self.xml.replace("</%s:Complemento>" % ns, ""))
        xml_timbrado = xml_timbrado.replace("</%s:Comprobante>" % ns, "")
        if not "<%s:Complemento>" % ns in xml_timbrado:
            xml_timbrado += "<%s:Complemento>"  % ns
        xml_timbrado += complemento
        xml_timbrado += "</%s:Complemento></%s:Comprobante>" % (ns, ns)
        xml_timbrado = " ".join(xml_timbrado.split())
        self.cfdi_xml = xml_timbrado
        self.xml_timbrado = xml_timbrado
        return xml_timbrado

    def generar_xml_retencion_dividendos(self):
        xml = u'<?xml version="1.0" encoding="UTF-8"?>'
        xml += u'''<retenciones:Retenciones 
    xmlns:retenciones="http://www.sat.gob.mx/esquemas/retencionpago/1" 
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
    xmlns:enajenaciondeacciones="http://www.sat.gob.mx/esquemas/retencionpago/1/enajenaciondeacciones" 
    xsi:schemaLocation="http://www.sat.gob.mx/esquemas/retencionpago/1 
    http://www.sat.gob.mx/esquemas/retencionpago/1/retencionpagov1.xsd" 

    Version="1.0" CveRetenc="06" '''
        xml += u'''FolioInt="%s" FechaExp="%s-07:00" DescRetenc="0.00" Cert="%s" NumCert="%s">''' % (
            self.FolioInt, self.iso_date(self.FechaExp), self.Cert, self.NumCert
        )
        xml += u'<retenciones:Emisor RFCEmisor="%s" NomDenRazSocE="%s"/>' % (
            self.RFCEmisor, self.NomDenRazSocE,
        )
        xml += u'''<retenciones:Receptor Nacionalidad="Nacional">
    <retenciones:Nacional RFCRecep="%s" NomDenRazSocR="%s" CURPR="%s"/>
  </retenciones:Receptor>''' % (self.RFCRecep, self.NomDenRazSocR, self.CURPR)

        xml += u'<retenciones:Periodo MesIni="%s" MesFin="%s" Ejerc="%s"/>' % (
            self.MesIni, self.MesFin, self.Ejerc,
        )
  
        xml += u'<retenciones:Totales montoTotOperacion="%s" montoTotGrav="%s" montoTotExent="0" montoTotRet="%s">' % (
            self.montoTotOperacion, self.montoTotGrav, self.montoTotRet,
        )
        xml += u'''<retenciones:ImpRetenidos TipoPagoRet="Pago definitivo" montoRet="0.00" Impuesto="01"/>
  </retenciones:Totales>
  <retenciones:Complemento>
    <enajenaciondeacciones:EnajenaciondeAcciones Version="1.0" ContratoIntermediacion="NO EXISTE EN EL CATALOGO" Ganancia="0.00" Perdida="0.00"/>
  </retenciones:Complemento>
</retenciones:Retenciones>'''

        self.xml = xml

    def _post_timbrar_callback(self):
        """
        __DOCS__
        """
        if POST_TIMBRADO_CALLBACK:
            POST_TIMBRADO_CALLBACK(self)
    
    def _error_callback(self, error):
        """
        __DOCS__
        """
        if ERROR_CALLBACK:
            ERROR_CALLBACK(self, error)


    def generar_xml_retencion_pagosextranjeros(self):
        xml = u'<?xml version="1.0" encoding="utf-8"?>'
        xml += u'''<retenciones:Retenciones 
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
        xsi:schemaLocation="http://www.sat.gob.mx/esquemas/retencionpago/1 
        http://www.sat.gob.mx/esquemas/retencionpago/1/retencionpagov1.xsd 
        http://www.sat.gob.mx/esquemas/retencionpago/1/pagosaextranjeros 
        http://www.sat.gob.mx/esquemas/retencionpago/1/pagosaextranjeros/pagosaextranjeros.xsd" 
        Version="1.0" 
        FolioInt="%s" 
        NumCert="%s" 
        Cert="%s" 
        FechaExp="%s" 
        CveRetenc="18" 
        xmlns:retenciones="http://www.sat.gob.mx/esquemas/retencionpago/1">''' % (self.FolioInt, self.NumCert, self.Cert, )

        '''
  <retenciones:Emisor RFCEmisor="CTO140131BQ6" NomDenRazSocE="Comercializadora Toxic, S.A. de C.V." />
  <retenciones:Receptor Nacionalidad="Extranjero">
    <retenciones:Extranjero NomDenRazSocR="EPIC RIGTHS LLCC" />
  </retenciones:Receptor>
  <retenciones:Periodo MesIni="7" MesFin="7" Ejerc="2018" />
  <retenciones:Totales montoTotOperacion="70115" montoTotGrav="70115" montoTotExent="0" montoTotRet="7011">
    <retenciones:ImpRetenidos BaseRet="70115" Impuesto="01" montoRet="7011" TipoPagoRet="Pago definitivo" />
  </retenciones:Totales>
  <retenciones:Complemento>
    <pagosaextranjeros:Pagosaextranjeros EsBenefEfectDelCobro="NO" Version="1.0" xmlns:pagosaextranjeros="http://www.sat.gob.mx/esquemas/retencionpago/1/pagosaextranjeros">
      <pagosaextranjeros:NoBeneficiario DescripcionConcepto="Regalias" ConceptoPago="3" PaisDeResidParaEfecFisc="US" />
    </pagosaextranjeros:Pagosaextranjeros>
    <tfd:TimbreFiscalDigital xmlns:tfd="http://www.sat.gob.mx/TimbreFiscalDigital" xsi:schemaLocation="http://www.sat.gob.mx/TimbreFiscalDigital http://www.sat.gob.mx/TimbreFiscalDigital/TimbreFiscalDigital.xsd" version="1.0" UUID="48BD78FB-580D-4566-BDBF-F7A51D0B0778" FechaTimbrado="2018-07-19T09:22:27" noCertificadoSAT="00001000000306850881" selloCFD="R/dX5+oz+m8ZeSZ41t7BkMz2jiGaF7XGbcFcDEGBVJMz43m7dKGdqN6jNLCYsVshY5ROBpHMFj0PSkOvWdenp8vkg6C1WbQIQ4rzpvA9ruMzUnjT6vNGJFe5O5RdbDZHdEB/Wba1IBk/N7q63JB8aZ7dcaasSGjGL7RswsMxrl75sCGutrbjsbTeebmiPSSEMcLA6LhyNm/FH7FUfwPgsQPiLcaumNhvDJW7aH4VGiwrnng6LFQ/NC5qX8jVByqXpj0B6Pu60/VtZVVdVdsY7fGI3mO/7Tb5fzmJB4b8XNA69g6ntLP4my8VIPU8NiwmhmY7oFBrco+Thhs2bXpKZw==" selloSAT="PtH12pewPdy7xkLiDfsfGTYA92UN96jNd73bNdpBcxA4VyI41BdgOkQj/VlheYWO+ai9wRpfOaFnOr2/K5lD4CCPeHqMaWxsq/1CS+W0YwBVblocYNUqsLf5xqCvkN5LYZEKFWkQDJ2dsD7xqQllfiSOo/46xDx4yhzjFObfBA4=" />
  </retenciones:Complemento>
</retenciones:Retenciones>'''
        self.xml = xml


    def generar_xml_retencion_dividendos(self):
        xml = u'<?xml version="1.0" encoding="UTF-8"?>'
        xml += u'''<retenciones:Retenciones 
    xmlns:retenciones="http://www.sat.gob.mx/esquemas/retencionpago/1" 
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
    xmlns:enajenaciondeacciones="http://www.sat.gob.mx/esquemas/retencionpago/1/enajenaciondeacciones" 
    xsi:schemaLocation="http://www.sat.gob.mx/esquemas/retencionpago/1 
    http://www.sat.gob.mx/esquemas/retencionpago/1/retencionpagov1.xsd" 

    Version="1.0" CveRetenc="06" '''
        xml += u'''FolioInt="%s" FechaExp="%s-07:00" DescRetenc="0.00" Cert="%s" NumCert="%s">''' % (
            self.FolioInt, self.iso_date(self.FechaExp), self.Cert, self.NumCert
        )
        xml += u'<retenciones:Emisor RFCEmisor="%s" NomDenRazSocE="%s"/>' % (
            self.RFCEmisor, self.NomDenRazSocE,
        )
        xml += u'''<retenciones:Receptor Nacionalidad="Nacional">
    <retenciones:Nacional RFCRecep="%s" NomDenRazSocR="%s" CURPR="%s"/>
  </retenciones:Receptor>''' % (self.RFCRecep, self.NomDenRazSocR, self.CURPR)

        xml += u'<retenciones:Periodo MesIni="%s" MesFin="%s" Ejerc="%s"/>' % (
            self.MesIni, self.MesFin, self.Ejerc,
        )
  
        xml += u'<retenciones:Totales montoTotOperacion="%s" montoTotGrav="%s" montoTotExent="0" montoTotRet="%s">' % (
            self.montoTotOperacion, self.montoTotGrav, self.montoTotRet,
        )
        xml += u'''<retenciones:ImpRetenidos TipoPagoRet="Pago definitivo" montoRet="0.00" Impuesto="01"/>
  </retenciones:Totales>
  <retenciones:Complemento>
    <enajenaciondeacciones:EnajenaciondeAcciones Version="1.0" ContratoIntermediacion="NO EXISTE EN EL CATALOGO" Ganancia="0.00" Perdida="0.00"/>
  </retenciones:Complemento>
</retenciones:Retenciones>'''

        self.xml = xml

    def _post_timbrar_callback(self):
        from cfdi.callbacks import POST_TIMBRADO_CALLBACK
        """
        __DOCS__
        """
        if POST_TIMBRADO_CALLBACK:
            POST_TIMBRADO_CALLBACK(self)
    
    def _error_callback(self, error):
        from cfdi.callbacks import ERROR_CALLBACK
        """
        __DOCS__
        """
        if ERROR_CALLBACK:
            ERROR_CALLBACK(self, error)



class CfdiPago():

    def __init__(self, cfdi_instance, receptor, codigo_postal, sustitucion=None):
        self.Receptor = receptor
        self.sustituicion = None
        self.xml = ""
        self.codigo_postal = codigo_postal
        self.pagos = []
        self.NomBancoOrdExt = ""
        self.CtaOrdenante = ""
        self.RfcEmisorCtaOrd = ""
        self.RfcEmisorCtaBen = ""
        self.CtaBeneficiario = ""
        self.TipoCadPago = ""
        self.CertPago = ""
        self.CadPago = ""
        self.SelloPago = ""
        self.cfdi_instance = cfdi_instance
        self.timezone = settings.TIME_ZONE


    def generar_cfdi(self, configuracion, timbrado_prueba=None, pac=None):
        """
        Datos de acuerdo a la guía de llenado de complemento de pagos
        http://www.sat.gob.mx/informacion_fiscal/factura_electronica/Documents/Complementoscfdi/Guia_comple_pagos.pdf
        """
        
        from .functions import obtener_cfdi_base
        cfdi = obtener_cfdi_base(
            configuracion, 
            timbrado_prueba=timbrado_prueba, 
            pac=pac
        )
        
        cfdi.SubTotal = "0"
        cfdi.Total = "0"
        cfdi.Moneda = "XXX"
        cfdi.TipoDeComprobante = "P"
        cfdi.LugarExpedicion = self.codigo_postal
        cfdi.timezone = self.timezone

        cfdi.Receptor = self.Receptor
        cfdi.Receptor["UsoCFDI"] = "P01"
        cfdi.conceptos = [{
            "ClaveProdServ":"84111506",
            "Cantidad":"1",
            "ClaveUnidad":"ACT",
            "Descripcion":"Pago",
            "ValorUnitario":"0",
            "Importe":"0",
        }]
        cfdi.Fecha = self.Fecha
        cfdi.id = self.cfdi_instance.id
        cfdi.CfdiRelacionados = getattr(self, "CfdiRelacionados", {})
        
        
        if not self.pagos:

            recepcion_pago = {}
            recepcion_pago["FechaPago"] = self.FechaPago
            recepcion_pago["FormaDePagoP"] = self.FormaDePagoP
            recepcion_pago["MonedaP"] = self.MonedaP
            if self.MonedaP == "MXN":
                recepcion_pago["TipoCambioP"] = None
            else:
                recepcion_pago["TipoCambioP"] = self.TipoCambioP

            recepcion_pago["Monto"] = "%.2f" % self.Monto
            recepcion_pago["NumOperacion"] = self.NumOperacion
            recepcion_pago["NomBancoOrdExt"] = self.NomBancoOrdExt
            recepcion_pago["CtaOrdenante"] = self.CtaOrdenante
            recepcion_pago["RfcEmisorCtaOrd"] = self.RfcEmisorCtaOrd
            recepcion_pago["RfcEmisorCtaBen"] = self.RfcEmisorCtaBen
            recepcion_pago["CtaBeneficiario"] = self.CtaBeneficiario
            recepcion_pago["TipoCadPago"] = self.TipoCadPago
            recepcion_pago["CertPago"] = self.CertPago
            recepcion_pago["CadPago"] = self.CadPago
            recepcion_pago["SelloPago"] = self.SelloPago
            
            recepcion_pago["documentos"] = self.documentos
            self.pagos = [recepcion_pago, ]

        for rp in self.pagos:
            rp["DoctoRelacionado_set"] = []
            for documento in rp["documentos"]:
                if not documento['cfdi_uuid']:
                    self.cfdi_instance.cfdi_status = (
                        u"La factura %s no tiene UUID o no "
                        "está timbrada." % documento['folio_serie']
                    )
                    self.cfdi_instance.save()
                    return self.cfdi_instance

                saldo_actual = documento['saldo']
                saldo_anterior = saldo_actual + documento['importe_abono']
                tipo_cambio_dr = None
                if documento['moneda'] != rp["MonedaP"]:
                    tipo_cambio_dr = documento['tipo_cambio']

                if documento.get('metodo_pago'):
                    metodo_de_pago_dr = documento.get('metodo_pago')
                else:
                    metodo_de_pago_dr = "PPD"
                rp["DoctoRelacionado_set"].append({
                    "IdDocumento": documento['cfdi_uuid'],
                    "Serie":documento['serie'],
                    "Folio":documento['folio'],
                    "MonedaDR":documento['moneda'],
                    'TipoCambioDR':tipo_cambio_dr,
                    'MetodoDePagoDR':metodo_de_pago_dr,
                    'NumParcialidad':documento['numero_parcialidad'],
                    'ImpSaldoAnt':"%.2f" % saldo_anterior,
                    'ImpPagado': "%.2f" % documento['importe_abono'],
                    'ImpSaldoInsoluto':"%.2f" % saldo_actual,
                })

        cp = ComplementoPago()
        cp.pagos = self.pagos
        cfdi.complementos.append(cp)
        self.cfdi_instance.generar_xml(cfdi)
        self.xml = cfdi.xml
        #if not timbrar:
            #La opción de solo generar el XML fue enviada como parametro
        #    return False
        #Se Guardan los tiempos de timbrado
      
        return self.cfdi_instance

        
class XmlNewObject:
    def __init__(self, *args, **kwargs):
        self.texto = kwargs.get("texto", "").replace("\n", "")
        self.nombre_elemento = kwargs.get("nombre_elemento", "")
        self.lista_etiqueta = []

        if kwargs.get("prefix") is None:
            self.prefix = "cfdi"
        else:
            self.prefix = kwargs.get("prefix")
            
        self.num_elementos = 0


    @property
    def exists(self):
        return self.texto > ""


    def validar_cfdi(self):
        #cfdi_sello = xml_text.split(' Sello="', 1)[1].split('"')[0]
        #cfdi_certificado = xml_text.split(' Certificado="', 1)[1].split('"')[0]

        cfdi_sello = self.get("Sello")
        cfdi_certificado = self.get("Certificado")

        #tfd_text = extraer_tfd(xml_text)
        #tfd_sello = tfd_text.split(' SelloSAT="', 1)[1].split('"')[0]
        #nc = tfd_text.split(' NoCertificadoSAT="', 1)[1].split('"')[0]
        complemento = self.find("Complemento")
        tfd = complemento.find("TimbreFiscalDigital", "tfd")
        tfd_sello = tfd.get("SelloSAT")
        nc = tfd.get("NoCertificadoSAT")
        tfd_certificado = self.get_or_create_certificado(nc).pem


        # Cadena original comprobante
        cfdi_error = self.validar_sello(cfdi_sello, cfdi_certificado, XSLT_PATH_CFDI)
        #tfd_error = validar_sello(tfd_text, tfd_sello, tfd_certificado, XSLT_PATH_TFD)
        tfd_error = self.validar_sello(tfd_sello, tfd_certificado, XSLT_PATH_TFD)

        return [cfdi_error, tfd_error]

    def validar_sello(self, sello, certificado, xslt_path):
        from io import BytesIO
        from lxml import etree
        import subprocess

        """Regresa un string con el error (si hubo algún error)"""

        some_file_or_file_like_object = BytesIO(self.texto.encode("utf-8"))
        tree = etree.parse(some_file_or_file_like_object)
        #etree.tostring(tree)


        sello_path = "/tmp/sello"
        co_path = "/tmp/co"
        cert_path = "/tmp/cert"

        styledoc = etree.parse(xslt_path)
        transform = etree.XSLT(styledoc)
        cadena_original = str(transform(tree))

        #http://www.validacfd.com/phpbb3/viewtopic.php?t=10
        cer_pem_text = "-----BEGIN CERTIFICATE-----\n"
        for chunk in chunkstring(certificado, 64):
            cer_pem_text += chunk + "\n"
        cer_pem_text += "-----END CERTIFICATE-----\n"

        sello_l64 = ""
        for chunk in chunkstring(sello, 64):
            sello_l64 += chunk + "\n"


        with open(sello_path, "w") as tmpfile: 
            tmpfile.write(sello_l64)

        with open(co_path, "w") as tmpfile: 
            tmpfile.write(cadena_original)

        with open(cert_path, "w") as tmpfile: 
            tmpfile.write(cer_pem_text)
            
        cmd1 = f'openssl x509 -in {cert_path} -pubkey -noout -out /tmp/pubkey.txt'
        cmd2 = f'openssl enc -base64 -d -in {sello_path} -out /tmp/sellobin.txt'
        cmd3 = f'openssl dgst -sha256 -verify /tmp/pubkey.txt -signature /tmp/sellobin.txt {co_path}'

        try:
            subprocess.call(cmd1.split())
        except subprocess.CalledProcessError as e:
            return f"Hubo un error al correr el cmd1 {cmd1}"

        try:
            subprocess.call(cmd2.split())
        except subprocess.CalledProcessError as e:
            return f"Hubo un error al correr el cmd2 {cmd2}"

        try:
            resultado = subprocess.check_output(cmd3.split())
        except subprocess.CalledProcessError as e:
            return f"Hubo un error al correr el cmd3 {cmd3}"

        #No hubo errores
        return None

    def get_or_create_certificado(self, nc):
        from . import models
        try:
            return models.CertificadoSello.objects.get(numero=nc)
        except:
            cert = models.CertificadoSello(numero=nc)
            cert.set_certificado()
            return cert

    def set_lista_etiqueta(self, nombre_elemento, prefix=None):

        if prefix != "":
            prefix = prefix or self.prefix
            nombre_elemento = "%s:%s" % (prefix, nombre_elemento)


        tag = "<%s" % nombre_elemento

        self.lista_etiqueta = re.findall(
            r"(?:(?:<%s[^>]*/>)|<%s(?!\w+)[^>]*>.*?</%s\s?>)"
            % (nombre_elemento, nombre_elemento, nombre_elemento),
            self.texto,
            flags=re.IGNORECASE,
        )
        self.num_elementos = len(self.lista_etiqueta)

    def find(self, nombre_elemento, prefix=None):
        obj = getattr(self, nombre_elemento, None)
        if obj:
            return obj

        self.set_lista_etiqueta(nombre_elemento, prefix=prefix)
        tmp_dic = {}
        index = 0

        if self.num_elementos > 1:
            for i, e in enumerate(self.lista_etiqueta):
                texto = self.get_texto_elemento(i)
                le = re.findall(
                    r"</?\w+:\w+[^>]*(?<!/)>",
                    self.texto.split(texto)[0],
                    flags=re.IGNORECASE,
                )[-1]
                if le.startswith("</"):
                    index = i
                    break

        return self.get_elemento(nombre_elemento, index=index, prefix=prefix)

    def find_list(self, nombre_elemento, prefix=None):
        self.set_lista_etiqueta(nombre_elemento, prefix=prefix)
        lista = []
        ind = 0
        for le in self.lista_etiqueta:
            lista.append(
                self.get_elemento(nombre_elemento, index=ind, prefix=prefix)
            )
            ind += 1
        return lista

    def get_texto_elemento(self, index=0):
        return self.lista_etiqueta[index]

    def get_elemento(self, nombre, index=0, prefix=None):
        if prefix != "":
            prefix = (prefix or self.prefix)
        if self.num_elementos <= 0:
            return self.__class__(texto="", prefix=prefix)
        obj = self.__class__(prefix=prefix)
        obj.nombre_elemento = nombre
        obj.texto = self.get_texto_elemento(index)
        setattr(self, nombre, obj)
        return obj

    def get_num(self, nombre_attr, default=None):
        valor = self.get(nombre_attr, default=None)
        return to_decimal(valor)

    def get(self, nombre_attr, default=None):
        lista_valor = re.split(
            r"\s%s\s*=\s*[\'\"]" % nombre_attr, self.texto, flags=re.IGNORECASE
        )
        if len(lista_valor) <= 1:
            return default
        valor = re.split(r"[\'\"]", lista_valor[1])[0].strip()
        if not valor:
            return default
        return self.unescape(valor)

    def unescape(self, string):
        from cfdi.utils import unescape
        try:
            return unescape(string.decode("utf-8"))
        except:
            return unescape(string)


    def to_dict(self):

        try:
            return self._dic
        except:

            nombre_elemento = "%s:%s" % (self.prefix, self.nombre_elemento)


            etiquetas = re.findall(
                r"<%s[^>]*>" % nombre_elemento,                
                self.texto,
                flags=re.IGNORECASE,
            )
            if not etiquetas:
                self._dic = {}
                return {}

            etiqueta = etiquetas[0]

            nombre_variables = re.findall(
                r"\s(\w+)=",                
                etiqueta,
                flags=re.IGNORECASE,
            )
            self._dic = {

            }

            for n in nombre_variables:
                self._dic[n] = self.get(n)

        return self._dic