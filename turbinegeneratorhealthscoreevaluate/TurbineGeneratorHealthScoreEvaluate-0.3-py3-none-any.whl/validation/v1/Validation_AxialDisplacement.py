import datetime as dt
import numpy as np

from TurbineGeneratorHealthScoreEvaluate.toolbox.v1.Method_AxialDisplacement import AxialDisplacement


def main():
	datas = np.random.rand(1, 5000).ravel() * 0.108

	timestamps = []
	nowTime = dt.datetime.now()
	for i in range(5000):
		_time = nowTime - dt.timedelta(seconds=(5000 - i) * 7)
		timestamps.append(_time.strftime("%Y-%m-%d %H:%M:%S"))

	obj = AxialDisplacement()
	for i in range(5000):
		obj.update_and_determine(datas[i], timestamps[i])
		print(obj.determine)


if __name__ == '__main__':
	main()