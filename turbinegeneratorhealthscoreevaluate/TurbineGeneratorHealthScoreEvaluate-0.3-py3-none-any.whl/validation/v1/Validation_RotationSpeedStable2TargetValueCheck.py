import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.animation import FuncAnimation
from commonMethods_zhaozl_green.toolbox.Method_mysqlOperator import mysqlOperator
from TurbineGeneratorHealthScoreEvaluate.toolbox.v1.Method_RotationSpeedStable2TargetValueCheck import RotationSpeedStable2TargetValueCheck

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
	                    password=password)
	content = '时间戳,发电机励端轴瓦温度'
	condition = "(时间戳>=\'2020-03-20 16:00:00\') and (时间戳<=\'2020-03-21 17:20:00\')"
	data = obj.selectData(content=content, condition=condition)
	dataRecord = data["发电机励端轴瓦温度"].tolist()

	determineRecord = []

	for i in range(len(dataRecord)):
		rotationObj = RotationSpeedStable2TargetValueCheck(ratingRotationSpeed=76.2, dataBuffer=rotationObj.dataBuffer if "rotationObj" in globals().keys() else [], sigmaCoef=3)
		rotationObj.updateSample(dataRecord[i])
		determineRecord.append(rotationObj.determine)

	fig, ax = plt.subplots()
	plt.grid()
	ax.set_xlim(0, 10000)
	ax.set_ylim(0, 100)

	ln0, = ax.plot([], [], ":")
	ln1, = ax.plot([], [], color="red", marker="o")
	txt1 = ax.text([], [], "")
	point1, = ax.plot([], [], color="red", marker="*")

	i = np.arange(len(dataRecord))

	def update(_i):
		ax.set_xlim((0, _i+10))
		if _i != 0:
			ax.set_ylim((min(dataRecord[0:_i])-2, max(dataRecord[0:_i])+2))
		ln0.set_data(np.arange(_i), dataRecord[0:_i])
		ln1.set_data(_i, dataRecord[_i])
		if determineRecord[0:_i] is not []:
			markedPoints_x = np.asarray(np.arange(_i))[determineRecord[0:_i]]
			markedPoints_y = np.asarray(dataRecord[0:_i])[determineRecord[0:_i]]
			point1.set_data(markedPoints_x, markedPoints_y)

	ani = FuncAnimation(fig, update, i, interval=1)
	plt.show()


if __name__ == '__main__':
	main()