"""
Version
-------
v1:
	截止2022.01.25,定义了如下类与函数:

	Classes
	-------
	1. AirCoolerHeatExchangeEfficiency: 空冷器换热效率计算.
	2. CoolerPerformance: 冷却器冷却性能计算.
	3. ExcitingCurrent: 励磁电流计算.
	4. InsulationDegrade: 绝缘劣化度计算.
	5. QualitativeTrendAnalysis: 定性趋势分析.
	6. RotationSpeedInstantAroundTargetValueCheck: 转速(瞬时)是否处于目标值附近.
	7. RotationSpeedStable2TargetValueCheck: 转速(持续)是否处于目标值附近.
	8. RotorWindingTemperRise: 转速(持续)是否处于目标值附近.
	9. StartingProcessVoltageClimbingStageDetermine: 升压阶段判断.
	10. StatorWindingTemperRise: 定子绕组温升计算.
	11. ThermalStabilityDetermine: 热稳定判断.TODO:以下在模型部署环境中，使用globals()的方法不一定能够取得缓存量,需要测试.如是,需要在属性初始化时通过关键字指定
			- StatorThermalStabilityDetermine: 定子热稳定判断.
			- ThrustBearingThermalStabilityDetermine: 推力轴承热稳定判断.
			- GuideBearingThermalStabilityDetermine: 导轴承热稳定判断.
	12. ThrustBearingPadTemperClimbingVelocity: 推力轴承瓦温上升速率计算.
	13. ThrustBearingPadTemperEvenness: 推理轴瓦温度单测点均匀度计算.
	14. RubberSealAgingDegree: 橡胶密封件老化程度计算
	15. IdlingSpinningStatusDetermine: 机组空转状态判断
	16. AxialDisplacement: 轴向位移于稳态过程中最大值的计算.
	17. AxisCentricity_WeightUnbalance_HydraulicUnbalance: 计算轴线对中水平、质量不平衡水平、水力不平衡判断下,某频幅值变化率或相对变化率.
	18. ElectromagneticUnbalance: 计算电磁不平衡判断下,某频幅值变化率或相对变化率.
	19. NoLoadStatusDetermine: 机组空载状态判断,转速为额定转速(附近),相电压为额定值(附近),且空转.
	20. StructuralPartsFixingStatus: 结构件固定情况判断.
	21. AirGapGradient: 计算气隙不均匀度.
	22. StatorWindingEndVibration: 计算多个定子端部振动测点最大值.
    23. StatorCoreVibration:定子铁心振动某频率振幅分量计算.

	GenericMethods
    ---------
    1. localOutlierFilter: 离群点清洗，使用IQR原则.
    2. formatTimestampTransfer2Int:	根据指定的格式，将格式化的时间戳转换为unixTimestamp列表.
    3. progressiveLocalMaximumValueFilter:渐进式局部最大值过滤.
"""