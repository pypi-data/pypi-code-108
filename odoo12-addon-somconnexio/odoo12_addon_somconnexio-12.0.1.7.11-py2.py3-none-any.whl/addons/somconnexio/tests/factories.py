import factory
from factory import fuzzy
import datetime
import random
factory.Faker._DEFAULT_LOCALE = 'es_ES'


class OdooModel(object):
    """ Represents Tryton's model """

    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class OdooModelFactory(factory.Factory):
    """ Generates Tryton's model instances """

    class Meta:
        abstract = True
        model = OdooModel
        strategy = 'build'

    id = factory.Sequence(lambda n: n)
    create_date = fuzzy.FuzzyDate(
        start_date=datetime.date(2008, 1, 1),
        end_date=datetime.date(2011, 1, 1)
    )

    @classmethod
    def _create(cls, target_class, *args, **kwargs):
        return target_class(*args, **kwargs)


class CountryFactory(OdooModelFactory):
    name = factory.Faker("country")
    code = factory.Faker("country_code")


class StateFactory(OdooModelFactory):
    name = factory.Faker("state")
    code = random.choice(["M", "B"])


class PartnerFactory(OdooModelFactory):
    street = factory.Faker("street_address")
    street2 = factory.Faker("secondary_address")
    zip = factory.Faker("postcode")
    city = factory.Faker("city")
    email = factory.Faker("email")
    state_id = factory.SubFactory(StateFactory)
    country_id = factory.SubFactory(CountryFactory)
    phone = factory.Faker("phone_number")
    firstname = factory.Faker("first_name")
    lastname = factory.Faker("last_name")
    name = factory.Faker("name")
    lang = random.choice(["es_ES", "ca_ES"])
    vat = factory.Faker("doi")
    ref = factory.Sequence(lambda n: n)

    @property
    def full_street(self):
        return "{} {}".format(self.street, self.street2)


class OpenCellConfigurationFactory(OdooModelFactory):
    customer_category_code = 'CLIENT'
    seller_code = 'SC'


class ProductFactory(OdooModelFactory):
    default_code = "CODE"

    def __init__(self, code=None):
        if code:
            self.default_code = code


class ContractLineFactory(OdooModelFactory):
    product_id = factory.SubFactory(ProductFactory)
    date_start = fuzzy.FuzzyDate(
        start_date=datetime.date(2008, 1, 1),
        end_date=datetime.date(2011, 1, 1)
    )


class BankFactory(OdooModelFactory):
    bic = factory.Faker("swift")
    name = "Banco Santander"


class BankAccountFactory(OdooModelFactory):
    sanitized_acc_number = factory.Faker('iban')
    bank_id = factory.SubFactory(BankFactory)


class MandateFactory(OdooModelFactory):
    partner_bank_id = factory.SubFactory(BankAccountFactory)


class ContractFactory(OdooModelFactory):
    contract_line_ids = factory.List([ContractLineFactory()])
    partner_id = factory.SubFactory(PartnerFactory)
    invoice_partner_id = factory.SubFactory(PartnerFactory)
    mandate_id = factory.SubFactory(MandateFactory)
    terminate_date = fuzzy.FuzzyDate(
        start_date=datetime.date(2020, 1, 1),
        end_date=datetime.date(2021, 1, 1)
    )
    code = factory.Sequence(lambda n: n)
