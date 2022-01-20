from datetime import datetime



class AccountBalanceInfo:
    def __init__(self, accountBalance):
        #Current account balance amount
        self.amount = accountBalance["balance"]
        #Account currency name for the given currency code, example "United States Dollar"
        self.currencyName = accountBalance["currencyName"]
        #Account ISO-4217 3 letter currency code. See https://www.iso.org/iso-4217-currency-codes.html.
        #Example : USD
        self.currencyCode = accountBalance["currencyCode"]
        #Account balance last updated date
        self.updatedAt = accountBalance["updatedAt"]





