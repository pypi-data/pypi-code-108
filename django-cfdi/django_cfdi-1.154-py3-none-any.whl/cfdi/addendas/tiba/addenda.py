from django.template.loader import render_to_string
from django.conf import settings

CAMPOS_ENCABEZADOS = (
	("referencia", "str"),
	("observacion", "str"),
)

def generar_addenda(diccionario):
    return render_to_string("cfdi/addendas/tiba.xml", diccionario)
