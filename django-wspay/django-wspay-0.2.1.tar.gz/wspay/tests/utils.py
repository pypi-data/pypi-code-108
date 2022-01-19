TRANSACTION_REPORT = {
    'WsPayOrderId': '96a5f58f-764c-4640-90ea-591280893bff',
    'UniqueTransactionNumber': 46370,
    'Signature': ''.join([
        '719cbb3ea1edb3cde1bf839c39be2be9fc43f96d317f862007b341862e623870110c1e2b27d556394',
        'ae76543d18a10120f6f9ea9753af4086aca036ef75010c1'
    ]),
    'STAN': '38967',
    'ApprovalCode': '961792',
    'ShopID': 'MYSHOP',
    'ShoppingCartID': '1c731772-e407-45f8-b576-7e20b0e8642d',
    'Amount': 78,
    'CurrencyCode': 191,
    'ActionSuccess': '1',
    'Success': '1',
    'Authorized': '1',
    'Completed': '0',
    'Voided': '0',
    'Refunded': '0',
    'PaymentPlan': '0000',
    'Partner': 'Pbz',
    'OnSite': '1',
    'CreditCardName': 'AMEX',
    'CreditCardNumber': '377500*****1007',
    'ECI': '',
    'CustomerFirstName': 'John',
    'CustomerLastName': 'Doe',
    'CustomerAddress': 'Street address 10',
    'CustomerCity': 'City',
    'CustomerCountry': 'HR',
    'CustomerPhone': '0911111111111111',
    'CustomerZIP': '51000',
    'CustomerEmail': 'john@doe.com',
    'TransactionDateTime': '20200423102457',
    'IsLessThen30DaysFromTransaction': True,
    'CanBeCompleted': True,
    'CanBeVoided': True,
    'CanBeRefunded': False,
    'Token': '09bf3d95-7a57-43f3-873a-216467a39925',
    'TokenNumber': '1007',
    'ExpirationDate': '2006'
}


def secret_key():
    """Resolve secret key setting."""
    return 'MojSecret'
