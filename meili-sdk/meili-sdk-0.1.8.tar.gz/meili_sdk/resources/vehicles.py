from meili_sdk.models.vehicle import Vehicle
from meili_sdk.resources.base import BaseResource


class SDKVehicleResource(BaseResource):
    def get_vehicles(self, **filters):
        return self.get("sdk/vehicles/", expected_class=Vehicle, filters=filters)

    def create_vehicle(self, vehicle):
        return self.post("sdk/vehicles/", data=vehicle, expected_class=Vehicle)

    def get_vehicle(self, uuid):
        return self.get(f"sdk/vehicles/{uuid}/", expected_class=Vehicle)

    def update_vehicle(self, vehicle):
        return self.patch(
            f"sdk/vehicles/{vehicle.uuid}/", data=vehicle, expected_class=Vehicle
        )

    def delete_vehicle(self, vehicle):
        return self.delete(f"sdk/vehicles/{vehicle.uuid}/", expected_class=Vehicle)
