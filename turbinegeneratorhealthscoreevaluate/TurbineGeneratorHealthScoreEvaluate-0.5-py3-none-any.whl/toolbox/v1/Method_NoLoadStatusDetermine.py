import numpy as np
import pandas as pd


class NoLoadStatusDetermine:
	def __init__(self, **kwargs):
		"""
		机组空载状态判断,转速为额定转速(附近),相电压为额定值(附近),且空转

		[1] 参数
		----------
		noloadMaximumTolerancedSpeedDiff:
		    float,判断当前转速为额定转速的最大允许偏差范围(%),默认0.05
		ratedRotationSpeed:
		    float,额定转速(r/min),54.55
		noloadMaximumTolerancedPhaseVoltageDiff:
		    float,判断当前相电压为额定电压的最大允许偏差范围(%),默认0.001
		ratedPhaseVoltage:
		    float,额定电压(kV),默认7.967

		[2] 方法
		----------
		determine:
		    输入瞬时转速rotationSpeed, 相电压phaseVoltage, 空转状态判断idlingSpinningStatus进行超限判断

		[3] 返回
		-------
		determine:
		    该方法返回"空载状态"判断结果,Bool

		[4] 示例
		--------
		>>> seq = np.ones(5000)
		>>> obj = NoLoadStatusDetermine()
		>>> record = []
		>>> rotationSpeed = (seq*54 + np.random.randn(1, 5000)).ravel()
		>>> phaseVoltage = (seq*7.967 + np.random.randn(1, 5000)).ravel()
		>>> idlingSpinningStatus = [True]*5000
		>>> for i in range(len(seq)):
		>>> 	record.append(obj.determine(rotationSpeed[i], phaseVoltage[i], idlingSpinningStatus[i]))
		>>> record = np.asarray(record).astype(int)
		>>> plt.hlines(54.55*1.05, 1, 5000, "b")
		>>> plt.hlines(54.55*0.95, 1, 5000, "b")
		>>> plt.plot(rotationSpeed, "b", alpha=0.3)
		>>> plt.twinx()
		>>> plt.hlines(7.967 * 1.01, 1, 5000, "y")
		>>> plt.hlines(7.967 * 0.99, 1, 5000, "y")
		>>> plt.scatter(np.arange(5000), phaseVoltage, color="y", alpha=0.3)
		>>> plt.bar(np.arange(len(record)), record*20, width=1, alpha=0.2)
		>>> plt.show()
		"""
		keys = kwargs.keys()
		self._noloadMaximumTolerancedSpeedDiff = kwargs["noloadMaximumTolerancedSpeedDiff"] if "noloadMaximumTolerancedSpeedDiff" in keys else 0.05  # %
		self._ratedRotationSpeed = kwargs["ratedRotationSpeed"] if "ratedRotationSpeed" in keys else 54.55  # r/min
		self._noloadMaximumTolerancedPhaseVoltageDiff = kwargs["noloadMaximumTolerancedPhaseVoltageDiff"] if "noloadMaximumTolerancedPhaseVoltageDiff" in keys else 0.01  # %
		self._ratedPhaseVoltage = kwargs["ratedPhaseVoltage"] if "ratedPhaseVoltage" in keys else 7.967  # kV

	def determine(self, rotationSpeed: float, phaseVoltage: float, idlingSpinningStatus: bool):
		_rotationSpeedEligible = (rotationSpeed <= (self._ratedRotationSpeed * (1 + self._noloadMaximumTolerancedSpeedDiff)))and(rotationSpeed >= (self._ratedRotationSpeed * (1 - self._noloadMaximumTolerancedSpeedDiff)))
		_phaseVoltageEligible = (phaseVoltage <= (self._ratedPhaseVoltage * (1 + self._noloadMaximumTolerancedPhaseVoltageDiff)))and(phaseVoltage >= (self._ratedPhaseVoltage * (1 - self._noloadMaximumTolerancedPhaseVoltageDiff)))
		if _rotationSpeedEligible&_phaseVoltageEligible&idlingSpinningStatus:
			return True
		else:
			return False
