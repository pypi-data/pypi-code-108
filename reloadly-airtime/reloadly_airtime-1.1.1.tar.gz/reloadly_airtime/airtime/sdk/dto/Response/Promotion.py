import json

class Promotion:
    def __init__(self):
        #Unique identifier for the given promotion
        self.Id = 0
        #Id of operator to which the promotion applies
        self.operatorId = 0
        #Title of the promotion
        self.title = ''
        #2nd title for the promotion if any
        self.title2 = ''
        #Description of the promotion
        self.description = ''
        #Date on which the promotion starts
        self.denominations = ''
        #Date on which the promotion ends
        self.localDenominations = ''
        #Amounts for which the promotion applies
        self.endDate = None
        #Amounts (in destination country currency) for which the promotion applies
        self.startDate = None

