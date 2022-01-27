from django.template.loader import render_to_string
from django.conf import settings


CAMPOS_ENCABEZADOS = (
    ("ri_emisor", "str"),
    ("ri_receptor", "str"),
    ("folio_orden_compra", "str"),
    ("folio_nota_recepcion", "str"),
    ("numero_proveedor", "str"),
    ("tipo_cargo", "str"),
    ("observaciones", "str"),
)


def generar_addenda(diccionario):
    return render_to_string("cfdi/addendas/loreal.xml", diccionario)
