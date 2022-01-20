from django.template.loader import render_to_string
from django.conf import settings


CAMPOS_ENCABEZADOS = (
    ("instrucciones_especiales", "str"),
    ("fecha_referencia", "date"),
    ("orden_compra", "int"),
    ("id_referencia_iv", "int"),
    ("id_referencia_atz", "int"),
    ("numero_referencia_atz", "int"),
    ("numero_nota", "int"),
    ("ngl_comprador", "int"),
    ("nombre_departamento", "str"),
    ("ngl_vendedor", "int"),
    ("ngl_envio", "int"),
    ("nombre_envio", "str"),
    ("calle_envio", "str"),
    ("ciudad_envio", "str"),
    ("cp_envio", "str"),
)


def generar_addenda(diccionario):
    return render_to_string("cfdi/addendas/amece.xml", diccionario)
