import numpy as np
from .GenericMethods import localOutlierFilter


class StatorThermalStabilityDetermine:
	def __init__(self, **kwargs):
		"""
		TODO:在部署时,需要测试是否能够使用globals()的方式从环境中获取变量
		根据各个测点的稳定状态持续最小时间限值、稳定状态数据最大峰峰限值，综合判定定子是否处于热稳定态

		[1] 参数
		----------
		apparentPowerStablePeriodLimit:
		    float,视在功率热稳定判定时间限值(秒),即,视在功率的判定时间区间不应小于该范围,默认4*3600
		apparentPowerStableValueLimit:
		    float,视在功率热稳定判定数据限值(MVA),即,视在功率的判定时间内,峰峰值不应大于该值,默认5
		airCoolerInletTemperStablePeriodLimit:
		    float,空冷器进水温度热稳定判定时间限值(秒),即,空冷器进水温度的判定时间区间不应小于该范围,默认3600
		airCoolerInletTemperStableValueLimit:
		    float,空冷器进水温度热稳定判定数据限值(℃),即,空冷器进水温度的判定时间内,峰峰值不应大于该值,默认0.5
		statorTemperStablePeriodLimit:
		    float,定子温度热稳定判定时间限值(秒),即,定子温度的判定时间区间不应小于该范围,默认3600
		statorTemperStableValueLimit:
		    float,定子温度热稳定判定数据限值(℃),即,定子温度的判定时间内,峰峰值不应大于该值,默认1
		coldWindTemperStablePeriodLimit:
		    float,冷风温度热稳定判定时间限值(秒),即,冷风温度的判定时间区间不应小于该范围,默认3600
		coldWindTemperStableValueLimit:
		    float,冷风温度热稳定判定数据限值(℃),即,冷风温度的判定时间内,峰峰值不应大于该值,默认0.5
		hotWindTemperStablePeriodLimit:
		    float,热风温度热稳定判定时间限值(秒),即,热风温度的判定时间区间不应小于该范围,默认3600
		hotWindTemperStableValueLimit:
		    float,热风温度热稳定判定数据限值(℃),即,热风温度的判定时间内,峰峰值不应大于该值,默认0.5
		airCoolerOutletTemperStablePeriodLimit:
		    float,空冷器出水温度热稳定判定时间限值(秒),即,空冷器出水温度的判定时间区间不应小于该范围,默认3600
		airCoolerOutletTemperStableValueLimit:
		    float,空冷器出水温度热稳定判定数据限值(℃),即,空冷器出水温度的判定时间内,峰峰值不应大于该值,默认0.5
		iqrCoef:
		    float,进行峰峰值计算前,使用IQR方法进行离群点筛查时的IQR系数,默认1.5

		[2] 方法
		----------
		updateRecord:
			更新时间戳及所有进行定子热稳定判断所需的变量;判定当前样本输入后,各测点及其历史缓存是否支持"定子热稳定"

		[3] 返回
		----------
		determineResultGroup:
		    所有判据在当期的判断结果集合

		statorThermalStableStatus:
		    定子热稳定状态判断结果

		[4] 示例1
		----------
		>>> obj = StatorThermalStabilityDetermine()
		>>> itemRecord = []
		>>> resRecord = []
		>>> for i in range(1000):
		>>>     if i < 500:
		>>>         item = 50 + np.random.random() * 10
		>>>     else:
		>>>         item = 50 + np.random.random() / 10
		>>>     itemRecord.append(item)
		>>>     obj.updateRecord(timestamp=1551230000 + i * 300, apparentPower=item, airCoolerInletTemper=item,
		>>>                  statorTemper=item, coldWindTemper=item, hotWindTemper=item, airCoolerOutletTemper=item)
		>>>     resRecord.append(int(obj.statorThermalStableStatus))
		>>> plt.plot(resRecord, "red")
		>>> plt.twinx()
		>>> plt.plot(itemRecord)
		>>> plt.show()

		[5] 备注
		-----
		* 只支持单个同类测点的实测值输入

		"""
		keys = kwargs.keys()
		# ===== 外部参数 ===== #
		# 视在功率限制
		self._apparentPowerStablePeriodLimit = kwargs[
			"apparentPowerStablePeriodLimit"] if "apparentPowerStablePeriodLimit" in keys else 4 * 3600
		self._apparentPowerStableValueLimit = kwargs[
			"apparentPowerStableValueLimit"] if "apparentPowerStableValueLimit" in keys else 5
		# 空冷器进口水温限制
		self._airCoolerInletTemperStablePeriodLimit = kwargs[
			"airCoolerInletTemperStablePeriodLimit"] if "airCoolerInletTemperStablePeriodLimit" in keys else 3600
		self._airCoolerInletTemperStableValueLimit = kwargs[
			"airCoolerInletTemperStableValueLimit"] if "airCoolerInletTemperStableValueLimit" in keys else 0.5
		# 定子温度限制
		self._statorTemperStablePeriodLimit = kwargs[
			"statorTemperStablePeriodLimit"] if "statorTemperStablePeriodLimit" in keys else 3600
		self._statorTemperStableValueLimit = kwargs[
			"statorTemperStableValueLimit"] if "statorTemperStableValueLimit" in keys else 1
		# 冷风温度限制
		self._coldWindTemperStablePeriodLimit = kwargs[
			"coldWindTemperStablePeriodLimit"] if "coldWindTemperStablePeriodLimit" in keys else 3600
		self._coldWindTemperStableValueLimit = kwargs[
			"coldWindTemperStableValueLimit"] if "coldWindTemperStableValueLimit" in keys else 0.5
		# 热风温度限制
		self._hotWindTemperStablePeriodLimit = kwargs[
			"hotWindTemperStablePeriodLimit"] if "hotWindTemperStablePeriodLimit" in keys else 3600
		self._hotWindTemperStableValueLimit = kwargs[
			"hotWindTemperStableValueLimit"] if "hotWindTemperStableValueLimit" in keys else 0.5
		# 空冷器出口水温限制
		self._airCoolerOutletTemperStablePeriodLimit = kwargs[
			"airCoolerOutletTemperStablePeriodLimit"] if "airCoolerOutletTemperStablePeriodLimit" in keys else 3600
		self._airCoolerOutletTemperStableValueLimit = kwargs[
			"airCoolerOutletTemperStableValueLimit"] if "airCoolerOutletTemperStableValueLimit" in keys else 0.5
		# LOF监测IQR方法系数
		self._iqrCoef = kwargs["iqrCoef"] if "iqrCoef" in keys else 1.5
		# ===== 内部参数 ===== #
		self.__apparentPowerRecord = []
		self.__airCoolerInletTemperRecord = []
		self.__statorTemperRecord = []
		self.__coldWindTemperRecord = []
		self.__hotWindTemperRecord = []
		self.__airCoolerOutletTemperRecord = []
		# ===== 输出参数 ===== #
		self.determineResultGroup = []
		self.statorThermalStableStatus = None

	def __determine_and_refreshRecord(self, itemName, privateName="_StatorThermalStabilityDetermine"):
		"""
		根据各个测点的稳定状态持续最小时间限值、稳定状态数据最大峰峰限值，综合各测点判定定子是否处于热稳定态；当各测点数据时间超出用于判定
		其稳定态所需的最小时间限值时，更新缓存

		- 峰峰值计算前，使用IQR的离群点检测方法过滤突变点

		:param itemName: str, 需要进行稳定性判断的对象测点名称，如"apparentPower", "airCoolerInletTemper", "statorTemper", "coldWindTemper", "hotWindTemper", "airCoolerOutletTemper"等
		:param privateName: str, 给调用对象内部参数__getAttribute__使用的类名称，默认"_StatorThermalStabilityDetermine"
		:return: None
		"""
		timeBuffer = []
		dataBuffer = []
		[timeBuffer.append(zipItem[0]) for zipItem in self.__getattribute__(privateName + "__" + itemName + "Record")]
		[dataBuffer.append(zipItem[-1]) for zipItem in self.__getattribute__(privateName + "__" + itemName + "Record")]
		locs2Determine = np.where(
			np.asarray(timeBuffer) >= (timeBuffer[-1] - self.__getattribute__("_" + itemName + "StablePeriodLimit")),
			True, False)
		timeBuffer = np.asarray(timeBuffer)[locs2Determine]
		dataBuffer = np.asarray(dataBuffer)[locs2Determine]
		dataBuffer = localOutlierFilter(dataBuffer, coef=self._iqrCoef)
		peak2peakRangeLowerThanThreshold = max(dataBuffer) - min(dataBuffer) <= self.__getattribute__(
			"_" + itemName + "StableValueLimit")
		determineSectionIsLongEnough = (
			timeBuffer[-1] - timeBuffer[0] >= self.__getattribute__("_" + itemName + "StablePeriodLimit"))
		if peak2peakRangeLowerThanThreshold and determineSectionIsLongEnough:
			self.determineResultGroup.append(True)  # 热稳定
		else:
			self.determineResultGroup.append(False)  # 非热稳定
		cache = np.asarray(self.__getattribute__(privateName + "__" + itemName + "Record"))[locs2Determine].tolist()
		self.__setattr__(privateName + "__" + itemName + "Record", cache)

	def updateRecord(self, timestamp, **kwargs):
		"""
		更新时间戳及所有进行定子热稳定判断所需的变量;判定当前样本输入后,各测点及其历史缓存是否支持"定子热稳定"

        :param timestamp: 样本时间戳(秒),unixTimestamp
        :type timestamp: int
        :key apparentPower: 视在功率(MVA)
        :key airCoolerInletTemper: 空冷器进水口水温(℃)
        :key airCoolerOutletTemper: 空冷器出水口水温(℃)
        :key statorTemper: 定子温度(℃)
        :key coldWindTemper: 冷风温度(℃)
        :key hotWindTemper: 热风温度(℃)
        :return: None
        :rtype: None
		"""
		privateName = "_StatorThermalStabilityDetermine"
		names = ["apparentPower", "airCoolerInletTemper", "statorTemper", "coldWindTemper", "hotWindTemper",
		         "airCoolerOutletTemper"]
		# 更新数据Record
		[self.__getattribute__(privateName + "__" + item + "Record").append((timestamp, kwargs[item])) for item in
		 names]
		# 判定各测点及其历史缓存是否支持"定子热稳定"，并更新各测点缓存
		[self.__determine_and_refreshRecord(item, privateName) for item in names]
		self.statorThermalStableStatus = all(self.determineResultGroup)
		self.determineResultGroup = []


class ThrustBearingThermalStabilityDetermine:
	def __init__(self, **kwargs):
		"""
		根据各个测点的稳定状态持续最小时间限值、稳定状态数据最大峰峰限值，综合判定推力轴承是否处于热稳定态

		[1] 参数
		----------
		thrustBearingInletTemperStablePeriodLimit:
		    float,推力轴承进口水温热稳定判定时间限值(秒),即,判定时间区间不应小于该范围,默认4*3600
		thrustBearingInletTemperStableValueLimit:
		    float,推力轴承进口水温热稳定判定数据限值(℃),即,判定时间内峰峰值不应大于该值,默认0.5
		thrustBearingOutletTemperStablePeriodLimit:
		    float,推力轴承进口水温热稳定判定时间限值(秒),即,判定时间区间不应小于该范围,默认3600
		thrustBearingOutletTemperStablePeriodLimit:
		    float,推力轴承进口水温热稳定判定数据限值(℃),即,判定时间内峰峰值不应大于该值,默认0.5
		thrustBearingPadTemperStablePeriodLimit:
		    float,推力轴承瓦温热稳定判定时间限值(秒),即,判定时间区间不应小于该范围,默认3600
		thrustBearingPadTemperStablePeriodLimit:
		    float,推力轴承瓦温热稳定判定数据限值(℃),即,判定时间内峰峰值不应大于该值,默认0.5
		thrustBearingOilTemperStablePeriodLimit:
		    float,推力轴承油温热稳定判定时间限值(秒),即,判定时间区间不应小于该范围,默认3600
		thrustBearingOilTemperStablePeriodLimit:
		    float,推力轴承油温热稳定判定数据限值(℃),即,判定时间内峰峰值不应大于该值,默认0.5
		thrustBearingOilTemperStablePeriodLimit:
		    float,推力轴承油温热稳定判定数据限值(℃),即,判定时间内峰峰值不应大于该值,默认0.5
		thrustBearingOilTemperStablePeriodLimit:
		    float,推力轴承油温热稳定判定数据限值(℃),即,判定时间内峰峰值不应大于该值,默认0.5
		iqrCoef:
		    float,进行峰峰值计算前,使用IQR方法进行离群点筛查时的IQR系数,默认1.5

		[2] 方法
		----------
		updateRecord:
			更新时间戳及所有进行推力轴承热稳定判断所需的变量;判定当前样本输入后,各测点及其历史缓存是否支持"推力轴承热稳定"

		[3] 返回
		----------
		determineResultGroup:
		    所有判据在当期的判断结果集合

		thrustBearingThermalStableStatus:
		    推力轴承热稳定状态判断结果

		[4] 示例1
		----------
		>>> obj = ThrustBearingThermalStabilityDetermine()
		>>> itemRecord = []
		>>> resRecord = []
		>>> for i in range(1000):
		>>>     if i < 500:
		>>>         item = 50 + np.random.random() * 10
		>>>		else:
		>>>			item = 50 + np.random.random() / 10
		>>>		itemRecord.append(item)
		>>>		obj.updateRecord(timestamp=1551230000 + i * 300, thrustBearingInletTemper=item, thrustBearingOutletTemper=item,
		>>>		                 thrustBearingPadTemper=item, thrustBearingOilTemper=item)
		>>>		resRecord.append(int(obj.thrustBearingThermalStableStatus))
		>>>	plt.plot(resRecord, "red")
		>>>	plt.twinx()
		>>>	plt.plot(itemRecord)
		>>>	plt.show()

		[5] 备注
		-----
		* 只支持单个同类测点的实测值输入

		"""
		keys = kwargs.keys()
		# 推力进口水温限制
		self._thrustBearingInletTemperStablePeriodLimit = kwargs[
			"thrustBearingInletTemperStablePeriodLimit"] if "thrustBearingInletTemperStablePeriodLimit" in keys else 4 * 3600
		self._thrustBearingInletTemperStableValueLimit = kwargs[
			"thrustBearingInletTemperStableValueLimit"] if "thrustBearingInletTemperStableValueLimit" in keys else 0.5
		# 推力出口水温限制
		self._thrustBearingOutletTemperStablePeriodLimit = kwargs[
			"thrustBearingOutletTemperStablePeriodLimit"] if "thrustBearingOutletTemperStablePeriodLimit" in keys else 3600
		self._thrustBearingOutletTemperStableValueLimit = kwargs[
			"thrustBearingOutletTemperStableValueLimit"] if "thrustBearingOutletTemperStableValueLimit" in keys else 0.5
		# 推力瓦温限制
		self._thrustBearingPadTemperStablePeriodLimit = kwargs[
			"thrustBearingPadTemperStablePeriodLimit"] if "thrustBearingPadTemperStablePeriodLimit" in keys else 3600
		self._thrustBearingPadTemperStableValueLimit = kwargs[
			"thrustBearingPadTemperStableValueLimit"] if "thrustBearingPadTemperStableValueLimit" in keys else 0.5
		# 推力油温限制
		self._thrustBearingOilTemperStablePeriodLimit = kwargs[
			"thrustBearingOilTemperStablePeriodLimit"] if "thrustBearingOilTemperStablePeriodLimit" in keys else 3600
		self._thrustBearingOilTemperStableValueLimit = kwargs[
			"thrustBearingOilTemperStableValueLimit"] if "thrustBearingOilTemperStableValueLimit" in keys else 0.5
		# LOF监测IQR方法系数
		self._iqrCoef = kwargs["iqrCoef"] if "iqrCoef" in keys else 1.5
		# ===== 内部参数 ===== #
		self.__thrustBearingInletTemperRecord = []
		self.__thrustBearingOutletTemperRecord = []
		self.__thrustBearingPadTemperRecord = []
		self.__thrustBearingOilTemperRecord = []
		# ===== 输出参数 ===== #
		self.determineResultGroup = []
		self.thrustBearingThermalStableStatus = None

	def __determine_and_refreshRecord(self, itemName, privateName="_ThrustBearingThermalStabilityDetermine"):
		"""
		根据各个测点的稳定状态持续最小时间限值、稳定状态数据最大峰峰限值，综合各测点判定定子是否处于热稳定态；当各测点数据时间超出用于判定
		其稳定态所需的最小时间限值时，更新缓存

		- 峰峰值计算前，使用IQR的离群点检测方法过滤突变点

		:param itemName: str, 需要进行稳定性判断的对象测点名称，如"thrustBearingInletTemper", "thrustBearingOutletTemper", "thrustBearingPadTemper", "thrustBearingOilTemper"等
		:param privateName: str, 给调用对象内部参数__getAttribute__使用的类名称，默认"_ThrustBearingThermalStabilityDetermine"
		:return: None
		"""
		timeBuffer = []
		dataBuffer = []
		[timeBuffer.append(zipItem[0]) for zipItem in
		 self.__getattribute__(privateName + "__" + itemName + "Record")]
		[dataBuffer.append(zipItem[-1]) for zipItem in
		 self.__getattribute__(privateName + "__" + itemName + "Record")]
		locs2Determine = np.where(
			np.asarray(timeBuffer) >= (
					timeBuffer[-1] - self.__getattribute__("_" + itemName + "StablePeriodLimit")),
			True, False)
		timeBuffer = np.asarray(timeBuffer)[locs2Determine]
		dataBuffer = np.asarray(dataBuffer)[locs2Determine]
		dataBuffer = localOutlierFilter(dataBuffer, coef=self._iqrCoef)
		peak2peakRangeLowerThanThreshold = max(dataBuffer) - min(dataBuffer) <= self.__getattribute__(
			"_" + itemName + "StableValueLimit")
		determineSectionIsLongEnough = (
			timeBuffer[-1] - timeBuffer[0] >= self.__getattribute__("_" + itemName + "StablePeriodLimit"))
		if peak2peakRangeLowerThanThreshold and determineSectionIsLongEnough:
			self.determineResultGroup.append(True)  # 热稳定
		else:
			self.determineResultGroup.append(False)  # 非热稳定
		cache = np.asarray(self.__getattribute__(privateName + "__" + itemName + "Record"))[locs2Determine].tolist()
		self.__setattr__(privateName + "__" + itemName + "Record", cache)

	def updateRecord(self, timestamp, **kwargs):
		"""
		更新时间戳及所有进行推力轴承热稳定判断所需的变量;判定当前样本输入后,各测点及其历史缓存是否支持"推力轴承热稳定"

        :param timestamp: 样本时间戳(秒),unixTimestamp
        :type timestamp: int
        :key thrustBearingInletTemper: 推力轴承进口水温(℃)
        :key thrustBearingOutletTemper: 推力轴承出口水温(℃)
        :key thrustBearingPadTemper: 推力轴承瓦温(℃)
        :key thrustBearingOilTemper: 推力轴承油温(℃)
        :return: None
        :rtype: None
		"""
		privateName = "_ThrustBearingThermalStabilityDetermine"
		names = ["thrustBearingInletTemper", "thrustBearingOutletTemper", "thrustBearingPadTemper", "thrustBearingOilTemper"]
		# 更新数据Record
		[self.__getattribute__(privateName + "__" + item + "Record").append((timestamp, kwargs[item])) for item in
		 names]
		# 判定各测点及其历史缓存是否支持"推力轴承热稳定"，并更新各测点缓存
		[self.__determine_and_refreshRecord(item, privateName) for item in names]
		self.thrustBearingThermalStableStatus = all(self.determineResultGroup)
		self.determineResultGroup = []


class GuideBearingThermalStabilityDetermine:
	def __init__(self, **kwargs):
		"""
		根据各个测点的稳定状态持续最小时间限值、稳定状态数据最大峰峰限值，综合判定导轴承是否处于热稳定态

		[1] 参数
		----------
		guideBearingInletTemperStablePeriodLimit:
		    float,导轴承进口水温热稳定判定时间限值(秒),即,判定时间区间不应小于该范围,默认4*3600
		guideBearingInletTemperStableValueLimit:
		    float,导轴承进口水温热稳定判定数据限值(℃),即,判定时间内峰峰值不应大于该值,默认0.5
		guideBearingOutletTemperStablePeriodLimit:
		    float,导轴承进口水温热稳定判定时间限值(秒),即,判定时间区间不应小于该范围,默认3600
		guideBearingOutletTemperStablePeriodLimit:
		    float,导轴承进口水温热稳定判定数据限值(℃),即,判定时间内峰峰值不应大于该值,默认0.5
		guideBearingPadTemperStablePeriodLimit:
		    float,导轴承瓦温热稳定判定时间限值(秒),即,判定时间区间不应小于该范围,默认3600
		guideBearingPadTemperStablePeriodLimit:
		    float,导轴承瓦温热稳定判定数据限值(℃),即,判定时间内峰峰值不应大于该值,默认0.5
		guideBearingOilTemperStablePeriodLimit:
		    float,导轴承油温热稳定判定时间限值(秒),即,判定时间区间不应小于该范围,默认3600
		guideBearingOilTemperStablePeriodLimit:
		    float,导轴承油温热稳定判定数据限值(℃),即,判定时间内峰峰值不应大于该值,默认0.5
		guideBearingOilTemperStablePeriodLimit:
		    float,导轴承油温热稳定判定数据限值(℃),即,判定时间内峰峰值不应大于该值,默认0.5
		guideBearingOilTemperStablePeriodLimit:
		    float,导轴承油温热稳定判定数据限值(℃),即,判定时间内峰峰值不应大于该值,默认0.5
		iqrCoef:
		    float,进行峰峰值计算前,使用IQR方法进行离群点筛查时的IQR系数,默认1.5

		[2] 方法
		----------
		updateRecord:
			更新时间戳及所有进行导轴承热稳定判断所需的变量;判定当前样本输入后,各测点及其历史缓存是否支持"导轴承热稳定"

		[3] 返回
		----------
		determineResultGroup:
		    所有判据在当期的判断结果集合

		guideBearingThermalStableStatus:
		    导轴承热稳定状态判断结果

		[4] 示例1
		----------
		>>> obj = GuideBearingThermalStabilityDetermine()
		>>> itemRecord = []
		>>>	resRecord = []
		>>>	for i in range(1000):
		>>>		if i < 500:
		>>>			item = 50 + np.random.random() * 10
		>>>		else:
		>>>			item = 50 + np.random.random() / 10
		>>>		itemRecord.append(item)
		>>>		obj.updateRecord(timestamp=1551230000 + i * 300, guideBearingInletTemper=item, guideBearingOutletTemper=item,
		>>>		                 guideBearingPadTemper=item, guideBearingOilTemper=item)
		>>>		resRecord.append(int(obj.guideBearingThermalStableStatus))
		>>>	plt.plot(resRecord, "red")
		>>>	plt.twinx()
		>>>	plt.plot(itemRecord)
		>>>	plt.show()

		[5] 备注
		-----
		* 只支持单个同类测点的实测值输入

		"""
		keys = kwargs.keys()
		# 推力进口水温限制
		self._guideBearingInletTemperStablePeriodLimit = kwargs[
			"guideBearingInletTemperStablePeriodLimit"] if "guideBearingInletTemperStablePeriodLimit" in keys else 4 * 3600
		self._guideBearingInletTemperStableValueLimit = kwargs[
			"guideBearingInletTemperStableValueLimit"] if "guideBearingInletTemperStableValueLimit" in keys else 0.5
		# 推力出口水温限制
		self._guideBearingOutletTemperStablePeriodLimit = kwargs[
			"guideBearingOutletTemperStablePeriodLimit"] if "guideBearingOutletTemperStablePeriodLimit" in keys else 3600
		self._guideBearingOutletTemperStableValueLimit = kwargs[
			"guideBearingOutletTemperStableValueLimit"] if "guideBearingOutletTemperStableValueLimit" in keys else 0.5
		# 推力瓦温限制
		self._guideBearingPadTemperStablePeriodLimit = kwargs[
			"guideBearingPadTemperStablePeriodLimit"] if "guideBearingPadTemperStablePeriodLimit" in keys else 3600
		self._guideBearingPadTemperStableValueLimit = kwargs[
			"guideBearingPadTemperStableValueLimit"] if "guideBearingPadTemperStableValueLimit" in keys else 0.5
		# 推力油温限制
		self._guideBearingOilTemperStablePeriodLimit = kwargs[
			"guideBearingOilTemperStablePeriodLimit"] if "guideBearingOilTemperStablePeriodLimit" in keys else 3600
		self._guideBearingOilTemperStableValueLimit = kwargs[
			"guideBearingOilTemperStableValueLimit"] if "guideBearingOilTemperStableValueLimit" in keys else 0.5
		# LOF监测IQR方法系数
		self._iqrCoef = kwargs["iqrCoef"] if "iqrCoef" in keys else 1.5
		# ===== 内部参数 ===== #
		self.__guideBearingInletTemperRecord = []
		self.__guideBearingOutletTemperRecord = []
		self.__guideBearingPadTemperRecord = []
		self.__guideBearingOilTemperRecord = []
		# ===== 输出参数 ===== #
		self.determineResultGroup = []
		self.guideBearingThermalStableStatus = None

	def __determine_and_refreshRecord(self, itemName, privateName="_ThrustBearingThermalStabilityDetermine"):
		"""
		根据各个测点的稳定状态持续最小时间限值、稳定状态数据最大峰峰限值，综合各测点判定定子是否处于热稳定态；当各测点数据时间超出用于判定
		其稳定态所需的最小时间限值时，更新缓存

		- 峰峰值计算前，使用IQR的离群点检测方法过滤突变点

		:param itemName: str, 需要进行稳定性判断的对象测点名称，如"guideBearingInletTemper", "guideBearingOutletTemper", "guideBearingPadTemper", "guideBearingOilTemper"等
		:param privateName: str, 给调用对象内部参数__getAttribute__使用的类名称，默认"_ThrustBearingThermalStabilityDetermine"
		:return: None
		"""
		timeBuffer = []
		dataBuffer = []
		[timeBuffer.append(zipItem[0]) for zipItem in
		 self.__getattribute__(privateName + "__" + itemName + "Record")]
		[dataBuffer.append(zipItem[-1]) for zipItem in
		 self.__getattribute__(privateName + "__" + itemName + "Record")]
		locs2Determine = np.where(
			np.asarray(timeBuffer) >= (
					timeBuffer[-1] - self.__getattribute__("_" + itemName + "StablePeriodLimit")),
			True, False)
		timeBuffer = np.asarray(timeBuffer)[locs2Determine]
		dataBuffer = np.asarray(dataBuffer)[locs2Determine]
		dataBuffer = localOutlierFilter(dataBuffer, coef=self._iqrCoef)
		peak2peakRangeLowerThanThreshold = max(dataBuffer) - min(dataBuffer) <= self.__getattribute__(
			"_" + itemName + "StableValueLimit")
		determineSectionIsLongEnough = (
			timeBuffer[-1] - timeBuffer[0] >= self.__getattribute__("_" + itemName + "StablePeriodLimit"))
		if peak2peakRangeLowerThanThreshold and determineSectionIsLongEnough:
			self.determineResultGroup.append(True)  # 热稳定
		else:
			self.determineResultGroup.append(False)  # 非热稳定
		cache = np.asarray(self.__getattribute__(privateName + "__" + itemName + "Record"))[locs2Determine].tolist()
		self.__setattr__(privateName + "__" + itemName + "Record", cache)

	def updateRecord(self, timestamp, **kwargs):
		"""
		更新时间戳及所有进行导轴承热稳定判断所需的变量;判定当前样本输入后,各测点及其历史缓存是否支持"导轴承热稳定"

        :param timestamp: 样本时间戳(秒),unixTimestamp
        :type timestamp: int
        :key guideBearingInletTemper: 导轴承进口水温(℃)
        :key guideBearingOutletTemper: 导轴承出口水温(℃)
        :key guideBearingPadTemper: 导轴承瓦温(℃)
        :key guideBearingOilTemper: 导轴承油温(℃)
        :return: None
        :rtype: None
		"""
		privateName = "_GuideBearingThermalStabilityDetermine"
		names = ["guideBearingInletTemper", "guideBearingOutletTemper", "guideBearingPadTemper", "guideBearingOilTemper"]
		# 更新数据Record
		[self.__getattribute__(privateName + "__" + item + "Record").append((timestamp, kwargs[item])) for item in
		 names]
		# 判定各测点及其历史缓存是否支持"导轴承热稳定"，并更新各测点缓存
		[self.__determine_and_refreshRecord(item, privateName) for item in names]
		self.guideBearingThermalStableStatus = all(self.determineResultGroup)
		self.determineResultGroup = []