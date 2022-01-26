import numpy as np


INFINITESIMAL = 0.1**6


class CoolerPerformance:
	def __init__(self, **kwargs):
		"""
	    根据输入的冷却器油温、水温,计算冷却器性能指标值

	    [1] 参数
	    ----------
	    oilTempers:
	        list[float], 油温数组
	    coldWaterTemper:
	        list[float], 冷水温度数组
	    warmWaterTemper:
	        list[float], 热水温度数组

	    [2] 返回
	    -------
	    coolerPerformance:
	        冷却器性能指标值

	    [3] 示例
	    --------
	    >>>  # ===== 数据调用 ===== #
	    >>>  databaseName = 'bearing_pad_temper'
	    >>>  tableName = '轴承瓦温20200320_20200327_原始数据'
	    >>>  host = 'localhost'
	    >>>  port = 3306
	    >>>  userID = 'root'
	    >>>  password = '000000'
	    >>>  obj = mysqlOperator(databaseName=databaseName, tableName=tableName, host=host, port=port, userID=userID,
	    >>>                      password=password)
	    >>>  content = '发电机励端轴瓦温度,发电机汽端轴瓦温度,发电机9轴承回油温度,发电机10轴承回油温度,发电机励端轴瓦温度,发电机汽端轴瓦温度,发电机9轴承回油温度,发电机10轴承回油温度'
	    >>>  condition = "(时间戳>=\'2020-03-20 16:00:00\') and (时间戳<=\'2020-03-20 20:00:00\')"
	    >>>  data = obj.selectData(content=content, condition=condition)
	    >>>  data.columns = ["冷油温度1", "冷油温度2", "热油温度1", "热油温度2", "热水温度1", "热水温度2", "冷水温度1", "冷水温度2"]
	    >>>  performanceRecord = []
	    >>>  for i in range(len(data)):
	    >>>  	_data = data.iloc[i, :]
	    >>>  	perfObj = CoolerPerformance(oilTempers=data.iloc[i, 0:4].tolist(),
	    >>>  	                            warmWaterTemper=list(map(lambda x: x * 1.003, data.iloc[i, 4:6].tolist())),
	    >>>  	                            coldWaterTemper=data.iloc[i, 4:6].tolist())
	    >>>  	performanceRecord.append(perfObj.coolerPerformance)
	    >>>  plt.plot(performanceRecord)
	    >>>  plt.show()
	    """

		keys = kwargs.keys()
		self._oilTempers = kwargs["oilTempers"] if "oilTempers" in keys else []
		self._coldWaterTemper = kwargs["coldWaterTemper"] if "coldWaterTemper" in keys else []
		self._warmWaterTemper = kwargs["warmWaterTemper"] if "warmWaterTemper" in keys else []
		if self._oilTempers is not []:
			self.__oilTemperDiff = max(self._oilTempers) - min(self._oilTempers)
		else:
			self.__oilTemperDiff = 0
		if (self._coldWaterTemper is not []) and (self._warmWaterTemper is not []):
			self.__waterTemperDiff = np.mean(self._warmWaterTemper) - np.mean(self._coldWaterTemper)
		else:
			self.__waterTemperDiff = 0
		self.coolerPerformance = self.__performanceCal()

	def __performanceCal(self):
		"""
		冷却器冷却性能指标计算

		:math:`T_热油 = max(T_油温)`

		:math:`T_冷油 = min(T_油温)`

		:math:`T_1 = T_热油 - T_冷油`

		:math:`T_2 = avg( T_热水温 ) - avg( T_冷水温 )`

		当 :math:`T_1/T_2 > 1.7`, :math:`T_m = (T_1 - T_2) / ln( T_1 / T_2 )`

		当 :math:`T_1/T_2 \\leq 1.7`, :math:`T_m = avg(T_1 + T_2)`

		"""
		global INFINITESIMAL

		if self.__oilTemperDiff/self.__waterTemperDiff > 1.7:
			return (self.__oilTemperDiff - self.__waterTemperDiff) / (np.log(self.__oilTemperDiff/(self.__waterTemperDiff+INFINITESIMAL)) + INFINITESIMAL)
		else:
			return np.mean([self.__oilTemperDiff, self.__waterTemperDiff])
