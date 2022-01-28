import numpy as np


class InsulationDegrade:
	"""
	绝缘剩余安全裕度计算

	:math:`[1 - lg(N + 1)] \\times e^a`, :math:`a={-(t/40)^{9.6}}`, :math:`N=定子绕组发生过热次数`

	[1] 参数
	----------
	runningSince:
	    int，投产时间（秒级），如1577808000，unixTimestamp，optional，默认1577808000=2020-01-01 00:00:00
	maximumTimeGapThreshold:
	    int，最近一次过热报警时间与当前报警时间间隔不应低于此限值（秒），optional，默认1年=86400
	minimumTimeGapThreshold:
	    int，过热最小持续时间（秒），optional，默认2分钟=120
	temperUpperThreshold:
	    float，过热报警阈值，optional，默认125
	bufferLimit:
	    int，暂存的近期温度记录尺寸，尺寸过大会导致报警延迟，optional，默认50
	fuzzyPercentage:
	    float，当过热状态中断/跳变时，近期温度记录中若超限次数达到此阈值，则仍认为发生了过热，optional，默认0.1

	[2] 方法
	----------
	decide:
	    是否需要进行过热计数的判断逻辑：
		当温度超标（判断依据：近期暂存的温度数据中有一定比例的数据为超限值）、持续时间超过限值（判断依据：近期暂存的温度数据中超限值的
		数据持续时间超过限值）、距离上一次过热报警时间已经超过最小限定时，计数器+1

	[3] 返回
	-------
	insulationRemainSafeMargin:
	    绝缘剩余安全裕度值

	counter:
		过热报警计数

	[4] 示例1
	--------
	>>> values = data['汽机润滑油冷油器出口总管油温1']
	>>>	insulationObject = InsulationDegrade(temperUpperThreshold=20)
	>>>	NRecorder = []
	>>>	insulationRemainSafeMarginRecorder = []
	>>>	for i in range(len(data)):
	>>>		insulationObject.decide(values[i], times[i])
	>>>		NRecorder.append(insulationObject.counter)
	>>>		insulationRemainSafeMarginRecorder.append(insulationObject.insulationRemainSafeMargin)

	[5] 备注
	-----
	* 当需要进行相关判断的值为各种逻辑聚合值时（如某测点近期均值），需要在外部进行预处理

	"""

	def __init__(self, **kwargs):
		keys = kwargs.keys()
		# ==== 外部参数 ==== #
		# int，投产时间（秒级），如1577808000，unixTimestamp，默认1577808000=2020-01-01 00:00:00
		self._runningSince = kwargs["runningSince"] if "runningSince" in keys else 1577808000
		# int，最近一次过热报警时间与当前报警时间间隔不应低于此限值（秒），默认1年=86400
		self._maximumTimeGapThreshold = kwargs["maximumTimeGapThreshold"] if "maximumTimeGapThreshold" in keys else 86400
		# int，过热最小持续时间（秒），默认2分钟=120
		self._minimumTimeGapThreshold = kwargs["minimumTimeGapThreshold"] if "minimumTimeGapThreshold" in keys else 120
		# float，过热报警阈值，默认125
		self._temperUpperThreshold = kwargs["temperUpperThreshold"] if "temperUpperThreshold" in keys else 125
		# int，暂存的近期温度记录尺寸，尺寸过大会导致报警延迟，默认50
		self._bufferLimit = kwargs["bufferLimit"] if "bufferLimit" in keys else 50
		# float，当过热状态中断/跳变时，近期温度记录中若超限次数达到此阈值，则仍认为发生了过热，默认0.1
		self._fuzzyPercentage = kwargs["fuzzyPercentage"] if "fuzzyPercentage" in keys else 0.1

		# ==== 内部参数 ==== #
		# 环境变量，上一次过热报警时间
		self.__latestOverHeatTime = None
		# 环境变量，近期时间记录，无论限值是否达到报警值
		self.__time_buffer = []
		# 环境变量，近期温度记录，无论限值是否达到报警值
		self.__temper_buffer = []

		# ==== 输出 ==== #
		# 绝缘剩余安全裕度值
		self.insulationRemainSafeMargin = None
		# 过热报警计数
		self.counter = 0

	def __count(self, gap: int):
		"""
		计数

		:param gap int，计数步长
		"""
		self.counter += gap

	def __timeBufferUpdate(self, newValue: int):
		"""
		时间记录更新，依据记录尺寸限值滑动

		:param newValue: int, 需要更新的数据
		"""
		self.__time_buffer.append(newValue)
		if len(self.__time_buffer) > self._bufferLimit:
			self.__time_buffer.pop()

	def __temperBufferUpdate(self, newValue: float):
		"""
		温度记录更新，依据记录尺寸限值滑动

		:param newValue: float, 需要更新的数据
		"""
		self.__temper_buffer.append(newValue)
		if len(self.__temper_buffer) > self._bufferLimit:
			self.__temper_buffer.pop()

	@staticmethod
	def __insulationRemainSafeMargin(N: int, runningSince: int, currentTime: int) -> float:
		"""
		绝缘剩余安全裕度计算

		:param N: int, 当前过热次数计数
		:param runningSince: int, 投产时间（秒级），如1577808000，unixTimestamp，默认1577808000=2020-01-01 00:00:00
		:param currentTime: int, 当前时间（秒级），如1577808000，unixTimestamp
		:return: float 绝缘剩余安全裕度计算
		"""
		deltaYears = (currentTime - runningSince) / (365 * 24 * 3600)
		cache = -(deltaYears / 40) ** 9.6
		return (1 - np.log10(N + 1)) * np.exp(cache)

	def decide(self, temper: float, timestamp: int):
		"""
		是否需要进行过热计数的判断逻辑：
		当温度超标（判断依据：近期暂存的温度数据中有一定比例 `fuzzyPercentage` 的数据为超限值）、持续时间超过限值（判断依据：近期暂存的温度数据中超限值的
		数据持续时间超过限值）、距离上一次过热报警时间已经超过最小限定时，计数器+1

		:param temper: float, 需要进行判断的温度
		:param timestamp: int, 需要进行判断的时间
		:return: None
		"""
		self.__timeBufferUpdate(timestamp)
		self.__temperBufferUpdate(temper)
		if temper >= self._temperUpperThreshold:
			alarmArray = np.where(np.asarray(self.__temper_buffer) >= self._temperUpperThreshold, 1, 0)
			alarmArrayCumSumRatio = np.cumsum(alarmArray) / len(alarmArray)
			alarmLocs = np.where(np.asarray(alarmArrayCumSumRatio) >= self._fuzzyPercentage)[0]
			if not self.__latestOverHeatTime:
				self.__latestOverHeatTime = timestamp - self._maximumTimeGapThreshold - 1
			# 距离上一次过热报警时间是否达到最小时间间隔
			condition1 = (timestamp - self.__latestOverHeatTime) >= self._maximumTimeGapThreshold
			# 当期温度超标持续时间达到最小时间间隔
			condition2 = (self.__time_buffer[alarmLocs[-1]] - self.__time_buffer[alarmLocs[0]]) >= self._minimumTimeGapThreshold
			if condition1 and condition2:
				self.__count(1)
				self.__latestOverHeatTime = timestamp - 1
		self.insulationRemainSafeMargin = self.__insulationRemainSafeMargin(self.counter, self._runningSince, timestamp)

