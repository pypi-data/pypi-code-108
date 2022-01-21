from pymasmovil.client import Client


class Contract:
    """
    Parent class to OrderItem and Asset,
    which share a very similar class structure and attributes
    """

    id = ""
    account_id = ""
    name = ""
    surname = ""
    productName = ""
    phone = ""
    status = ""
    createdDate = ""
    productId = ""
    productRelation = ""
    initDate = ""
    attributes = {
        "Apellidos": "",
        "ICCID_Donante": "",
        "Nombre": "",
        "Numero_de_Documento": "",
        "Operador_Donante_Movil": "",
        "Operador_Receptor_Movil": "",
        "Tipo_de_Documento": "",
        "Tipo_de_Linea": "",
        "Fecha_de_solicitud_del_abonado": "",
        "Porcentaje_Consumo_Bono": "",
    }
    additionalBonds = []
    promotions = []
    simAttributes = {
        "ICCID": "",
        "IMSI": "",
        "PIN": "",
        "PIN2": "",
        "PUK": "",
        "PUK2": "",
    }
    tarAttributes = {
        "Fecha_planificada_de_entrega": "",
    }

    def __init__(self, **kwargs):

        for key, value in kwargs.items():
            if key in ["attributes", "simAttributes", "tarAttributes"] and value:
                attribute_dict = getattr(self, key).copy()
                for inner_key, inner_value in value.items():
                    if inner_key in attribute_dict:
                        attribute_dict[inner_key] = inner_value
                setattr(self, key, attribute_dict)
            else:
                if hasattr(self.__class__, key):
                    setattr(self, key, value)

    @classmethod
    def get(cls, session, contract_id):
        """
        Returns a Contract instance (order_item or asset) obtained by id.
        :param contract_id:

        :return: Contract:
        """

        response = Client(session).get(route="{}/{}".format(cls._route, contract_id))

        return response
