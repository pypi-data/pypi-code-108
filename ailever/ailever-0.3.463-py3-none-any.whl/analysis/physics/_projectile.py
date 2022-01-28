import numpy as np
import matplotlib.pyplot as plt

class Projectile:
    r"""
	o1 = Projectile(time=30, v0=100, theta=np.pi/4)
	p2 = Projectile(time=30, v0=100, theta=np.pi/5)
	p3 = Projectile(time=30, v0=500, theta=np.pi/10)
    """
    def __init__(self, time=30, v0=10, theta=np.pi/4):
        self.g = 9.80665
        self.s_x = [0]
        self.s_y = [0]
        self.v_x = [v0*np.cos(theta)]
        self.v_y = [v0*np.sin(theta)]
        self.a_x = [0]
        self.a_y = [-self.g]
        self.__compile(time)
        self.__visualize()

    def __compile(self, time):
        for t in range(time):
            if t == 0:
                a_x0 = self.a_x[0]
                a_y0 = self.a_y[0]
                v_x0 = self.v_x[0]
                v_y0 = self.v_y[0]
                s_x0 = self.s_x[0]
                s_y0 = self.s_y[0]
            else:
                self.a_x.append(9)
                self.a_y.append(a_y0)
                self.v_x.append(v_x0)
                self.v_y.append(v_y0 + a_y0*t)
                self.s_x.append(s_x0 + v_x0*t)
                self.s_y.append(s_y0 + v_y0*t + (1/2)*a_y0*t**2)

    def __visualize(self):
        plt.plot(self.s_x, self.s_y)
