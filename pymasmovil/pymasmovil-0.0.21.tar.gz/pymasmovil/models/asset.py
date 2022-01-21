from pymasmovil.client import Client
from pymasmovil.models.contract import Contract
from pymasmovil.errors.exceptions import UnknownMMError


class Asset(Contract):
    _route = "/v2/assets"

    maxNumTariff = ""
    numTariff = ""
    assetType = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def get(cls, session, asset_id):
        contract = super().get(session, asset_id)

        return cls(**contract["asset"])

    @classmethod
    def get_by_phone(cls, session, phone):
        """
        Retrieve the asset associated to a given phone number from the MM sytem.

        :param:
            phone (str): Phone number of the contract we expect
        :return: dict containing the asset from the MM response
        """
        params = {"rowsPerPage": 1, "actualPage": 1, "phone": phone}

        response = Client(session).get(cls._route, **params)

        return cls(**response["rows"][0])

    @classmethod
    def update_product(
        cls,
        session,
        asset_id,
        transaction_id,
        product_id="",
        execute_date="",
        additional_bonds=[],
        bonds_to_remove=[],
        promotions=[],
        promotions_to_remove=[],
    ):
        """
        Modify asset request:
            - change tariff
            - add one-shot bonds

        :param:
            asset_id (str): MM Asset ID
            transaction_id (str): Unique and correlative 18-length numeric code
            productId (str): ID from the new tariff we want to apply
                            [only for change tariff]
            execute_date (str): request date [only for change tariff]
            additional_bonds (list): additional bonds to add
            bonds_to_remove (list): additional bonds to delete
            promotions (list): promotions to add
            bonds_to_remove (list): promotions to delete
        :return: modified asset
        """

        route = "{}/{}/change-asset".format(cls._route.replace("v2", "v1"), asset_id)

        active_change = {
            "transactionId": transaction_id,
            "assetInfo": {
                "executeDate": execute_date,
                "productId": product_id,
                "additionalBonds": additional_bonds,
                "removeBonds": [{"assetId": bond_id} for bond_id in bonds_to_remove],
                "promotions": promotions,
                "removePromotions": [{"assetId": bond_id} for bond_id
                                     in promotions_to_remove],
            }
        }

        response = Client(session).patch(route, (), active_change)

        if response == "Petición aceptada":
            return response
        else:
            raise UnknownMMError(response)
