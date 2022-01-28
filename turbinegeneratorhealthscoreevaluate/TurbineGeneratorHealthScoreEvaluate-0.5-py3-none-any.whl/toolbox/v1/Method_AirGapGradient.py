import numpy as np


INFINITESIMAL = 0.1**6

class AirGapGradient:
    def __init__(self):
        """
        计算气隙不均匀度

        [1] 参数
        ----------
        -/-

        [2] 方法
        ----------
        unevenness:
            计算不均匀度

        [3] 返回
        -------
        gradient:
            不均匀度

            :math:`(max(X) - min(X)) \\div {average(X)}`

        _buffer:
            dataframe,近期轴位移值与时间戳缓存,"axialDisplacement","timestamp"

        [4] 示例
        --------
        >>> a = list(np.arange(0, 1, 1/10))
        >>> b = list(np.arange(0, 2, 1/100))
        >>> c = list(np.arange(0, 3, 1/1000))
        >>> obj = AirGapGradient()
        >>> obj.unevenness(a, b, c)
        >>> print(obj.gradient)
        """
        self.gradient = None

    def unevenness(self, *args):
        """
        计算不均匀度

        :param args: 一个或多个[float]型的变量
        :type args: list
        """
        _maxes = []
        _mines = []
        _means = []
        for i in range(len(args)):
            _maxes.append(max(args[i]))
            _mines.append(min(args[i]))
            _means.append(np.average(args[i]))
        self.gradient = (max(_maxes) - min(_mines)) / (np.average(_means) + INFINITESIMAL)


if __name__ == '__main__':
    a = list(np.arange(0, 1, 1/10))
    b = list(np.arange(0, 2, 1/100))
    c = list(np.arange(0, 3, 1/1000))
    obj = AirGapGradient()
    obj.unevenness(a, b, c)
    print(obj.gradient)



