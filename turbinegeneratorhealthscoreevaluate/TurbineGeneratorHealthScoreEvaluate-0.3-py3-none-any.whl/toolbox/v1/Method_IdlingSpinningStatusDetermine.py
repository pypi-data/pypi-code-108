import numpy as np
import pandas as pd


class IdlingSpinningStatusDetermine:
	def __init__(self, **kwargs):
		"""
		机组空转状态判断

		[1] 参数
		----------
		idlingMinimumTolerancedSpeed:
		    float,转速允许的最小限值(r/min),默认3,当超过该转速时,认为机组在旋转状态
		idlingMaximumTolerancedExcitingCurrent:
		    float,励磁电流允许的最大零漂(A),默认10

		[2] 方法
		----------
		determine:
		    输入瞬时转速rotationSpeed,励磁电流excitingCurrent进行超限判断

		[3] 返回
		-------
		-/-:
		    该方法返回"空转状态"判断结果,Bool

		[4] 示例
		--------
		>>> seq = np.arange(0, 5, 5/3000)
		>>> noise = np.random.randn(1, len(seq)).ravel().tolist()
		>>> record = []
		>>> for i in seq + noise:
		>>> 	idlingObj = IdlingSpinningStatusDetermine(idlingMinimumTolerancedSpeed=2, idlingMaximumTolerancedExcitingCurrent=4)
		>>> 	record.append(1 if idlingObj.determine(i, i/2) else 0)
		>>> plt.title("转速与励磁电流运行情况")
		>>> plt.plot((seq + noise), "r", label="转速", alpha=0.2)
		>>> plt.hlines(2, 0, 3000, "r")
		>>> plt.plot((seq + noise)/2, "b", label="励磁电流", alpha=0.2)
		>>> plt.hlines(4, 0, 3000, "b")
		>>> plt.legend()
		>>> plt.twinx()
		>>> plt.bar(np.arange(len(record)), record, width=1, alpha=0.2, color="g")
		>>> plt.show()
		"""
		keys = kwargs.keys()
		self._idlingMinimumTolerancedSpeed = kwargs["idlingMinimumTolerancedSpeed"] if "idlingMinimumTolerancedSpeed" in keys else 3  # r/min
		self._idlingMaximumTolerancedExcitingCurrent = kwargs["idlingMaximumTolerancedExcitingCurrent"] if "idlingMaximumTolerancedExcitingCurrent" in keys else 10  # A

	def determine(self, rotationSpeed, excitingCurrent):
		if (rotationSpeed >= self._idlingMinimumTolerancedSpeed) and (excitingCurrent <= self._idlingMaximumTolerancedExcitingCurrent):
			return True
		else:
			return False
