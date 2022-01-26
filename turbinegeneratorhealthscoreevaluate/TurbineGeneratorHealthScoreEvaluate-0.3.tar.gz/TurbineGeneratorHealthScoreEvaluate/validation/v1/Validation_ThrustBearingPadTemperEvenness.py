import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from commonMethods_zhaozl_green.toolbox.Method_mysqlOperator import mysqlOperator
from matplotlib.animation import FuncAnimation
from TurbineGeneratorHealthScoreEvaluate.toolbox.v1.Method_ThrustBearingPadTemperEvenness import ThrustBearingPadTemperEvenness


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
	content = '时间戳,发电机励端轴瓦温度,发电机汽端轴瓦温度'
	condition = "(时间戳>=\'2020-03-20 16:00:00\') and (时间戳<=\'2020-03-20 18:00:00\')"
	data = obj.selectData(content=content, condition=condition)
	# ===== 模拟数据输入与模型调用 ===== #
	evennessRecorder = []
	bufferCache = None
	bufferSize = 100
	for i in range(len(data)):
		evenObj = ThrustBearingPadTemperEvenness(temperBuffer=bufferCache, bufferSize=bufferSize)
		_tempers = data.iloc[i, 1:].values.tolist()
		evenObj.update_and_determine(_tempers)
		bufferCache = evenObj._temperBuffer
		evennessRecorder.append(evenObj.evennessIndex)
	# ===== 绘图 ===== #
	length = np.arange(len(data))
	fig, axes = plt.subplots(2, 1, tight_layout=True)
	axe0 = axes[0]
	axe1 = axes[1]
	axe0.set_xlim(0, len(data))
	axe0.set_ylim(50, 100)
	axe0.set_title(f"发电机励端轴瓦温度 bufferSize={bufferSize}")
	axe1.set_xlim(0, len(data))
	axe1.set_ylim(50, 100)
	axe1.set_title(f"发电机汽端轴瓦温度 bufferSize={bufferSize}")
	line0, = axe0.plot([], [], "b:")
	point0, = axe0.plot([], [], "ro")
	axe0_even = axe0.twinx()
	line0_even, = axe0_even.plot([], [], color="cyan", linestyle="--")
	txt0 = plt.text(0, 0.04, "-/-", fontsize=12)
	line1, = axe1.plot([], [], "b:")
	point1, = axe1.plot([], [], "ro")
	axe1_even = axe1.twinx()
	line1_even, = axe1_even.plot([], [], color="cyan", linestyle="--")
	txt1 = plt.text(0, 0.04, "-/-", fontsize=12)

	def update(_i):
		_x_point = _i
		_y_point0 = data["发电机励端轴瓦温度"][_i]
		_y_point1 = data["发电机汽端轴瓦温度"][_i]
		if _i != 0:
			_ylim0_min = min(data["发电机励端轴瓦温度"][0:_i])
			_ylim0_max = max(data["发电机励端轴瓦温度"][0:_i])
			_ylim1_min = min(data["发电机汽端轴瓦温度"][0:_i])
			_ylim1_max = max(data["发电机汽端轴瓦温度"][0:_i])
		else:
			_ylim0_min = 50
			_ylim0_max = 100
			_ylim1_min = 50
			_ylim1_max = 100
		axe0.set_xlim(0, _i + 10)
		axe0.set_ylim(_ylim0_min * 0.99, _ylim0_max * 1.01)
		point0.set_data(_x_point, _y_point0)  # 温度运行点
		line0.set_data(np.arange(_i), data["发电机励端轴瓦温度"][0:_i].tolist())  # 稳定运行线
		if _i != 0:
			line0_even.set_data(np.arange(_i), np.asarray(evennessRecorder[0:_i])[:, 0])  # 稳定运行线
			txt0.set_text(f"{np.asarray(evennessRecorder[_i])[0]}")
		axe1.set_xlim(0, _i + 10)
		axe1.set_ylim(_ylim1_min * 0.99, _ylim1_max * 1.01)
		point1.set_data(_x_point, _y_point1)  # 温度运行点
		line1.set_data(np.arange(_i), data["发电机汽端轴瓦温度"][0:_i].tolist())  # 稳定运行线
		if _i != 0:
			line1_even.set_data(np.arange(_i), np.asarray(evennessRecorder[0:_i])[:, 1])  # 稳定运行线
			txt1.set_text(f"{np.asarray(evennessRecorder[_i])[1]}")

	ani = FuncAnimation(fig, update, length, interval=1)
	plt.show()
	# ani.save("ThrustBearingPadTemperEvenness.gif", fps=30, writer="pillow")


if __name__ == '__main__':
	main()


