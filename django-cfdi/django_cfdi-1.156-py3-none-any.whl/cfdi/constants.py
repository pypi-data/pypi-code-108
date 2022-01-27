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


