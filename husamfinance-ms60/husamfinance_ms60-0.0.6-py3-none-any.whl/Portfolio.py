from InstrumentAdvanced import InstrumentAdvanced
import pandas as pd

class Portfolio:
	def __init__(self , portfolioName ):
		self.portfolioName = portfolioName
		self.instruments = pd.DataFrame() #stockname , stockdata , stocksignals