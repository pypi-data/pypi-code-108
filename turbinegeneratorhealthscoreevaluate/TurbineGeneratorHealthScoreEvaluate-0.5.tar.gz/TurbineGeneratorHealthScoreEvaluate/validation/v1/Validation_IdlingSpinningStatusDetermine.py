import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from TurbineGeneratorHealthScoreEvaluate.toolbox.v1.Method_IdlingSpinningStatusDetermine import IdlingSpinningStatusDetermine

def main():
	seq = np.arange(0, 5, 5/3000)
	noise = np.random.randn(1, len(seq)).ravel().tolist()
	record = []
	for i in seq + noise:
		idlingObj = IdlingSpinningStatusDetermine(idlingMinimumTolerancedSpeed=2, idlingMaximumTolerancedExcitingCurrent=4)
		record.append(1 if idlingObj.determine(i, i/2) else 0)

	plt.title("转速与励磁电流运行情况")
	plt.plot((seq + noise), "r", label="转速", alpha=0.2)
	plt.hlines(2, 0, 3000, "r")
	plt.plot((seq + noise)/2, "b", label="励磁电流", alpha=0.2)
	plt.hlines(4, 0, 3000, "b")
	plt.legend()
	plt.twinx()
	plt.bar(np.arange(len(record)), record, width=1, alpha=0.2, color="g")
	plt.show()


if __name__ == '__main__':
	main()
