import matplotlib.pyplot as plt
import numpy as np
from TurbineGeneratorHealthScoreEvaluate.toolbox.v1.Method_ThermalStabilityDetermine import \
	ThrustBearingThermalStabilityDetermine


def main():
	obj = ThrustBearingThermalStabilityDetermine()
	itemRecord = []
	resRecord = []
	for i in range(1000):
		if i < 500:
			item = 50 + np.random.random() * 10
		else:
			item = 50 + np.random.random() / 10

		itemRecord.append(item)
		obj.updateRecord(timestamp=1551230000 + i * 300, thrustBearingInletTemper=item, thrustBearingOutletTemper=item,
		                 thrustBearingPadTemper=item, thrustBearingOilTemper=item)
		resRecord.append(int(obj.thrustBearingThermalStableStatus))

	plt.plot(resRecord, "red")
	plt.twinx()
	plt.plot(itemRecord)
	plt.show()


if __name__ == '__main__':
	main()
