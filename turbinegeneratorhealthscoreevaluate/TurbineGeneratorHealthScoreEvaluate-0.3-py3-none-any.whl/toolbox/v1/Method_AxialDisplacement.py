import datetime as dt
import pandas as pd


class AxialDisplacement:
	def __init__(self, **kwargs):
		"""
		输入轴向位移及时间戳,先对稳态数据进行判断,再取稳态数据的最大值最为轴位移最大值

		[1] 参数
		----------
		timeRangeLimit:
		    float,进行近期轴向位移最值偏差判断的时间范围,s,默认600
		upperDisplacementLimit:
		    float,轴向位移偏差上限,mm,默认0.1
		buffer:
		    dateframe,轴位移数值与时间戳的缓存,列名为"axialDisplacement","timestamp"

		[2] 方法
		----------
		update_and_determine:
		    更新轴位移与时间戳缓存,并判断所定义时间段内轴位移值是否满足"稳态数据"的判断,并输出近期轴位移最大值

		[3] 返回
		-------
		determine:
		    稳态时间段轴向位移最值,{"inSteadyState": 当前所选时间范围内数据是否为稳态, "axialDisplaceMaximum": 当前所选时间范围内最大轴位移值, "valueRange": 当前所选时间范围内最值范围}

		_buffer:
		    dataframe,近期轴位移值与时间戳缓存,"axialDisplacement","timestamp"

		[4] 示例1
		--------
		>>> datas = np.random.rand(1, 5000).ravel() * 0.108
		>>> timestamps = []
		>>> nowTime = dt.datetime.now()
		>>> for i in range(5000):
		>>> 	_time = nowTime - dt.timedelta(seconds=(5000 - i)*7)
		>>> 	timestamps.append(_time.strftime("%Y-%m-%d %H:%M:%S"))
		>>> obj = AxialDisplacement()
		>>> for i in range(5000):
		>>> 	obj.update_and_determine(datas[i], timestamps[i])
		>>> 	print(obj.determine)
		"""
		keys = kwargs.keys()
		# ===== 输出参数 ===== #
		self._timeRangeLimit = kwargs["timeRangeLimit"] if "timeRangeLimit" in keys else 60 * 10
		self._upperDisplacementLimit = kwargs[
			"upperDisplacementLimit"] if "upperDisplacementLimit" in keys else 0.1  # mm
		# ===== 外部、内部、输出参数 ===== #
		self._buffer = kwargs["buffer"] if ("buffer" in keys) and (len(kwargs["buffer"]) != 0) else pd.DataFrame([], columns=["axialDisplacement","timestamp"])
		# ===== 输出参数 ===== #
		self.determine = None

	def update_and_determine(self, axialDisplace: float, ts: str):
		"""
		更新轴位移与时间戳缓存,并判断所定义时间段内轴位移值是否满足"稳态数据"的判断,并输出近期轴位移最大值

		:param axialDisplace: float,轴位移值,mm
		:param ts: str,样本时间戳,%Y-%m-%d %H:%M:%S
		:return: None
		"""
		self._buffer = self._buffer.append({"axialDisplacement": axialDisplace, "timestamp": ts}, ignore_index=True)
		_timeEnd = dt.datetime.strptime(self._buffer["timestamp"].iloc[-1], "%Y-%m-%d %H:%M:%S")
		_timeStart = dt.datetime.strptime(self._buffer["timestamp"].iloc[0], "%Y-%m-%d %H:%M:%S")
		if (_timeEnd - _timeStart).seconds >= self._timeRangeLimit:
			_values = self._buffer["axialDisplacement"].values
			_diff = max(_values) - min(_values)
			if _diff <= self._upperDisplacementLimit:
				self.determine = {"inSteadyState": True, "axialDisplaceMaximum": max(_values), "valueRange": f"{min(_values)}~{max(_values)}"}
			else:
				self.determine = {"inSteadyState": False, "axialDisplaceMaximum": None, "valueRange": f"{min(_values)}~{max(_values)}"}
			self._buffer = self._buffer.iloc[1: None]
