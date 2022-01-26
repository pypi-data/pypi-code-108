from commonMethods_zhaozl_green.toolbox.Method_mysqlOperator import mysqlOperator
from TurbineGeneratorHealthScoreEvaluate.toolbox.v1.Method_RotationSpeedInstantAroundTargetValueCheck import RotationSpeedInstantAroundTargetValueCheck
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

pd.set_option('display.max_columns', 10000, 'display.width', 10000,
              'max_rows', 20, 'display.unicode.east_asian_width', True)
np.set_printoptions(threshold=np.inf)


def main():
	databaseName = 'bearing_pad_temper'
	tableName = '轴承瓦温20200320_20200327_原始数据'
	host = 'localhost'
	port = 3306
	userID = 'root'
	password = '000000'
	obj = mysqlOperator(databaseName=databaseName, tableName=tableName, host=host, port=port, userID=userID,
	           password = password)
	content = '时间戳,发电机励端轴瓦温度'
	condition = "(时间戳>=\'2020-03-20 16:00:00\') and (时间戳<=\'2020-03-21 17:20:00\')"
	data = obj.selectData(content=content, condition=condition)
	dataRecord = data["发电机励端轴瓦温度"].tolist()

	determineRecord = []
	for i in range(len(dataRecord)):
		rotationObj = RotationSpeedInstantAroundTargetValueCheck(ratingRotationSpeed=76.2, toleranceCoef=1.005)
		rotationObj.check(dataRecord[i])
		determineRecord.append(rotationObj.determine)

	determineRecord = np.where(np.asarray(determineRecord) == True, 1, 0)
	plt.plot(dataRecord)
	plt.twinx()
	plt.plot(determineRecord)
	plt.show()


if __name__ == '__main__':
	main()