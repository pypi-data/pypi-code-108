from django.template.loader import render_to_string
from django.conf import settings



CAMPOS_ENCABEZADOS = (
	("no_acreedor", "str"),
	("clave_transp", "str"),
	("id_analitico", "str"),
	("tipo_producto", "str"),
	("cedula", "str"),
	("contrato", "str"),
	("analitico", "str"),
)


def generar_addenda(diccionario):
    return render_to_string("cfdi/addendas/pemex.xml", diccionario)
