import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from commonMethods_zhaozl_green.toolbox.Method_mysqlOperator import mysqlOperator
from matplotlib.animation import FuncAnimation


class ThrustBearingPadTemperEvenness:
	def __init__(self, **kwargs):
		"""
	    推力轴承瓦温单测点均匀度计算

	    [1] 参数
	    ----------
	    bufferSize:
	        int,缓存尺寸,optional,默认50
	    temperBuffer:
	        dataframe,缓存数据,初始化该类时如不指定,则使用默认值,如指定,则使用指定数据作为初始缓存,optional,默认None

	    [2] 方法
	    ----------
	    update_and_determine:
	        更新测点数据,并计算均匀度

	    [3] 返回
	    -------
	    temperBuffer:
	        dataframe,缓存数据,可在每次迭代结束后输出并在初始化该类时进行指定

	    evennessIndex:
	        均匀度指标量

	    [4] 示例
	    --------
	    >>> # ===== 数据调用 ===== #
	    >>> databaseName = 'bearing_pad_temper'
	    >>> tableName = '轴承瓦温20200320_20200327_原始数据'
	    >>> host = 'localhost'
	    >>> port = 3306
	    >>> userID = 'root'
	    >>> password = '000000'
	    >>> obj = mysqlOperator(databaseName=databaseName, tableName=tableName, host=host, port=port, userID=userID,
	    >>>                     password=password)
	    >>> content = '时间戳,发电机励端轴瓦温度,发电机汽端轴瓦温度'
	    >>> condition = "(时间戳>=\'2020-03-20 16:00:00\') and (时间戳<=\'2020-03-20 18:00:00\')"
	    >>> data = obj.selectData(content=content, condition=condition)
	    >>> # ===== 模拟数据输入与模型调用 ===== #
	    >>> evennessRecorder = []
	    >>> bufferCache = None
	    >>> bufferSize = 100
	    >>> for i in range(len(data)):
	    >>>     evenObj = ThrustBearingPadTemperEvenness(temperBuffer=bufferCache, bufferSize=bufferSize)
	    >>>     _tempers = data.iloc[i, 1:].values.tolist()
	    >>>     evenObj.update_and_determine(_tempers)
	    >>>     bufferCache = evenObj._temperBuffer
	    >>>     evennessRecorder.append(evenObj.evennessIndex)
	    >>> # ===== 绘图 ===== #
	    >>> length = np.arange(len(data))
	    >>> fig, axes = plt.subplots(2, 1, tight_layout=True)
	    >>> axe0 = axes[0]
	    >>> axe1 = axes[1]
	    >>> axe0.set_xlim(0, len(data))
	    >>> axe0.set_ylim(50, 100)
	    >>> axe0.set_title(f"发电机励端轴瓦温度 bufferSize={bufferSize}")
	    >>> axe1.set_xlim(0, len(data))
	    >>> axe1.set_ylim(50, 100)
	    >>> axe1.set_title(f"发电机汽端轴瓦温度 bufferSize={bufferSize}")
	    >>> line0, = axe0.plot([], [], "b:")
	    >>> point0, = axe0.plot([], [], "ro")
	    >>> axe0_even = axe0.twinx()
	    >>> line0_even, = axe0_even.plot([], [], color="cyan", linestyle="--")
	    >>> txt0 = plt.text(0, 0.04, "-/-", fontsize=12)
	    >>> line1, = axe1.plot([], [], "b:")
	    >>> point1, = axe1.plot([], [], "ro")
	    >>> axe1_even = axe1.twinx()
	    >>> line1_even, = axe1_even.plot([], [], color="cyan", linestyle="--")
	    >>> txt1 = plt.text(0, 0.04, "-/-", fontsize=12)
	    >>>
	    >>> def update(_i):
	    >>>     _x_point = _i
	    >>>     _y_point0 = data["发电机励端轴瓦温度"][_i]
	    >>>     _y_point1 = data["发电机汽端轴瓦温度"][_i]
	    >>>     if _i != 0:
	    >>>     	_ylim0_min = min(data["发电机励端轴瓦温度"][0:_i])
	    >>>     	_ylim0_max = max(data["发电机励端轴瓦温度"][0:_i])
	    >>>     	_ylim1_min = min(data["发电机汽端轴瓦温度"][0:_i])
	    >>>     	_ylim1_max = max(data["发电机汽端轴瓦温度"][0:_i])
	    >>>     else:
	    >>>     	_ylim0_min = 50
	    >>>     	_ylim0_max = 100
	    >>>     	_ylim1_min = 50
	    >>>     	_ylim1_max = 100
	    >>>     axe0.set_xlim(0, _i+10)
	    >>>     axe0.set_ylim(_ylim0_min*0.99, _ylim0_max*1.01)
	    >>>     point0.set_data(_x_point, _y_point0)  # 温度运行点
	    >>>     line0.set_data(np.arange(_i), data["发电机励端轴瓦温度"][0:_i].tolist())  # 稳定运行线
	    >>>     if _i != 0:
	    >>>     	line0_even.set_data(np.arange(_i), np.asarray(evennessRecorder[0:_i])[:, 0])  # 稳定运行线
	    >>>     	txt0.set_text(f"{np.asarray(evennessRecorder[_i])[0]}")
	    >>>     axe1.set_xlim(0, _i+10)
	    >>>     axe1.set_ylim(_ylim1_min*0.99, _ylim1_max*1.01)
	    >>>     point1.set_data(_x_point, _y_point1)  # 温度运行点
	    >>>     line1.set_data(np.arange(_i), data["发电机汽端轴瓦温度"][0:_i].tolist())  # 稳定运行线
	    >>>     if _i != 0:
	    >>>     	line1_even.set_data(np.arange(_i), np.asarray(evennessRecorder[0:_i])[:, 1])  # 稳定运行线
	    >>>     	txt1.set_text(f"{np.asarray(evennessRecorder[_i])[1]}")
	    >>> ani = FuncAnimation(fig, update, length, interval=1)
	    >>> plt.show()
	    >>> # ani.save("ThrustBearingPadTemperEvenness.gif", fps=30, writer="pillow")

	    [5] 备注
	    -----
	    * temperBuffer,dataframe,缓存数据,可在每次迭代结束后输出并在初始化该类时进行指定

	    """

		keys = kwargs.keys()
		# ===== 外部参数、内部参数 ===== #
		self._bufferSize = kwargs["bufferSize"] if "bufferSize" in keys else 50
		self._temperBuffer = kwargs["temperBuffer"] if ("temperBuffer" in keys) and (kwargs["temperBuffer"] is not None) else None
		# ===== 输出参数 ===== #
		self.evennessIndex = None

	def update_and_determine(self, args):
		"""
		更新测点数据,并计算均匀度

		:math:`\\frac {max(buffer) - min(buffer)} {average(buffer)}`

		:param args: 需要进行均匀度计算的测点数据
		:type args: list[float]
		:return: None
		"""
		_newTemperBuffer = pd.DataFrame([args], columns=["temper_" + str(i) for i in range(len(args))])
		if self._temperBuffer is not None:
			self._temperBuffer = pd.concat([self._temperBuffer, _newTemperBuffer], axis=0)
		else:
			self._temperBuffer = _newTemperBuffer
		self._temperBuffer = self._temperBuffer.reset_index(drop=True)
		if len(self._temperBuffer) > self._bufferSize:
			self._temperBuffer = self._temperBuffer.iloc[-self._bufferSize: None].reset_index(drop=True)
		_averages = self._temperBuffer.mean()
		_maxes = self._temperBuffer.max()
		_mines = self._temperBuffer.min()
		self.evennessIndex = ((_maxes - _mines) / _averages).values.tolist()
