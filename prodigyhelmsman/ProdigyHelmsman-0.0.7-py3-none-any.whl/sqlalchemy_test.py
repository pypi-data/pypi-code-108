import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()
ass_country_currency_table = db.Table('association', Base.metadata,
    db.Column('country_cca2', db.ForeignKey('country.cca2')),
    db.Column('currency_curr_iso', db.ForeignKey('currency.curr_iso'))
)


class Country(Base):
    __tablename__ = 'country'

    # id   = Column(Integer, primary_key = True)
    cca2 = db.Column(db.String(2), primary_key = True)
    cca3 = db.Column(db.String(3), unique = True)
    name_common = db.Column(db.String(100))
    curr_iso = db.Column(db.String(3))
    children = relationship(
            "Currency",
            secondary = ass_country_currency_table
    )

    def __str__(self):
        return f"<Country(id = {self.id}, cca3 = {self.cca3}, " \
               f"cca2 = {self.cca2}, name_common = {self.name_common}, " \
               f"curr_iso = {self.curr_iso}"


class Currency(Base):
    __tablename__ = 'currency'

    curr_iso = db.Column(db.String(3), primary_key = True)
    name = db.Column(db.String(50))
    symbol = db.Column(db.String(25))

    def __str__(self):
        return f"<Currency(curr_iso = {self.curr_iso}, name = {self.name}"


class PopulateCountry():
    def __init__(self, p_session) :
        self.session = p_session
        self.test_data = [
        ('ZAF', 'ZA', 'South Africa', 'ZAR'),
        ('USA', 'US', 'United States of America', 'USD'),
        ('GBR', 'GB', 'United Kingdom', 'GBP'),
        ('DER', 'DE', 'Federal Republic of Germany', 'EUR'),
        ('AUS', 'AU', 'Australia', 'AUD'),
    ]

    def add_test_data(self) :
        for country in self.test_data:
            self.session.add(
                    Country(
                            cca3 = country[0],
                            cca2 = country[1],
                            name_common = country[2],
                            curr_iso = country[3]
                    )
            )
        session.commit()
        pass


class PopulateCurrency() :
    def __init__(self, p_session):
        self.session = p_session
        self.test_data = [
        ('ZAR', 'South African rand', 'R'),
        ('USD', 'United States dollar', '$'),
        ('GBP', 'Pound sterling', '£'),
        ('EUR', 'Euro', '€'),
        ('AUD', 'Australian dollar', '$'),
    ]

    def add_test_data(self):
        for currency in self.test_data :
            self.session.add(
                    Currency(
                            curr_iso = currency[0],
                            name = currency[1],
                            symbol = currency[2],
                    )
            )
        pass
        session.commit()


engine = db.create_engine('mysql://TestUser1:1re$UtseT@localhost/t_sqlalchemy', echo=True)
connection = engine.connect()
metadata = db.MetaData(bind=connection)
metadata.tables()
Session = sessionmaker(bind=engine)
session = Session()
metadata.create_all()

pass

# engine = create_engine('sqlite:///:memory:', echo=True)
pop_country = PopulateCountry(session).add_test_data()
pop_currency = PopulateCurrency(session).add_test_data()
