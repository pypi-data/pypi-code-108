from django.template.loader import render_to_string
from django.conf import settings

TIPOS = (
    ("Cristales", "Cristales"),
	("Honorarios", "Honorarios"),
	("Gruas", "Gruas"),
	("Asistencia", "Asistencia"),
	("Reparaciones", "Reparaciones"),
	("Refacciones", "Refacciones"),
	("GMedicos", "GMedicos"),
)


CAMPOS_ENCABEZADOS = (
    ("clave_proveedor", "str"),
    ("tipo", TIPOS),
    ("no_siniestro", "str"),
    ("orden_pago", "str"),
	("cristales_deducible", "decimal"),
	("codigo_nags", "str"),
	("costo_honorarios", "decimal"),
	("costo_gruas", "decimal"),
	("costo_asistencia", "decimal"),
	("num_valuacion_inicial", "str"),
	("costo_reparaciones", "decimal"),
	("numero_vale_refacciones", "str"),
	("pase_medico", "str"),
	("costo_gmedicos", "decimal"),
)


def generar_addenda(diccionario):
    return render_to_string("cfdi/addendas/multiasistencia.xml", diccionario)
