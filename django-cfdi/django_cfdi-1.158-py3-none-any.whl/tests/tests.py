from cfdi.utils import get_xml_object
from cfdi.models import DescargaCfdi
from cfdi import CFDI
from django.test import TestCase
import os
import datetime
from cfdi.functions import obtener_cfdi_base
from django.utils import timezone
from django.conf import settings

def get_factura_str():
    tests_dir = os.path.dirname(__file__)
    with open(os.path.join(tests_dir, "data/factura.xml")) as xml_file:
        return xml_file.read()

class UtilTest(TestCase):
    def setUp(self):
        pass

    def test_load_func(self):
        from cfdi.callbacks import ERROR_CALLBACK
        assert callable(ERROR_CALLBACK) == True

    def test_get_xml_object(self):
        xml_factura = get_factura_str()
        xml_obj = get_xml_object(xml_factura)
        assert xml_obj.emisor.rfc == "AAA010101AAA"


class CFDITest(TestCase):

    def setUp(self):
        self.xml_factura = get_factura_str()

    def test_generar_sello(self):
        # xml_obj = get_xml_object(self.xml_factura)
        # cfdi = CFDI()
        # cfdi.generar_sello()
        pass

    def test_solicitar_descarga_cfdi(self):
        
        from cfdi.models import DescargaCfdi
        fecha_final = datetime.date.today()
        fecha_inicio = fecha_final - datetime.timedelta(days=5)

        rfc = "ADE180219RE0"
        '''
        dc = DescargaCfdi(
            rfc_solicitante=rfc, 
            fecha_inicio=fecha_inicio, 
            fecha_final=fecha_final,
            pfx_fiel=settings.TES_PFX_FIEL, 
            password_fiel="XXXXX", 
            rfc_receptor=rfc,
        )

        
        dc.solicitar_descarga()
        dc.solicitar_status_descarga()
        '''
        dc = DescargaCfdi.objects.order_by("creado").last()
        
        
    def test_generar_cfdi(self):
        
        from cfdi.complementos import ComplementoINE, ComplementoImpuestosLocales
        configuracion = {
            "no_certificado":settings.TEST_NO_CERTIFICADO,
            "certificado":settings.TEST_CERTIFICADO,
            "rfc":settings.TEST_RFC,
            "razon_social":settings.TEST_RAZON_SOCIAL,
            "regimen_fiscal":settings.TEST_REGIMEN_FISCAL,
            "pem":settings.TEST_PEM,
        }

        cfdi = obtener_cfdi_base(
            configuracion, 
            timbrado_prueba=True, 
            pac="dfacture"
        )
        cfdi.Fecha = datetime.datetime.now()
        cfdi.timezone = "America/Hermosillo"
        cfdi.FormaDePago = "01"
        cfdi.FormaPago = "01"
        cfdi.Moneda = "MXN"
        cfdi.password = "12345678a"
        cfdi.TipoDeComprobante = "I"
        cfdi.MetodoPago = "PUE"
        cfdi.Total = "106.00"
        cfdi.LugarExpedicion = "83175"
        #Receptor
        cfdi.Receptor = {}
        cfdi.Receptor["Rfc"] = "XAXX010101000"
        cfdi.Receptor["Nombre"] = "PG"
        cfdi.Receptor["UsoCFDI"] = "P01"
        cfdi.traslados = []
        subtotal = 100
        cfdi.SubTotal = "%.2f" % subtotal

        iva = 16
        iva_factor = 0.16
        if iva:
            cfdi.traslados.append({
                "Impuesto":"002",
                "Importe":"%.2f" % (iva),
                "TasaOCuota":"%.6f" % iva_factor,
                "TipoFactor":"Tasa",
            })

        concepto = {
            "Cantidad":"1",
            "ClaveUnidad":"ACT",
            "ClaveProdServ":"84111506",
            "Unidad":"Actividad",
            "Descripcion":"TEST DJANGO CFDI ",
            "ValorUnitario":"%.6f" % subtotal,
            "Importe": "%.6f" % subtotal,
            "traslados":[],
            "retenciones":[],

        }
        if iva:
            concepto["traslados"].append({
                "Impuesto":"002",
                "Importe":"%.2f" % (iva),
                "TasaOCuota": "%.6f" % iva_factor,
                "Base":"%.6f" % subtotal,
                "TipoFactor":"Tasa",
            })

        cfdi.conceptos = [concepto, ]
        cfdi.TotalImpuestosTrasladados = "%.2f" % iva

        cine = ComplementoINE()
        cine.tipo_proceso = "Ordinario"
        cine.tipo_comite = "Ejecutivo Nacional"
        cine.ambito = "Local"
        cine.id_contabilidad = 21
        cfdi.complementos.append(cine)

        retenciones_locales = []
        dic_imp_loc = {
            "nombre":"asdasd",
            "tasa":10,
            "monto":10,
        }
        
        retenciones_locales.append(dic_imp_loc)

        if retenciones_locales :
            cil = ComplementoImpuestosLocales()
            cil.retenciones_locales = retenciones_locales
            cfdi.complementos.append(cil)


        cfdi.generar_xml_v33()
        #error_sello = cfdi.generar_sello()
        #cfdi.sellar_xml()
        #timbrado = cfdi.timbrar_xml()
        #if not timbrado:
        #    print(cfdi.cfdi_status)

