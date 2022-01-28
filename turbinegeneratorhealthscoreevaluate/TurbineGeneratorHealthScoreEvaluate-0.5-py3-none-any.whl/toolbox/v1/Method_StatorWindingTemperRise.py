class StatorWindingTemperRise:
	"""
	使用解析法Scu1=6.83x(10^-7)(I^2)+16.38计算定子绕组理论温升，并使用实测温升与对应电流下理论温升比值作为输出

	[1] 参数
	----------
	U0:
	    float, 额定电压,optional,默认20000

	[2] 方法
	----------
	temperRiseCal:
	    计算温升理论值。
	    当输入只有current时，使用预训练的参数进行计算，当输入还包括a、b、c、d、e时，使用新的系数进行计算。

	temperRiseRateCal:
	    计算温升实测值与理论值比值

	[3] 返回
	-------
	temperRise_theoretic:
	    理论温升

	temperRiseRate:
	    实测值与理论温升比值

	[4] 示例1
	--------
	>>> statorWindingTemperRiseObj = StatorWindingTemperRise()
	>>> res_cal = []
	>>> res_theory = []
	>>> for item in current:
	>>> 	statorWindingTemperRiseObj.temperRiseCal(item*10 + 8128)
	>>> 	# statorWindingTemperRiseObj.temperRiseCal(item*10 + 8128, voltage=20000, a=1, b=1, c=1, d=1, e=1)
	>>> 	statorWindingTemperRiseObj.temperRiseRateCal(60)
	>>> 	res_cal.append(statorWindingTemperRiseObj.temperRiseRate)
	>>> 	res_theory.append(statorWindingTemperRiseObj.temperRise_theoretic)
	>>> plt.plot(res_theory)
	>>> plt.show()

	[6] 备注
	-----
	* 当需要进行相关判断的值为各种逻辑聚合值时（如某测点近期均值），需要在外部进行预处理
	* 当需要进行热稳定判断时，需要在外部进行判断

	"""

	def __init__(self, **kwargs):
		keys = kwargs.keys()
		# ===== 内部参数 ===== #
		# 额定电压
		self.__U0 = kwargs["U0"] if "U0" in keys else 20000
		# ===== 输出 ===== #
		self.temperRise_theoretic = None
		self.temperRiseRate = None

	def __cal_kUd(self, U: float):
		"""
		计算电压变化率

		:param U: float 实测电压，单位V
		:return: None
		"""
		self.__kUd = U / self.__U0

	@staticmethod
	def equation(kUd, current, a, b, c, d, e):
		"""
		根据拟合公式计算定子绕组温升解析计算值

		:param kUd: float, 电压变化率
		:param current: float, 实测电流
		:param a: float,模型参数
		:param b: float,模型参数
		:param c: float,模型参数
		:param d: float,模型参数
		:param e: float,模型参数
		:return: float 定子绕组温升解析计算值
		"""
		return a*current**2 + b*current + c*kUd**2 + d / kUd + e

	def temperRiseCal(self, current: float, **kwargs):
		"""
		计算温升。当输入只有current时，使用预训练的参数进行计算，当输入还包括a、b、c、d、e时，使用新的系数进行计算。

		:param current: float,实测电流
		:param kwargs: dict,定子绕组温升解析计算公式参数,包括a、b、c、d、e
		:return: None,℃
		"""
		if len(kwargs.keys()) > 0:
			self.__cal_kUd(kwargs["voltage"])  # 计算kUd
			self.temperRise_theoretic = self.equation(self.__kUd, current, kwargs["a"], kwargs["b"], kwargs["c"], kwargs["d"], kwargs["e"])
		else:
			self.temperRise_theoretic = 6.83*(10**(-7))*(current**2)+16.38

	def temperRiseRateCal(self, measuredTemperRise: float):
		"""
		计算温升实测值与理论值比值

		:param measuredTemperRise: float, 实测温升，℃
		:return: None
		"""
		self.temperRiseRate = measuredTemperRise / self.temperRise_theoretic
