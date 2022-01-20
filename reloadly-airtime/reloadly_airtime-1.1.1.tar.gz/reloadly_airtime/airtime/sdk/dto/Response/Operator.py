import json
from reloadly_airtime.airtime.sdk.dto.Response.SimplifiedCountry import SimplifiedCountry
from reloadly_airtime.airtime.sdk.enums.DenominationType import DenominationType
from reloadly_airtime.airtime.sdk.dto.Response.FxRate import FxRate

#Class that represents a Reloadly airtime operator object. Related to the {@link OperatorOperations}
class Operator:
    def __init__(self):
        #Unique id assign to each operator.
        self.Id = 0
        #Name of the mobile operator.
        self.name = ''
        #Whether the mobile operator is a prepaid data bundle. Prepaid bundles are a mixture of calls, data,
        #SMS and social media access which the users can purchase other than airtime credits
        self.bundle = False
        #Whether the operator is a prepaid data only
        self.data = False
        #Whether the operator is pin based
        self.pinBased = False
        #Whether the operator supports local amounts
        self.supportsLocalAmounts = False
        #Operator amount denomination type
        self.denominationType = DenominationType()
        #ISO-3 currency code of user account
        self.senderCurrencyCode = ''
        #User account currency symbol
        self.senderCurrencySymbol = ''
        #ISO-3 currency code of operator destination country
        self.destinationCurrencyCode = ''
        #Destination currency symbol
        self.destinationCurrencySymbol = ''
        #International discount assigned for this operator
        self.internationalDiscount = 0.0
        #Local discount assigned for this operator
        self.localDiscount = 0.0
        #Most popular international amount for this operator
        self.mostPopularInternationalAmount = 0.0
        #Most popular local amount for this operator
        self.mostPopularLocalAmount = 0.0
        #Operator's country
        self.country = SimplifiedCountry()
        #Current fx rate for this operator
        self.fxrate = FxRate()
        #Suggested whole amounts when denomination type is 'FIXED'
        self.suggestedAmounts = None
        #Suggested amounts map containing (amount in sender currency, amount in recipient currency)
        #when denomination type is 'FIXED'
        self.suggestedAmountsMap = None
        #Minimum amount when denomination type is 'RANGE' will be empty/null for 'FIXED' denomination type
        self.minAmount = 0.0
        #Maximum amount when denomination type is 'RANGE', will be empty/null for 'FIXED' denomination type
        self.localMinAmount = 0.0
        #Minimum local amount when denomination type is 'RANGE', will be empty/null for 'FIXED' 
        #denomination type
        self.localMaxAmount = 0.0
        #Maximum local amount when denomination type is 'RANGE', will be empty/null for 'FIXED' denomination
        self.maxAmount = 0.0
        #Available operator amounts when denomination type is 'FIXED', will be empty/null for 'RANGE 
        #denomination type
        self.fixedAmounts = None
        #Available operator local amounts when denomination type is 'FIXED', will be empty/null for 'RANGE 
        #denomination type
        self.localFixedAmounts = None
        #International fixed amounts descriptions
        self.fixedAmountsDescriptions = None
        #Local fixed amounts descriptions
        self.localFixedAmountsDescriptions=None
        #Logo url of the mobile operator
        self.logoUrls = None
        #Available promotions for this operator if any
        self.promotions = None



        


