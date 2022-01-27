from django.template.loader import render_to_string
from django.conf import settings

CAMPOS_ENCABEZADOS = (
    ("orden", "str"),
)

def generar_addenda(diccionario):
    return render_to_string("cfdi/addendas/agnico.xml", diccionario)
