from django.template.loader import render_to_string
from cfdi.functions import to_decimal

class CfdiComplemento():
    xmlns_list = []
    schemaLocation = ""
    def get_xml_string(self):
        xml = render_to_string(
            self.template, 
            { 'complemento': self, }
        )
        
        return xml

class ComplementoINE(CfdiComplemento):
    tipo_proceso = ""
    tipo_comite = ""
    clave_entidad = ""
    id_contabilidad = ""
    ambito = ""
    template = 'cfdi/complementos/ine.xml'

    xmlns_list = [
        'xmlns:ine="http://www.sat.gob.mx/ine"',
    ]
    schemaLocation = 'http://www.sat.gob.mx/ine http://www.sat.gob.mx/ine http://www.sat.gob.mx/sitio_internet/cfd/ine/ine11.xsd'

    def get_ambito_entidad(self):
        if self.ambito:
            return self.ambito

        from cfdi.classes import escape
        if "estatal" in escape(self.tipo_comite).lower():
            return "Federal"
        else:
            return "Local"

    
class ComplementoIEDU(CfdiComplemento):
    nombreAlumno = ""
    CURP = ""
    nivelEducativo = ""
    autRVOE = ""
    rfcPago = ""
    template = 'cfdi/complementos/iedu.xml'

class ComplementoDetallista(CfdiComplemento):
    documentStatus = ""
    entityType = ""
    code = ""
    detallista = ""
    cantidad_letra = ""
    referenceIdentification = ""
    fecha_oc = ""
    deliveryNote = ""
    fecha_referencia = ""
    buyerGLN = ""
    personDepartament = ""
    sellerGLN = ""
    template = 'cfdi/complementos/detallista.xml'

    xmlns_list = [
        'xmlns:detallista="http://www.sat.gob.mx/detallista"',
    ]
    schemaLocation = "http://www.sat.gob.mx/detallista http://www.sat.gob.mx/sitio_internet/cfd/detallista/detallista.xsd"


class ComplementoImpuestosLocales(CfdiComplemento):
    retenciones_locales = []
    traslados_locales = []
    template = 'cfdi/complementos/impuestos_locales.xml'

    xmlns_list = [
        'xmlns:implocal="http://www.sat.gob.mx/implocal"',
    ]
    schemaLocation = "http://www.sat.gob.mx/implocal http://www.sat.gob.mx/sitio_internet/cfd/implocal/implocal.xsd"

    @property
    def total_retenciones_locales(self):
        total = 0
        for rl in self.retenciones_locales:
            total += to_decimal(rl["monto"])
        return total

    @property
    def total_traslados_locales(self):
        total = 0
        for rl in self.traslados_locales:
            total += to_decimal(rl["monto"])
        return total
 
class ComplementoComercioExterior(CfdiComplemento):

    CertificadoOrigen = ""
    ClaveDePedimento = ""
    NumCertificadoOrigen = ""
    NumeroExportadorConfiable = ""
    Incoterm = ""
    Observaciones = ""
    Subdivision = ""
    TipoCambioUSD = ""
    TipoOperacion = ""
    TotalUSD = ""
    Emisor = {}
    Receptor = {}
    template = 'cfdi/complementos/comercio_exterior.xml'

    xmlns_list = [
        'xmlns:cce11="http://www.sat.gob.mx/ComercioExterior11"',
    ]

class ComplementoContruccionLicencia(CfdiComplemento):
    licencia = ""
    calle = ""
    no_exterior = ""
    no_interior = ""
    colonia = ""
    localidad = ""
    referencia = ""
    municipio = ""
    estado = ""
    codigo_postal = ""
    template = 'cfdi/complementos/construccion_licencia.xml'

    xmlns_list = [
        'xmlns:servicioparcial="http://www.sat.gob.mx/servicioparcialconstruccion"',
    ]
    schemaLocation = "http://www.sat.gob.mx/servicioparcialconstruccion http://www.sat.gob.mx/sitio_internet/cfd/servicioparcialconstruccion/servicioparcialconstruccion.xsd"

class ComplementoLeyendasFiscales(CfdiComplemento):
    leyendasFiscales = []
    template = 'cfdi/complementos/leyendas_fiscales.xml'
    
    xmlns_list = [
        'xmlns:leyendasFisc="http://www.sat.gob.mx/leyendasFiscales"',
    ]
    schemaLocation = "http://www.sat.gob.mx/leyendasFiscales http://www.sat.gob.mx/sitio_internet/cfd/leyendasFiscales/leyendasFisc.xsd"


class ComplementoNomina(CfdiComplemento):
    TipoNomina = ""
    TipoNomina = ""
    FechaPago = ""
    FechaInicialPago = ""
    FechaFinalPago = ""
    NumDiasPagados = ""
    NumDiasPagados = ""
    Emisor = {}
    Receptor = {}
    Percepciones = {}
    Deducciones = {}
    OtrosPagos = {}
    Incapacidades = {}
    TotalPercepciones = ""
    TotalDeducciones = ""
    TotalOtrosPagos = ""
    
    template = 'cfdi/complementos/nomina.xml'
    xmlns_list = [
        'xmlns:nomina12="http://www.sat.gob.mx/nomina12"',
        'xmlns:catNomina="http://www.sat.gob.mx/sitio_internet/cfd/catalogos/Nomina"',
        'xmlns:tdCFDI="http://www.sat.gob.mx/sitio_internet/cfd/tipoDatos/tdCFDI"',
        'xmlns:catCFDI="http://www.sat.gob.mx/sitio_internet/cfd/catalogos"',
    ]
    schemaLocation = "http://www.sat.gob.mx/nomina12 http://www.sat.gob.mx/sitio_internet/cfd/nomina/nomina12.xsd"


class ComplementoPago(CfdiComplemento):
    pagos = []
    template = 'cfdi/complementos/pago.xml'
    xmlns_list = [
        'xmlns:pago10="http://www.sat.gob.mx/Pagos"',
    ]
    schemaLocation = "http://www.sat.gob.mx/Pagos http://www.sat.gob.mx/sitio_internet/cfd/Pagos/Pagos10.xsd"


class ComplementoCartaPorte(CfdiComplemento):
    pagos = []
    template = 'cfdi/complementos/carta_porte.xml'
    xmlns_list = [
        #'xmlns:cartaporte="http://www.sat.gob.mx/CartaPorte"',
        'xmlns:cartaporte20="http://www.sat.gob.mx/CartaPorte20"',

    ]
    schemaLocation = "http://www.sat.gob.mx/cfd/3 http://www.sat.gob.mx/sitio_internet/cfd/3/cfdv33.xsd http://www.sat.gob.mx/CartaPorte20 http://www.sat.gob.mx/sitio_internet/cfd/CartaPorte/CartaPorte20.xsd"