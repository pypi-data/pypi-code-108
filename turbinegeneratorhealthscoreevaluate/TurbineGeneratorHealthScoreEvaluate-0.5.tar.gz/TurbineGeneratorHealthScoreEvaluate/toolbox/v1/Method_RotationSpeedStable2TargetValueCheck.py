from commonMethods_zhaozl_green.toolbox.Method_mysqlOperator import mysqlOperator
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

pd.set_option('display.max_columns', 10000, 'display.width', 10000,
              'max_rows', 20, 'display.unicode.east_asian_width', True)
np.set_printoptions(threshold=np.inf)


class RotationSpeedStable2TargetValueCheck:
	def __init__(self, **kwargs):
		"""
		用于对“转速是否稳定处于某一目标值附近”进行判断

		[1] 参数
		----------
		ratingRotationSpeed:
		    float,目标转速,默认54.5
		sigmaCoef:
			float,n*sigma准则系数n,默认3
		dataBufferSize:
			int,缓存尺寸,默认50
		dataBuffer:
			list,缓存数据,可以在每一次迭代时,将上一次迭代过程的数据缓存通过此参数在本次迭代时进行继承/指定,默认[]

		[2] 方法
		----------
		updateSample:
			更新数据与缓存,并判断当前数据是否稳定于目标值附近

		[3] 返回
		----------
		dataBuffer:
		    list,缓存数据,可以在每一次迭代时,将上一次迭代过程的数据缓存通过此参数在本次迭代时进行继承/指定

		determine:
		    bool,当前数据是否稳定在目标值附近的判断结果

		[4] 示例1
		----------
		>>> databaseName = 'bearing_pad_temper'
		>>> tableName = '轴承瓦温20200320_20200327_原始数据'
		>>> host = 'localhost'
		>>> port = 3306
		>>> userID = 'root'
		>>> password = '000000'
		>>> obj = mysqlOperator(databaseName=databaseName, tableName=tableName, host=host, port=port, userID=userID,
		>>>                     password=password)
		>>> content = '时间戳,发电机励端轴瓦温度'
		>>> condition = "(时间戳>=\'2020-03-20 16:00:00\') and (时间戳<=\'2020-03-21 17:20:00\')"
		>>> data = obj.selectData(content=content, condition=condition)
		>>> dataRecord = data["发电机励端轴瓦温度"].tolist()
		>>> determineRecord = []
		>>> for i in range(len(dataRecord)):
		>>> 	rotationObj = RotationSpeedStable2TargetValueCheck(ratingRotationSpeed=76.2, dataBuffer=rotationObj.dataBuffer if "rotationObj" in globals().keys() else [], sigmaCoef=3)
		>>> 	rotationObj.updateSample(dataRecord[i])
		>>> 	determineRecord.append(rotationObj.determine)
		>>> determineRecord = np.where(np.asarray(determineRecord) == True, 1, 0)
		>>> plt.plot(dataRecord)
		>>> plt.twinx()
		>>> plt.plot(determineRecord)
		>>> plt.show()

		[5] 备注
		----------
		* dataBuffer,缓存数据可以在每一次迭代时,将上一次迭代过程的数据缓存通过此参数在本次迭代时进行继承/指定

		"""

		keys = kwargs.keys()
		# ===== 外部参数 ===== #
		# 目标转速
		self._ratingRotationSpeed = kwargs["ratingRotationSpeed"] if "ratingRotationSpeed" in keys else 54.5
		# n*sigma准则系数n
		self._sigmaCoef = kwargs["sigmaCoef"] if "sigmaCoef" in keys else 3
		# 缓存尺寸
		self._dataBufferSize = kwargs["dataBufferSize"] if "dataBufferSize" in keys else 50
		# ===== 外部参数、内部参数、输出参数 ===== #
		# 缓存数据,可以在每一次迭代时,将上一次迭代过程的数据缓存通过此参数在本次迭代时进行继承/指定
		self.dataBuffer = kwargs["dataBuffer"] if "dataBuffer" in keys else []
		# ===== 内部参数 ===== #
		# 标准差,当样本数量为1时,标准差为0;当样本数量不超过30时,计算样本标准差;当样本数量超过30时,计算总体标准差
		self.__sigma = None
		# ===== 输出参数 ===== #
		# 当前数据是否稳定在目标值附近的判断结果
		self.determine = False

	def updateSample(self, _newValue):
		"""
		更新数据与缓存,并判断当前数据是否稳定于目标值附近

		:param _newValue: 检测是否稳定于目标值附近的样本数据对象
		:type _newValue: float
		:return: None
		"""
		self.dataBuffer.append(_newValue)
		self.dataBuffer.pop(0) if len(self.dataBuffer) > self._dataBufferSize else None
		self.__sigma_average_cal()
		self.__determine(_newValue)

	def __sigma_average_cal(self):
		currentBufferSize = len(self.dataBuffer)
		if currentBufferSize == 1:
			self.__sigma = 0
		elif currentBufferSize <= 30:
			self.__sigma = np.std(self.dataBuffer, ddof=0)
		else:
			self.__sigma = np.std(self.dataBuffer, ddof=1)

	def __determine(self, _newValue):
		if np.abs(_newValue-self._ratingRotationSpeed) <= self._sigmaCoef * self.__sigma:
			self.determine = True
		else:
			self.determine = False
