import sys

import matplotlib.pyplot as plt
import numpy as np
from TurbineGeneratorHealthScoreEvaluate.toolbox.v1.Method_ThermalStabilityDetermine import \
	StatorThermalStabilityDetermine


def main():
	obj = StatorThermalStabilityDetermine()
	itemRecord = []
	resRecord = []
	for i in range(5000):
		if i < 500:
			item = 50 + np.random.random() * 10
		else:
			item = 50 + np.random.random() / 10

		itemRecord.append(item)
		obj.updateRecord(timestamp=1551230000 + i * 300, apparentPower=item, airCoolerInletTemper=item,
		                 statorTemper=item,
		                 coldWindTemper=item, hotWindTemper=item, airCoolerOutletTemper=item)
		resRecord.append(int(obj.statorThermalStableStatus))

	plt.plot(resRecord, "red")
	plt.twinx()
	plt.plot(itemRecord)
	plt.show()


if __name__ == '__main__':
	main()
