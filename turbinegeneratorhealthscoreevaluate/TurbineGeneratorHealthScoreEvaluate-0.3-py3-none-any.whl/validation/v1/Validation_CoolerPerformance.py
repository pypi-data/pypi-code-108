import numpy as np
import matplotlib.pyplot as plt
from TurbineGeneratorHealthScoreEvaluate.toolbox.v1.Method_CoolerPerformance import CoolerPerformance
from commonMethods_zhaozl_green.toolbox.Method_mysqlOperator import mysqlOperator


def main():
	# ===== 数据调用 ===== #
	databaseName = 'bearing_pad_temper'
	tableName = '轴承瓦温20200320_20200327_原始数据'
	host = 'localhost'
	port = 3306
	userID = 'root'
	password = '000000'
	obj = mysqlOperator(databaseName=databaseName, tableName=tableName, host=host, port=port, userID=userID,
	                    password=password)
	content = '发电机励端轴瓦温度,发电机汽端轴瓦温度,发电机9轴承回油温度,发电机10轴承回油温度,发电机励端轴瓦温度,发电机汽端轴瓦温度,发电机9轴承回油温度,发电机10轴承回油温度'
	condition = "(时间戳>=\'2020-03-20 16:00:00\') and (时间戳<=\'2020-03-20 20:00:00\')"
	data = obj.selectData(content=content, condition=condition)
	data.columns = ["冷油温度1", "冷油温度2", "热油温度1", "热油温度2", "热水温度1", "热水温度2", "冷水温度1", "冷水温度2"]
	performanceRecord = []
	for i in range(len(data)):
		_data = data.iloc[i, :]
		perfObj = CoolerPerformance(oilTempers=data.iloc[i, 0:4].tolist(),
		                            warmWaterTemper=list(map(lambda x: x * 1.003, data.iloc[i, 4:6].tolist())),
		                            coldWaterTemper=data.iloc[i, 4:6].tolist())
		performanceRecord.append(perfObj.coolerPerformance)
	plt.plot(performanceRecord)
	plt.show()


if __name__ == '__main__':
	main()


