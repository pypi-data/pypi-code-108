'''Demo REST API to do enquiries of the details of a country.

The strange name comes from the name of an entity and  helmsman whois also
a navigator hence looking for details of a country.  TThe strange name  also
contribute to finding a unique name on yPI and at the same time not squatting
usefull names on the public domain.
'''
import json
from webob.exc import HTTPForbidden

from reahl.web.fw import UserInterface, CheckedRemoteMethod, JsonResult
from reahl.component.modelinterface import Field, EmailField
from reahl.component.exceptions import AccessRestricted
from reahl.web.bootstrap.page import HTML5Page
from reahl.web.bootstrap.ui import P, Ul, Li
from reahl.domain.systemaccountmodel import (
    AccountManagementInterface,
    LoginSession,
    EmailAndPasswordSystemAccount,
)
from reahl.sqlalchemysupport import Session, Base
from sqlalchemy import Integer, Column, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship


class CountryCurrency(Base):
    __tablename__ = 'country_currency'

    country_id = Column(Integer, ForeignKey('country.id'), primary_key=True)
    currency_id = Column(Integer, ForeignKey('currency.id'), primary_key=True)


class Country(Base):
    __tablename__ = 'country'

    id = Column(Integer, primary_key=True)
    cca2 = Column(String(2), unique=True)
    cca3 = Column(String(3), unique=True)
    name_common = Column(String(100))
    active = Column(Boolean)

    # many to many Country<->Currency
    currencies = relationship(
        'Currency', secondary="country_currency", viewonly=True
    )  # , overlaps="currencies")

    def __init__(self, cca2, cca3, name_common, active):
        self.cca2 = cca2
        self.cca3 = cca3
        self.name_common = name_common
        self.active = active

    def __str__(self):
        return f"<Country(id = {self.id}, cca3 = {self.cca3}, \
            cca2 = {self.cca2}, name_common = {self.name_common}, \
            name_common = {self.name_common} \
            active = {self.active}"

    def __repr__(self):
        return f"Country({self.cca2}, {self.cca3}, {self.name_common}, {self.active})"


class Currency(Base):
    __tablename__ = 'currency'

    id = Column(Integer, primary_key=True)
    curr_iso = Column(String(3), unique=True)
    name = Column(String(50))
    symbol = Column(String(25))
    # many to many Country<->Currency
    countries = relationship(
        'Country', secondary='country_currency', viewonly=True
    )  # , overlaps="currencies")

    def __init__(self, curr_iso, name, symbol):
        self.curr_iso = curr_iso
        self.name = name
        self.symbol = symbol

    def __str__(self):
        return f"<Currency(curr_iso = {self.curr_iso}, name = {self.name}"

    def __repr__(self):
        return f"Country({self.curr_iso}, {self.name}, {self.symbol})"


class JsonField(Field):
    def parse_input(self, unparsed_input):
        return json.loads(unparsed_input if unparsed_input != '' else 'null')

    def unparse_input(self, parsed_value):
        return json.dumps(parsed_value)


class CheckedRemoteMethod2(CheckedRemoteMethod):
    def handle_get_or_post(self, request, input_values):
        try:
            return super().handle_get_or_post(request, input_values)
        except AccessRestricted as e:
            raise HTTPForbidden(str(e))


class APIPage(HTML5Page):
    def __init__(self, view):
        super().__init__(view)
        methods = [
            # CheckedRemoteMethod2(
            #         view, 'create_country', self.create_country,
            #         JsonResult(JsonField()), disable_csrf_check=True,
            #         cca3 = Field(),
            #         cca2 = Field(),
            #         name_common = Field(),
            #         curr_iso = Field()
            # ),
            CheckedRemoteMethod2(
                view,
                'delete_country',
                self.delete_country,
                JsonResult(JsonField()),
                disable_csrf_check=True,
                cca=Field(),
            ),
            CheckedRemoteMethod2(
                view,
                'find_country',
                self.find_country,
                JsonResult(JsonField()),
                immutable=True,
                disable_csrf_check=True,
                cca=Field(),
            ),
            CheckedRemoteMethod2(
                view,
                'list_countries',
                self.list_countries,
                JsonResult(JsonField()),
                immutable=True,
                disable_csrf_check=True,
                curr_iso=Field(),
            ),
            CheckedRemoteMethod(
                view,
                'log_in',
                self.log_in,
                JsonResult(JsonField()),
                disable_csrf_check=True,
                user_name=EmailField(),
                password=Field(),
            ),
        ]

        self.add_child(P(view, text='This is the ProdigyHelmsman API. Methods:'))
        self.add_child(Ul(view))
        for method in methods:
            view.add_resource(method)
            self.add_child(Li(view)).add_child(
                P(
                    view,
                    text='%s [%s]: %s'
                    % (method.name, method.http_methods, method.get_url()),
                )
            )

    def can_access_api(self):
        login_session = LoginSession.for_current_session()
        return login_session.is_logged_in()

    # def create_country(self, cca3 = None, cca2 = None, name = None):
    #     Session.add(Country(
    #             cca3 = cca3,
    #             cca2 = cca2,
    #             name_common = name,
    #     ))
    #     return True

    def delete_country(self, cca=None):
        if cca:
            country = None
            if len(cca) == 2:
                country = Session.query(Country).filter_by(cca2=cca).first()
            elif len(cca) == 3:
                country = Session.query(Country).filter_by(cca3=cca).first()
            if country:
                country.active = False
        return {}

    def find_country(self, cca=None):
        # import pdb;pdb.set_trace()
        if len(cca) == 2:
            country = (
                Session.query(Country)
                .filter(Country.cca2 == cca, Country.active == True)
                .first()
            )
        else:
            country = (
                Session.query(Country)
                .filter(Country.cca3 == cca, Country.active == True)
                .first()
            )
        if country:
            return [
                {
                    'cca3': country.cca3,
                    'cca2': country.cca2,
                    'name_common': country.name_common,
                }
            ]
        return []

    def list_countries(self, curr_iso=None):
        countries_data = []
        if curr_iso:
            rows = (
                Session.query(Country, Currency)
                .filter(
                    CountryCurrency.country_id == Country.id,
                    CountryCurrency.currency_id == Currency.id,
                    Currency.curr_iso == curr_iso,
                    Country.active == True,
                )
                .order_by(Country.name_common)
                .all()
            )
        else:
            rows = (
                Session.query(Country, Currency)
                .filter(
                    CountryCurrency.country_id == Country.id,
                    CountryCurrency.currency_id == Currency.id,
                    Country.active == True,
                )
                .order_by(Country.name_common)
                .all()
            )
        for det in rows:
            countries_data.append(
                {
                    'cca3': det.Country.cca3,
                    'cca2': det.Country.cca2,
                    'name_common': det.Country.name_common,
                    'curr_iso': det.Currency.curr_iso,
                }
            )
        return countries_data

    def log_in(self, user_name=None, password=None):
        AccountManagementInterface.for_current_session()
        print(f'logging in with {user_name}[{password}]')
        EmailAndPasswordSystemAccount.log_in(user_name, password, False)
        return self.can_access_api()


class APIUI(UserInterface):
    def assemble(self):
        self.define_view('/api', title='API', page=APIPage.factory())
