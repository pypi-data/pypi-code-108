import matplotlib.pyplot as plt
import numpy as np
from TurbineGeneratorHealthScoreEvaluate.toolbox.v1.Method_RotorWindingTemperRise import RotorWindingTemperRise


def main():
	# ===== 调用数据 ===== #
	current = np.random.random(2000)
	# ===== 主过程 ===== #
	rotorWindingTemperRiseObj = RotorWindingTemperRise()
	res_rate = []
	res_theory = []
	for item in current:
		rotorWindingTemperRiseObj.temperRiseCal(item*10 + 1833)
		rotorWindingTemperRiseObj.temperRiseRateCal(50)
		res_theory.append(rotorWindingTemperRiseObj.temperRise_theoretic)
		res_rate.append(rotorWindingTemperRiseObj.temperRiseRate)
	plt.plot(res_theory)
	# plt.plot(res_rate)
	plt.show()


if __name__ == '__main__':
	main()