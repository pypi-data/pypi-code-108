import matplotlib.pyplot as plt
import numpy as np
from TurbineGeneratorHealthScoreEvaluate.toolbox.v1.Method_ExcitingCurrent import ExcitingCurrent


def main():
	# ===== 调用数据 ===== #
	voltage = np.random.random(2000)
	# ===== 主过程 ===== #
	excitingCurrentObj = ExcitingCurrent()
	res_rate = []
	res_theory = []
	for item in voltage:
		excitingCurrentObj.excitingCurrentCal(7.967+item/100, 7.967+item/100, 7.967+item/100)
		excitingCurrentObj.excitingCurrentRateCal(1084.861+item/100)
		res_theory.append(excitingCurrentObj.excitingCurrent_theoretic)
		res_rate.append(excitingCurrentObj.excitingCurrentRate)
	plt.plot(res_rate)
	plt.twinx()
	plt.plot(res_theory, color='red', alpha=0.2, linestyle=":")
	plt.show()


if __name__ == '__main__':
	main()
