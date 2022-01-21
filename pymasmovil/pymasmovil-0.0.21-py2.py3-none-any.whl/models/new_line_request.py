from datetime import datetime


class NewLineRequest:
    """
    Since GET /order-item/:id response and the POST /order-item request don't
    match except for a few attributes, this class aims to build an OrderItem instance
    mapping these few matching attributes.
    The specification doesn't explicitly state the optimistic equivalence presented here,
    so this mapping needs to be reviewed later on.
    """

    def __init__(self, new_order_item, account_id):
        self.lineInfo = new_order_item["lineInfo"][0]
        self.account_id = account_id

    def to_order_item(self):
        """
        Maps the atttributes of a NewLineRequest instance, as specified in Swagger,
        to the attributes of an OrderItem instance, as specified in a
        GET response.

        :return: dict
        """

        return {
            "account_id": self.account_id,
            "name": self.lineInfo.get("name"),
            "surname": self.lineInfo.get("surname"),
            "phone": self.lineInfo.get("phoneNumber"),
            "orderType": "OrderItem",
            "status": "Esperando para enviar",
            "productName": "Unknown",
            "createdDate": datetime.now(),
            "lastModifiedDate": datetime.now(),
            "attributes": {
                "Nombre": self.lineInfo.get("name"),
                "Apellidos": self.lineInfo.get("surname"),
                "ICCID_Donante": self.lineInfo.get("iccid_donante"),
                "Tipo_de_Documento": self.lineInfo.get("documentType"),
                "Numero_de_Documento": self.lineInfo.get("docid"),
                "Operador_Donante_Movil": self.lineInfo.get("donorOperator"),
                "Operador_Receptor_Movil": "Som Connexió",
                "Fecha_de_solicitud_del_abonado": datetime.now(),
            },
            "simAttributes": {
                "ICCID": self.lineInfo.get("iccid"),
            },
        }
