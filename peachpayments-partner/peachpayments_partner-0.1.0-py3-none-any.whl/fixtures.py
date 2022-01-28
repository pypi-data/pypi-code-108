"""Fixtures to be used in schemas examples and tests."""

from copy import deepcopy

AMOUNT = "22.50"
CURRENCY = "ZAR"
PAYMENT_BRAND = "PartnerBrand"
UNIQUE_ID = "b4508276b8d146728dac871d6f68b45d"
CONNECTOR_TX_ID = "a4508276a8d146728ddc871d6f68b45d"
TIMESTAMP = "2021-04-23T07:41:25.519947Z"
NOTIFICATION_URL = "https://peachnotify.com"
PAYMENT_TYPE_DEBIT = "DB"
PAYMENT_TYPE_REFUND = "RF"
CODE = "000.000.100"
MERCHANT_TRANSACTION_ID = "test-12345"
CLEARING_INSTITUTE_SESSION_ID = "6262"
EXPIRY_MONTH = "01"
EXPIRY_YEAR = "2030"
HOLDER = "Jane Doe"
SHOPPER_RESULT_URL = "https://peachredirect.com"
CUSTOM_FIELD = {"some key": "some value"}


BROWSER = {
    "acceptHeader": "application/json",
    "language": "EN",
    "screenHeight": "1080",
    "screenWidth": "1920",
    "timezone": "30",
    "userAgent": " Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0",
    "javaEnabled": "false",
    "javascriptEnabled": "true",
    "screenColorDepth": "24",
    "challengeWindow": "01",
}

CUSTOMER = {
    "email": "jane.doe@example.com",
    "fax": "02919392022",
    "givenName": "Jane",
    "surname": "Doe",
    "mobile": "+27610107822",
    "phone": "+27210030000",
    "ip": "1.2.3.4",
    "merchantCustomerLanguage": "EN",
    "status": "NEW",
    "merchantCustomerId": "sxxopjqy",
    "taxId": "4550045030303",
    "taxType": "tax type",
    "birthDate": "1977-07-09",
    "browser": deepcopy(BROWSER),
}
CARD = {"number": "4242424242424242", "expiryMonth": EXPIRY_MONTH, "expiryYear": EXPIRY_YEAR}
DEBIT_REQUEST_CARD = {
    "number": CARD["number"],
    "expiryMonth": EXPIRY_MONTH,
    "expiryYear": EXPIRY_YEAR,
    "cvv": "123",
    "holder": deepcopy(HOLDER),
}
STATUS_RESPONSE_CARD = {
    "bin": "455112",
    "last4Digits": "2315",
    "holder": deepcopy(HOLDER),
    "expiryMonth": EXPIRY_MONTH,
    "expiryYear": EXPIRY_YEAR,
}
DATA = {
    "city": "Cape Town",
    "company": "Company name",
    "country": "ZA",
    "houseNumber1": "25567",
    "postcode": "8001",
    "state": "Nasarawa",
    "street1": "Langtree Lane",
    "street2": "Loe Street",
    "customer": deepcopy(CUSTOMER),
}
RECON = {
    "ciMerchantNumber": "1234581823141",
    "rrn": "1234567899876Test",
    "stan": "928374718193Test",
    "authCode": "90341",
    "resultCode": "200",
}
MANDATE = {
    "dateOfSignature": "2021-07-04",
    "id": "3Kk3RwXveu06keeSJjA5ikZwPbYRRYa3yJ7",
    "reference": "iSsZbu17vtk0BEW1G1ZuFHGpsWJQ1DzM",
}
BANK_ACCOUNT = {
    "holder": "Test Customer",
    "bankName": "Test Bank",
    "number": "0741184112341235",
    "iban": "GB29NWBK60161331926819",
    "bic": "GRAYZAJC",
    "bankCode": "Test1234",
    "country": "ZA",
    "mandate": deepcopy(MANDATE),
    "transactionDueDate": "2021-07-04",
}
CART_ITEM = {
    "name": "Laptop",
    "merchantItemId": "item123",
    "quantity": "125",
    "price": "5.25",
    "description": "Cart item description",
    "weightInKg": "5.25",
    "category": "electronics",
}
CART = {
    "cartItem": deepcopy(CART_ITEM),
    "tax": "20.00",
    "shippingAmount": "12.25",
    "discount": "02.25",
}

RESULT = {"code": CODE}

ERROR_CODE = "800.100.174"
ERROR_RESULT_DETAIL = {"value": "-20.00", "description": "transaction declined (invalid amount)"}
ERROR_RESULT = {"code": ERROR_CODE}

REDIRECT = {
    "url": "https://partner.com/redirect",
    "method": "GET",
    "parameters": [{"name": "any", "value": "format"}],
}


DEBIT_REQUEST = {
    "uniqueId": UNIQUE_ID,
    "configuration": {},
    "amount": AMOUNT,
    "currency": CURRENCY,
    "paymentBrand": PAYMENT_BRAND,
    "paymentType": PAYMENT_TYPE_DEBIT,
    "customer": deepcopy(CUSTOMER),
    "customParameters": deepcopy(CUSTOM_FIELD),
    "merchantName": "Shopping Merchant",
    "merchantTransactionId": MERCHANT_TRANSACTION_ID,
    "merchantInvoiceId": "20170630-4072-00",
    "notificationUrl": NOTIFICATION_URL,
    "shopperResultUrl": SHOPPER_RESULT_URL,
    "card": deepcopy(DEBIT_REQUEST_CARD),
    "billing": deepcopy(DATA),
    "shipping": deepcopy(DATA),
    "cart": deepcopy(CART),
    "clearingInstituteSessionId": CLEARING_INSTITUTE_SESSION_ID,
    "timestamp": TIMESTAMP,
    "some_random_field": "Ready for some unexpected fields",
}
DEBIT_RESPONSE = {
    "uniqueId": UNIQUE_ID,
    "amount": AMOUNT,
    "currency": CURRENCY,
    "paymentBrand": PAYMENT_BRAND,
    "paymentType": PAYMENT_TYPE_DEBIT,
    "result": deepcopy(RESULT),
    "resultDetails": {},
    "redirect": deepcopy(REDIRECT),
    "connectorTxID1": CONNECTOR_TX_ID,
    "clearingInstituteSessionId": CLEARING_INSTITUTE_SESSION_ID,
    "customParameters": deepcopy(CUSTOM_FIELD),
    "timestamp": TIMESTAMP,
}
REFUND_REQUEST = {
    "uniqueId": UNIQUE_ID,
    "configuration": deepcopy(CUSTOM_FIELD),
    "amount": AMOUNT,
    "currency": CURRENCY,
    "paymentBrand": PAYMENT_BRAND,
    "paymentType": PAYMENT_TYPE_REFUND,
    "customer": deepcopy(CUSTOMER),
    "customParameters": deepcopy(CUSTOM_FIELD),
    "notificationUrl": NOTIFICATION_URL,
    "timestamp": TIMESTAMP,
    "some_random_field": "Ready for some unexpected fields",
}
REFUND_RESPONSE = {
    "uniqueId": UNIQUE_ID,
    "amount": AMOUNT,
    "currency": CURRENCY,
    "paymentBrand": PAYMENT_BRAND,
    "paymentType": PAYMENT_TYPE_REFUND,
    "result": {"code": CODE},
    "resultDetails": {},
    "connectorTxID1": CONNECTOR_TX_ID,
    "customParameters": deepcopy(CUSTOM_FIELD),
    "timestamp": TIMESTAMP,
}
STATUS_RESPONSE = {
    "uniqueId": UNIQUE_ID,
    "amount": AMOUNT,
    "currency": CURRENCY,
    "paymentBrand": PAYMENT_BRAND,
    "paymentType": PAYMENT_TYPE_DEBIT,
    "result": deepcopy(RESULT),
    "resultDetails": {},
    "connectorTxID1": CONNECTOR_TX_ID,
    "card": deepcopy(STATUS_RESPONSE_CARD),
    "bankAccount": deepcopy(BANK_ACCOUNT),
    "clearingInstituteSessionId": CLEARING_INSTITUTE_SESSION_ID,
    "recon": deepcopy(RECON),
    "timestamp": TIMESTAMP,
}
WEBHOOK_REQUEST = {
    "uniqueId": UNIQUE_ID,
    "amount": AMOUNT,
    "currency": CURRENCY,
    "paymentBrand": PAYMENT_BRAND,
    "paymentType": "DB",
    "customParameters": deepcopy(CUSTOM_FIELD),
    "clearingInstituteSessionId": "6262",
    "result": {"code": CODE},
    "resultDetails": {},
    "connectorTxID1": CONNECTOR_TX_ID,
    "card": deepcopy(STATUS_RESPONSE_CARD),
    "recon": deepcopy(RECON),
    "bankAccount": deepcopy(BANK_ACCOUNT),
    "timestamp": TIMESTAMP,
    "some_random_field": "Ready for some unexpected fields",
}
PARAMETER_ERRORS = [
    {"value": None, "name": "authenticationValue", "message": "Partner API requires authenticationValue"}
]
ERROR_RESPONSE = {
    "result": deepcopy(ERROR_RESULT),
    "resultDetails": {},
    "timestamp": TIMESTAMP,
}
ERROR_400_RESULT = {
    "code": "700.400.200",
    "parameterErrors": PARAMETER_ERRORS,
}
ERROR_400_RESPONSE = {
    "result": deepcopy(ERROR_400_RESULT),
    "resultDetails": {},
    "timestamp": TIMESTAMP,
}
CANCEL_REQUEST = {
    "notificationUrl": NOTIFICATION_URL,
    "configuration": deepcopy(CUSTOM_FIELD),
    "paymentBrand": PAYMENT_BRAND,
    "timestamp": TIMESTAMP,
    "clearingInstituteSessionId": "6486",
    "merchantTransactionId": MERCHANT_TRANSACTION_ID,
    "customParameters": deepcopy(CUSTOM_FIELD),
    "some_random_field": "Ready for some unexpected fields",
}
CANCEL_RESPONSE = {
    "uniqueId": UNIQUE_ID,
    "paymentBrand": PAYMENT_BRAND,
    "result": {"code": "100.396.101"},
    "connectorTxID1": CONNECTOR_TX_ID,
    "customParameters": deepcopy(CUSTOM_FIELD),
    "resultDetails": {},
    "timestamp": TIMESTAMP,
}

SUCCESS_RESPONSE = {"result": {"code": "000.000.100"}, "timestamp": TIMESTAMP}
