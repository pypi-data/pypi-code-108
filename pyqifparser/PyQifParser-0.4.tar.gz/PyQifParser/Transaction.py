# -*- coding: utf-8 -*-
"""

@author: Uwe Ziegenhagen, ziegenhagen@gmail.com
"""

class Transaction():
    """
        A single transaction
    """

    def __init__(self):
        """
            Initializes an empty transaction
        """
        self.clear()

    def clear(self):
        """
            resets the transaction
        """
        self.__amount = None
        self.__date = None
        self.__cleared = None
        self.__reference = None
        self.__payee = None
        self.__description = None
        self.__category = None
        self.__class = None

    @property
    def date(self):
        """
            returns the date for this transaction
        """
        return self.__date

    @date.setter
    def date(self, date):
        self.__date = date

    @property
    def amount(self):
        """
            returns the amount for the transaction (field 'T')
        """
        return self.__amount

    @amount.setter
    def amount(self, amount=1):
        try:
            self.__amount = float(amount.replace(',', ''))
        except ValueError:
            print(amount)

    @property
    def cleared(self):
        """
            returns the value of the cleared flag as string (field 'C')
        """
        return self.__cleared

    @cleared.setter
    def cleared(self, cleared):
        self.__cleared = cleared

    @property
    def reference(self):
        """
            returns the numerical reference, field 'N'
        """
        return self.__reference

    @reference.setter
    def reference(self, reference):
        self.__reference = reference

    @property
    def payee(self):
        """
            returns the counterparty, as provided by field 'P'
        """
        return self.__payee

    @payee.setter
    def payee(self, name):
        self.__payee = name

    @property
    def description(self):
        """
            returns the description, as provided by field 'M'
        """
        return self.__description

    @description.setter
    def description(self, text):
        self.__description = text

    @property
    def category(self):
        """
            returns the category, field 'L'
        """
        return self.__category

    @category.setter
    def category(self, text):
        self.__category = text

    @property
    def qclass(self):
        """
            returns the class, field ''
        """
        return self.qclass

    @qclass.setter
    def qclass(self, text):
        self.__qclass = text





if __name__ == "__main__":
    """
        Some test code
    """
    t = Transaction()
    t.date = '22.02.2020'
    t.amount = "1"
    print(t.date, t.amount)

    u = Transaction()
    u.date = '11.1.1900'
    u.amount = "2"
    u.clear()
    print(u.date, u.amount) # None, None
    