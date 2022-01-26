import numpy as np
from commonMethods_zhaozl_green.toolbox.Method_mysqlOperator import mysqlOperator
from TurbineGeneratorHealthScoreEvaluate.toolbox.v1.GenericMethods import formatTimestampTransfer2Int
from TurbineGeneratorHealthScoreEvaluate.toolbox.v1.Method_ThrustBearingPadTemperClimbingVelocity import \
	ThrustBearingPadTemperClimbingVelocity
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


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
	condition = "(时间戳>=\'2020-03-20 16:00:00\') and (时间戳<=\'2020-03-20 18:00:00\')"
	data = obj.selectData(content=content, condition=condition)
	timeRecord = formatTimestampTransfer2Int(data["时间戳"].tolist())
	dataRecord = data["发电机励端轴瓦温度"].tolist()

	_moveAvg = []
	climbingVelocityRecord = []

	_timeCache, _valueCache, _valueBuffer_moveAvgCache = [None], [None], []
	for (_time, _value) in zip(timeRecord, dataRecord):
		velObj = ThrustBearingPadTemperClimbingVelocity(timeBuffer=_timeCache, valueBuffer=_valueCache,
		                                                valueBuffer_moveAvg=_valueBuffer_moveAvgCache)
		velObj.update(_time, _value)
		_timeCache = velObj.timeBuffer
		_valueCache = velObj.valueBuffer
		_valueBuffer_moveAvgCache = velObj.valueBuffer_moveAvg

		_moveAvg.append(velObj.valueBuffer_moveAvg[-1])

		climbingVelocityRecord.append(velObj.climbingVelocity)

	climbingVelocityRecord_array = np.asarray(climbingVelocityRecord)
	climbingVelocityRecord_array_noNone = np.where(climbingVelocityRecord_array == None, -1,
	                                               climbingVelocityRecord_array)
	climbingVelocityRecord_array_noNone_climbings = np.where(climbingVelocityRecord_array_noNone <= 0,
	                                                         None,
	                                                         climbingVelocityRecord_array_noNone)

	fig, ax = plt.subplots(tight_layout=True)
	ax.grid(color="r", ls="--")
	ax_twin = ax.twinx()

	measuredLine, = ax.plot([], [], ":")
	avgLine, = ax.plot([], [], "--", color="cyan")
	measuredPoint, = ax.plot([], [], color="blue", marker="o")
	climbingPoint, = ax_twin.plot([], [], color="red", marker="*", linestyle="")

	ax.set_xlim(0, len(dataRecord))
	ax.set_ylim(0, 100)

	def updateLine(_i):
		_x = np.arange(len(dataRecord))[_i]
		_y = dataRecord[_i]
		if _i == 0:
			ax.set_xlim(0, _i + 10)
			ax.set_ylim(dataRecord[0] * 0.98, dataRecord[0] * 1.02)
		elif _i < 500:
			ax.set_xlim(0, _i + 10)
			ax.set_ylim(min(dataRecord[0:_i]) * 0.98, max(dataRecord[0:_i]) * 1.02)
		else:
			ax.set_xlim(_i - 500 - 10, _i + 10)
			ax.set_ylim(min(dataRecord[_i - 500:_i]) * 0.98, max(dataRecord[_i - 500:_i]) * 1.02)

		measuredPoint.set_data(_x, _y)
		climbingPoint.set_data(np.arange(len(dataRecord))[0:_i], climbingVelocityRecord_array_noNone_climbings[0:_i])
		measuredLine.set_data(np.arange(len(dataRecord))[0:_i], dataRecord[0:_i])
		avgLine.set_data(np.arange(len(dataRecord))[0:_i], _moveAvg[0:_i])

	ani = FuncAnimation(fig, updateLine, np.arange(len(dataRecord)), interval=1)
	# ani.save("dynamic.gif", fps=5, writer="pillow")
	plt.show()


if __name__ == '__main__':
	main()
