import matplotlib.pyplot as plt

from commonMethods_zhaozl_green.toolbox.Method_mysqlOperator import mysqlOperator
from TurbineGeneratorHealthScoreEvaluate.toolbox.v1.Method_ElectromagneticUnbalance import ElectromagneticUnbalance


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
	condition = "(时间戳>=\'2020-03-20 16:00:00\') and (时间戳<=\'2020-03-20 20:20:00\')"
	data = obj.selectData(content=content, condition=condition)

	dataRecord = data["发电机励端轴瓦温度"].tolist()

	ratioRecord = []
	_buffer = None
	for i in range(len(dataRecord)):
		obj = ElectromagneticUnbalance(buffer=_buffer)
		obj.gradientCal(dataRecord[i])
		ratioRecord.append(obj.ratio)
		_buffer = obj.buffer

	plt.subplot(211)
	plt.plot(dataRecord)
	plt.subplot(212)
	plt.plot(ratioRecord)
	plt.show()

if __name__ == '__main__':
	main()
