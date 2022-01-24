from src.husamfinance.InstrumentTalib import InstrumentTalib
from copy import deepcopy
import talib
import pandas as pd
import numpy as np
from src.husamfinance.InstrumentSignal import InstrumentSignal

class InstrumentTalibAdvanced(InstrumentTalib):
	def __init__(self,name):
		InstrumentTalib.__init__(self,name)
		self.signals = pd.DataFrame(columns=['Signal Type','Status'])

	def __str__(self):
		return self.signals.to_string()

	def __repr__(self):
		return self.signals

	def getBuyCount(self):
		return self.signals["Status"].value_counts()[InstrumentSignal.BUY]

	def getSellCount(self):
		return self.signals["Status"].value_counts()[InstrumentSignal.SELL]

	def getNeutralCount(self):
		return self.signals["Status"].value_counts()[InstrumentSignal.NEUTRAL]

	def getSignals(self):
		return self.signals

	def addSignal(self , signalType , signalStatus):
		self.signals = self.signals.append({'Signal Type': signalType,'Status' : signalStatus} , ignore_index=True)

	def trendline(self , columnName, order=1):
		data = self.getColumn(columnName).copy(deep = True)
		data.dropna(inplace=True)
		new_index = [i for i in range(data.size)]
		data.index = new_index

		coeffs = np.polyfit(data.index.values, list(data), order)
		slope = coeffs[-2]
		return float(slope)


	def BB_signal(self):
		if "BBUpper" not in self.getData():
			self.appendBB(14)

		if self.getColumn("Close")[-1] < self.getColumn("BBLower")[-1]:
			self.addSignal("BB" , InstrumentSignal.BUY)
		elif self.getColumn("Close")[-1] > self.getColumn("BBUpper")[-1]:
			self.addSignal("BB" , InstrumentSignal.SELL)
		elif self.getColumn("Close")[-1] > self.getColumn("BBLower")[-1] and self.getColumn("Close")[-1] < self.getColumn("BBUpper")[-1]:
			self.addSignal("BB" , InstrumentSignal.NEUTRAL)
		else:
			self.addSignal("BB" , InstrumentSignal.NULL)

	def HT_signal(self):
		pass
	def KAMA_signal(self):
		if "KAMA" not in self.getData():
			self.appendKAMA(14)		

		if self.trendline("KAMA") > 0:
			self.addSignal("KAMA" , InstrumentSignal.BUY)
		elif self.trendline("KAMA") < 0:
			self.addSignal("KAMA" , InstrumentSignal.SELL)
		elif self.trendline("KAMA") == 0:
			self.addSignal("KAMA" , InstrumentSignal.NEUTRAL)
		else:
			self.addSignal("KAMA" , InstrumentSignal.NULL)

	def SAR_signal(self):
		if "SAR" not in self.getData():
			self.appendSAR()

		if self.getColumn("SAR")[-1] < self.getColumn("Close")[-1]:
			self.addSignal("SAR" , InstrumentSignal.BUY)
		elif self.getColumn("SAR")[-1] > self.getColumn("Close")[-1]:
			self.addSignal("SAR" , InstrumentSignal.SELL)
		elif self.getColumn("SAR")[-1] == self.getColumn("Close")[-1]:
			self.addSignal("SAR" , InstrumentSignal.NEUTRAL)
		else:
			self.addSignal("SAR" , InstrumentSignal.NULL)


	def RSI_signal(self):
		if  "RSI" not in self.getData():
			self.appendRSI(14)

		if self.getColumn("RSI")[-1] <= 30 :
			self.addSignal("RSI" , InstrumentSignal.BUY)
		elif self.getColumn("RSI")[-1] >= 70:
			self.addSignal("RSI" , InstrumentSignal.SELL)
		elif self.getColumn("RSI")[-1] > 30 and self.getColumn("RSI")[-1] < 70:
			self.addSignal("RSI" , InstrumentSignal.NEUTRAL)
		else:
			self.addSignal("RSI" , InstrumentSignal.NULL)

	def MACD_signal(self):
		if "MACD" not in self.getData():
			self.appendMACD()

		if self.getColumn("MACD_Hist")[-1] > 0:
			self.addSignal("MACD",InstrumentSignal.BUY)
		elif self.getColumn("MACD_Hist")[-1] < 0:
			self.addSignal("MACD",InstrumentSignal.SELL)
		elif self.getColumn("MACD_Hist")[-1] == 0:
			self.addSignal("MACD",InstrumentSignal.SELL)
		else:
			self.addSignal("MACD" , InstrumentSignal.NULL)

	def ADX_signal(self):
		if "ADX" not in self.getData():
			self.appendADX(14)

		if self.getColumn("ADX")[-1] > 25 :
			self.addSignal("ADX" , InstrumentSignal.BUY)
		elif self.getColumn("ADX")[-1] < 20 :
			self.addSignal("ADX" , InstrumentSignal.SELL)
		elif self.getColumn("ADX")[-1] < 25 and self.getColumn("ADX")[-1] > 20:
			self.addSignal("ADX" , InstrumentSignal.NEUTRAL)
		else:
			self.addSignal("ADX" , InstrumentSignal.NULL)


