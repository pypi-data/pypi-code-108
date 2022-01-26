import numpy as np
import matplotlib.pyplot as plt
import sys
import pandas as pd

from TurbineGeneratorHealthScoreEvaluate.toolbox.v1.Method_StartingProcessVoltageClimbingStageDetermine import StartingProcessVoltageClimbingStageDetermine
from TurbineGeneratorHealthScoreEvaluate.toolbox.v1.GenericMethods import formatTimestampTransfer2Int
from commonMethods_zhaozl_green.toolbox.Method_mysqlOperator import mysqlOperator


pd.set_option('display.max_columns', 10000,  'display.width', 10000,
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
	                    password=password)
	content = '时间戳,发电机励端轴瓦温度'
	condition = "(时间戳>=\'2020-03-20 16:00:00\') and (时间戳<=\'2020-03-20 17:20:00\')"
	data = obj.selectData(content=content, condition=condition)

	timeIntRecord = formatTimestampTransfer2Int(data["时间戳"])
	timeStrRecord = data["时间戳"].tolist()
	dataRecord = data["发电机励端轴瓦温度"].tolist()

	statusRecord = []
	data_bufferCache = None
	for i in range(len(timeIntRecord)):
		obj = StartingProcessVoltageClimbingStageDetermine(dataBuffer=data_bufferCache)
		# print(f"{i} / {len(timeIntRecord)}")
		obj.updateSample(dataRecord[i])
		statusRecord.append(obj.currentSample_status)
		data_bufferCache = obj.dataBuffer

		if len(statusRecord) >= 1:
			plt.plot(dataRecord[0:len(statusRecord)])
			plt.xticks(np.arange(len(statusRecord)), labels=statusRecord)
			plt.pause(0.001)

		for item in ['timeIntRecord', 'timeStrRecord', 'dataRecord', 'LOSS_EACH_EPOCH',
		             'StartingProcessVoltageClimbingStageDetermine', 'statusRecord', 'timestamp_bufferCache',
		             'data_bufferCache']:
			print(f"{sys.getsizeof(locals().get(item))}, ", end="")
		print(end="\n")
	plt.show()


if __name__ == '__main__':
	main()
