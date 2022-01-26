from Turbine
import numpy as np

def main():
    a = list(np.arange(0, 1, 1/10))
    b = list(np.arange(0, 2, 1/100))
    c = list(np.arange(0, 3, 1/1000))
    obj = AirGapGradient()
    obj.unevenness(a, b, c)
    print(obj.gradient)




if __name__ == '__main__':
    main()

