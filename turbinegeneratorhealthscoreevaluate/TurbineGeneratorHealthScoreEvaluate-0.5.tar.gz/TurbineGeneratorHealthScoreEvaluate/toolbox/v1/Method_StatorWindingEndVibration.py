import numpy as np


class StatorWindingEndVibration:
    def __init__(self, *args):
        """
        计算多个定子端部振动测点最大值

        [1] 参数
        ----------
        *args:
            tuple[list],多个list型的定子端部振动测点通频值

        [2] 返回
        -------
        maximumVibration:
            多个定子端部振动测点通频值的最大值

        [3] 示例1
        --------
        >>> a = np.arange(0, 3, 0.001)
        >>> b = np.arange(0, 2, 0.001)
        >>> c = np.arange(0, 6.3, 0.001)
        >>> print(StatorWindingEndVibration(a, b, c).maximumVibration)
        """
        _maxes = []
        for i in range(len(args)):
            _maxes.append(max(args[i]))

        self.maximumVibration = max(_maxes)


if __name__ == '__main__':
    a = np.arange(0, 3, 0.001)
    b = np.arange(0, 2, 0.001)
    c = np.arange(0, 6.3, 0.001)
    print(StatorWindingEndVibration(a, b, c).maximumVibration)