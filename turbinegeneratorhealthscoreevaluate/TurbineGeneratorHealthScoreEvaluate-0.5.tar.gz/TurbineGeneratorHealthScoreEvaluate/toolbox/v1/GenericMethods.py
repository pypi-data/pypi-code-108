import numpy as np
from time import mktime, strptime
from multiprocessing import Process


def localOutlierFilter(rawData: list, coef=1.5) -> list:
	"""
	离群点清洗，使用IQR原则
	:param rawData: list[float],需要进行离群点过滤的原始数据
	:param coef: IQR系数,默认1.5
	:return: list
	"""
	Q3 = np.quantile(rawData, 0.75)
	Q1 = np.quantile(rawData, 0.25)
	IQR = Q3 - Q1
	locs1 = np.where(np.asarray(rawData) <= (Q1 - coef * IQR), 0, 1) + np.where(
		np.asarray(rawData) >= (Q3 + coef * IQR), 0, 1)
	locs2 = locs1 == 2
	if len(np.asarray(rawData)[locs2].tolist()) != 0:
		return np.asarray(rawData)[locs2].tolist()
	else:
		return rawData


def formatTimestampTransfer2Int(formatTimestampStr: list, format="%Y-%m-%d %H:%M:%S") -> list:
	"""
	根据指定的格式，将格式化的时间戳转换为unixTimestamp列表

	:param formatTimestampStr: list[str], 符合format参数格式的时间戳列表
	:param format: str, "%Y-%m-%d %H:%M:%S"
	:return: list[int],unixTime列表
	"""
	res = []
	for item in formatTimestampStr:
		res.append(int(mktime(strptime(str(item), format))))
	return res

def progressiveLocalMaximumValueFilter(rawData: list, filteredSampleMaximumQuant=20):
	"""
	渐进式局部最大值过滤

	:param rawData: 需要进行最值过滤的数据集
	:param filteredSampleMaximumQuant: 过滤出的最值数量不应该超过此数目
	:return: None
	"""
	filteredLocalMaxmumSamples = []  # 筛选出的局部最大值样本
	CENTROID_SHIFT_INDEX_THRESHOLD = 0.1**5  # 质心滑动距离(门限值)
	LOF_COEF = 1.5  # LOF系数(初始值)
	_centroidShiftIndex = 10**5  # 质心滑动距离(初始值)
	_filteredSampleQuant = 10**5  # 筛出样本数量,此处指筛出的局部极大值点数量(初始值),每次筛出的数量不宜过多
	_data = rawData
	while (_centroidShiftIndex >= CENTROID_SHIFT_INDEX_THRESHOLD) and (_filteredSampleQuant>=filteredSampleMaximumQuant):
		_oldAvg = np.average(_data)
		i = 0
		_filteredData = []
		while (len(_data) - len(_filteredData)) >= filteredSampleMaximumQuant:
			_filteredData = localOutlierFilter(_data, coef=LOF_COEF*1.1**i)
			i += 1
		_newAvg = np.average(_filteredData)
		_filteredSampleQuant = len(list(set(_data).difference(set(_filteredData))))
		filteredLocalMaxmumSamples = filteredLocalMaxmumSamples + list(set(_data).difference(set(_filteredData)))
		_data = _filteredData
		_centroidShiftIndex = np.abs(_newAvg - _oldAvg)
	return list(filteredLocalMaxmumSamples)

import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

class cruiserLocalMaximumValueFilter:
	def __init__(self, rawData: list):
		self._maxCruiseDistance = max(np.around(len(rawData) / 5).astype(int), 1)
		_scaler = MinMaxScaler(feature_range=(0, 1))
		self._rawData_std = list(_scaler.fit_transform(np.array(rawData).reshape(-1, 1)).flatten())
		self._cruisersLocs = self.__initCruises(self._rawData_std)

		# plt.subplot(311)
		# plt.hist(rawData, bins=200)
		# plt.subplot(323)
		# plt.hist(self._cruisersLocs, bins=50)
		self.__cruise(shiftGradientThreshold=1, shiftTimesEachCruiserThreshold=20)
		# plt.subplot(324)
		# plt.hist(self._cruisersLocs, bins=50)
		# plt.subplot(313)
		# plt.plot(np.asarray(rawData)[self._cruisersLocs])
		# plt.show()

		self.filteredData = np.asarray(rawData)[self._cruisersLocs]


	@staticmethod
	def __initCruises(_data)->list:
		seedsQuant = len(_data) * 5
		return list(map(lambda x: np.around(x).astype(int), list((np.random.rand(1, seedsQuant) * len(_data)).flatten())))


	def __cruise(self, shiftGradientThreshold, shiftTimesEachCruiserThreshold, _maxTries=30):
		global _cruiserLoc
		__cruisersTotalHeight = self.__cruisersTotalHeightCal()
		_shiftGradient = 10
		_shiftTimes = 0
		__locsCruiserNotToGo = []
		while (_shiftGradient >= shiftGradientThreshold) and (_shiftTimes<=shiftTimesEachCruiserThreshold):
			_sectionStart = 0
			_sectionEnd = len(self._cruisersLocs)
			for i in np.arange(_sectionStart, _sectionEnd):
				try:
					_cruiserLoc = self._cruisersLocs[i]
					_randomSeed = np.random.randint(-self._maxCruiseDistance, self._maxCruiseDistance)
					_tries = 0
					_historyLocs = []
					_historyValues = []
					while (self._rawData_std[min(max(_cruiserLoc + _randomSeed, 0), len(self._rawData_std) - 1)] <
						   self._rawData_std[_cruiserLoc - 1]) and (_tries < _maxTries):
						_historyLocs.append(min(max(_cruiserLoc + _randomSeed, 0), len(self._rawData_std) - 1))
						_historyValues.append(
							self._rawData_std[min(max(_cruiserLoc + _randomSeed, 0), len(self._rawData_std) - 1)])
						_randomSeed = np.random.randint(-self._maxCruiseDistance, self._maxCruiseDistance)
						_tries += 1
					if _tries >= _maxTries:
						_loc = np.where(np.asarray(_historyValues) == max(_historyValues), True, False)
						_latestLoc = self._cruisersLocs[i]
						_newestLoc = np.asarray(_historyLocs)[_loc]
						if _newestLoc not in __locsCruiserNotToGo:
							self._cruisersLocs[i] = list(_newestLoc)[0]
							if _latestLoc!=_newestLoc[0]:
								self._cruisersLocs = np.asarray(self._cruisersLocs)[np.where(np.asarray(self._cruisersLocs)==_latestLoc, False, True)]
								__locsCruiserNotToGo.append(_latestLoc)

					else:
						_newestLoc = min(max(_cruiserLoc + _randomSeed, 0), len(self._rawData_std) - 1)
						_latestLoc = self._cruisersLocs[i]
						self._cruisersLocs[i] = _newestLoc
						self._cruisersLocs = np.asarray(self._cruisersLocs)[np.where(np.asarray(self._cruisersLocs)==_latestLoc, False, True)]
						__locsCruiserNotToGo.append(_latestLoc)
				except Exception as e:
					pass
			_shiftTimes += 1
			_shiftGradient = self.__cruisersTotalHeightCal()

	def __cruisersTotalHeightCal(self):
		return sum(np.asarray(self._rawData_std)[np.subtract(self._cruisersLocs, 1)])
