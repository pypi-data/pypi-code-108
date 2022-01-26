import time


class RubberSealAgingDegree:
	def __init__(self, **kwargs):
	    """
	    计算橡胶密封件老化程度

	    :math:`2^{T_i/T_0} - 1`

	    :math:`T_i 当前累积运行时间(年)`

	    :math:`T_0 设计运行年限(年)`

	    [1] 参数
	    ----------
	    sinceYear:
	        int,设备投运时间(年),默认2000
	    nowYear:
	        int,当前时间(年),默认系统时间
	    designLife:
	        float,设计使用年限(年),默认20

	    [2] 返回
	    -------
	    agingDegree:
	        float,老化程度.应当属于[0, 1]

	    [3] 示例
	    --------
	    >>> for i in range(2000, 2051, 1):
	    >>>     print(i, RubberSealAgingDegree(sinceYear=2000, nowYear=i, designLife=20).agingDegree)

	    """
	    keys = kwargs.keys()
	    self.__sinceYear = kwargs["sinceYear"] if "sinceYear" in keys else 2000
	    self.__nowYear = kwargs["nowYear"] if "nowYear" in keys else int(time.localtime().tm_year)
	    self.__rubberPartDesignLife = kwargs["designLife"] if "designLife" in keys else 20
	    self.agingDegree = None
	    self.__agingDegreeCal()

	def __agingDegreeCal(self):
		t = self.__nowYear - self.__sinceYear
		self.agingDegree = 2**(t/self.__rubberPartDesignLife) - 1
