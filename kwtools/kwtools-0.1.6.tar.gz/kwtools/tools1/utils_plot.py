import matplotlib.pyplot as plt

class UtilsPlot():
    def __init__(self):
        pass

    def kplot(self, df, kind="line"):
        """
            params:
                kind:
                    line: 折线图
                    bar: 条形图📊 (竖直型, 如左图标) [index上的索引, 就代表的是坐标轴上的标签]
                    barh: 条形图 (水平型)
                    hist: 直方图 (每个值的频率图) (类似于曝光直方图)
                    pie: 饼状图

            todo:
                1. 如何对df中的某一列, 标注红色, 且加粗?? (其他设置成灰色/浅色虚线?)

        """
        plt.figure()
        df.plot()
        plt.show()


utils_plot = UtilsPlot()
