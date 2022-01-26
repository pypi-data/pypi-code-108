import sys
import codecs
import re
import datetime, math
from cfdi import XmlNewObject, Object
from .functions import to_decimal, to_int, to_datetime, to_precision_decimales
from .constants import CLAVES_COMBUSTIBLE, METODOS_PAGO

def es_producto_combustible(claveprodserv):
    return claveprodserv in CLAVES_COMBUSTIBLE

def get_fecha_cfdi(fecha):
    if fecha:
        fecha_str = fecha.replace("Z", "").split('.')[0][0:19]
        return to_datetime(
            datetime.datetime.strptime(fecha_str, "%Y-%m-%dT%H:%M:%S")
        )

def es_timbrado_prueba(cfdi_no_certificado_sat):
    """Los certificados del SAT que NO empiezan con 1 se consideran de prueba"""

    if not cfdi_no_certificado_sat:
        return False

    if cfdi_no_certificado_sat == "00000000000000000000":
        return True
        
    return not (
        cfdi_no_certificado_sat.startswith("0") or
        cfdi_no_certificado_sat.startswith("1") 
    )

def get_xml_value(xml_content, field):
    try:
        return (
            xml_content.split('%s="' % field)[1].split('"')[0].upper().strip()
        )
    except:
        return ""
        
def unescape(string):
    return (
        str(string)
        .replace("&apos;", "'")
        .replace("&quot;", '"')
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&amp;", "&")
    )

def get_field(field, value):
    """
    Agrega el campo al XML según el valor de dicho
    campo en la clase CFDI.
    """
    if value == "" or value is None:
        return ""

    return '%s="%s" ' % (field, escape(value))
    
def remover_addenda(xml):
    if "<cfdi:Addenda" in xml:
        if '</cfdi:Addenda>' in xml:
            return xml.split("<cfdi:Addenda")[0] + xml.split("</cfdi:Addenda>")[1]
        else:
            return re.sub(r'<cfdi:Addenda.+?/>', '', xml)

    return xml

def get_addenda(tipo_addenda, diccionario):
    import importlib
    addenda = importlib.import_module("%s.addendas.%s.addenda" % (
        __package__, tipo_addenda
    ))
    return addenda.generar_addenda(diccionario)
    

def decode_text(txt, es_cfdi=True):
    """
    Recibe un string lo intenta codificar en utf8 y otros posibles
    encodings, y regresa el texto como unicode.
    """

    if es_cfdi:
        """ 
            SI EL TEXTO ES UN CFDI XML Y EMPIEZA CON UN '?' 
            SE QUITA EL SIGNO PARA QUE SEA UN XML VÁLIDO
        """

        if isinstance(txt, bytes):
            signo = b"?"
        else:
            signo = "?"

        if txt.startswith(signo):
            txt = txt[1:]

    if not isinstance(txt, bytes):
        return txt

    e = None
    for encoding in ["utf-8", "cp1252", ]:
        try:
            return txt.decode(encoding)
        except UnicodeDecodeError as exception:
            e = exception
            continue
        else:
            break
    else:
        raise e


def get_xml_object(xml_text):

    """
    El tipo de cambio de la moneda USD lo toma de la bsae de datos central,
    de acuerdo al tipo de cambio del DOF.
    """
    TIPOS_REGIMEN = (
        # (1, 'Asimilados a salarios (DESCONTINUADO)'),
        (2, "Sueldos y salarios"),
        (3, "Jubilados"),
        (4, "Pensionados"),
        (
            5,
            (
                "Asimilados a salarios, Miembros de las Sociedades "
                "Cooperativas de Producción."
            ),
        ),
        (
            6,
            (
                "Asimilados a salarios, Integrantes de Sociedades "
                "y Asociaciones Civiles"
            ),
        ),
        (
            7,
            (
                "Asimilados a salarios, Miembros de consejos directivos, "
                "de vigilancia, consultivos, honorarios a administradores, "
                "comisarios y gerentes generales."
            ),
        ),
        (8, "Asimilados a salarios, Actividad empresarial (comisionistas)"),
        (9, "Asimilados a salarios, Honorarios asimilados a salarios"),
        (10, "Asimilados a salarios, Ingresos acciones o títulos valor"),
    )

    RIESGO_PUESTOS = (
        (0, "------"),
        (1, "Clase I"),
        (2, "Clase II"),
        (3, "Clase III"),
        (4, "Clase IV"),
        (5, "Clase V"),
        (99, "No aplica")
    )

    xml_text = xml_text.strip()

    if not xml_text:
        return None

    xml_text = decode_text(xml_text)
    cond1 = xml_text.encode("utf-8").startswith(codecs.BOM_UTF8 + b"<")
    cond2 = xml_text.encode("utf-8").startswith(b"<")

    if not cond1 and not cond2:
        return None

    xml_text = remover_addenda(xml_text)
    soup = XmlNewObject(texto=xml_text)
    xml = Object()
    xml.validar_cfdi = soup.validar_cfdi
    xml.complemento = None
    version = 3
    reg_entero = re.compile(r"[^\d]+")
    o = soup.find("comprobante")
    xml.es_v33 = False
    xml.es_v4 = False

    if o.get("version", "") == "3.3":   
        xml.es_v33 = True
    elif o.get("version", "") == "4.0":
        xml.es_v4 = True

    if o.get("version", "") == "3.3" or o.get("version", "") == "4.0":   

        xml.formadepago = o.get("metodopago", "")
        xml.metododepago = o.get("formapago", "")
    else:
        xml.formadepago = o.get("formadepago", "")
        xml.metododepago = o.get("metododepago", "")
        if o.find("regimenfiscal"):
            xml.regimen = o.find("regimenfiscal").get("regimen")

    xml.forma_pago_at = 1 if xml.formadepago == "PPD" else 0
    xml.version = version
    xml.total = o.get("total", "")
    xml.sello = o.get("sello", "")
    xml.noaprobacion = o.get("noaprobacion", "")
    xml.anoaprobacion = o.get("anoaprobacion", "")
    xml.nocertificado = o.get("nocertificado", "")
    xml.folio = reg_entero.sub("", o.get("folio", "")[-9:])
    xml.serie = o.get("serie", "")
    xml.fecha_str = o.get("fecha", "")
    xml.fecha_dt = get_fecha_cfdi(xml.fecha_str)

    # __PENDIENTE__ eliminar para evitar confusiones
    # con la fecha en formato texto o datetime
    xml.fecha = xml.fecha_str

    xml.subtotal = o.get("subtotal", "")
    xml.descuento = o.get("descuento", "")

    xml.numctapago = o.get("numctapago", "")
    xml.condicionesdepago = o.get("condicionesdepago", "")
    xml.moneda = o.get("moneda", "")
    xml.tipocambio = o.get("tipocambio", "1")

    xml.tipodecomprobante = o.get("tipodecomprobante", "")
    xml.lugarexpedicion = o.get("lugarexpedicion", "")

    ######## EMISOR ########
    xml.emisor = Object()
    xml.emisor.rfc = o.find("emisor").get("rfc", "").strip()
    xml.emisor.nombre = unescape(o.find("emisor").get("nombre"))
    if o.get("version", "") == "3.3":
        xml.regimen = o.find("emisor").get("regimenfiscal", "")

    xml.emisor.domiciliofiscal = Object()
    xml.emisor.domiciliofiscal.calle = (
        o.find("emisor").find("domiciliofiscal").get("calle", "")[:500]
    )
    xml.emisor.domiciliofiscal.noexterior = (
        o.find("emisor").find("domiciliofiscal").get("noexterior", "")[:100]
    )
    xml.emisor.domiciliofiscal.nointerior = (
        o.find("emisor").find("domiciliofiscal").get("nointerior", "")[:100]
    )
    xml.emisor.domiciliofiscal.colonia = (
        o.find("emisor").find("domiciliofiscal").get("colonia", "")[:100]
    )
    xml.emisor.domiciliofiscal.municipio = (
        o.find("emisor").find("domiciliofiscal").get("municipio", "")[:255]
    )
    xml.emisor.domiciliofiscal.localidad = (
        o.find("emisor").find("domiciliofiscal").get("localidad", "")[:255]
    )
    xml.emisor.domiciliofiscal.estado = (
        o.find("emisor").find("domiciliofiscal").get("estado", "")[:255]
    )
    xml.emisor.domiciliofiscal.pais = (
        o.find("emisor").find("domiciliofiscal").get("pais", "")[:100]
    )
    xml.emisor.domiciliofiscal.codigopostal = (
        o.find("emisor").find("domiciliofiscal").get("codigopostal", "")[:6]
    )
    ########

    ######## RECEPTOR ########
    xml.receptor = Object()
    xml.receptor.rfc = o.find("receptor").get("rfc", "").strip()
    xml.receptor.nombre = unescape(o.find("receptor").get("nombre"))
    xml.receptor.regimen = o.find("receptor").get("regimen") or o.find(
        "receptor"
    ).get("regimenfiscal")
    xml.receptor.registro_patronal = o.find("receptor").get("registropatronal")
    xml.receptor.usocfdi = o.find("receptor").get("usocfdi")

    xml.receptor.domicilio = Object()
    xml.receptor.domicilio.calle = (
        o.find("receptor").find("domicilio").get("calle", "")
    )
    xml.receptor.domicilio.noexterior = (
        o.find("receptor").find("domicilio").get("noexterior", "")
    )
    xml.receptor.domicilio.nointerior = (
        o.find("receptor").find("domicilio").get("nointerior", "")
    )
    xml.receptor.domicilio.colonia = (
        o.find("receptor").find("domicilio").get("colonia", "")
    )
    xml.receptor.domicilio.municipio = (
        o.find("receptor").find("domicilio").get("municipio", "")
    )
    xml.receptor.domicilio.localidad = (
        o.find("receptor").find("domicilio").get("localidad", "")
    )
    xml.receptor.domicilio.estado = (
        o.find("receptor").find("domicilio").get("estado", "")
    )
    xml.receptor.domicilio.pais = (
        o.find("receptor").find("domicilio").get("pais", "")
    )
    xml.receptor.domicilio.codigopostal = (
        o.find("receptor").find("domicilio").get("codigopostal", "")[0:5]
    )
    direccion_completa = xml.receptor.domicilio.calle

    if xml.receptor.domicilio.noexterior:
        direccion_completa = "%s #%s" % (
            direccion_completa,
            xml.receptor.domicilio.noexterior,
        )

    if xml.receptor.domicilio.colonia:
        direccion_completa = "%s Col: %s" % (
            direccion_completa,
            xml.receptor.domicilio.colonia,
        )

    if xml.receptor.domicilio.codigopostal:
        direccion_completa = "%s CP: %s" % (
            direccion_completa,
            xml.receptor.domicilio.codigopostal,
        )

    direccion_completa = "%s %s %s" % (
        direccion_completa,
        xml.receptor.domicilio.municipio,
        xml.receptor.domicilio.estado,
    )

    xml.receptor.domicilio.completa = direccion_completa
    ########
    xml.iva = 0
    xml.importe_tasa_cero = 0
    xml.importe_tasa_general = 0
    xml.importe_tasa_frontera = 0
    xml.importe_exento = 0

    xml.descuento_tasa_cero = 0
    xml.descuento_tasa_general = 0
    xml.descuento_tasa_frontera = 0
    xml.descuento_exento = 0

    xml.total_tasa_cero = 0
    xml.total_tasa_general = 0
    xml.total_tasa_frontera = 0
    xml.total_exento = 0
    xml.tasa_cero = False
    xml.ieps = 0
    xml.retencion_isr = 0
    xml.retencion_iva = 0
    total_traslados = 0
    total_retenciones = 0

    conceptos = o.find("conceptos").find_list("concepto")
    xml.conceptos = []
    xml.documentos_relacionados = []
    xml.tipo_relacion = o.find("CfdiRelacionados").get("tiporelacion")

    for dr in o.find("CfdiRelacionados").find_list("cfdirelacionado"):
        xml.documentos_relacionados.append({
            "uuid":dr.get("uuid")
        })

    importe_tasa_frontera = 0
    total_impuestos_tasa_fronetra = 0
    importe_tasa_general = 0
    total_impuestos_tasa_general = 0

    xml.importe_iva_frontera = 0
    xml.importe_iva_tasa_general = 0
    xml.total_no_objeto_iva = 0

    for c in conceptos:
        tasa_iva_concepto = ""
        tasa_ieps_concepto = ""
        total_iva = 0
        total_ieps = 0
        base_iva = ""
        base_ieps = ""
        tipo_factor_ieps = "tasa"
        cuota_ieps = None
        descuento = to_decimal(c.get("descuento"))
        total_traslado_concepto = 0
        importe_tasa_frontera_concepto = 0
        importe_tasa_general_concepto = 0
        cantidad = to_decimal(c.get("cantidad"))
        es_combustible = False
        es_tasa_cero = False

        retencion_iva_concepto = 0
        retencion_isr_concepto = 0

        if xml.es_v33 or xml.es_v4:
            importe_concepto = to_decimal(c.get("importe"))
            claveprodserv = c.get("claveprodserv", "")
            total_base_iva = 0
            for tras in c.find_list("traslado"):
                if tras.get("impuesto").upper() == "002":
                    total_iva += to_decimal(tras.get("importe"))

                    if tras.get("tipofactor", "").lower() != "exento":
                        total_base_iva += to_decimal(tras.get("base"))
                elif tras.get("impuesto").upper() == "003":
                    total_ieps += to_decimal(tras.get("importe"))

            total_impuestos = (total_ieps + total_iva)
            es_combustible = es_producto_combustible(
                claveprodserv
            )
            ieps_no_objeto_iva = False
            if es_combustible and total_ieps:
                #ieps_no_objeto_iva = True
                #xml.total_no_objeto_iva += total_ieps
                es_combustible = False

            for tras in c.find_list("traslado"):
                tasa_iva = ""
                tasa_ieps = ""
                cuota_ieps = None
                importe_traspaso = to_decimal(tras.get("importe"))
                base_traslado = to_decimal(tras.get("base"))
                if total_impuestos:
                    factor_traslado = (
                        importe_traspaso /
                        total_impuestos
                    )
                else:
                    factor_traslado = 1

                if tras.get("tipofactor", "").lower() == "exento":
                    tasa_iva = "exento"
                    tasa_iva_concepto = tasa_iva
                    xml.importe_exento += base_traslado
                    xml.descuento_exento += (descuento * factor_traslado) 

                elif to_decimal(tras.get("base")):
                    if tras.get("impuesto").upper() == "002":
                        tasa_iva = tras.get("tasaocuota")
                        tasa_iva_concepto = tasa_iva
                        if tras.get("tipofactor", "").lower() == "exento":
                            tasa_iva = "exento"

                    elif tras.get("impuesto").upper() == "003":
                        tasa_ieps = tras.get("tasaocuota")
                        tasa_ieps_concepto = tasa_ieps
                        tipo_factor_ieps = tras.get("tipofactor").lower()
                        if tipo_factor_ieps == "cuota":
                            cuota_ieps = tasa_ieps

                    total_traslado_concepto += importe_traspaso

                    if tras.get("impuesto").upper() == "002":
                        factor_base_iva = (
                            base_traslado/
                            total_base_iva
                        )
                        es_frontera = to_decimal(tasa_iva) == to_decimal("0.08")
                        if es_frontera:
                            xml.importe_iva_frontera += importe_traspaso
                        else:
                            xml.importe_iva_tasa_general += importe_traspaso

                        es_tasa_cero = (
                            tasa_iva
                            and not to_decimal(tasa_iva)
                            and tasa_iva != "exento"
                        )

                        if tasa_iva:
                            # SI ES COMBUSTIBLE, TOMA TODO EL IMPORTE DEL
                            # CONCEPTO PARA EL TOTAL DE TASA GENERAL/FRONTERA
                            if es_combustible:
                                importe_tasa = base_traslado
                                xml.total_no_objeto_iva += (
                                    (importe_concepto - descuento) -
                                    to_precision_decimales(base_traslado, 6)
                                )
                            else:
                                total_base_iva -= total_ieps
                                importe_tasa = total_base_iva * factor_base_iva

                            if to_decimal(tasa_iva):
                                if es_frontera:
                                    importe_tasa_frontera += importe_tasa
                                    total_impuestos_tasa_fronetra += (
                                        importe_traspaso
                                    )                   
                                    xml.descuento_tasa_frontera += descuento * factor_traslado 
                                    if not es_combustible:
                                        xml.importe_tasa_frontera += importe_tasa
                                else:

                                    importe_tasa_general += importe_tasa
                                    total_impuestos_tasa_general += importe_traspaso 
                                    xml.descuento_tasa_general += descuento * factor_traslado                   
                                    if not es_combustible:
                                        xml.importe_tasa_general += importe_tasa

                            elif es_tasa_cero:                
                                xml.importe_tasa_cero += importe_tasa
                                xml.total_tasa_cero += (
                                    importe_tasa + importe_traspaso
                                )
                                xml.descuento_tasa_cero += descuento * factor_traslado

                    if es_combustible:
                        cuota_ieps = (
                            importe_concepto - descuento - base_traslado
                        ) / cantidad


            for t in c.find_list("retencion"):
                if t.get("impuesto").upper() == "002":
                    xml.retencion_iva += to_decimal(t.get("importe"))
                    retencion_iva_concepto += to_decimal(t.get("importe"))
                elif t.get("impuesto").upper() == "001":
                    xml.retencion_isr += to_decimal(t.get("importe"))
                    retencion_isr_concepto += to_decimal(t.get("importe"))

            xml.iva += total_iva
            xml.ieps += total_ieps

            if total_iva:
                if not ieps_no_objeto_iva:
                    total_impuestos_tasa_general += total_ieps
            elif es_tasa_cero:
                xml.total_tasa_cero += total_ieps

        else:
            base_iva = to_decimal(c.get("importe"))
            tasa_iva_concepto = to_decimal("0.16")


        xml.conceptos.append(
            {
                "cantidad": to_decimal(cantidad),
                "claveprodserv": c.get("claveprodserv"),
                "claveunidad": c.get("claveunidad"),
                "descripcion": unescape(c.get("descripcion")),
                "importe": c.get("importe"),
                "noidentificacion": unescape(
                    c.get("noidentificacion", "").strip()
                )[:100],
                "unidad": (
                    c.get("unidad") or c.get("claveunidad")
                ),  # version 3.3,
                "valorunitario": c.get("valorunitario"),
                "tasa_iva": tasa_iva_concepto,
                "total_iva": total_iva,
                "tasa_ieps": tasa_ieps_concepto,
                "total_ieps": total_ieps,
                "base_iva": base_iva,
                "base_ieps": base_ieps,
                "tipo_factor_ieps": tipo_factor_ieps,
                "descuento": descuento,
                "importe_con_descuento": (
                    to_decimal(c.get("importe")) - to_decimal(descuento)
                ),
                "cuota_ieps": to_precision_decimales(cuota_ieps, 4),
                "es_combustible": es_combustible, 
                "retencion_iva":retencion_iva_concepto,
                "retencion_isr":retencion_isr_concepto,               
            }
        )


    xml.retencion_iva = to_precision_decimales(xml.retencion_iva, 2)
    xml.retencion_isr = to_precision_decimales(xml.retencion_isr, 2)
    xml.total_tasa_frontera += to_precision_decimales(
        importe_tasa_frontera, 2
    ) + to_precision_decimales(total_impuestos_tasa_fronetra, 2)

    xml.total_tasa_general += to_precision_decimales(
        importe_tasa_general, 2
    ) + to_precision_decimales(total_impuestos_tasa_general, 2)

    if not xml.es_v33 and not xml.es_v4:
        for t in o.find("impuestos").find("traslados").find_list("traslado"):
            importe_traslado = to_decimal(t.get("importe"))
            if t.get("impuesto") == "IVA":
                xml.iva += importe_traslado
                xml.importe_iva_tasa_general += importe_traslado 
            elif t.get("impuesto") == "IEPS":
                xml.ieps += importe_traslado

    xml.es_comprobante_pago = False
    xml.complemento_pago = o.find("pagos", "pago10")

    if xml.complemento_pago.exists:
        xml.es_comprobante_pago = True
        xml.complemento_pago.pagos = []

        xml.pagos = []
        for pago in xml.complemento_pago.find_list("pago"):        

            pago_dic = {
                "abono_fecha_pago":pago.get("fechapago"),
                "abono_forma_pago":pago.get("formadepagop"),
                "abono_forma_pago_text":dict(METODOS_PAGO).get(pago.get("formadepagop"), ""),
                "abono_moneda":pago.get("monedap"),
                "abono_monto":pago.get("monto"),
                "abono_num_operacion":pago.get("numoperacion"),
                "banco_ordenante":pago.get("nombancoordext"),
                "cuenta_ordenante":pago.get("ctaordenante"),
                "rfc_cuenta_ordenante":pago.get("rfcemisorctaord"),
                "rfc_cuenta_beneficiario":pago.get("rfcemisorctaben"),
                "cuenta_beneficiario":pago.get("ctabeneficiario"),
                "documentos_relacionados":[],
            }


            for p in pago.find_list("doctorelacionado", "pago10"):
                doc_relacionado_dic = {
                    "imp_pagado": p.get("imppagado"),
                    "imp_saldo_ant": p.get("impsaldoant"),
                    "imp_saldo_insoluto": p.get("impsaldoinsoluto"),
                    "metodo_pago": p.get("metododepagodr"),
                    "moneda": p.get("monedadr"),
                    "num_parcialidad": p.get("numparcialidad"),
                    "folio": p.get("folio"),
                    "serie": p.get("serie"),
                    "iddocumento": p.get("iddocumento"),
                }
                pago_dic["documentos_relacionados"].append(doc_relacionado_dic)
                xml.pagos.append(doc_relacionado_dic)

            xml.complemento_pago.pagos.append(pago_dic)


    xml.impuestos = Object()
    xml.impuestos.totalimpuestostrasladados = o.find("impuestos").get_num(
        "totalimpuestostrasladados"
    )

    xml.impuestos.totalImpuestosRetenidos = o.find("impuestos").get_num(
        "totalimpuestosretenidos"
    )
    xml.impuestos_locales_traslados = []
    xml.impuestos_locales_retenciones = []
    xml.total_impestos_locales_traslados = 0
    xml.total_impestos_locales_retenciones = 0

    retenciones_locales = o.find("impuestoslocales","implocal").find_list("RetencionesLocales")
    if retenciones_locales:
        for il in retenciones_locales:
            xml.impuestos_locales_retenciones.append(
                {
                    "nombre": il.get("implocretenido"),
                    "importe": il.get("importe"),
                    "tasa": il.get("tasaderetencion"),
                }
            )
            xml.total_impestos_locales_retenciones += to_decimal(il.get("importe"))

    traslados_locales = o.find("impuestoslocales","implocal").find_list("TrasladosLocales")
    if traslados_locales:
        for il in traslados_locales:
            xml.impuestos_locales_traslados.append(
                {
                    "nombre": il.get("imploctrasladado"),
                    "importe": il.get("importe"),
                    "tasa": il.get("tasadetraslado"),
                }
            )
            xml.total_impestos_locales_traslados += to_decimal(il.get("importe"))


    if not xml.iva:
        xml.tasa_cero = True

    xml.importe_tasa_general = to_precision_decimales(xml.importe_tasa_general)
    xml.importe_tasa_cero = to_precision_decimales(xml.importe_tasa_cero)
    xml.total_tasa_general = to_precision_decimales(xml.total_tasa_general)
    xml.total_tasa_cero = (
        to_precision_decimales(xml.total_tasa_cero)
        #+ xml.total_impestos_locales
    )


    xml.total_tasa_frontera = to_precision_decimales(xml.total_tasa_frontera)


    xml.total_exento = xml.importe_exento
    
    if xml.total_tasa_general:
        xml.total_tasa_general -= (
            xml.total_impestos_locales_retenciones-
            xml.total_impestos_locales_traslados
        )


    if not xml.total_no_objeto_iva:
        xml.total_no_objeto_iva = (
            to_decimal(xml.total) -
            xml.total_tasa_general - 
            xml.total_tasa_frontera - 
            xml.total_tasa_cero -
            xml.total_exento
        )

    if xml.total_tasa_general or xml.total_tasa_frontera:
        """
            SI HAY IMPUESTOS RETENIDOS, SE SUMA AL EXENTO POR QUE 
            SE LE RESTA ARRIBA (TOTAL_TASA_GENERAL O TOTAL_TASA_FRONTERA)
        """
        xml.total_no_objeto_iva += xml.impuestos.totalImpuestosRetenidos

    xml.total_no_objeto_iva = to_precision_decimales(xml.total_no_objeto_iva)

    total_tasas = {}
    total_tasas["total_tasa_general"] = xml.total_tasa_general
    total_tasas["total_tasa_cero"] = xml.total_tasa_cero
    total_tasas["total_tasa_frontera"] = xml.total_tasa_frontera
    total_tasas["total_exento"] = xml.total_exento
    total_tasas["total_no_objeto_iva"] = xml.total_no_objeto_iva
    
    tasa_mayor = sorted(total_tasas.items(), key=lambda item: item[1], reverse=True)[0]
    suma_tasas = (
        xml.total_tasa_general +
        xml.total_tasa_cero +
        xml.total_tasa_frontera +
        xml.total_exento +
        xml.total_no_objeto_iva 
    )
    diferencia = (
        to_precision_decimales(suma_tasas, 2) - 
        to_precision_decimales(xml.total, 2)
    )

    if to_decimal(math.fabs(diferencia)) == to_decimal("0.01"):
        importe_tasa = (
            getattr(xml, tasa_mayor[0]) -
            diferencia

        )
        setattr(
            xml,
            tasa_mayor[0], #key
            importe_tasa
        )

    if version == 3:
        xml.complemento = Object()
        xml.complemento.timbrefiscaldigital = Object()
        complemento = o.find("complemento")

        for version_ecc in ["ecc11", "ecc12"]:

            estado_cuenta_combustible = XmlNewObject(texto=xml_text).find(
                "EstadoDeCuentaCombustible", version_ecc
            )
            conceptos_combustible = []
            for concepto in estado_cuenta_combustible.find_list(
                "ConceptoEstadoDeCuentaCombustible", version_ecc
            ):
                iva = (
                    concepto.find("Traslados", version_ecc)
                    .find_list("Traslado", version_ecc)[0]
                    .get("Importe")
                )
                conceptos_combustible.append(
                    {
                        "fecha": concepto.get("Fecha"),
                        "rfc": concepto.get("Rfc"),
                        "importe": to_decimal(concepto.get("Importe")),
                        "iva": to_decimal(iva),
                    }
                )

        xml.complemento.conceptos_combustible = conceptos_combustible
        xml.complemento.timbrefiscaldigital.uuid = ""
        if complemento.exists:
            tfd = complemento.find("timbrefiscaldigital", "tfd")
            if not tfd.exists:
                tfd = complemento.find("timbrefiscaldigital", "")

            if tfd.exists:
                xml.complemento.timbrefiscaldigital.version = tfd.get(
                    "version"
                )
                xml.complemento.timbrefiscaldigital.uuid = tfd.get("uuid")
                xml.complemento.timbrefiscaldigital.fechatimbrado_str = tfd.get(
                    "fechatimbrado"
                )
                xml.complemento.timbrefiscaldigital.fechatimbrado_dt = get_fecha_cfdi(
                    xml.complemento.timbrefiscaldigital.fechatimbrado_str
                )
                xml.complemento.timbrefiscaldigital.sellocfd = tfd.get(
                    "sellocfd"
                )
                xml.complemento.timbrefiscaldigital.nocertificadosat = tfd.get(
                    "nocertificadosat"
                )
                xml.complemento.timbrefiscaldigital.sellosat = tfd.get(
                    "sellosat"
                )
                xml.complemento.timbrefiscaldigital.rfcprovcertif = tfd.get(
                    "rfcprovcertif", ""
                )

                if xml.complemento.timbrefiscaldigital.uuid:
                    xml.uuid = xml.cfdi_uuid = xml.complemento.timbrefiscaldigital.uuid

                    xml.complemento.timbrefiscaldigital.cadenaoriginal = (
                        "||1.0|%s|%s|%s|%s||"
                        % (
                            xml.complemento.timbrefiscaldigital.uuid,
                            xml.complemento.timbrefiscaldigital.fechatimbrado_str,
                            xml.complemento.timbrefiscaldigital.sellocfd,
                            xml.complemento.timbrefiscaldigital.nocertificadosat,
                        )
                    )

                    xml.qrcode = 'https://' + \
                        'verificacfdi.facturaelectronica.sat.gob.mx' + \
                        '/default.aspx?&id=%s&re=%s&rr=%s&tt=%s&fe=%s' % (
                        
                        xml.complemento.timbrefiscaldigital.uuid,
                        xml.emisor.rfc,
                        xml.receptor.rfc,
                        xml.total,
                        xml.sello[-8:],
                    )

                else:
                    xml.complemento.timbrefiscaldigital.cadenaoriginal = ""

            nominas_xml = complemento.find_list("nomina", "nomina12")
            if not nominas_xml:
                nominas_xml = complemento.find_list("nomina", "nomina")

            nominas = []
            for nomina_xml in nominas_xml:
                nomina_object = Object()
                nomina_version = nomina_xml.get("version")

                receptor_nomina = nomina_xml.find("receptor")
                nomina_object.numero_empleado = receptor_nomina.get(
                    "numempleado", ""
                )
                nomina_object.curp = receptor_nomina.get("curp", "")
                nomina_object.nss = receptor_nomina.get(
                    "numseguridadsocial", ""
                )
                nomina_object.tipo_regimen = to_int(
                    receptor_nomina.get("tiporegimen", "")
                )
                nomina_object.get_tipo_regimen_display = dict(
                    TIPOS_REGIMEN
                ).get(to_int(nomina_object.tipo_regimen), "")
                nomina_object.fecha_inicio = nomina_xml.get(
                    "fechainicialpago", ""
                )
                nomina_object.fecha_fin = nomina_xml.get(
                    "fechafinalpago", ""
                )
                nomina_object.fecha_pago = nomina_xml.get(
                    "fechapago", ""
                )
                nomina_object.dias = nomina_xml.get(
                    "numdiaspagados", ""
                )
                nomina_object.departamento = receptor_nomina.get(
                    "departamento", ""
                )
                nomina_object.puesto = receptor_nomina.get(
                    "puesto", ""
                )
                nomina_object.tipo_contrato = receptor_nomina.get(
                    "tipocontrato", ""
                )
                nomina_object.tipo_jornada = receptor_nomina.get(
                    "tipojornada", ""
                )
                nomina_object.riesgo_puesto = receptor_nomina.get(
                    "riesgopuesto", ""
                )
                if to_int(nomina_object.riesgo_puesto):
                    nomina_object.get_riesgo_puesto_display = dict(
                        RIESGO_PUESTOS
                    ).get(to_int(nomina_object.riesgo_puesto), None)
                else:
                    nomina_object.get_riesgo_puesto_display = None
                    
                nomina_object.sdi = receptor_nomina.get(
                    "salariodiariointegrado", ""
                )
                nomina_object.sbc = receptor_nomina.get(
                    "salariobasecotapor", ""
                )
                nomina_object.fecha_iniciorel_laboral = receptor_nomina.get(
                    "fechainiciorellaboral", ""
                )
                nomina_object.antiguedad = receptor_nomina.get(
                    "Antig\xfcedad", ""
                )
                nomina_object.clabe = receptor_nomina.get("clabe", "")
                nomina_object.periodicidadpago = receptor_nomina.get(
                    "periodicidadpago", ""
                )
                nomina_object.claveentfed = receptor_nomina.get(
                    "claveentfed", ""
                )
                nomina_object.registro_patronal = nomina_xml.find(
                    "emisor"
                ).get("registropatronal", "")
                esncf = nomina_xml.find("emisor").get("entidadsncf", {})
                nomina_object.origen_recurso = esncf.get(
                    "origenrecurso", ""
                )
                nomina_object.monto_recurso_propio = esncf.get(
                    "montorecursopropio", ""
                )
                nomina_object.tipo_nomina = nomina_xml.get(
                    "tiponomina", ""
                )

                percepciones = nomina_xml.find("percepciones").find_list(
                    "percepcion"
                )
                nomina_object.percepciones = []
                nomina_object.total_gravado = 0
                nomina_object.total_exento = 0
                nomina_object.total_percepciones = 0
                if percepciones:
                    for p in percepciones:
                        nomina_object.percepciones.append(
                            {
                                "clave": p.get("clave"),
                                "concepto": p.get("concepto"),
                                "importegravado": p.get("importegravado"),
                                "importeexento": p.get("importeexento"),
                                "tipo": p.get("tipopercepcion"),
                            }
                        )
                        nomina_object.total_gravado += to_decimal(
                            p.get("importegravado")
                        )
                        nomina_object.total_exento += to_decimal(
                            p.get("importeexento")
                        )
                        nomina_object.total_percepciones += to_decimal(
                            p.get("importegravado")
                        ) + to_decimal(
                            p.get("importeexento")
                        )

                otrospagos = nomina_xml.find("otrospagos").find_list(
                    "otropago"
                )
                nomina_object.otrospagos = []
                nomina_object.total_otrospagos = 0
                if otrospagos:
                    for p in otrospagos:

                        nomina_object.subsidio = 0
                        subsidio = p.find("subsidioalempleo")
                        if subsidio.exists:
                            nomina_object.subsidio = to_decimal(
                                subsidio.get("subsidiocausado")
                            )

                        nomina_object.otrospagos.append(
                            {
                                "clave": p.get("clave"),
                                "concepto": p.get("concepto"),
                                "importe": p.get("importe"),
                                "tipo": p.get("tipootropago"),
                            }
                        )
                        nomina_object.total_otrospagos += to_decimal(
                            p.get("importe")
                        )

                deducciones = nomina_xml.find("deducciones").find_list(
                    "deduccion"
                )
                nomina_object.deducciones = []
                nomina_object.total_deducciones = 0
                if deducciones:
                    for d in deducciones:
                        nomina_object.deducciones.append(
                            {
                                "clave": d.get("clave"),
                                "concepto": d.get("concepto"),
                                "importe": d.get("importe"),
                                "tipo": d.get("tipodeduccion"),
                            }
                        )
                        nomina_object.total_deducciones += to_decimal(
                            d.get("importe")
                        )

                horasextra = nomina_xml.find("horasextra").find_list(
                    "horaextra"
                )
                nomina_object.horasextra = []

                if horasextra:
                    for he in horasextra:
                        nomina_object.horasextra.append(he)

                incapacidades = nomina_xml.find("incapacidades").find_list(
                    "incapacidad"
                )
                nomina_object.incapacidades = []
                if incapacidades:
                    for i in incapacidades:
                        nomina_object.incapacidades.append(i)

                nomina_object.total_percibido = to_decimal(xml.total)
                nominas.append(nomina_object)


            if nominas:
                xml.complemento.nominas = nominas
                xml.complemento.nomina =  nominas[0]
            else:
                xml.complemento.nominas = []
                xml.complemento.nomina = None

            ine = complemento.find("ine", "ine")
            if ine.exists:
                xml.complemento.ine = Object()
                xml.complemento.ine.tipoproceso = ine.get("tipoproceso", "")
                xml.complemento.ine.tipocomite = ine.get("tipocomite", "")
                if ine.find("entidad"):
                    xml.complemento.ine.claveentidad = ine.find("entidad").get(
                        "claveentidad", ""
                    )
                    if ine.find("entidad").find("contabilidad"):
                        xml.complemento.ine.idcontabilidad = (
                            ine.find("entidad")
                            .find("contabilidad")
                            .get("idcontabilidad", "")
                        )

            iedu = complemento.find("insteducativas", "iedu")
            if iedu.exists:
                xml.complemento.iedu = Object()
                xml.complemento.version = iedu.get("version")
                xml.complemento.autrvoe = iedu.get("autrvoe")
                xml.complemento.nombre_alumno = iedu.get("nombrealumno")
                xml.complemento.curp = iedu.get("curp")
                xml.complemento.nivel_educativo = iedu.get("niveleducativo")
                xml.complemento.rfc_pago = iedu.get("rfcpago")

    carta_porte = complemento.find("cartaporte", "cartaporte20")

    if carta_porte.exists:
        xml.complemento_carta_porte = carta_porte.to_dict()
        carta_porte_dic = xml.complemento_carta_porte
        carta_porte_dic["ubicaciones"] = []
        for ucp in  carta_porte.find("ubicaciones").find_list("ubicacion"):
            ubicacion = ucp.to_dict()
            ubicacion["origen"] = ucp.find("origen").to_dict()
            ubicacion["domicilio"] = ucp.find("domicilio").to_dict()
            ubicacion["destino"] = ucp.find("destino").to_dict()
            carta_porte_dic["ubicaciones"].append(ubicacion)


        carta_porte_dic["mercancias"] = []
        for mercancia in  carta_porte.find("mercancias").find_list("mercancia"):
            mercancia_dic = mercancia.to_dict()
            mercancia_dic["mercancia"] = ucp.find("mercancia").to_dict()
            carta_porte_dic["mercancias"].append(mercancia_dic)

        autotransporte_federal = carta_porte.find("mercancias").find("Autotransporte")
        carta_porte_dic["autotransporte_federal"] = autotransporte_federal.to_dict()
        carta_porte_dic["autotransporte_federal"]["identificacion_vehicular"] = autotransporte_federal.find("identificacionvehicular").to_dict()
        carta_porte_dic["autotransporte_federal"]["seguros"] = autotransporte_federal.find("Seguros").to_dict()

        figura_transporte = carta_porte.find("figuratransporte")
        carta_porte_dic["figura_transporte"] = figura_transporte.to_dict()
        carta_porte_dic["figura_transporte"]["tipos_figura"] = []

        for op in figura_transporte.find_list("TiposFigura"):
            figura_dic = op.to_dict()
            figura_dic["domicilio"] = op.find("domicilio").to_dict()
            carta_porte_dic["figura_transporte"]["tipos_figura"].append(figura_dic)
            
    else:
        xml.complemento_carta_porte = None

    xml.es_dolares = False
    xml.es_euros = False
    xml.importe = (
        to_decimal(xml.total)
        - to_decimal(xml.iva)
        - to_decimal(xml.ieps)
        + xml.impuestos.totalImpuestosRetenidos
    )

    xml.total = to_decimal(xml.total)
    xml.subtotal = to_decimal(xml.subtotal)
    
    if not xml.moneda.upper() in ["MXN", "MN", "PESOS", "MX"]:
        if "USD" in xml.moneda.upper() or xml.moneda.upper().startswith("D"):
            xml.es_dolares = True
        elif "EUR" in xml.moneda.upper() or xml.moneda.upper().startswith("E"):
            xml.es_euros = True
        else:
            if to_decimal(xml.tipocambio) > 1:
                xml.es_dolares = True

    return xml

def descargar_cfdi_masivo():
    print("aaa")

def validar_cfdi(cfdi_xml):
    """
    Utilería de validación de CFDI's, usa el proyecto de nodejs 
    https://gitlab.com/admintotal/validacfdi-cli
    retorna una tupla (valido, error_string)
    """
    from django.conf import settings
    import subprocess
    import os

    if not settings.CFDI_NODE_BIN or not settings.CFDI_VALIDADOR_PATH:
        raise Exception(
            "Es necesario especificar las variables CFDI_NODE_BIN y "
            "CFDI_VALIDADOR_PATH en su settings.py"
        )
    
    cfdi_obj = XmlNewObject(texto=cfdi_xml)
    complemento = cfdi_obj.find("Complemento")
    tfd = complemento.find("TimbreFiscalDigital", "tfd")
    uuid = tfd.get("UUID")
    nc = tfd.get("NoCertificadoSAT")
    cer = cfdi_obj.get_or_create_certificado(nc)
    cer.set_certificado()
    cer_path = cer.get_path()

    cfdi_path = f"/tmp/{uuid}.xml"
    with open(cfdi_path, "w") as tmp_file:
        tmp_file.write(cfdi_xml)
    
    if not os.path.exists(cfdi_path):
        return False, f"No existe la ruta {cfdi_path}"
    
    if not os.path.exists(cer_path):
        return False, f"No existe la ruta {cer_path}"

    try:
        subprocess.check_output([
            settings.CFDI_NODE_BIN,
            settings.CFDI_VALIDADOR_PATH,
            "--cfdi", cfdi_path,
            "--certificado-sat", cer_path,
        ], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        return False, str(e.output.decode())
    finally:
        if os.path.exists(cfdi_path):
            os.remove(cfdi_path)
    
    return True, None
