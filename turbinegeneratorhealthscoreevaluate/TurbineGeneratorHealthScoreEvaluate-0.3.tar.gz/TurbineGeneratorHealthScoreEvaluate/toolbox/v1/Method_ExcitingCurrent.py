import numpy as np


class ExcitingCurrent:
	"""
	使用解析法If=1.7307*U^2-1.6628*U+0.9431计算开机升压过程励磁电流，并使用实测值(归一化值)与对应三相电压均值下的理论值(归一化值)比值作为输出

	[1] 方法
	----------
	excitingCurrentCal:
	    根据三相电压均值(归一化值)计算励磁电流理论值(归一化值)

	excitingCurrentRateCal:
	    计算励磁电流实测值(归一化值)与理论值(归一化值)比值

	[2] 返回
	-------
	excitingCurrent_theoretic:
	    励磁电流理论值(归一化值)

	excitingCurrentRate:
	    励磁电流实测值（归一化值）与理论值(归一化值)比值

	[3] 示例1
	--------
	>>> excitingCurrentObj = ExcitingCurrent()
	>>> res_rate = []
	>>> res_theory = []
	>>> for item in voltage:
	>>> 	excitingCurrentObj.excitingCurrentCal(7.967+item/100, 7.967+item/100, 7.967+item/100)
	>>> 	excitingCurrentObj.excitingCurrentRateCal(1084.861+item/100)
	>>> 	res_theory.append(excitingCurrentObj.excitingCurrent_theoretic)
	>>> 	res_rate.append(excitingCurrentObj.excitingCurrentRate)
	>>> plt.plot(res_rate)
	>>> plt.twinx()
	>>> plt.plot(res_theory, color='red', alpha=0.2, linestyle=":")
	>>> plt.show()

	[4] 备注
	-----
	* 当需要进行相关判断的值为各种逻辑聚合值时（如某测点近期均值），需要在外部进行预处理
	* 当需要进行热稳定判断时，需要在外部进行判断

	"""

	def __init__(self, **kwargs):
		keys = kwargs.keys()
		# ===== 外部参数 ===== #
		self._basicExcitingCurrent = kwargs["basicExcitingCurrent"] if "basicExcitingCurrent" in keys else 1084.861
		self._basic3PhasesVoltagesAvg = kwargs["basic3PhasesVoltagesAvg"] if "basic3PhasesVoltagesAvg" in keys else 7.967
		# ===== 输出 ===== #
		self.excitingCurrent_theoretic = None
		self.excitingCurrentRate = None

	def excitingCurrentCal(self, Ua: float, Ub: float, Uc: float):
		"""
		根据三相电压均值(归一化值)计算励磁电流理论值(归一化值)

		:param Ua: float,A相电压,kV
		:param Ub: float,B相电压,kV
		:param Uc: float,C相电压,kV
		:return: None,无量纲,归一化值
		"""
		U = np.average([Ua, Ub, Uc]) / self._basic3PhasesVoltagesAvg
		self.excitingCurrent_theoretic = 1.7307*(U**2)-1.6628*U+0.9431

	def excitingCurrentRateCal(self, excitingCurrent: float):
		"""
		计算励磁电流实测值(归一化值)与理论值(归一化值)比值

		:param excitingCurrent: float, 实测励磁电流，A
		:return: None
		"""
		self.excitingCurrentRate = excitingCurrent / self._basicExcitingCurrent / self.excitingCurrent_theoretic
