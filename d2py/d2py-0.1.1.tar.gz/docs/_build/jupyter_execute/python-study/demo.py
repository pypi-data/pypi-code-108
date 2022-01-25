#!/usr/bin/env python
# coding: utf-8

# # Jupyter Notebook

# ## 简单运算

# In[1]:


a = 5
b = 2
c = a + b
print(c)


# ## 画图

# In[2]:


import plotly.graph_objects as go

fig = go.Figure()
# fill down to xaxis
fig.add_trace(go.Scatter(x=[1, 2, 3, 4],
                         y=[0, 2, 3, 5],
                         fill='tozeroy'))
# fill to trace0 y
fig.add_trace(go.Scatter(x=[1, 2, 3, 4],
                         y=[3, 5, 1, 7],
                         fill='tonexty'))

f = go.FigureWidget(fig) # go.FigureWidget 保证正常显示
f


# In[3]:


import plotly.express as px
df = px.data.gapminder()
fig = px.area(df, x="year", y="pop",
              color="continent",
              line_group="country")
fig.show()


# In[4]:


import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.broken_barh([(110, 30), (150, 10)], (10, 9), facecolors='blue')
ax.broken_barh([(10, 50), (100, 20), (130, 10)], (20, 9),
               facecolors=('red', 'yellow', 'green'))
ax.set_ylim(5, 35)
ax.set_xlim(0, 200)
ax.set_xlabel('seconds since start')
ax.set_yticks([15, 25])
ax.set_yticklabels(['Bill', 'Jim'])
ax.grid(True)
ax.annotate('race interrupted', (61, 25),
            xytext=(0.8, 0.9), textcoords='axes fraction',
            arrowprops=dict(facecolor='black', shrink=0.05),
            fontsize=16,
            horizontalalignment='right', verticalalignment='top')

plt.show()


# ## 画一朵花

# In[1]:


from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator
 
from matplotlib.font_manager import FontProperties
# # 用于解决 Windows 系统，显示中文字体的问题
# font = FontProperties(fname=r"c:\windows\fonts\simsun.ttc", size=45)  
 
import matplotlib.pyplot as plt
import numpy as np
 
fig = plt.figure()
ax = plt.axes(projection='3d')
 
[x , t] = np.meshgrid(np.array(range(25))/24.0,np.arange(0, 575.5,0.5)/575*17*np.pi - 2*np.pi)
p = np.pi/2 * np.exp(-t/(8*np.pi))
u = 1 - (1 - np.mod(3.6*t, 2 * np.pi)/np.pi) **4/2
y = 2 * (x ** 2-x)**2*np.sin(p)
r = u * (x*np.sin(p) + y * np.cos(p))
 
surf = ax.plot_surface(r * np.cos(t),r * np.sin(t), u *(x*np.cos(p)-y*np.sin(p)),           rstride = 10,cstride=10 ** 10,cmap = cm.gist_heat,linewidth=7,antialiased=True)
 
# plt.title(u'你好！',fontproperties=font)
# plt.title('你好！')
ax.set_xticks([])
ax.set_yticks([])
ax.set_zticks([])
plt.show()


# In[ ]:




