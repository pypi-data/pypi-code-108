from commonMethods_zhaozl_green.toolbox.Method_mysqlOperator import mysqlOperator
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

pd.set_option('display.max_columns', 10000, 'display.width', 10000,
              'max_rows', 20, 'display.unicode.east_asian_width', True)
np.set_printoptions(threshold=np.inf)


class RotationSpeedInstantAroundTargetValueCheck:
	def __init__(self, **kwargs):
		"""
		用于对“转速是否瞬间处于某一目标值附近”进行判断

		[1] 参数
		----------
		ratingRotationSpeed:
		    float,目标转速,默认54.5
		toleranceCoef:
			float,误差系数,应当大于1,默认1.005
		determine:
			bool,当前数据是否瞬间在目标值附近的判断结果

		[2] 方法
		----------
		check:
			检验当前输入数据是否在指定的目标值及其容忍限之间

		[3] 返回
		----------
		determine:
		    bool,当前数据是否瞬间在目标值附近的判断结果

		[4] 示例
		----------
		>>> databaseName = 'bearing_pad_temper'
		>>> tableName = '轴承瓦温20200320_20200327_原始数据'
		>>> host = 'localhost'
		>>> port = 3306
		>>> userID = 'root'
		>>> password = '000000'
		>>> obj = mysqlOperator(databaseName=databaseName, tableName=tableName, host=host, port=port, userID=userID,
		>>>            password = password)
		>>> content = '时间戳,发电机励端轴瓦温度'
		>>> condition = "(时间戳>=\'2020-03-20 16:00:00\') and (时间戳<=\'2020-03-21 17:20:00\')"
		>>> data = obj.selectData(content=content, condition=condition)
		>>> dataRecord = data["发电机励端轴瓦温度"].tolist()
		>>> determineRecord = []
		>>> for i in range(len(dataRecord)):
		>>> 	rotationObj = RotationSpeedInstantAroundTargetValueCheck(ratingRotationSpeed=76.2, toleranceCoef=1.005)
		>>> 	rotationObj.check(dataRecord[i])
		>>> 	determineRecord.append(rotationObj.determine)
		>>> determineRecord = np.where(np.asarray(determineRecord) == True, 1, 0)
		>>> plt.plot(dataRecord)
		>>> plt.twinx()
		>>> plt.plot(determineRecord)
		>>> plt.show()
		"""

		keys = kwargs.keys()
		# ===== 外部参数 ===== #
		# 目标转速
		self._ratingRotationSpeed = kwargs["ratingRotationSpeed"] if "ratingRotationSpeed" in keys else 54.5
		# 误差系数
		self._toleranceCoef = kwargs["toleranceCoef"] if "toleranceCoef" in keys else 1.005
		# ===== 输出参数 ===== #
		# 当前数据是否瞬间在目标值附近的判断结果
		self.determine = False

	def check(self, _newValue):
		"""
		检验当前输入数据是否在指定的目标值及其容忍限之间

		:param _newValue: 需要进行判断的对象数据
		:type _newValue: float
		:return: None
		"""
		if (2 - self._toleranceCoef) * self._ratingRotationSpeed <= _newValue <= self._toleranceCoef * self._ratingRotationSpeed:
			self.determine = True
		else:
			self.determine = False
