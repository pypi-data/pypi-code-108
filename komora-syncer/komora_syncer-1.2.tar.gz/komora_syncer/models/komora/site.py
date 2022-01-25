from komora_syncer.models.komora.location import Location
from komora_syncer.models.komora.address import Address
from komora_syncer.models.komora.site_contact import SiteContact


class Site():
    def __init__(self, name, description, facility, latitude, longitude, contacts, address, isActive, locations, id, organizationId, organizationName, code, typeId, typeName):
        self.name = name
        self.description = description
        self.facility = facility
        self.latitude = latitude
        self.longitude = longitude
        self.code = code
        self.typeId = typeId
        self.typeName = typeName
        self.isActive = isActive
        self.id = id

        self.organizationId = organizationId
        self.organizationName = organizationName

        if address:
            self.address = Address(**address)
        else:
            self.address = address

        if locations:
            self.locations = []
            for location in locations:
                self.locations.append(Location(**location))
        else:
            self.locations = locations

        if contacts:
            self.contacts = []
            for contact in contacts:
                self.contacts.append(SiteContact(**contact))
        else:
            self.contacts = contacts

        self.flatten_locations = flatten_locations(
            self.locations) if self.locations else []


def flatten_locations(nested_locations):
    result = []

    def flat(nested_locations):
        for location in nested_locations:
            result.append(location)
            flat(location.locations)
        return result

    flat(nested_locations)
    return result
