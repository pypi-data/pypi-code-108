import matplotlib.pyplot as plt
import numpy as np
from TurbineGeneratorHealthScoreEvaluate.toolbox.v1.Method_StatorWindingTemperRise import StatorWindingTemperRise


def main():
	# ===== 调用数据 ===== #
	current = np.random.random(2000)
	# ===== 主过程 ===== #
	statorWindingTemperRiseObj = StatorWindingTemperRise()
	res_cal = []
	res_theory = []
	for item in current:
		statorWindingTemperRiseObj.temperRiseCal(item*10 + 8128)
		# statorWindingTemperRiseObj.temperRiseCal(item*10 + 8128, voltage=20000, a=1, b=1, c=1, d=1, e=1)
		statorWindingTemperRiseObj.temperRiseRateCal(60)
		res_cal.append(statorWindingTemperRiseObj.temperRiseRate)
		res_theory.append(statorWindingTemperRiseObj.temperRise_theoretic)
	plt.plot(res_theory)
	plt.show()


if __name__ == '__main__':
	main()
