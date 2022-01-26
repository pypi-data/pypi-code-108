import numpy as np
import pandas as pd


INFINITESIMAL = 10**-6


class AirCoolerHeatExchangeEfficiency:
	def __init__(self, **kwargs):
		"""
	    对每次输入的、满足波动比例范围限制的视在功率值进行记录,并根据输入的冷热水温度、冷热风温度,计算当前空冷器的热交换效率

	    [1] 参数
	    ----------
	    bufferSize:
	        int,缓存尺寸,默认50
	    floatingRangePercentage:
	        float,波动范围,当新的样本超出该波动范围时,触发清楚缓存并重新记录缓存,默认0.05
	    apparentPowerRecord:
	        list[float],视在功率缓存记录

	    [2] 方法
	    ----------
	    update_and_determine:
	    			更新视在功率缓存数据,并计算冷却器效率指标值

	    [3] 返回
	    -------
	    efficiencyIndex:
	        冷却器效率指标值

	    _apparentPowerRecord:
	        每次迭代时的视在功率缓存,可以在该类初始化时进行指定

	    [4] 示例
	    --------
	    >>> # ===== 数据调用 ===== #
	    >>> databaseName = 'bearing_pad_temper'
	    >>> tableName = '轴承瓦温20200320_20200327_原始数据'
	    >>> host = 'localhost'
	    >>> port = 3306
	    >>> userID = 'root'
	    >>> password = '000000'
	    >>> obj = mysqlOperator(databaseName=databaseName, tableName=tableName, host=host, port=port, userID=userID,
	    >>>                     password=password)
	    >>> content = '发电机励端轴瓦温度,发电机汽端轴瓦温度,发电机9轴承回油温度,发电机10轴承回油温度,发电机励端轴瓦温度,发电机汽端轴瓦温度,发电机9轴承回油温度,发电机10轴承回油温度,有功功率'
	    >>> condition = "(时间戳>=\'2020-03-20 16:00:00\') and (时间戳<=\'2020-03-20 20:00:00\')"
	    >>> data = obj.selectData(content=content, condition=condition)
	    >>> data.columns = ["热风温度1", "热风温度2", "冷风温度1", "冷风温度2", "热水温度1", "热水温度2", "冷水温度1", "冷水温度2", "有功功率"]
	    >>> for item in data:
	    >>> 	if "热" in item:
	    >>> 		data[item] = pd.Series((data[item].values.tolist() + np.random.rand(1, len(data[item]))).flatten())
	    >>>
	    >>> efficiencyIndexRecorder = []
	    >>> windTemperDiffRecorder = []
	    >>> waterTemperDiffRecorder = []
	    >>> apparentPowerRecordCache = []
	    >>> for i in range(len(data)):
	    >>> 	effObj = AirCoolerHeatExchangeEfficiency(apparentPowerRecord=apparentPowerRecordCache)
	    >>> 	effObj.update_and_determine(coldWaterTempers=data[["冷水温度1", "冷水温度2"]].iloc[i, :].tolist(),
	    >>> 	                            warmWaterTempers=data[["热水温度1", "热水温度2"]].iloc[i, :].tolist(),
	    >>> 	                            coldWindTempers=data[["冷风温度1", "冷风温度2"]].iloc[i, :].tolist(),
	    >>> 	                            warmWindTempers=data[["热风温度1", "热风温度2"]].iloc[i, :].tolist(),
	    >>> 	                            apparentPower=data[["有功功率"]].iloc[i, :].values)
	    >>> 	apparentPowerRecordCache = effObj._apparentPowerRecord
	    >>> 	windTemperDiffRecorder.append(effObj._windTemperDiff)
	    >>> 	waterTemperDiffRecorder.append(effObj._waterTemperDiff)
	    >>> 	efficiencyIndexRecorder.append(effObj.efficiencyIndex)
	    >>>
	    >>> plt.plot(windTemperDiffRecorder, "b:")
	    >>> plt.plot(waterTemperDiffRecorder, "g:")
	    >>> plt.twinx()
	    >>> plt.plot(efficiencyIndexRecorder, "r")
	    >>> plt.show()

	    [5] 备注
	    -----
	    * 类属性_apparentPowerRecord可在该类初始化时使用关键字apparentPowerRecord进行指定

	    """
		keys = kwargs.keys()

		self._bufferSize = kwargs["bufferSize"] if "bufferSize" in keys else 50
		self._floatingRangePercentage = kwargs["floatingRangePercentage"] if "floatingRangePercentage" in keys else 0.05
		self._apparentPowerRecord = kwargs["apparentPowerRecord"] if ("apparentPowerRecord" in keys) and (kwargs["apparentPowerRecord"] is not []) else []

		self._coldWaterTempers, self._warmWaterTempers = None, None
		self._coldWindTempers, self._warmWindTempers = None, None
		self._windTemperDiff, self._waterTemperDiff = None, None
		self.efficiencyIndex = None

	def update_and_determine(self, **kwargs):
		"""
		更新视在功率缓存数据,当新视在功率数据样本数值 `AP` 符合当前视在功率缓存 `buffer` 所允许的范围内(±floatingRangePercentage)时,触发对效率指标值 `efficiencyIndex` 的计算:

		:math:`avg(buffer) \\times (1 - floatingRangePercentage) \\leq AP \\leq avg(buffer) \\times (1 + floatingRangePercentage)`

		当新视在功率数据样本数值不符合上述条件限制时,视在功率缓存清除并重新记录

		:math:`T_1 冷热风温差`

		:math:`T_2 冷热水温差`

		:math:`T_m 冷却性能指标量`

		:math:`T_m = \\frac{T_1 - T_2} {ln(T_1 / T_2)}, 当\\frac {T_1}{T_2} > 1.7`

		:math:`T_m = \\frac{T_1 + T_2} {2}, 当\\frac {T_1}{T_2} \\leq 1.7`

		:key coldWaterTempers: list[float],冷水温度
		:key warmWaterTempers: list[float],热水温度
		:key coldWindTempers: list[float],冷风温度
		:key warmWindTempers: list[float],热风温度
		:key apparentPower: float,视在功率
		:return: None
		"""
		self._coldWaterTempers = kwargs["coldWaterTempers"]
		self._warmWaterTempers = kwargs["warmWaterTempers"]
		self._coldWindTempers = kwargs["coldWindTempers"]
		self._warmWindTempers = kwargs["warmWindTempers"]
		_apparentPower = kwargs["apparentPower"]
		_apparentPowerRecordAvg = np.mean(self._apparentPowerRecord) if self._apparentPowerRecord else _apparentPower
		if _apparentPowerRecordAvg*(1-self._floatingRangePercentage)<=_apparentPower<=_apparentPowerRecordAvg*(1+self._floatingRangePercentage):
			self._apparentPowerRecord.append(_apparentPower)
			self._windTemperDiff = np.mean(self._warmWindTempers) - np.mean(self._coldWindTempers)
			self._waterTemperDiff = np.mean(self._warmWaterTempers) - np.mean(self._coldWaterTempers)
			self.__determine()
			if len(self._apparentPowerRecord) >= self._bufferSize:
				self._apparentPowerRecord.pop(0)
		else:
			self._apparentPowerRecord = []
			self._apparentPowerRecord.append(_apparentPower)
			self._windTemperDiff = np.mean(self._warmWindTempers) - np.mean(self._coldWindTempers)
			self._waterTemperDiff = np.mean(self._warmWaterTempers) - np.mean(self._coldWaterTempers)
			self.__determine()

	def __determine(self):
		global INFINITESIMAL

		if self._windTemperDiff / self._waterTemperDiff > 1.7:
			self.efficiencyIndex = (self._windTemperDiff - self._waterTemperDiff) / (np.log(self._windTemperDiff / (self._waterTemperDiff+INFINITESIMAL)) + INFINITESIMAL)
		else:
			self.efficiencyIndex = np.mean([self._windTemperDiff, self._waterTemperDiff])
