"""
Classes
-------
1. AirCoolerHeatExchangeEfficiency: 空冷器换热效率计算.
	* 对每次输入的、满足波动比例范围限制(当前缓存均值±5%范围内)的 `视在功率值` 进行记录,并根据输入的冷热水温度、冷热风温度,计算当前空冷器的热交换效率
	* 每次计算后的缓存使用_apparentPowerRecord属性导出,并在每次迭代前类初始化时使用关键字apparentPowerRecord初始化
	* 热稳定工况的判断逻辑不在此中

2. CoolerPerformance: 冷却器冷却性能计算.
	* 对每次输入的冷热水温、冷热油温进行实时计算
	* 热稳定工况的判断逻辑不在此中

3. ExcitingCurrent: 励磁电流计算.
	* 使用解析法 :math:`If=1.7307 \\times U^2 - 1.6628 \\times U + 0.9431` 计算开机升压过程励磁电流，并使用实测值(归一化值)与对应三相电压均值下的理论值(归一化值)比值作为输出
	* `开机升压阶段` 的判断逻辑不在此中
	* 当需要进行相关判断的值为各种逻辑聚合值时(如某测点近期均值),需要在外部进行预处理
	* 当需要进行热稳定判断时,需要在外部进行判断

4. InsulationDegrade: 绝缘劣化度计算.
	* 使用解析法 :math:`[1 - lg(N + 1)] \\times e^a`, :math:`a={-(t/40)^{9.6}}`, :math:`N=定子绕组发生过热次数`
	* 当温度超标（判断依据：近期暂存的温度数据中有一定比例 `_fuzzyPercentage` 的数据为超限值）、持续时间超过限值（判断依据：近期暂存的温度数据中超限值的数据持续时间超过限值）、距离上一次过热报警时间已经超过最小限定时，计数器+1
	* 当需要进行相关判断的值为各种逻辑聚合值时（如某测点近期均值），需要在外部进行预处理

5. QualitativeTrendAnalysis: 定性趋势分析.
	* 见类描述

6. RotationSpeedInstantAroundTargetValueCheck: 转速(瞬时)是否处于目标值附近.
	* 用于对“转速是否瞬间处于某一目标值附近”进行判断

7. RotationSpeedStable2TargetValueCheck: 转速(持续)是否处于目标值附近.
	* 用于对“转速是否稳定处于某一目标值附近”进行判断
	* 缓存使用dataBuffer属性传出,并在初始化时使用dataBuffer关键字传入
	* 缓存数据可以在每一次迭代时使用关键字dataBuffer导出,将上一次迭代过程的数据缓存通过此参数在本次迭代(初始化时使用dataBuffer指定)时进行继承/指定

8. RotorWindingTemperRise: 转速(持续)是否处于目标值附近.
	* 使用解析法 :math:`Scu2=1.512 \\times (10^{-5}) \\times {If^2}-1.5` 计算转子绕组理论温升,并使用实测温升与对应励磁电流下理论温升比值作为输出

9. StartingProcessVoltageClimbingStageDetermine: 升压阶段判断.
	* 通过对近期数据样本进行缓存，在每次新样本进入后的迭代过程中，先使用IQR的方式进行异常点筛查，后使用线性拟合对当前缓存中的数据求取斜率值，并根据指定的斜率判断当前数据近期的变化状态（不变A/上升B/下降C）
	* 每次迭代完成时,使用dataBuffer对缓存数据进行输出,并在下一次迭代初始化时使用关键字dataBuffer进行指定

10. StatorWindingTemperRise: 定子绕组温升计算.
	* 使用解析法 :math:`Scu1=6.83 \\times (10^{-7})(I^2)+16.38` 计算定子绕组理论温升，并使用实测温升与对应电流下理论温升比值作为输出

11. ThermalStabilityDetermine: 热稳定判断.
	* 包括以下子类:TODO:以下在模型部署环境中，使用globals()的方法不一定能够取得缓存量,需要测试.如是,需要在属性初始化时通过关键字指定
		- StatorThermalStabilityDetermine: 定子热稳定判断.
			- 发电机视在功率稳定在4个小时以上，偏差在5MVA以内
			- 空冷器进口水温稳定在4个小时以上，偏差在0.5℃以内
			- 最后1个小时内定子温度偏差在1℃以内，冷风温度、空冷器出口水温、热风温度偏差在0.5℃以内
		- ThrustBearingThermalStabilityDetermine: 推力轴承热稳定判断.
			- 推力进口水温稳定在4个小时以上，偏差在0.5℃以内
			- 最后1个小时内推力瓦温、推力油温、推力出口水温偏差在0.5℃以内
		- GuideBearingThermalStabilityDetermine: 导轴承热稳定判断.
			- 导轴承进口水温稳定在4个小时以上，偏差在0.5℃以内
			- 最后1个小时内瓦温、油温、出口水温偏差在0.5℃以内

12. ThrustBearingPadTemperClimbingVelocity: 推力轴承瓦温上升速率计算.
	- 通过不断输入数据与时间戳样本,对缓存量进行滑动平均并计算出升温速率(℃/s)经变换后,升温速率(℃/min)与maximumBearableVelocity进行比较得出的最终温升速率
	- 包括timeBuffer、valueBuffer、valueBuffer_moveAvg在内的缓存量可以使用关键字timeBuffer、valueBuffer、valueBuffer_moveAvg进行输出,并在类初始化时使用上述关键字进行指定

13. ThrustBearingPadTemperEvenness: 推理轴瓦温度单测点均匀度计算.
	- 缓存量可以使用关键字_temperBuffer进行输出,并在类初始化时使用关键字temperBuffer进行指定

14. RubberSealAgingDegree: 橡胶密封件老化程度计算.
	- 使用 :math:`2^{T_i/T_0} - 1` , `T_i` 当前累积运行时间(年), `T_0` 设计运行年限(年)计算老化程度

15. IdlingSpinningStatusDetermine: 机组空转状态判断.

16. AxialDisplacement: 轴向位移于稳态过程中最大值的计算.

17. AxisCentricity_WeightUnbalance_HydraulicUnbalance: 计算轴线对中水平、质量不平衡水平、水力不平衡判断下,某频幅值变化率或相对变化率.

18. ElectromagneticUnbalance: 计算电磁不平衡判断下,某频幅值变化率或相对变化率.

19. NoLoadStatusDetermine: 机组空载状态判断,转速为额定转速(附近),相电压为额定值(附近),且空转.

20. StructuralPartsFixingStatus: 结构件固定情况判断.

Functions
---------
1. localOutlierFilter: 离群点清洗，使用IQR原则
	- 输入输出数据均为list

2. formatTimestampTransfer2Int:	根据指定的格式，将格式化的时间戳转换为unixTimestamp列表
	- 输入输出数据均为list

"""

from . import *
