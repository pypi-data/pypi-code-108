import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from TurbineGeneratorHealthScoreEvaluate.toolbox.v1.Method_NoLoadStatusDetermine import NoLoadStatusDetermine

def main():
	seq = np.ones(5000)
	obj = NoLoadStatusDetermine()

	record = []
	rotationSpeed = (seq*54 + np.random.randn(1, 5000)).ravel()
	phaseVoltage = (seq*7.967 + np.random.randn(1, 5000)).ravel()
	idlingSpinningStatus = [True]*5000
	for i in range(len(seq)):
		record.append(obj.determine(rotationSpeed[i], phaseVoltage[i], idlingSpinningStatus[i]))
	record = np.asarray(record).astype(int)

	plt.hlines(54.55*1.05, 1, 5000, "b")
	plt.hlines(54.55*0.95, 1, 5000, "b")
	plt.plot(rotationSpeed, "b", alpha=0.3)
	plt.twinx()
	plt.hlines(7.967 * 1.01, 1, 5000, "y")
	plt.hlines(7.967 * 0.99, 1, 5000, "y")
	plt.scatter(np.arange(5000), phaseVoltage, color="y", alpha=0.3)
	plt.bar(np.arange(len(record)), record*20, width=1, alpha=0.2)
	plt.show()



if __name__ == '__main__':
    main()



