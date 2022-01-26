class RotorWindingTemperRise:
	"""
	使用解析法Scu2=1.512x(10^-5)(If^2)-1.5计算转子绕组理论温升，并使用实测温升与对应励磁电流下理论温升比值作为输出

	[1] 方法
	----------
	temperRiseCal:
	    计算温升理论值。

	temperRiseRateCal:
	    计算温升实测值与理论值比值

	[2] 返回
	-------
	temperRise_theoretic:
	    理论温升

	temperRiseRate:
	    实测值与理论温升比值

	[3] 示例1
	--------
	>>> rotorWindingTemperRiseObj = RotorWindingTemperRise()
	>>> res_rate = []
	>>> res_theory = []
	>>> for item in current:
	>>> 	rotorWindingTemperRiseObj.temperRiseCal(item*10 + 1833)
	>>> 	rotorWindingTemperRiseObj.temperRiseRateCal(50)
	>>> 	res_theory.append(rotorWindingTemperRiseObj.temperRise_theoretic)
	>>> 	res_rate.append(rotorWindingTemperRiseObj.temperRiseRate)
	>>> plt.plot(res_theory)
	>>> plt.plot(res_rate)
	>>> plt.show()

	[4] 备注
	-----
	* 当需要进行相关判断的值为各种逻辑聚合值时（如某测点近期均值），需要在外部进行预处理
	* 当需要进行热稳定判断时，需要在外部进行判断

	"""

	def __init__(self):
		# ===== 输出 ===== #
		self.temperRise_theoretic = None
		self.temperRiseRate = None

	def temperRiseCal(self, current: float):
		"""
		计算温升

		:param current: float,实测电流
		:return: None,℃
		"""
		self.temperRise_theoretic = 1.512*(10**-5)*(current**2)-1.5

	def temperRiseRateCal(self, measuredTemperRise: float):
		"""
		计算温升实测值与理论值比值

		:param measuredTemperRise: float, 实测温升,℃
		:return: None
		"""
		self.temperRiseRate = measuredTemperRise / self.temperRise_theoretic
