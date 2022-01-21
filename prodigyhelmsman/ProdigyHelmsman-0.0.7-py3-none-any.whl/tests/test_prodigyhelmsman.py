import json

from reahl.tofu import Fixture, uses
from reahl.tofu.pytestsupport import with_fixtures
from reahl.browsertools.browsertools import Browser
from reahl.sqlalchemysupport import Session
from reahl.domain.systemaccountmodel import EmailAndPasswordSystemAccount
from prodigyhelmsman.prodigyhelmsman import APIUI, Country, Currency, CountryCurrency
from reahl.sqlalchemysupport_dev.fixtures import SqlAlchemyFixture
from reahl.web_dev.fixtures import WebFixture


@uses(web_fixture=WebFixture)
class LoginFixture(Fixture):

    user_email = 'admin@realhelmsman.co.za'
    password = 'topsecret'

    def new_browser(self):
        return Browser(self.web_fixture.new_wsgi_app(site_root=APIUI))

    def new_account(self):
        account = EmailAndPasswordSystemAccount(email=self.user_email)
        Session.add(account)
        account.set_new_password(account.email, self.password)
        account.activate()
        return account


@uses(web_fixture=WebFixture)
class PopulateCountry(Fixture):
    test_data = [
        ('ZAF', 'ZA', 'South Africa', True),
        ('USA', 'US', 'United States of America', True),
        ('GBR', 'GB', 'United Kingdom', True),
        ('DER', 'DE', 'Federal Republic of Germany', True),
        ('AUS', 'AU', 'Australia', True),
        ('LSO', 'LS', 'Lesotho', True),
        ('SWZ', 'SZ', 'Eswatini', True),
    ]
    # INSERT INTO country (cca3, cca2, name_common, active) VALUES('ZAF', 'ZA', 'South Africa', True), ('USA', 'US', 'United States of America', True), ('GBR', 'GB', 'United Kingdom', True), ('DER', 'DE', 'Federal Republic of Germany', True), ('AUS', 'AU', 'Australia', True), ('LSO', 'LS', 'Lesotho', True), ('SWZ', 'SZ', 'Eswatini', True);
    pass

    def add_test_data(self):
        for country in self.test_data:
            Session.add(
                Country(
                    cca3=country[0],
                    cca2=country[1],
                    name_common=country[2],
                    active=country[3],
                )
            )
        pass


@uses(web_fixture=WebFixture)
class PopulateCurrency(Fixture):
    test_data = [
        ('ZAR', 'South African rand', 'R'),
        ('USD', 'United States dollar', '$'),
        ('GBP', 'Pound sterling', '£'),
        ('EUR', 'Euro', '€'),
        ('AUD', 'Australian dollar', '$'),
        ('LSL', 'Lesotho loti', 'l'),
        ('SZL', 'Swazi lilangeni', 'L'),
    ]
    # INSERT INTO currency (curr_iso, nam, symbol) VALUES ('ZAR', 'South African rand', 'R'), ('USD', 'United States dollar', '$'), ('GBP', 'Pound sterling', '£'), ('EUR', 'Euro', '€'), ('AUD', 'Australian dollar', '$'), ('LSL', 'Lesotho loti', 'l'), ('SZL', 'Swazi lilangeni', 'L');

    def add_test_data(self):
        for currency in self.test_data:
            Session.add(
                Currency(
                    curr_iso=currency[0],
                    name=currency[1],
                    symbol=currency[2],
                )
            )
        pass


@uses(web_fixture=WebFixture)
class PopulateCountryCurrency(Fixture):
    test_data = [
        ('ZA', 'ZAR'),
        ('US', 'USD'),
        ('GB', 'GBP'),
        ('DE', 'EUR'),
        ('AU', 'AUD'),
        ('LS', 'ZAR'),
        ('LS', 'LSL'),
        ('SZ', 'ZAR'),
        ('SZ', 'SZL'),
    ]
    # INSERT INTO country_currency (country_id, currency_id) VALUES ((SELECT id FROM country WHERE cca2="ZA"), (SELECT id FROM currency WHERE curr_iso="ZAR")), ((SELECT id FROM country WHERE cca2="US"), (SELECT id FROM currency WHERE curr_iso="USD")), ((SELECT id FROM country WHERE cca2="GB"), (SELECT id FROM currency WHERE curr_iso="GBP")),((SELECT id FROM country WHERE cca2="DE"), (SELECT id FROM currency WHERE curr_iso="EUR")), ((SELECT id FROM country WHERE cca2="AU"), (SELECT id FROM currency WHERE curr_iso="AUD")), ((SELECT id FROM country WHERE cca2="LS"), (SELECT id FROM currency WHERE curr_iso="ZAR")), ((SELECT id FROM country WHERE cca2="LS"), (SELECT id FROM currency WHERE curr_iso="LSL")), ((SELECT id FROM country WHERE cca2="SZ"), (SELECT id FROM currency WHERE curr_iso="ZAR")), ((SELECT id FROM country WHERE cca2="SZ"), (SELECT id FROM currency WHERE curr_iso="SZL"));

    def add_test_data(self):
        for cntry, curr in self.test_data:
            cntry_det = Session.query(Country).filter(Country.cca2 == cntry).first()
            curr_det = Session.query(Currency).filter(Currency.curr_iso == curr).first()
            Session.add(
                CountryCurrency(country_id=cntry_det.id, currency_id=curr_det.id)
            )
            pass
        pass


@with_fixtures(
    SqlAlchemyFixture,
    LoginFixture,
    PopulateCountry,
    PopulateCurrency,
    PopulateCountryCurrency,
)
def demo_setup(
    sql_alchemy_fixture,
    login_fixture,
    country_fixture,
    currency_fixture,
    country_currency_fixture,
):
    sql_alchemy_fixture.commit = True

    login_fixture.new_account()
    country_fixture.add_test_data()
    currency_fixture.add_test_data()
    country_currency_fixture.add_test_data()


@with_fixtures(LoginFixture)
def test_delete_country_none(login_fixture):

    browser = login_fixture.browser
    Session.add(Country(cca3='LSO', cca2='LS', name_common='Lesotho', active=True))
    Session.add(Country(cca3='ZAF', cca2='ZA', name_common='South Africa', active=True))
    browser.post('/api/_delete_country_method', {'cca': ''})
    result = json.loads(browser.last_response.body)
    assert result == {}
    assert browser.last_response.status == '200 OK'
    rec = Session.query(Country).order_by(Country.name_common).all()
    actual = [i.cca2 for i in rec if i.active]
    expected = ['LS', 'ZA']
    assert actual == expected


@with_fixtures(LoginFixture)
def test_delete_country_non_existing(login_fixture):
    
    browser = login_fixture.browser
    Session.add(Country(cca3='LSO', cca2='LS', name_common='Lesotho', active=True))
    Session.add(Country(cca3='ZAF', cca2='ZA', name_common='South Africa', active=True))
    browser.post('/api/_delete_country_method', {'cca': 'ZZZ'})
    result = json.loads(browser.last_response.body)
    assert browser.last_response.status == '200 OK'
    assert result == {}
    rec = Session.query(Country).order_by(Country.name_common).all()
    actual = [i.cca2 for i in rec if i.active]
    expected = ['LS', 'ZA']
    assert actual == expected


@with_fixtures(LoginFixture)
def test_delete_country_existing(login_fixture):
    browser = login_fixture.browser
    Session.add(Country(cca3 = 'LSO', cca2 = 'LS', name_common = 'Lesotho', active = True))
    Session.add(Country(cca3 = 'ZAF', cca2 = 'ZA', name_common = 'South Africa', active = True))
    browser.post('/api/_delete_country_method', {'cca': 'ZAF'})
    result = json.loads(browser.last_response.body)
    assert browser.last_response.status == '200 OK'
    assert result == {}
    rec = Session.query(Country).order_by(Country.name_common).all()
    actual = [i.cca2 for i in rec if i.active]
    expected = ['LS']
    assert actual == expected


@with_fixtures(LoginFixture)
def test_add_country_existing(login_fixture):
    browser = login_fixture.browser
    Session.add(Country(cca3 = 'LSO', cca2 = 'LS', name_common = 'Lesotho', active = True))
    Session.add(Country(cca3 = 'ZAF', cca2 = 'ZA', name_common = 'South Africa', active = False))
    browser.post('/api/_add_country_method', {'cca2': 'ZA', 'cca3': 'ZAF', 'name_common': 'South Africa'})
    result = json.loads(browser.last_response.body)
    assert browser.last_response.status == '200 OK'
    assert result == {}
    rec = Session.query(Country).filter(Country.active == True).order_by(Country.name_common).all()
    actual = [i.cca2 for i in rec if i.active]
    expected = ['LS', 'ZA']
    assert actual == expected


@with_fixtures(LoginFixture)
def test_add_country_new(login_fixture):
    browser = login_fixture.browser
    Session.add(Country(cca3 = 'LSO', cca2 = 'LS', name_common = 'Lesotho', active = True))
    Session.add(Country(cca3 = 'ZAF', cca2 = 'ZA', name_common = 'South Africa', active = True))
    browser.post('/api/_add_country_method', {'cca2': 'RU', 'cca3': 'RUS', 'name_common': 'Russia'})
    result = json.loads(browser.last_response.body)
    assert browser.last_response.status == '200 OK'
    assert result == {}
    rec = Session.query(Country).order_by(Country.name_common).all()
    actual = [i.cca2 for i in rec if i.active]
    expected = ['LS', 'RU', 'ZA']
    assert actual == expected


@with_fixtures(LoginFixture, PopulateCountry)
def test_find_country(login_fixture, country_fixture):

    browser = login_fixture.browser

    country_fixture.add_test_data()
    browser.open('/api/_find_country_method?cca=ZAF')
    result = json.loads(browser.last_response.body)
    assert result == [{'cca3': 'ZAF', 'cca2': 'ZA', 'name_common': 'South Africa'}]

    browser.open('/api/_find_country_method?cca=ZA')
    result = json.loads(browser.last_response.body)
    assert result == [{'cca3': 'ZAF', 'cca2': 'ZA', 'name_common': 'South Africa'}]

    browser.open('/api/_find_country_method?cca=South Africa')
    result = json.loads(browser.last_response.body)
    assert result == []


@with_fixtures(LoginFixture)
def test_list_countries(login_fixture):

    browser = login_fixture.browser

    browser.open('/api/_list_countries_method')
    result = json.loads(browser.last_response.body)
    assert result == []

    Session.add(Country(cca3='LSO', cca2='LS', name_common='Lesotho', active=True))
    Session.add(Currency(curr_iso='ZAR', name='South African rand', symbol='R'))
    Session.add(Currency(curr_iso='LSL', name='Lesotho loti', symbol='L'))

    cntry_det = Session.query(Country).filter(Country.cca2 == 'LS').first()
    curr_det = Session.query(Currency).filter(Currency.curr_iso == 'ZAR').first()
    Session.add(CountryCurrency(country_id=cntry_det.id, currency_id=curr_det.id))

    browser.open('/api/_list_countries_method')
    result = json.loads(browser.last_response.body)
    assert result == [
        {'cca3': 'LSO', 'cca2': 'LS', 'name_common': 'Lesotho', 'curr_iso': 'ZAR'},
    ]

    curr_det = Session.query(Currency).filter(Currency.curr_iso == 'LSL').first()
    Session.add(CountryCurrency(country_id=cntry_det.id, currency_id=curr_det.id))

    browser.open('/api/_list_countries_method')
    result = json.loads(browser.last_response.body)
    assert result == [
        {'cca3': 'LSO', 'cca2': 'LS', 'name_common': 'Lesotho', 'curr_iso': 'ZAR'},
        {'cca3': 'LSO', 'cca2': 'LS', 'name_common': 'Lesotho', 'curr_iso': 'LSL'},
    ]

    browser.open('/api/_list_countries_method?curr_iso=LSL')
    result = json.loads(browser.last_response.body)
    assert result == [
        {'cca3': 'LSO', 'cca2': 'LS', 'name_common': 'Lesotho', 'curr_iso': 'LSL'}
    ]

    browser.open('/api/_list_countries_method?curr_iso=ZZZ')
    result = json.loads(browser.last_response.body)
    assert result == []


@with_fixtures(LoginFixture)
def test_logging_in(login_fixture):
    browser = login_fixture.browser

    browser.open('/api')
    browser.view_source()  # Prints out a list of available remote methods, what HTTP method to use when calling them, and their URL

    browser.post(
        '/api/_log_in_method',
        {'user_name': login_fixture.account.email, 'password': login_fixture.password},
    )
    assert browser.last_response.status == '200 OK'
    result = json.loads(browser.last_response.body)
    assert result is True
