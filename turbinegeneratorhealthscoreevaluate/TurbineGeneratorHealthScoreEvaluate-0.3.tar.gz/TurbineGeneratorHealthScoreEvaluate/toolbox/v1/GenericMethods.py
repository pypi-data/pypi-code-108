import numpy as np
from time import mktime, strptime


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
