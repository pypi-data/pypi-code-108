PACS = {
    "PRUEBA": 0,
    "PRODIGIA": 1,
    "FINKOK": 2,
    "STOCONSULTING": 3,
    "DFACTURE": 4,
}

CHOICES_PACS = []
for nombre,valor in PACS.items():
	CHOICES_PACS.append((valor, nombre))

CLAVES_COMBUSTIBLE = ["15101506", "15101505", "15101509", "15101514", "15101515", "15101500"]


ADDENDAS = (
    ("", "-------"),
    ("agnico", "Agnico Eagle"),
    ("ahmsa", "AHMSA"),
    ("coppel", "Coppel"),
    ("loreal", "Loreal"),
    ("multiasistencia", "Multiasistencia"),
    ("pemex", "Pemex"),
    ("lacomer", "Comercial Mexicana"),
)

METODOS_PAGO = (
    #('NA', 'NA'),
    ("01", "01 Efectivo"),
    ("02", "02 Cheque nominativo"),
    ("03", "03 Transferencia electrónica de fondos"),
    ("04", "04 Tarjeta de crédito"),
    ("05", "05 Monedero electrónico"),
    ("06", "06 Dinero electrónico"),
    ("08", "08 Vales de despensa"),
    ("12", "12 Dación en pago"),
    ("13", "13 Pago por subrogación"),
    ("14", "14 Pago por consignación"),
    ("15", "15 Condonación"),
    ("17", "17 Compensación"),
    ("23", "23 Novación"),
    ("24", "24 Confusión"),
    ("25", "25 Remisión de deuda"),
    ("26", "26 Prescripción o caducidad"),
    ("27", "27 A satisfacción del acreedor"),
    ("28", "28 Tarjeta de débito"),
    ("29", "29 Tarjeta de servicio"),
    ("30", "30 Aplicación de anticipos"),
    ("31", "31 Intermediario pagos"),
    ("99", "99 Por definir")
)

MOTIVOS_CANCELACION_CFDI = (
    (
        "01", "Comprobante emitido con errores con relación", 
        """
        Aplica cuando la factura generada contiene un error en la clave del producto, 
        valor unitario, descuento o cualquier otro dato, por lo que se debe reexpedir.
        Primero se sustituye la factura y cuando se solicita la cancelación, 
        se incorpora el folio de la factura que sustituye a la cancelada.
        """
    ),

    (
        "02", "Comprobante emitido con errores sin relación", 
        """
        Aplica cuando la factura generada contiene un error en la clave del producto, 
        valor unitario, descuento o cualquier otro dato y no se requiera relacionar 
        con otra factura generada.
        """,
    ),
        
    (
        "03", "No se llevó a cabo la operación", 
        "Aplica cuando se facturó una operación que no se concreta."
    ),
    (
        "04", 
        "Operación nominativa relacionada en la factura global", 
        """
        Aplica cuando se incluye una venta en la factura global de operaciones 
        con el público en general y, posterior a ello, el cliente solicita su factura nominativa; 
        es decir, a su nombre y RFC. Se cancela la factura global, se reexpide sin incluir 
        la operación por la que se solicita factura. Se expide la factura nominativa.
        """
    ),
)

MOTIVOS_CANCELACION_CFDI_OP =[]
for mc in MOTIVOS_CANCELACION_CFDI:
    MOTIVOS_CANCELACION_CFDI_OP.append((mc[0], f"{mc[0]} {mc[1]}"))




REGIMEN_FISCAL_FISICA_OP =(
    #FISICA
    ("605", "Sueldos y Salarios e Ingresos Asimilados a Salarios"),
    ("606", "Arrendamiento"),
    ("608", "Demás ingresos"),
    ("611", "Ingresos por Dividendos (socios y accionistas)"),
    ("612", "Personas Físicas con Actividades Empresariales y Profesionales"),
    ("614", "Ingresos por intereses"),
    ("616", "Sin obligaciones fiscales"),
    ("621", "Incorporación Fiscal"),
    #("622", "Actividades Agrícolas, Ganaderas, Silvícolas y Pesqueras "),
    ("629", "De los Regímenes Fiscales Preferentes y de las Empresas Multinacionales"),
    ("630", "Enajenación de acciones en bolsa de valores"),
    ("615", "Régimen de los ingresos por obtención de premios"),
    ("625", "Régimen de las Actividades Empresariales con ingresos a través de Plataformas Tecnológicas"),
    ("626", "Régimen Simplificado de Confianza"),
)

REGIMEN_FISCAL_MORAL_OP = (
    #MORAL
    ("601", "General de Ley Personas Morales" ),
    ("603", "Personas Morales con Fines no Lucrativos" ),
    ("609", "Consolidación" ),
    ("620", "Sociedades Cooperativas de Producción que optan por diferir sus ingresos" ),
    ("622", "Actividades Agrícolas, Ganaderas, Silvícolas y Pesqueras "),
    ("623", "Opcional para Grupos de Sociedades" ),
    ("624", "Coordinados" ),
    ("628", "Hidrocarburos" ),
    ("607", "Régimen de Enajenación o Adquisición de Bienes" ),
    ("626", "Régimen Simplificado de Confianza"),
)

REGIMEN_FISCAL_TODOS = (
    REGIMEN_FISCAL_FISICA_OP +
    REGIMEN_FISCAL_MORAL_OP +
    (("610", "Residentes en el Extranjero sin Establecimiento Permanente en México" ), )
)

REGIMEN_FISCAL_OP = []
for TMPRF in REGIMEN_FISCAL_TODOS:
    REGIMEN_FISCAL_OP.append(
        (TMPRF[0], f"{TMPRF[0]} - {TMPRF[1]}"),
    )