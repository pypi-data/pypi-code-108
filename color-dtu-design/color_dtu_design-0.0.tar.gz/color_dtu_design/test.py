from color_design import*
import matplotlib.pyplot as plt
t = color_design("pink")

x = range(0,5)
y = range(0,5)

plt.plot(x,y, color = t.color)
plt.show()