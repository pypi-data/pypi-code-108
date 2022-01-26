from django.template.loader import render_to_string
from django.conf import settings


CAMPOS_ENCABEZADOS = (
    ("folio_factura", "str"),
    ("aprobacion_sat", "str"),
    ("buyer_gln", "str"),
    ("seller_gln", "str"),
    
)

CAMPOS_DETALLE = (
    ("gtin", "str"),
)

def generar_addenda(diccionario):
    return render_to_string("cfdi/addendas/lacomer.xml", diccionario)
