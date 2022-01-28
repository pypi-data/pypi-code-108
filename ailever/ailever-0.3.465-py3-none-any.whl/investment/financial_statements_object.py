from abc import *

class Balance(metaclass=ABCMeta):
    def __init__(self):
        pass



class Income(metaclass=ABCMeta):
    def __init__(self):
        self.sales_revenue = None
        self.COGS = None # cost of goods sold
        self.gross_profit = self.gross_margin()

        self.operating_expenses = None
        self.operating_profit = self.operating_income() # SG&A

        self.non_operating_revenue = None
        self.non_operating_expense = None
        self.non_operating_profit = self.non_operating_income()
        self.EBIT = self.earning_before_interests_and_taxes() # EBIT
        
        self.financial_income = None
        self.financial_expense = None
        self.IBIE = self.income_before_interest_expense()
        self.EBT = self.earnings_before_income_taxes()

        self.income_taxes = None
        self.net_income = self.net_earning()

    def gross_margin(self):
        return self.sales_revenue - self.COGS
    
    def operating_income(self):
        return self.gross_profit - self.operating_expenses
    
    def non_operating_income(self):
        return self.non_operating_revenue - self.non_operating_expense

    def earning_before_interests_and_taxes(self):
        return self.operating_profit + self.non_operating_profit
   
    def income_before_interest_expense(self):
        return self.EBIT + self.financial_income

    def earnings_before_income_taxes(self):
        return self.IBIE - self.financial_expense

    def net_earning(self):
        return income_before_taxes - self.income_taxes



class CashFlow(metaclass=ABCMeta):
    def __init__(self):
        pass



class EquityChange(metaclass=ABCMeta):
    def __init__(self):
        pass



