m = _mov(id=15317)
proveedor = Cliente.objects.get(id=1768)
"""    
m.crear_fondo_cliente(
            monto_fondo=m.total,
            comentarios=u"Fondo generado por devolución.",
            es_monedero=m.orden.aplicaciones_credito_cliente.filter(cancelado=False, credito__es_monedero=True).exists(),
            cliente=proveedor,
            origen_creado=1
        )
"""
m.tipo_pago = 1
m.monto_efectivo = 0
m.monto_transferencia = 0
m.nota_pagada = False
m.save()