import numpy as np
import pandas as pd
import re
import datetime

from scipy.optimize import leastsq


def decisionTree(Id, I_, Is, htc, hts, verbose=False):
	"""
	i表示当前片段，i-1表示前序片段

	当前片段起始于：:math:`(t_b{^i}, y_b{^i})`, 截止于：:math:`(t_e{^i}, y_e{^i})`

	前序片段截止于：:math:`(t_e{^{i-1}}, y_e{^{i-1}})`

	变量定义：① :math:`I = y_e{^i} - y_e{^{i-1}}`， ② :math:`Is = y_e{^i} - y_b{^i}`， ③ :math:`Id = y_b{^i} - y_e{^{i-1}}`

	- 判断逻辑：

	1. :math:`|Id| < htc`,则片段i-1与i连续,否则不连续

	1.1. :math:`|Id| < htc`, :math:`|I| < hts` 时, 则片段i为趋势不变（A/Ax), 否则片段i-1与i上升(B)/下降(C)

	1.1.1. :math:`|Id| < htc`, :math:`|I| < hts`, :math:`I > 0` 时, 则片段i-1与i为上升(B)

	1.1.2. :math:`|Id| < htc`, :math:`|I| < hts`, :math:`I < 0` 时, 则片段i-1与i为下降(C)

	2. :math:`|Id| \\ge\\ htc` 时, 则片段i-1与i不连续

	2.1. :math:`|Id| \\ge\\ htc`, :math:`|Is| \\le\\ hts` 时, 则片段i-1与i正步(D)/负步(E)

	2.1.1. :math:`|Id| \\ge\\ htc`, :math:`|Is| \\le\\ hts`, :math:`Id > 0` 时, 则片段i-1与i正步(D)

	2.1.2. :math:`|Id| \\ge\\ htc`, :math:`|Is| \\le\\ hts`, :math:`Id < 0` 时, 则片段i-1与i负步(E)

	2.2. :math:`|Id| \\ge\\ htc`, :math:`|Is| > hts`, :math:`sign(Id * Is) > 0` 时, 则片段i-1与i上升(B)/下降(C)

	2.2.1. :math:`|Id| \\ge\\ htc`, :math:`|Is| > hts`, :math:`sign(Id * Is) > 0`, :math:`Id > 0` 时, 则片段i-1与i上升(B)

	2.2.2. :math:`|Id| \\ge\\ htc`, :math:`|Is| > hts`, :math:`sign(Id * Is) > 0`, :math:`Id < 0` 时, 则片段i-1与i下降(C)

	2.3. :math:`|Id| \\ge\\ htc`, :math:`|Is| > hts`, :math:`sign(Id * Is) < 0` 时, 则片段i-1与i上-下瞬变(F)/下-上瞬变(G)

	2.2.1. :math:`|Id| \\ge\\ htc`, :math:`|Is| > hts`, :math:`sign(Id * Is) < 0`, :math:`Id > 0` 时, 则片段i-1与i为上-下瞬变(F)

	2.2.2. :math:`|Id| \\ge\\ htc`, :math:`|Is| > hts`, :math:`sign(Id * Is) < 0`, :math:`Id < 0` 时, 则片段i-1与i为下-上瞬变(G)
	"""

	Id_abs = abs(Id)
	I_abs = abs(I_)
	Is_abs = abs(Is)
	IdIs_sign = np.sign(Id * Is)
	vector = [int(Id_abs < htc), int(I_abs >= hts), int(Is_abs <= hts), int(I_ >= 0), int(Id > 0), int(IdIs_sign > 0)]
	findStr = "".join(list(map(str, vector)))
	results = ["B", "C", "Ax", "D",
	           "E", "B", "C", "F",
	           "G"]
	patterns = [r"11[\w]1[\w]{2}", r"11[\w]0[\w]{2}", r"10[\w]{4}", r"0[\w]1[\w]1[\w]",
	            r"0[\w]1[\w]0[\w]", r"0[\w]0[\w]11", r"0[\w]0[\w]01", r"0[\w]0[\w]10",
	            r"0[\w]0[\w]00"]
	for i, item in enumerate(patterns):
		_pattern = re.compile(item)
		res = _pattern.match(findStr)
		if res:
			print(">>> ", findStr, item, results[i], res.group()) if verbose else None
			return results[i]


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


class QualitativeTrendAnalysis:
	def __init__(self, _htc=0.2, _hts=0.6, _data_fitting_minimum_size=30,
	             _data_fitting_maximum_size=1000, _cumulative_sum_upper_threshold=1, _fitting_max_try=20):
		"""
	    [1] 参数
	    ----------
	    _htc:
	        float,用于判断片段i-1与i是否连续的阈值, default 0.2
	    _hts:
	        float,当片段i-1与i连续时，用于判断片段i为不变、上升/下降的阈值;当片段i-1与i不连续时，用于判断片段i为正步/负步、
	        上升/下降/上-下瞬变/下-上瞬变的阈值, default 0.6
	    _data_fitting_minimum_size:
	        int,当片段中累积的数据小于该值时,不对当前片段数据做趋势判断,不宜过大,否则片段趋势判断失真, default 30
	    _data_fitting_maximum_size:
	        int,当片段中累积的数据达到该值时,及时当前片段数据为达到做趋势判断的条件,仍执行,不宜过小, default 1000,TODO:尚未测试
	    _cumulative_sum_upper_threshold:
	        float,当片段原始数据与拟合数据的残差和小于该值时,认为拟合结果可靠,可以继续对此片段收集新数据,
	        否则结束该片段的数据收集, default 1
	    _fitting_max_try:
	        int,针对每一个片段在其拟合结果达到期望前的最大拟合次数,达到此限值却仍未有最佳拟合参数时,将新的数据最为新片段,
	        当前片段结束数据收集, default 20

	    [2] 方法
	    ----------
	    getNewData:
	        获取新的数据,并判断是否开启新的片段.当前片段数据结束收集,可能原因包括: \n
	        ①达到最大拟合次数时,数据拟合结果的残差和仍超标,结束数据收集; \n
	        ②片段数据总量达到最大限值,结束数据收集; \n
	        结束片段数据收集后,开启新的片段,并对形成的片段进行拟合,记录拟合参数 \n

	    trendAnalyze:
	        片段趋势分析

	    fittingResultCalculate:
	        使用[各片段数据量]、[各片段拟合参数]、[各片段瞬时趋势符号]计算所有片段的拟合值,同时原样输出[各片段瞬时趋势符号],
	        及各片段在原始数据中结束位置的集合

	    slowlyDriftAdjust:
	        使用原始数据、原始数据的片段趋势粗析结果、原始数据的片段分割位置集合，进行缓慢飘移检测。输出检测后的各片段趋势符号集合

	    [3] 示例
	    --------

	    >>> from Method_QualitativeTrendAnalysis import QualitativeTrendAnalysis
	    >>> import matplotlib.pyplot as plt
	    >>>
	    >>> qta_obj = QualitativeTrendAnalysis(_data_fitting_minimum_size=100, _htc=0.2, _hts=0.6)
	    >>> eachSnippetDataQuantRecord = []
	    >>> eachSnippetParamRecord = []
	    >>> trendSymbol_instant_record = []
	    >>> deltaTime_record = []
	    >>> Id_record = []
	    >>> Is_record = []
	    >>> I_record = []
	    >>> for i, item in enumerate(data['发电机定子线圈出水温度1']):
	    >>>     qta_obj.getNewData(item, str(i))
	    >>>     if not qta_obj.currentSnippetIsUpdating:  # 当当前片段停止更新时，意味着：①新的数据在多次拟合后误差仍超标；②当前片段的数据量达到最大限；
	    >>>         eachSnippetDataQuantRecord.append(qta_obj.currentProcessingSnippetQuant)  # 记录每一个片段的数据量
	    >>>         eachSnippetParamRecord.append(qta_obj.currentProcessingSnippetNewestFittingParams)  # 记录每一个片段的拟合参数
	    >>>         deltaTime_record.append(qta_obj.currentSnippetDeltaTime)  # 记录每一个片段的持续时间
	    >>>         qta_obj.trendAnalyze(verbose=False)  # 计算当前片段的（瞬时）趋势符号
	    >>>         trendSymbol_instant_record.append(qta_obj.trendSymbol_instant)  # 记录当前片段的瞬时趋势符号
	    >>>         Id_record.append(qta_obj._Id)
	    >>>         Is_record.append(qta_obj._Is)
	    >>>         I_record.append(qta_obj._I)
	    >>> # 根据前序，计算所有数据的分片段拟合值"fitResult"、各片段符号"symbols"、各片段符号在所有数据中的x向位置
	    >>> yCal = qta_obj.fittingResultCalculate(eachSnippetDataQuantRecord, eachSnippetParamRecord, trendSymbol_instant_record)
	    >>> adjustSymbols = qta_obj.slowlyDriftAdjust(data['发电机定子线圈出水温度1'], yCal["symbols"], yCal["symbol_locs"])
	    """

		# 每次进行线性拟合时的最小数据尺寸，缓存的数据尺寸达到此限值时，开始对当前片段进行拟合
		self.DATA_FITTING_MINIMUM_SIZE = _data_fitting_minimum_size
		# 每次进行线性拟合时的最大数据尺寸，缓存的数据尺寸达到此限值时，若拟合的残差和值仍然低于门限值，则开启新的数据片段
		self.DATA_FITTING_MAXIMUM_SIZE = _data_fitting_maximum_size
		# 拟合验证的CumulativeSum最大误差门限
		self.CUMULATIVE_SUM_UPPER_THRESHOLD = _cumulative_sum_upper_threshold
		# 拟合验证的CumulativeSum计算值
		self.CUMULATIVE_SUM = None
		# 当前正在处理的数据片段的数据的缓存
		self.currentProcessingSnippetDataBuffer = []
		# 当前正在处理的数据片段的时间的缓存
		self.currentProcessingSnippetTimeBuffer = []
		# 当前片段结束更新时的数据量
		self.currentProcessingSnippetQuant = None
		# 当前片段最近一次拟合的参数
		self.currentProcessingSnippetNewestFittingParams = None
		# 当前的片段是否正在更新中
		self.currentSnippetIsUpdating = False
		# 尝试的最大拟合次数
		self.FITTING_MAX_TRY = _fitting_max_try
		# 上一个片段的参数
		self.lastSnippet_fittingParams = None
		self.lastSnippet_dataQuant = None
		# 决策参数
		self.htc = _htc  # 判断是否连续的阈值，上一片段结束点和当前片段起始点的y向差值
		self.hts = _hts  # 判断是否为“步”的阈值，当前片段端点间的y向差值
		self.trendSymbol_instant = None  # 瞬时的趋势符号，不排除缓慢飘移的情况
		# 私有参数
		self._Id = None
		self._Is = None
		self._I = None

		self.currentSnippetDeltaTime = 0
		self.currentSnippetTimeStart = 0
		self.currentSnippetTimeEnd = 0
		self.currentSnippetDataStart = None
		self.currentSnippetDataEnd = None

	def getNewData(self, _newData: float, _newTime: str, _newTimeMinimumDpi="s"):
		"""
		获取新的数据,并判断是否开启新的片段.当前片段数据结束收集,可能原因包括:
			①达到最大拟合次数时,数据拟合结果的残差和仍超标,结束数据收集;
			②片段数据总量达到最大限值,结束数据收集;
		结束片段数据收集后,开启新的片段,并对形成的片段进行拟合,记录拟合参数

		- 时间分辨率影响了转换成秒级unixTime时的缩小倍数,如,输入的为秒级数据,则_newTimeMinimumDpi="s",数据不做处理;
		输入的为毫秒级数据,则_newTimeMinimumDpi="ms",数据缩小1000;
		输入的为微秒级数据,则_newTimeMinimumDpi="μs",数据缩小1000000;
		输入的为纳秒级数据,则_newTimeMinimumDpi="ns",数据缩小1000000000;

		:param _newData: float, 新的数据
		:param _newTime: string, 新数据的时间戳
		:param _newTimeMinimumDpi: string, 时间戳的最小分辨率,default "s",秒级
		:return: None
		"""
		if _newTimeMinimumDpi == "s":
			_adjustNewTime = int(_newTime)
		elif _newTimeMinimumDpi == "ms":
			_adjustNewTime = int(_newTime) / 1000
		elif _newTimeMinimumDpi == "μs":
			_adjustNewTime = int(_newTime) / 1000000
		elif _newTimeMinimumDpi == "ns":
			_adjustNewTime = int(_newTime) / 1000000000
		else:
			raise ValueError(f"getNewData方法_newTimeMinimumDpi参数错误：{_newTimeMinimumDpi},可选参数为['s', 'ms', 'μs', 'ns']")

		# 在临时变量中记录新数据（不一定可以更新该数据）
		_currentProcessingSnippetDataBuffer = self.currentProcessingSnippetDataBuffer + [_newData]
		_currentProcessingSnippetTimeBuffer = self.currentProcessingSnippetTimeBuffer + [_adjustNewTime]
		# 尺寸检查，判断是否需要退出[0]位置的数据
		if len(_currentProcessingSnippetDataBuffer) > self.DATA_FITTING_MAXIMUM_SIZE:
			_currentProcessingSnippetDataBuffer.pop(0)
			_currentProcessingSnippetTimeBuffer.pop(0)
		# 尺寸检查，判断数据尺寸是否满足最小数据量要求
		iterResSumRecord = []
		iterParamsRecord = []
		if len(_currentProcessingSnippetDataBuffer) > self.DATA_FITTING_MINIMUM_SIZE:
			fittingTimeCount = 0
			while fittingTimeCount < self.FITTING_MAX_TRY:
				# 如果对于当前片段已有拟合参数，则对新数据形成的片段检查残差和
				_x = np.arange(len(_currentProcessingSnippetDataBuffer))
				_y = _currentProcessingSnippetDataBuffer
				p = None
				if self.currentProcessingSnippetNewestFittingParams is not None:
					resSum = np.sum(abs(residuals(self.currentProcessingSnippetNewestFittingParams, _x, _y)))  # 拟合后的残差和
					fittingParamsFrom = "inherit"
					iterParamsRecord.append(self.currentProcessingSnippetNewestFittingParams)
				else:
					p = fitting(_x, _y)
					resSum = np.sum(abs(residuals(p[0], _x, _y)))  # 拟合后的残差和
					fittingParamsFrom = "newCal"
					iterParamsRecord.append(p[0])
				iterResSumRecord.append(resSum)
				# 如果残差和满足条件，则接收新的数据
				if resSum < self.CUMULATIVE_SUM_UPPER_THRESHOLD:  # 接受拟合出的线性参数
					self.currentProcessingSnippetDataBuffer = _currentProcessingSnippetDataBuffer
					self.currentProcessingSnippetTimeBuffer = _currentProcessingSnippetTimeBuffer
					self.currentSnippetIsUpdating = True
					if fittingParamsFrom == "newCal":
						self.currentProcessingSnippetNewestFittingParams = p[0]
					break
				else:
					self.currentSnippetIsUpdating = False
					self.currentProcessingSnippetQuant = len(self.currentProcessingSnippetDataBuffer)
					self.currentSnippetDataStart = self.currentProcessingSnippetDataBuffer[0]
					self.currentSnippetDataEnd = self.currentProcessingSnippetDataBuffer[-1]
					self.CUMULATIVE_SUM = resSum
					self.currentSnippetTimeStart = int(self.currentProcessingSnippetTimeBuffer[0])
					self.currentSnippetTimeEnd = int(self.currentProcessingSnippetTimeBuffer[-1])
					self.currentSnippetDeltaTime = self.currentSnippetTimeEnd - self.currentSnippetTimeStart
				fittingTimeCount += 1
			minLoc_iterResSumRecord = np.where(np.array(iterResSumRecord) == np.min(iterResSumRecord))[0][0]
			self.currentProcessingSnippetNewestFittingParams = iterParamsRecord[minLoc_iterResSumRecord]
		else:
			self.currentSnippetIsUpdating = True
			self.currentProcessingSnippetDataBuffer.append(_newData)
			self.currentProcessingSnippetTimeBuffer.append(_adjustNewTime)
			self.currentProcessingSnippetNewestFittingParams = None
		# 检查当前片段是否正在更新，否，则不在当前片段中接收新的数据，将新数据放入新的片段中
		if self.currentSnippetIsUpdating:
			pass
		else:
			self.currentProcessingSnippetDataBuffer = [_newData]
			self.currentProcessingSnippetTimeBuffer = [_adjustNewTime]

	def trendAnalyze(self, **kwargs):
		"""
		片段趋势分析

		:param kwargs:
			verbose, bool 是否打印片段趋势的决策过程信息
		:return: None
		"""
		# 当当前片段没有更新时（新的数据触发当前片段收口）
		if not self.currentSnippetIsUpdating:
			# 如果不存在上一片段（初始化过程），则使用当前片段的相关参数进行初始化
			if self.lastSnippet_fittingParams is None:
				self.lastSnippet_dataQuant = self.currentProcessingSnippetQuant
				self.lastSnippet_fittingParams = self.currentProcessingSnippetNewestFittingParams
			# 趋势分析
			self._Id = linearFunc(self.currentProcessingSnippetNewestFittingParams, 0) - linearFunc(
				self.lastSnippet_fittingParams, self.lastSnippet_dataQuant - 1)
			self._Is = linearFunc(self.currentProcessingSnippetNewestFittingParams,
			                      self.currentProcessingSnippetQuant - 1) - linearFunc(
				self.currentProcessingSnippetNewestFittingParams, 0)
			self._I = linearFunc(self.currentProcessingSnippetNewestFittingParams,
			                     self.currentProcessingSnippetQuant - 1) - linearFunc(self.lastSnippet_fittingParams,
			                                                                          self.lastSnippet_dataQuant - 1)
			self.trendSymbol_instant = decisionTree(self._Id, self._I, self._Is, self.htc, self.hts,
			                                        verbose=kwargs['verbose'] if 'verbose' in kwargs.keys() else None)
			# 更新（上次）片段的相关参数记录
			self.lastSnippet_dataQuant = self.currentProcessingSnippetQuant
			self.lastSnippet_fittingParams = self.currentProcessingSnippetNewestFittingParams

	@staticmethod
	def fittingResultCalculate(_eachSnippetDataQuantRecord, _eachSnippetParamRecord, _trendSymbol_instant_record):
		"""
		使用[各片段数据量]、[各片段拟合参数]、[各片段瞬时趋势符号]计算所有片段的拟合值,同时原样输出[各片段瞬时趋势符号],
		及各片段在原始数据中结束位置的集合

		:param _eachSnippetDataQuantRecord: list[int],
				其中元素表示i位置(即第i号片段)的长度为Xi,与所有片段趋势集合_trendSymbol_instant_record位置i的片段趋势符号对应,
				如[30,40,31,32,...]与[G,E,Ax,Ax,...]中,30表示,在原始数据集合中,0~30的元素为一个G片段,40表示,在原始数据集合中,
				[30, 70)的元素为一个E片段
		:param _eachSnippetParamRecord: list,
				其中元素表示i位置(即第i号片段)的拟合参数为Xi,与所有片段趋势集合_trendSymbol_instant_record位置i的片段趋势符号对应
		:param _trendSymbol_instant_record: int
				其中元素表示i位置(即第i号片段)的趋势符号
		:return: 包含三个键: fitResult, symbols, symbol_locs.其中, fitResult表示, 所有数据的拟合结果,数据量与原始数据量可能有稍许出入,
				但差值不超过[最小拟合数据量限值]; symbols表示, 所有片段的原始(瞬时)趋势符号, symbol_locs表示, 与symbols中元素对应,
				表示当前片段在原始数据中的结束位置
		"""
		fittingResult = []
		for i in range(len(_eachSnippetDataQuantRecord)):
			x = np.arange(0, _eachSnippetDataQuantRecord[i])
			for j in x:
				y = linearFunc(_eachSnippetParamRecord[i], j)
				fittingResult.append(y)
		return {
			"fitResult": fittingResult,
			"symbols": _trendSymbol_instant_record,
			"symbol_locs": np.cumsum(_eachSnippetDataQuantRecord)
		}

	@staticmethod
	def slowlyDriftAdjust(originData: list, originSymbols: list, originSymbol_locs: list, coverage=0.6, hts=0.6,
	                      replaceAx=True):
		"""
		使用原始数据、原始数据的片段趋势粗析结果、原始数据的片段分割位置集合，进行缓慢飘移检测。输出检测后的各片段趋势符号集合。

		:param originData: list[float],
				需要进行缓慢飘移检测的原始数据,e.g. [1.1, 2.2, 3.3, 4.4, 5.5]
		:param originSymbols: list[str],
				已经进行片段趋势粗析的结果集合,e.g. ["Ax", "B", "Ax", "C", "D", "E", "F", "G"]
		:param originSymbol_locs: list[int],
				其中元素表示该位置（原始数据集合中的位置）与前序元素间的数据片段趋势对应originSymbols中元素所代表的的趋势符号,
				值得注意的是,集合内的元素表示相对于前序元素的位置间隔,如[30,60,90,120,150,180,210,...]与[G,E,Ax,Ax,Ax,D,Ax,...]中,
				30表示,在原始数据集合originData中,0~30的元素为一个G片段,60表示,在原始数据集合originData中,30~60的元素为一个E片段
		:param coverage: float ∈(0, 1],
				一组原始片段[Ax, Ax, Ax, Ax, Ax, Ax, Ax, Ax], 如果依据对原始数据的飘移检测发现，其大部分应为B/C,
				则根据B/C的覆盖百分比coverage判断是否应当将原始片段全部置为[B/C]*n, default 0.6, e.g. [11, 22, 33, 44, 55]
		:param hts: float,
				当片段i-1与i连续时，用于判断片段i为不变、上升/下降的阈值
				当片段i-1与i不连续时，用于判断片段i为正步/负步、上升/下降/上-下瞬变/下-上瞬变的阈值
		:param replaceAx: boolean,
				是否替换所有Ax为A,default True
		:return: 检测后的各片段趋势符号集合,集合中不应有过多的Ax存在,且在输入originSymbols中连续出现的"Ax"必须被替换为A/B/C或
				其排列组合的集合,e.g. ["A", "B", "Ax", "C", "D", "E", "F", "G"]
		"""
		_locs = []
		_adjustSymbols = originSymbols.copy()
		for i, item in enumerate(_adjustSymbols):
			if item == "Ax":
				if not _locs:
					_locs.append(i)
				else:
					_locs.append(i)
			else:
				if _locs:
					_originData = None
					_originMax, _originMin = None, None
					if len(_locs) != 1:
						_sectionStart = originSymbol_locs[_locs[0]]
						_sectionEnd = originSymbol_locs[_locs[-1]]
						_originData = originData[_sectionStart: _sectionEnd + 1]
						_originMax, _originMin = max(_originData), min(_originData)
					if _originData and (_originMax - _originMin >= hts):
						_maxLocs = np.where(np.array(_originData) == _originMax)[0]
						_minLocs = np.where(np.array(_originData) == _originMin)[0]
						if np.average(_maxLocs) > np.average(_minLocs):
							if (_maxLocs[-1] - _minLocs[0]) / len(_originData) >= coverage:
								for j in _locs:
									_adjustSymbols[j] = "B"
							else:
								_slowlyDriftStart = int(np.around(_minLocs[0] / len(_originData) * len(_locs)))
								_slowlyDriftLastfor = int(
									np.around((_maxLocs[-1] - _minLocs[0]) / len(_originData) * len(_locs)))
								cache = ["A"] * _slowlyDriftStart + \
								        ["B"] * _slowlyDriftLastfor + \
								        ["A"] * (len(_locs) - _slowlyDriftStart - _slowlyDriftLastfor)
								for m in range(len(cache)):
									_adjustSymbols[_locs[m]] = cache[m]
						else:
							if (_minLocs[-1] - _maxLocs[0]) / len(_originData) >= coverage:
								for j in _locs:
									_adjustSymbols[j] = "C"
							else:
								_slowlyDriftStart = int(np.around(_maxLocs[0] / len(_originData) * len(_locs)))
								_slowlyDriftLastfor = int(
									np.around((_minLocs[-1] - _maxLocs[0]) / len(_originData) * len(_locs)))
								cache = ["A"] * _slowlyDriftStart + \
								        ["C"] * _slowlyDriftLastfor + \
								        ["A"] * (len(_locs) - _slowlyDriftStart - _slowlyDriftLastfor)
								for k in range(len(cache)):
									_adjustSymbols[_locs[k]] = cache[k]
					_locs = []
		if replaceAx:
			_adjustSymbols = ["A" if item == "Ax" else item for item in _adjustSymbols]
		return _adjustSymbols


class QualitativeTrendDiagnosis:
	def __init__(self, instantSymbols, adjustSymbols, deltaTimes, timeStarts, timeEnds, dataStarts, dataEnds, **kwargs):
		self.__instantSymbols = instantSymbols
		self.__adjustSymbols = adjustSymbols
		self.__deltaTimes = deltaTimes
		self.__timeStarts = timeStarts
		self.__timeEnds = timeEnds
		self.__dataStarts = dataStarts
		self.__dataEnds = dataEnds
		self.__ADD_TRANSFERRED_TIMESTAMP = kwargs['timeTransfer'] if "timeTransfer" in kwargs.keys() else False
		__rawTrendAnalysisResult = {"instantSymbols": self.__instantSymbols,
		                            "adjustSymbols": self.__adjustSymbols,
		                            "deltaTimes": self.__deltaTimes,
		                            "timeStarts": self.__timeStarts,
		                            "timeEnds": self.__timeEnds,
		                            "dataStarts": self.__dataStarts,
		                            "dataEnds": self.__dataEnds}
		if self.__ADD_TRANSFERRED_TIMESTAMP:
			__timeStartsTransferred = list(
				map(lambda x: datetime.datetime.fromtimestamp(x).strftime("%Y-%m-%d %H:%M:%S"),
				    self.__timeStarts))
			__timeEndsTransferred = list(
				map(lambda x: datetime.datetime.fromtimestamp(x).strftime("%Y-%m-%d %H:%M:%S"),
				    self.__timeEnds))
			__rawTrendAnalysisResult = {**__rawTrendAnalysisResult, **{"timeStartsTrans": __timeStartsTransferred,
			                                                           "timeEndsTrans": __timeEndsTransferred}}
		self.trendAnalysisResult = pd.DataFrame(__rawTrendAnalysisResult)
		self.mergeResults = []
		self.identifyResults = []

	def diagnosis(self, regulation):
		snippetSymbols2Find = regulation["snippetSymbols2Find"].replace("|", "")
		snippetTimeCondition = regulation["snippetDeltaTimeLimits"].split("|")
		snippetValueCondition = regulation["snippetRangeValueLimits"].split("|")
		snippetSymbols2FindFrom_list = self.trendAnalysisResult["adjustSymbols"].values
		snippetSymbols2FindFrom_str = "".join(snippetSymbols2FindFrom_list)
		_pattern = re.compile(snippetSymbols2Find)  # 正则化编译规则
		matchElements = _pattern.findall(snippetSymbols2FindFrom_str)  # 按规则查找,并输出匹配项
		matchElementLocs = []
		matchElementLengths = []
		for item in matchElements:
			matchElementLocs.append(snippetSymbols2FindFrom_str.find(item))
			matchElementLengths.append(len(item))
		for i, item in enumerate(matchElementLocs):
			eachMatchResult = self.trendAnalysisResult.iloc[item: item + matchElementLengths[i]]
			"""
			整理单次匹配结果,输出:
			缓慢飘移检测后的片段符号、
			片段合并后的时间间隔、
			片段合并后的起始时间unixtime、
			片段合并后的结束时间unixtime、
			片段合并后的起始数值、
			片段合并后的结束数值、
			片段合并后的起始时间strftime
			片段合并后的结束时间strftime
			"""
			mergeResult = diagnosisResultMerge(eachMatchResult)
			identifyResult = diagnosisResultIdentify(mergeResult, snippetTimeCondition, snippetValueCondition)
			self.mergeResults.append(mergeResult)
			self.identifyResults.append(identifyResult)  # TODO:对合并之后的片段进行条件判断，输出Bool
			# identifyResult.append(mergeResult)


def diagnosisResultMerge(_eachMatchResult):
	_eachMatchResultMerge = {
		"MergedAdjustSymbols": [], "MergedDeltaTimes": [],
		"MergedTimeStartsUnix": [], "MergedTimeEndsUnix": [],
		"MergedDataStarts": [], "MergedDataEnds": [],
		"MergedTimeStarts": [], "MergedTimeEnds": []
	}

	symbols = _eachMatchResult["adjustSymbols"].values.tolist()
	symbols.append("-/-")
	_symbolRecord = [None]
	_locRecord = []
	mergeResult = {"adjustSymbol": [],"deltaTime": [],"timeStart": [],"timeEnd": [],"dataStart": [],"dataEnd": [],"timeStartTrans": [],"timeEndTrans": []}
	mergeResult = pd.DataFrame(mergeResult)
	for i, item in enumerate(symbols):
		res = None
		if _symbolRecord[-1] is None:
			_symbolRecord = [item]
			_locRecord = [i]
		elif _symbolRecord[-1] == item:
			_symbolRecord.append(item)
			_locRecord.append(i)
		else:
			res = merge(_eachMatchResult, _symbolRecord, _locRecord)
			_symbolRecord = [item]
			_locRecord = [i]
		if res is not None:
			mergeResult = pd.concat([mergeResult, res])
	return mergeResult.reset_index(drop=True)


def merge(_eachMatchResult, _symbolRecord, _locRecord):
	adjustSymbol = _eachMatchResult["adjustSymbols"].iloc[_locRecord[0]][0]
	deltaTime = np.sum(_eachMatchResult["deltaTimes"].iloc[_locRecord[0]: _locRecord[-1] + 1].values)
	timeStart = np.min(_eachMatchResult["timeStarts"].iloc[_locRecord[0]: _locRecord[-1] + 1].values)
	timeEnd = np.max(_eachMatchResult["timeEnds"].iloc[_locRecord[0]: _locRecord[-1] + 1].values)
	dataStart = _eachMatchResult["dataStarts"].iloc[_locRecord[0]: _locRecord[-1] + 1].values[0]
	dataEnd = _eachMatchResult["dataEnds"].iloc[_locRecord[0]: _locRecord[-1] + 1].values[-1]
	res = {
		"adjustSymbol": adjustSymbol,
		"deltaTime": deltaTime,
		"timeStart": timeStart,
		"timeEnd": timeEnd,
		"dataStart": dataStart,
		"dataEnd": dataEnd,
		"timeStartTrans": datetime.datetime.strftime(datetime.datetime.fromtimestamp(timeStart), "%Y-%m-%d %H:%M:%S"),
		"timeEndTrans": datetime.datetime.strftime(datetime.datetime.fromtimestamp(timeEnd), "%Y-%m-%d %H:%M:%S"),
	}
	return pd.DataFrame([res])


def diagnosisResultIdentify(_mergeResult, _timeLimits, _valueLimits):
	# 输入检查
	if not len(_mergeResult) == len(_timeLimits) == len(_valueLimits):
		raise ValueError(f"入参尺寸错误,"
		                 f"\n\t_mergeResult:\n\t\tlength:{len(_mergeResult)}"
		                 f"\n\t_timeLimits:\n\t\tlength:{len(_timeLimits)}"
		                 f"\n\t_valueLimits:\n\t\tlength:{len(_valueLimits)}")
	# 对deltaTime的条件分段
	for i in range(len(_timeLimits)):
		if ("and" not in _timeLimits[i]) and ("or" not in _timeLimits[i]):
			pass
		elif "and" in _timeLimits[i]:
			_timeLimits[i] = "(" + _timeLimits[i].replace(" and ", ") and (") + ")"
		elif "or" in _timeLimits[i]:
			_timeLimits[i] = "(" + _timeLimits[i].replace(" or ", ") or (") + ")"
		else:
			raise ValueError(f"入参错误,{_timeLimits[i]}")
	# 对data的条件分段
	for i in range(len(_valueLimits)):
		if ("and" not in _valueLimits[i]) and ("or" not in _valueLimits[i]):
			pass
		elif "and" in _valueLimits[i]:
			_valueLimits[i] = "(" + _valueLimits[i].replace(" and ", ") and (") + ")"
		elif "or" in _valueLimits[i]:
			_valueLimits[i] = "(" + _valueLimits[i].replace(" or ", ") or (") + ")"
		else:
			raise ValueError(f"入参错误,{_valueLimits[i]}")
	# 对deltaTime的条件判断
	_commandResults = []
	for i in range(len(_mergeResult)):
		_commandStr = _timeLimits[i].replace("t", str(_mergeResult["deltaTime"].values[i]))
		_commandResults.append(eval(_commandStr))
	timeConditionIdentifyRes = all(_commandResults)
	# 对data的条件判断
	_commandResults = []
	for i in range(len(_mergeResult)):
		_commandStr = _valueLimits[i]
		for item in ["<=v", "v>=", "<v", "v>"]:
			if item in _valueLimits[i]:
				_v = min(_mergeResult["dataStart"].iloc[i], _mergeResult["dataEnd"].iloc[i])
				if item[-1] == "v":
					cache = item.replace("v", "") + str(_v)
				else:
					cache = str(_v) + item.replace("v", "")
				_commandStr = _commandStr.replace(item, cache)
		for item in [">=v", "v<=", ">v", "v<"]:
			if item in _valueLimits[i]:
				_v = max(_mergeResult["dataStart"].iloc[i], _mergeResult["dataEnd"].iloc[i])
				if item[-1] == "v":
					cache = item.replace("v", "") + str(_v)
				else:
					cache = str(_v) + item.replace("v", "")
				_commandStr = _commandStr.replace(item, cache)
		_commandResults.append(eval(_commandStr))
	dataConditionIdentifyRes = all(_commandResults)
	return all([timeConditionIdentifyRes, dataConditionIdentifyRes])