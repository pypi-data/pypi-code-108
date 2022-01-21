from adumo.exceptions import AdumoInvalidCard


class Card:
    def __init__(
        self, account_number, expiration_month, expiration_year, security_code, _type
    ):
        self.account_number = account_number
        self.expiration_month = expiration_month
        self.expiration_year = expiration_year
        self.security_code = security_code
        self.type = _type

        self._clean()
        self.validate()

    def _clean(self):
        self.type = self.type.lower()
        self.account_number = self.account_number.replace(" ", "")

    def as_dict(self):
        return {
            "account-number": self.account_number,
            "expiration-month": self.expiration_month,
            "expiration-year": self.expiration_year,
            "card-security-code": self.security_code,
            "card-type": self.type,
        }

    def validate(self):
        if len(self.expiration_month) != 2:
            raise AdumoInvalidCard("expiration_month length should be 2")

        if len(self.expiration_year) != 4:
            raise AdumoInvalidCard("expiration_year length should be 4")

        if len(self.security_code) != 3:
            raise AdumoInvalidCard("security_code length should be 3")


class AccountHolder:
    def __init__(self, first_name, last_name, **kwargs):
        self.first_name = first_name
        self.last_name = last_name
        self.other_info = kwargs

    def as_dict(self):
        return {
            "first-name": self.first_name,
            "last-name": self.last_name,
            **self.other_info,
        }

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
