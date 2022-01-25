class Address:
    # DTO in OC - https://api.opencellsoft.com/7.X/json_AddressDto.html
    def __init__(self, address, zip, city, state, country):
        self.address = address
        self.zip = zip
        self.city = city
        self.state = state
        self.country = country

    def to_dict(self):
        return {
            "address1": self.address,
            "zipCode": self.zip,
            "city": self.city,
            "state": self.state,
            "country": self.country,
        }
