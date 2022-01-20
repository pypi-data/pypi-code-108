from datetime import datetime
import reloadly_airtime.airtime as airtime

class Discount:
    def __init__(self):
        self.percentage = 0.0
        self.internationalPercentage = 0.0
        self.localPercentage = 0.0
        self.updatedAt = datetime()
        self.operator = airtime.SimplifiedOperator()

