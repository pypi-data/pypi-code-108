# -*- coding: utf-8 -*-
"""
@author: Uwe Ziegenhagen, ziegenhagen@gmail.com

"""


# load the module
from PyQifParser import PyQifParser

#initialize the Parser
P = PyQifParser(r'C:\Users\Uwe\Nextcloud\QIF-Parser\Quicken_h.QIF')

# parse the file
P.parse()

# create a dataframe with the transactions
df = P.get_transactions()

# save the transactions in a pickle object
P.transactions_to_pickle('R:/test.pkl')

# export transactions, etc to several tabs in an Excel-sheet
P.to_excel('r:/export.xlsx')

P.to_beancount('r:/beancount.txt')
