class DRIVER:
    FREETDS = 'FreeTDS'
    ODBC_17 = 'ODBC+Driver+17+for+SQL+Server'
    NATIVE_11 = 'SQL+Server+Native+Client+11.0'

class Config:
    def __init__(self, host, user, password, db='univer', driver=DRIVER.FREETDS):
        self.host = host
        self.user = user
        self.password = password
        self.db = db
        self.driver = driver