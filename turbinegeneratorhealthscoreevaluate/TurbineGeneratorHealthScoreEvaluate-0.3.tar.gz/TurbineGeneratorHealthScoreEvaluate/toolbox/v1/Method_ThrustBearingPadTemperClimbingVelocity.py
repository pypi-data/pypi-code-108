import numpy as np
from scipy.optimize import leastsq

LOSS_EACH_EPOCH = 100


class ThrustBearingPadTemperClimbingVelocity:
	def __init__(self, **kwargs):
		"""
	    通过不断输入数据与时间戳样本,对缓存量进行滑动平均并计算出升温速率(℃/s)经变换后,升温速率(℃/min)与maximumBearableVelocity进行比较得出的最终温升速率

	    [1] 参数
	    ----------
	    timeBuffer:
	    	list[int],时间戳缓存.通过外部输入,可以在每次迭代过程结束时输出,并在下一次迭代开始前用于类的初始化,默认为[None]
	    valueBuffer:
	    	list[float],数据缓存.通过外部输入,可以在每次迭代过程结束时输出,并在下一次迭代开始前用于类的初始化,默认为[None]
	    valueBuffer_moveAvg:
	    	list[float],滑动平均值数据缓存.通过外部输入,可以在每次迭代过程结束时输出,并在下一次迭代开始前用于类的初始化,默认为[None]
	    bufferSize:
	    	int,对包括timeBuffer、valueBuffer和valueBuffer_moveAvg缓存量尺寸的控制参数,默认为5
	    minimumBufferSize:
	    	int,可以针对滑动平均缓存中数据进行拟合时,滑动平均缓存中数据的最小尺寸,不小于bufferSize,默认为bufferSize
	    maxEpoch:
	    	int,针对滑动平均缓存中数据进行拟合的最大次数,默认为20
	    fittingLossExitThreshold:
	    	float,退出拟合的损失值门限,默认为0.001
	    maximumBearableVelocity:
	    	float,当计算出的升温速率(℃/min)小于此值时,认为没有发生升温,否则认为有温升,默认为0.002
	    currentSample_kValue:
	    	float,输入当前样本后,经滑动平均计算出的升温速率(℃/s),默认为None
	    climbingVelocity:
	    	float,输入当前样本后,经滑动平均计算出的升温速率(℃/min)经与maximumBearableVelocity比较后得出的最终温升速率,默认为None

	    [2] 方法
	    ----------
	    update:
	        更新时间和数据的缓存buffer,使用滑动平均消除噪声,并计算MA后的数据线性拟合k值;变化该k值单位为℃/min,当该值超出最大容忍值时,输出该值作为温度变化速率,否则该值为0

	    [3] 返回
	    -------
	    currentSample_kValue:
	    	float,输入当前样本后,经滑动平均计算出的升温速率(℃/s),默认为None
	    climbingVelocity:
	    	float,输入当前样本后,经滑动平均计算出的升温速率(℃/min)经与maximumBearableVelocity比较后得出的最终温升速率,默认为None
	    timeBuffer:
	    	list[int],时间戳缓存.通过外部输入,可以在每次迭代过程结束时输出,并在下一次迭代开始前用于类的初始化,默认为[None]
	    valueBuffer:
	    	list[float],数据缓存.通过外部输入,可以在每次迭代过程结束时输出,并在下一次迭代开始前用于类的初始化,默认为[None]
	    valueBuffer_moveAvg:
	    	list[float],滑动平均值数据缓存.通过外部输入,可以在每次迭代过程结束时输出,并在下一次迭代开始前用于类的初始化,默认为[None]

	    [4] 示例1
	    --------
	    >>> databaseName = 'bearing_pad_temper'
	    >>> tableName = '轴承瓦温20200320_20200327_原始数据'
	    >>> host = 'localhost'
	    >>> port = 3306
	    >>> userID = 'root'
	    >>> password = '000000'
	    >>> obj = mysqlOperator(databaseName=databaseName, tableName=tableName, host=host, port=port, userID=userID,
	    >>>	                    password=password)
	    >>>	content = '时间戳,发电机励端轴瓦温度'
	    >>>	condition = "(时间戳>=\'2020-03-20 16:00:00\') and (时间戳<=\'2020-03-20 18:00:00\')"
	    >>>	data = obj.selectData(content=content, condition=condition)
	    >>> timeRecord = formatTimestampTransfer2Int(data["时间戳"].tolist())
	    >>> dataRecord = data["发电机励端轴瓦温度"].tolist()
	    >>> _moveAvg = []
	    >>> climbingVelocityRecord = []
	    >>> _timeCache, _valueCache, _valueBuffer_moveAvgCache = [None], [None], []
	    >>> for (_time, _value) in zip(timeRecord, dataRecord):
	    >>>     velObj = ThrustBearingPadTemperClimbingVelocity(timeBuffer=_timeCache, valueBuffer=_valueCache,
	    >>>     valueBuffer_moveAvg=_valueBuffer_moveAvgCache)
	    >>>     velObj.update(_time, _value)
	    >>>     _timeCache = velObj.timeBuffer
	    >>>     _valueCache = velObj.valueBuffer
	    >>>     _valueBuffer_moveAvgCache = velObj.valueBuffer_moveAvg
	    >>>     _moveAvg.append(velObj.valueBuffer_moveAvg[-1])
	    >>>    climbingVelocityRecord.append(velObj.climbingVelocity)
	    >>> climbingVelocityRecord_array = np.asarray(climbingVelocityRecord)
	    >>> climbingVelocityRecord_array_noNone = np.where(climbingVelocityRecord_array==None, -1, climbingVelocityRecord_array)
	    >>> climbingVelocityRecord_array_noNone_climbings = np.where(climbingVelocityRecord_array_noNone<=0, None, climbingVelocityRecord_array_noNone)
	    >>> fig, ax = plt.subplots(tight_layout=True)
	    >>> ax.grid(color="r", ls="--")
	    >>> ax_twin = ax.twinx()
	    >>> measuredLine, = ax.plot([], [], ":")
	    >>> avgLine, = ax.plot([], [], "--", color="cyan")
	    >>> measuredPoint, = ax.plot([], [], color="blue", marker="o")
	    >>> climbingPoint, = ax_twin.plot([], [], color="red", marker="*", linestyle="")
	    >>> ax.set_xlim(0, len(dataRecord))
	    >>> ax.set_ylim(0, 100)
	    >>>
	    >>> def updateLine(_i):
	    >>>     _x = np.arange(len(dataRecord))[_i]
	    >>>     _y = dataRecord[_i]
	    >>>     if _i == 0:
	    >>> 	    ax.set_xlim(0, _i+10)
	    >>> 	    ax.set_ylim(dataRecord[0]*0.98, dataRecord[0]*1.02)
	    >>>     elif _i < 500:
	    >>> 	    ax.set_xlim(0, _i+10)
	    >>> 	    ax.set_ylim(min(dataRecord[0:_i])*0.98, max(dataRecord[0:_i])*1.02)
	    >>>     else:
	    >>> 	    ax.set_xlim(_i-500-10, _i+10)
	    >>> 	    ax.set_ylim(min(dataRecord[_i-500:_i])*0.98, max(dataRecord[_i-500:_i])*1.02)
	    >>>     measuredPoint.set_data(_x, _y)
	    >>>     climbingPoint.set_data(np.arange(len(dataRecord))[0:_i], climbingVelocityRecord_array_noNone_climbings[0:_i])
	    >>>     measuredLine.set_data(np.arange(len(dataRecord))[0:_i], dataRecord[0:_i])
	    >>>     avgLine.set_data(np.arange(len(dataRecord))[0:_i], _moveAvg[0:_i])
	    >>>
	    >>> ani = FuncAnimation(fig, updateLine, np.arange(len(dataRecord)), interval=1)
	    >>> # ani.save("dynamic.gif", fps=5, writer="pillow")
	    >>> plt.show()

	    [5] 备注
	    -----
	    * 包括timeBuffer、valueBuffer、valueBuffer_moveAvg在内的缓存量.可以通过外部输入,可以在每次迭代过程结束时输出,并在下一次迭代开始前用于类的初始化

	    """

		keys = kwargs.keys()
		# ===== 外部参数、输出参数、内部参数 ===== #
		self.timeBuffer = kwargs["timeBuffer"] if ("timeBuffer" in keys) and (kwargs["timeBuffer"] != [None]) else [None]
		self.valueBuffer = kwargs["valueBuffer"] if ("valueBuffer" in keys) and (kwargs["valueBuffer"] != [None]) else [None]
		self.valueBuffer_moveAvg = kwargs["valueBuffer_moveAvg"] if ("valueBuffer_moveAvg" in keys) and (kwargs["valueBuffer_moveAvg"] != []) else []
		# ===== 外部参数 ===== #
		self._bufferSize = kwargs["bufferSize"] if "bufferSize" in keys else 5
		self._minimumBufferSize = kwargs["minimumBufferSize"] if ("minimumBufferSize" in keys) and (kwargs["minimumBufferSize"] <= self._bufferSize) else self._bufferSize
		self._maxEpoch = kwargs["maxEpoch"] if "maxEpoch" in keys else 20
		self._fittingLossExitThreshold = kwargs["fittingLossExitThreshold"] if "fittingLossExitThreshold" in keys else 0.001
		self._maximumBearableVelocity = kwargs["maximumBearableVelocity"] if "maximumBearableVelocity" in keys else 0.0002
		# ===== 输出参数 ===== #
		self.currentSample_kValue = None
		self.climbingVelocity = None

	def update(self, newTime: int, newValue: float):
		"""
		更新时间和数据的缓存buffer,使用滑动平均消除噪声,并计算MA后的数据线性拟合k值;变化该k值单位为℃/min,当该值超出最大容忍值时,输出该值作为温度变化速率,否则该值为0

		:param newTime: 当前新输入样本的unix时间戳(秒)
		:type newTime: int
		:param newValue: 当前新输入样本的值
		:type newValue: float
		:return: None
		"""
		self.timeBuffer.append(newTime)
		self.valueBuffer.append(newValue)
		if len(self.valueBuffer) == 2:
			self.valueBuffer_moveAvg.append(newValue)
		else:
			self.valueBuffer_moveAvg.append(np.mean(self.valueBuffer_moveAvg + [newValue]))
		self.timeBuffer = self.timeBuffer[-self._bufferSize:None]
		self.valueBuffer = self.valueBuffer[-self._bufferSize:None]
		self.valueBuffer_moveAvg = self.valueBuffer_moveAvg[-self._bufferSize:None]
		self.__fitMoveAverageArray()

	def __fitMoveAverageArray(self):
		global LOSS_EACH_EPOCH

		if len(self.valueBuffer_moveAvg) >= self._minimumBufferSize:
			_y = self.valueBuffer_moveAvg
			_x = np.arange(len(_y))
			epoch = 0
			lossFuncRecord = []
			lossFuncParamsRecord = []
			_lossEachEpoch = LOSS_EACH_EPOCH
			while (epoch <= self._maxEpoch) and (_lossEachEpoch >= self._fittingLossExitThreshold):
				p = fitting(_x, _y)
				_lossEachEpoch = np.sqrt(sum(list(map(lambda ele: ele ** 2, residuals(p[0], _x, _y)))))
				lossFuncRecord.append(_lossEachEpoch)
				lossFuncParamsRecord.append(p[0])
				epoch += 1
			_locs = np.where(np.asarray(lossFuncRecord) == min(lossFuncRecord), True, False)
			self.currentSample_kValue = np.asarray(lossFuncParamsRecord)[_locs].ravel().tolist()[0]
			self.climbingVelocity = self.currentSample_kValue/60 if self.currentSample_kValue/60 >= self._maximumBearableVelocity else 0


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
