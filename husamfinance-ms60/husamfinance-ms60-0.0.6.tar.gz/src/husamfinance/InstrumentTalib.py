from src.husamfinance.Instrument import Instrument
from copy import deepcopy
import talib

class InstrumentTalib(Instrument):
	def __init__(self,name):
		Instrument.__init__(self,name)

	# OVERLAP FUNCTIONS

	def appendBB(self , t_period):
		upperband, middleband, lowerband = talib.BBANDS(self.getColumn("Close"), timeperiod= t_period, nbdevup=2, nbdevdn=2, matype=0)
		self.addColumn("BBUpper" , upperband ) 
		self.addColumn("BBMid" , middleband ) 
		self.addColumn("BBLower" , lowerband) 

	def appendMA(self , t_period):
		self.addColumn("MA" , talib.MA(self.getColumn("Close"), timeperiod = t_period , matype = 0 ) )

	def appendEMA(self , t_period):
		self.addColumn("EMA" , talib.EMA(self.getColumn("Close"), timeperiod = t_period ) ) 

	def appendDEMA(self , t_period):
		self.addColumn("DEMA" , talib.DEMA(self.getColumn("Close"), timeperiod = t_period ) )

	def appendHT(self):
		self.addColumn("HT" , talib.HT_TRENDLINE(self.getColumn("Close") ) )

	def appendKAMA(self , t_period):
		self.addColumn("KAMA" , talib.KAMA(self.getColumn("Close"), timeperiod = t_period ) ) 

	def appendMAMA(self):
		mama, fama = talib.MAMA( self.getColumn("Close") , fastlimit=0, slowlimit=0)
		self.addColumn("MAMA" , mama)
		self.addColumn("FAMA" , fama)

	def appendMAVP(self):
		pass

	def appendMIDPOINT(self , t_period):
		self.addColumn("MIDPOINT" , talib.MIDPOINT(self.getColumn("Close") , timeperiod = t_period) ) 

	def appendMIDPRICE(self , t_period):
		self.addColumn("MIDPRICE" , talib.MIDPRICE(self.getColumn("High"), self.getColumn("Low"), timeperiod = t_period ))

	def appendSAR(self):
		'''
		A dot is placed below the price when it is trending upward, and above the price when it is trending downward.
		'''
		self.addColumn("SAR" , talib.SAR(self.getColumn("High") , self.getColumn("Low") ,  acceleration = 0, maximum = 0 ) ) 

	def appendSAREXT(self):
		self.addColumn("SAREXT" , talib.SAREXT(self.getColumn("High") , self.getColumn("Low") , startvalue=0, offsetonreverse=0, accelerationinitlong=0, accelerationlong=0, accelerationmaxlong=0, accelerationinitshort=0, accelerationshort=0, accelerationmaxshort=0) )

	def appendSMA(self , t_period):
		self.addColumn("SMA" , talib.SMA(self.getColumn("Close"), timeperiod=t_period))

	def appendT3(self , t_period):
		self.addColumn("T3" , talib.T3(self.getColumn("Close"), timeperiod=t_period, vfactor=0))

	def appendTEMA(self , t_period):
		self.addColumn("TEMA" , talib.TEMA(self.getColumn("Close"), timeperiod=t_period))

	def appendTRIMA(self , t_period):
		self.addColumn("TRIMA" , talib.TRIMA(self.getColumn("Close"), timeperiod=t_period))

	def appendWMA(self , t_period):
		self.addColumn("WMA" , talib.WMA(self.getColumn("Close"), timeperiod=t_period))

	# VOLUME INDICATOR FUNCTIONS

	def appendAD(self):
		"""
		eger uyusmazlık varsa, AD cizgisinin trendi fiyatin yonunu gosterebilir. 
		"""
		self.addColumn("AD" , talib.AD(self.getColumn("High"), self.getColumn("Low"), self.getColumn("Close"), self.getColumn("Volume")))

	def appendADOSC(self):
		"""
		If the price is rising and AD is falling (negative divergence) can indicate a bearish market
		If the price is falling and AD is rising (positive divergence) can indicate a bullish market
		"""
		self.addColumn("ADOSC" , talib.ADOSC( self.getColumn("High"), self.getColumn("Low"), self.getColumn("Close"), self.getColumn("Volume"), fastperiod=3, slowperiod=10) )

	def appendOBV(self):
		self.addColumn("OBV" , talib.OBV(self.getColumn("Close"), self.getColumn("Volume")))

	# MOMENTUM INDICATOR FUNCTIONS

	def appendADX(self , t_period):
		'''
		The ADX identifies a strong trend when the ADX is over 25 and a weak trend when the ADX is below 20
		'''
		self.addColumn("ADX" , talib.ADX(self.getColumn("High") , self.getColumn("Low") , self.getColumn("Close"), timeperiod=t_period))
		
	def appendADXR(self , t_period):
		self.addColumn("ADXR" , talib.ADXR(self.getColumn("High") , self.getColumn("Low") , self.getColumn("Close"), timeperiod=t_period))
		
	def appendAPO(self):
		self.addColumn("APO" , talib.APO(self.getColumn("Close"), fastperiod=12, slowperiod=26, matype=0))

	def appendAROON(self , t_period):
		aroondown, aroonup = talib.AROON(self.getColumn("High") , self.getColumn("Low"), timeperiod=t_period)
		self.addColumn("AROON_DOWN" , aroondown)
		self.addColumn("AROON_UP" , aroonup)

	def appendAROONOSC(self , t_period):
		self.addColumn("AROONOSC" , talib.AROONOSC(self.getColumn("High") , self.getColumn("Low") , timeperiod=t_period))
		
	def appendBOP(self):
		pass

	def appendCCI(self):
		pass

	def appendCMO(self):
		pass

	def appendDX(self):
		pass

	def appendMACD(self):
		'''
		 If the MACD is above the signal line, the histogram will be above the MACD’s baseline.
		 If the MACD is below its signal line, the histogram will be below the MACD’s baseline.
		 If Histogram above 0 then its bullish , bearish otherwise.
		'''
		macd, macdsignal, macdhist = talib.MACD(self.getColumn("Close"), fastperiod=12, slowperiod=26, signalperiod=9)
		self.addColumn("MACD" , macd)
		self.addColumn("MACD_Signal" , macdsignal)
		self.addColumn("MACD_Hist" , macdhist)

	def appendMACDEXT(self):
		pass

	def appendMACDFIX(self):
		pass

	def appendMFI(self):
		pass

	def appendMINUS_DI(self):
		pass

	def appendMINUS_DM(self):
		pass

	def appendMOM(self):
		pass

	def appendPLUS_DI(self):
		pass

	def appendPLUS_DM(self):
		pass

	def appendPPO(self):
		pass

	def appendROC(self):
		pass

	def appendROCP(self):
		pass

	def appendROCR(self):
		pass

	def appendROCR100(self):
		pass

	def appendRSI(self , t_period):
		'''
		 RSI reading of 70 or above indicate that a security is becoming overbought or overvalued, 
		 30 or below indicates an oversold or undervalued condition.
		 '''
		self.addColumn("RSI" , talib.RSI(self.getColumn("Close"), timeperiod=t_period))

	def appendSTOCH(self):
		pass

	def appendSTOCHF(self):
		pass

	def appendSTOCHRSI(self):
		pass

	def appendTRIX(self):
		pass

	def appendULTOSC(self):
		pass

	def appendWILLR(self):
		pass