from django.template.loader import render_to_string
from django.conf import settings

BODEGAS = (
    ("30001", "CULIACAN"),
    ("30002", "LEON"),
    ("30003", "HERMOSILLO"),
    ("30004", "LAGUNA"),
    ("30006", "MONTERREY"),
    ("30007", "GUADALAJARA"),
    ("30008", "AZCAPOTZALCO"),
    ("30009", "PUEBLA"),
    ("30010", "VILLA HERMOSA"),
    ("30011", "IZTAPALAPA"),
    ("30012", "IMP_MXL2"),
    ("30013", "MEXICALI"),
    ("30014", "IZCALLI"),
    ("30015", "IXTAPALUCA"),
    ("30016", "TECAMAC"),
    ("30017", "MERIDA"),
    ("30018", "LOS MOCHIS"),
    ("30019", "VERACRUZ"),
    ("30020", "GUADALAJARA II "),
    ("30021", "IXTAPALUCA IMP"),
    ("30022", "TOLUCA"),
    ("30030", "TECAMAC II"),
    ("30031", "PUEBLA II"),
)
REGIONES = (
    (1, "La Paz, Tijuana, Mexicali"),
    (2, "Culiacán, Hermosillo, Los Mochis."),
    (3, "Laguna."),
    (4, "Monterrey."),
    (5, "Guadalajara."),
    (6, "León, Izcalli."),
    (7, "Puebla."),
    (8, "Villahermosa, Merida."),
    (9, "México, Iztapalapa, Izcalli, Ixtapaluca, Tecamac."),
)


CAMPOS_ENCABEZADOS = (
    ("bodega_receptora", BODEGAS),
    ("bodega_destino", BODEGAS),
    ("numero_pedido_comprador", "int"),
    ("fecha_pedido_comprador", "date"),
    ("fecha_entrega", "date"),
    ("numero_pedimento", "str"),
    ("empresa_transportista", "str"),
)

CAMPOS_DETALLE = (
    ("lote_producto", "str"),
    ("numero_pedimento", "str"),
    ("fecha_produccion", "date"),
    ("numero_comprador", "str"),
    ("fecha_entrada", "date"),
)

def generar_addenda(diccionario):
    return render_to_string("cfdi/addendas/coppel.xml", diccionario)
