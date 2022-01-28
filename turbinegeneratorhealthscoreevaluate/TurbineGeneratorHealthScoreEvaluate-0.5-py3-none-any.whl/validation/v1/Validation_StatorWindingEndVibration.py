import numpy as np
from TurbineGeneratorHealthScoreEvaluate.toolbox.v1.Method_StatorWindingEndVibration import StatorWindingEndVibration


def main():
    a = np.arange(0, 3, 0.001)
    b = np.arange(0, 2, 0.001)
    c = np.arange(0, 6.3, 0.001)
    print(StatorWindingEndVibration(a, b, c).maximumVibration)

if __name__ == '__main__':
    main()