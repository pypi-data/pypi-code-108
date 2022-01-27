from django.template.loader import render_to_string


CAMPOS_ENCABEZADOS = (
    ("tipo_documento", "str"),
    ("clase_documento", "str"),
    ("encabezado_num_sociedad", "str"),
    ("encabezado_num_dicision", "str"),
    ("encabezado_num_proveedor", "str"),
    ("encabezado_correo", "str"),
    ("num_hoja_servicio", "str"),
    ("num_transporte", "str"),
    ("num_ctax_pag", "str"),
    ("ejercicio_ctax_pag", "str"),
    ("fecha_inicio_liquidacion", "date"),
    ("fecha_fin_liquidacion", "date"),
)

CAMPOS_DETALLE = ()

def generar_addenda(diccionario):
    return render_to_string("cfdi/addendas/ahmsa.xml", diccionario)
