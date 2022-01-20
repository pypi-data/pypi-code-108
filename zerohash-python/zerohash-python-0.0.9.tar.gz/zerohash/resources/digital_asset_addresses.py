from zerohash.resources.abstract import CreateableAPIResource, ListableAPIResource


class DigitalAssetAddresses(ListableAPIResource, CreateableAPIResource):
    OBJECT_NAME = "deposits.digital_asset_addresses"
