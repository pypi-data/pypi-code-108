from pymasmovil.client import Client
from pymasmovil.models.new_line_request import NewLineRequest
from pymasmovil.models.contract import Contract
from pymasmovil.errors.exceptions import NewLineRequestRequiredParamsError


class OrderItem(Contract):

    _route = "/v2/order-items"
    orderType = ""
    lastModifiedDate = ""
    KO_status = ["Cancelada", "Cancelando", "Esperando para cancelar", "Error"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def get(cls, session, order_item_id):
        contract = super().get(session, order_item_id)

        return cls(**contract["orderDetail"])

    @classmethod
    def create(cls, session, account, **new_order_item):
        """
        Creates an order-item and posts it to the given account

        :param account: account where we want to add the order-item
        :param **new_order_item:
        :return: order-item instance
        """

        post_route = "/v1/accounts/{}/order-items".format(account.id)

        cls._check_required_attributes(new_order_item)

        Client(session).post(post_route, (), new_order_item)

        new_line_request = NewLineRequest(new_order_item, account.id)

        return OrderItem(**new_line_request.to_order_item())

    def _check_required_attributes(new_order_item):
        """Check that all compulsary attributes for a portability request
        are present in the request dynamic fields"""

        required_attributes = ["idLine", "documentType", "iccid", "productInfo"]

        is_portability = False
        new_line_info = new_order_item["lineInfo"][0]

        if new_line_info.get("phoneNumber"):
            is_portability = True
            required_attributes.extend(["docid", "donorOperator"])

        if new_line_info.get("documentType") == "CIF":
            # Organization client
            required_attributes.append("corporateName")

        elif new_line_info.get("documentType") in ("NIF", "NIE", "Pasaporte"):
            # Particular client
            required_attributes.extend(["name", "surname"])

        order_item_filled_attributes = set(
            filter(new_line_info.get, new_line_info.keys())
        )

        missing_attributes = set(required_attributes) - order_item_filled_attributes

        if len(missing_attributes) != 0:
            raise NewLineRequestRequiredParamsError(
                is_portability, sorted(missing_attributes)
            )
