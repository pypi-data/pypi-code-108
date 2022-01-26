from .opencell_resource import OpenCellResource
from .opencell_types.description import Description
from .opencell_types.address import Address


class AccountHierarchyResource(OpenCellResource):
    MAX_LENGTH = 50

    @property
    def name(self):
        # DTO in OC - https://api.opencellsoft.com/7.X/json_NameDto.html
        first_name = (
            self.partner.firstname or ""
        )
        last_name = (
            self.partner.lastname or self.partner.name or ""
        )
        return {
            "firstName": first_name[:self.MAX_LENGTH],
            "lastName": last_name[:self.MAX_LENGTH],
        }

    @property
    def description(self):
        return Description(self.partner.name).text

    @property
    def address(self):
        return Address(
            address=self.partner.full_street,
            zip=self.partner.zip,
            city=self.partner.city,
            state=self.partner.state_id.name,
            country=self.partner.country_id.code
        ).to_dict()

    @property
    def vatNo(self):
        return self.partner.vat

    @property
    def contactInformation(self):
        # DTO in OC - https://api.opencellsoft.com/7.X/json_ContactInformationDto.html
        return {
            "email": self.email,
            "mobile": self.phone,
        }
