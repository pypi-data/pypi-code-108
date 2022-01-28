import numpy as np

from GenericMethods import localOutlierFilter
from scipy.optimize import leastsq


LOSS_EACH_EPOCH = 100  # 每次更新数据后，进行迭代拟合前的初始损失值，应当显著大于迭代过程中用以控制退出迭代过程的最小损失限值_fittingLossExitThreshold


class StartingProcessVoltageClimbingStageDetermine:
	def __init__(self, **kwargs):
		"""
		通过对近期数据样本进行缓存，在每次新样本进入后的迭代过程中，先使用IQR的方式进行异常点筛查，后使用线性拟合对当前缓存中的数据求取斜率值，并根据指定的斜率判断当前数据近期的变化状态（不变A/上升B/下降C）

		[1] 参数
		----------
		dataBuffer:
			list[float],数据缓存.通过外部输入,可以在每次迭代过程结束时输出,并在下一次迭代开始前用于类的初始化,默认为None
		fittingLossExitThreshold:
			float,每次更新数据时,退出迭代的最小损失值,默认0.1**6
		lofCoef:
			float,使用IQR进行离群点过滤时的系数,默认 1.5
		minimumBufferSize:
		  int,最小缓存量,当缓存数据少于此限值时,不进行拟合与判断,默认10
		buffSize:
			int,最大缓存量,当缓存数据高于此限值时,缓存数据顺序退出,默认500
		maxEpoch:
			int,最大拟合次数,默认50
		climbingStatusKValueThreshold:
			float,判断当前数据属于上升状态的最小k值,默认0.001
		droppingStatusKValueThreshold:
			float,判断当前数据属于下降状态的最大k值,默认-0.001

		[2] 方法
		----------
		updateSample:
			更新数据样本,并判断当前数据近期的变化状态

		[3] 返回
		----------
		dataBuffer:
			当前数据输入后的数据缓存
		currentSample_loss:
			当前样本输入后，最佳的拟合损失值
		currentSample_kValue:
			当前样本输入后，最佳的拟合损失值的k值
		currentSample_bias:
			当前样本输入后，最佳的拟合损失值的b值
		currentSample_status:
			当前样本输入后，判断出的上升/下降/不变状态

		[4] 示例1
		----------
		>>> databaseName = 'bearing_pad_temper'
		>>> tableName = '轴承瓦温20200320_20200327_原始数据'
		>>> host = 'localhost'
		>>> port = 3306
		>>> userID = 'root'
		>>> password = '000000'
		>>> obj = mysqlOperator(databaseName=databaseName, tableName=tableName, host=host, port=port, userID=userID,
		>>>                     password=password)
		>>> content = '时间戳,发电机励端轴瓦温度'
		>>> condition = "(时间戳>=\'2020-03-20 16:00:00\') and (时间戳<=\'2020-03-20 17:20:00\')"
		>>> data = obj.selectData(content=content, condition=condition)
		>>> timeIntRecord = formatTimestampTransfer2Int(data["时间戳"])
		>>> timeStrRecord = data["时间戳"].tolist()
		>>> dataRecord = data["发电机励端轴瓦温度"].tolist()
		>>> statusRecord = []
		>>> data_bufferCache = None
		>>> for i in range(len(timeIntRecord)):
		>>> 	obj = StartingProcessVoltageClimbingStageDetermine(dataBuffer=data_bufferCache)
		>>> 	# print(f"{i} / {len(timeIntRecord)}")
		>>> 	obj.updateSample(dataRecord[i])
		>>> 	statusRecord.append(obj.currentSample_status)
		>>> 	data_bufferCache = obj.dataBuffer
		>>> 	if len(statusRecord) >= 1:
		>>> 		plt.plot(dataRecord[0:len(statusRecord)])
		>>> 		plt.xticks(np.arange(len(statusRecord)), labels=statusRecord)
		>>> 		plt.pause(0.001)
		>>> 	for item in ['timeIntRecord', 'timeStrRecord', 'dataRecord', 'LOSS_EACH_EPOCH', 'StartingProcessVoltageClimbingStageDetermine', 'statusRecord', 'timestamp_bufferCache', 'data_bufferCache']:
		>>> 		print(f"{sys.getsizeof(locals().get(item))}, ", end="")
		>>> 	print(end='\\n')
		>>> plt.show()

		[5] 备注
		----------
		* 初始化该类时，可以使用dataBuffer传递上次迭代过程的数据缓存dataBuffer
		"""

		keys = kwargs.keys()
		# ===== 输出参数 ===== #
		# 数据缓存，是输出参数、外部参数、内部参数。通过外部输入，可以在每次迭代过程结束时输出，并在下一次迭代开始前用于类的初始化
		self.dataBuffer = kwargs["dataBuffer"] if ("dataBuffer" in keys) and (kwargs["dataBuffer"] is not None) else []
		# 当前样本输入后，最佳的拟合损失值
		self.currentSample_loss = None
		# 当前样本输入后，最佳的拟合损失值的k值
		self.currentSample_kValue = None
		# 当前样本输入后，最佳的拟合损失值的b值
		self.currentSample_bias = None
		# 当前样本输入后，判断出的上升/下降/不变状态
		self.currentSample_status = "-"
		# ===== 外部参数 ===== #
		# 每次更新数据时，退出迭代的最小损失值
		self._fittingLossExitThreshold = kwargs["fittingLossExitThreshold"] if "fittingLossExitThreshold" in keys else 0.1**6
		# 使用IQR进行离群点过滤时的系数
		self._lofCoef = kwargs["lofCoef"] if "lofCoef" in keys else 1.5
		# 最小缓存量，当缓存数据少于此限值时，不进行拟合与判断
		self._minimumBufferSize = kwargs["minimumBufferSize"] if "minimumBufferSize" in keys else 10
		# 最大缓存量，当缓存数据高于此限值时，缓存数据顺序退出
		self._buffSize = kwargs["bufferSize"] if "bufferSize" in keys else 500
		# 最大拟合次数
		self._maxEpoch = kwargs["maxEpoch"] if "maxEpoch" in keys else 50
		# 判断当前数据属于上升状态的最小k值
		self._climbingStatusKValueThreshold = kwargs["climbingStatusKValueThreshold"] if "climbingStatusKValueThreshold" in keys else 0.001
		# 判断当前数据属于下降状态的最大k值
		self._droppingStatusKValueThreshold = kwargs["droppingStatusKValueThreshold"] if "droppingStatusKValueThreshold" in keys else -0.001

	def updateSample(self, _newData):
		"""
		更新数据样本，并判断当前数据近期的变化状态

		:param _newData: 需要更新至缓存进行趋势判断的新数值
		:type _newData: float
		:return: None
		"""
		global LOSS_EACH_EPOCH  # 每次更新数据后，进行迭代拟合前的初始损失值，应当显著大于迭代过程中用以控制退出迭代过程的最小损失限值_fittingLossExitThreshold

		self.dataBuffer.append(_newData)

		self.dataBuffer.pop(0) if len(self.dataBuffer) > self._buffSize else None

		if len(self.dataBuffer) >= self._minimumBufferSize:
			dataBufferFiltered = localOutlierFilter(self.dataBuffer, coef=self._lofCoef)
			_y = dataBufferFiltered
			_x = np.arange(len(_y))

			epoch = 0
			lossFuncRecord = []
			lossFuncParamsRecord = []
			_lossEachEpoch = LOSS_EACH_EPOCH
			while (epoch <= self._maxEpoch) and (_lossEachEpoch >= self._fittingLossExitThreshold):
				p = fitting(_x, _y)
				_lossEachEpoch = np.sqrt(sum(list(map(lambda ele: ele**2, residuals(p[0], _x, _y)))))
				lossFuncRecord.append(_lossEachEpoch)
				lossFuncParamsRecord.append(p[0])
				epoch += 1
			_locs = np.where(np.asarray(lossFuncRecord) == min(lossFuncRecord), True, False)
			self.currentSample_loss = np.asarray(lossFuncRecord)[_locs].tolist()[0]
			self.currentSample_kValue = np.asarray(lossFuncParamsRecord)[_locs].ravel().tolist()[0]
			self.currentSample_bias = np.asarray(lossFuncParamsRecord)[_locs].ravel().tolist()[-1]

			if self._droppingStatusKValueThreshold < self.currentSample_kValue < self._climbingStatusKValueThreshold:
				self.currentSample_status = "A"
			elif self.currentSample_kValue <= self._droppingStatusKValueThreshold:
				self.currentSample_status = "C"
			else:
				self.currentSample_status = "B"

			self.dataBuffer.pop(0)


def linearFunc(p, x):
	k, b = p
	return k * x + b


def residuals(p, x, y):
	"""
	实验数据x, y和拟合函数之间的差，p为拟合需要找到的系数
	"""
	return y - linearFunc(p, x)


def fitting(x, y):
	p = (np.random.randn(1, 2))
	return leastsq(residuals, p, args=(x, y))
