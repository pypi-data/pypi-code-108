import json
from reloadly_airtime.airtime.sdk.dto.Response.TransactionBalanceInfo import TransactionBalanceInfo
from reloadly_airtime.airtime.sdk.dto.Response.PinDetail import PinDetail

class TopupTransaction:
    def __init__(self):
        #Unique Id of the transaction
        self.Id = 0
        #Unique Id of the transaction from the mobile operator if available
        self.operatorTransactionId = ''
        #Unique Id of the transaction provided by the user during at transaction request if any
        self.customIdentifier = ''
        #Unique id of the operator the transaction was sent to
        self.operatorId = 0
        #Topup recipient phone number (with country prefix)
        self.recepientPhone = ''
        #Topup recipient email
        self.recepientEmail = ''
        #Topup sender phone number that was provided at transaction request if any
        self.senderPhone = ''
        #ISO 3166-1 alpha-2 country code of topup destination country. See https://www.iso.org/obp/ui/#search
        self.countryCode = ''
        #Name of the mobile operator.
        self.operatorName = ''
        #Topup amount that was requested by sender
        self.requestedAmount = 0.0
        #Discount amount that was applied to the request sender's account balance for this transaction
        self.discount = 0.0
        #ISO-4217 3 letter currency code of discount field. 
        #See https://www.iso.org/iso-4217-currency-codes.html
        self.discountCurrencyCode=''
        #ISO-4217 3 letter currency code of requestedAmount field. 
        #See https://www.iso.org/iso-4217-currency-codes.html
        self.requestedAmountCurrencyCode = ''
        #Amount that was delivered in local currency
        self.deliveredAmount = 0.0
        #ISO-4217 3 letter currency code of deliveredAmount field.
        #See https://www.iso.org/iso-4217-currency-codes.html
        self.deliveredAmountCurrencyCode = ''
        #Time stamp recorded for this transaction
        self.date = None
        #User (you) account balance info after this transaction
        self.balanceInfo = TransactionBalanceInfo()
        #PIN detail info for PIN-based transactions
        self.pinDetail = PinDetail()

