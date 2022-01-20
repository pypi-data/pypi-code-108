import json

class TransactionBalanceInfo:
    def __init__(self):
        #Account balance prior to the transaction
        self.previousBalance = 0.0
        #Current account balance amount
        self.currentBalance = 0.0
        #Account ISO-4217 3 letter currency code. See https://www.iso.org/iso-4217-currency-codes.html.
        #Example : USD
        self.currencyCode = ''
        #Account currency name for the given currency code, example "United States Dollar"
        self.currencyName = ''
        #Account balance last updated date
        self.updatedAt = None

