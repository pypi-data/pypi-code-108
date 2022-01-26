import matplotlib.pyplot as plt
import numpy as np
from TurbineGeneratorHealthScoreEvaluate.toolbox.v1.Method_ThermalStabilityDetermine import \
	GuideBearingThermalStabilityDetermine


def main():
	obj = GuideBearingThermalStabilityDetermine()
	itemRecord = []
	resRecord = []
	for i in range(1000):
		if i < 500:
			item = 50 + np.random.random() * 10
		else:
			item = 50 + np.random.random() / 10

		itemRecord.append(item)
		obj.updateRecord(timestamp=1551230000 + i * 300, guideBearingInletTemper=item, guideBearingOutletTemper=item,
		                 guideBearingPadTemper=item, guideBearingOilTemper=item)
		resRecord.append(int(obj.guideBearingThermalStableStatus))

	plt.plot(resRecord, "red")
	plt.twinx()
	plt.plot(itemRecord)
	plt.show()


if __name__ == '__main__':
	main()
