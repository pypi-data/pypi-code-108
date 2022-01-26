import matplotlib.pyplot as plt
from commonMethods_zhaozl_green.toolbox import Method_mysqlOperator as mysqlOperator
import time
from TurbineGeneratorHealthScoreEvaluate.toolbox.v1.Method_InsulationDegrade import InsulationDegrade


def timeFormatTransfer_toUnixTime(_str: str) -> int:
	return int(time.mktime(time.strptime(_str, '%Y-%m-%d %H:%M:%S')))


def main():
	# ===== 调用数据 ===== #
	databaseName = 'bearing_pad_temper'
	tableName = '轴承瓦温20200320_20200327_原始数据'
	host = 'localhost'
	port = 3306
	userID = 'root'
	password = '000000'
	obj = mysqlOperator.mysqlOperator(databaseName=databaseName, tableName=tableName, host=host, port=port,
	                                  userID=userID, password=password)
	content = '时间戳,汽机润滑油冷油器出口总管油温1,发电机励端轴瓦温度'
	condition = "(时间戳>=\'2020-03-20 16:18:03\') and (时间戳<=\'2020-03-25 16:18:11\')"
	data = obj.selectData(content=content, condition=condition)
	print(data)
	# ===== 时间格式转换 ===== #
	times_str = data['时间戳'].tolist()
	times_str = list(map(str, times_str))
	times = list(map(timeFormatTransfer_toUnixTime, times_str))
	# ===== 主过程 ===== #
	values = data['汽机润滑油冷油器出口总管油温1']
	temperUpperThreshold = 20
	insulationObject = InsulationDegrade(temperUpperThreshold=temperUpperThreshold)
	NRecorder = []
	insulationRemainSafeMarginRecorder = []
	for i in range(len(data)):
		insulationObject.decide(values[i], times[i])
		NRecorder.append(insulationObject.counter)
		insulationRemainSafeMarginRecorder.append(insulationObject.insulationRemainSafeMargin)
	plt.plot(values)
	plt.axhline(y=temperUpperThreshold)
	plt.twinx()
	plt.plot(NRecorder)
	plt.plot(insulationRemainSafeMarginRecorder)
	plt.show()


if __name__ == '__main__':
	main()
