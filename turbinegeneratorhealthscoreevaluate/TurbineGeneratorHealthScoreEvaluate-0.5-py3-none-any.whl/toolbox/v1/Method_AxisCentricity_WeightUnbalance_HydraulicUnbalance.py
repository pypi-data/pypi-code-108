INFINITESIMAL = 0.1**8
class AxisCentricity_WeightUnbalance_HydraulicUnbalance:
    """
    计算轴线对中水平、质量不平衡水平、水力不平衡判断下,某频幅值变化率或相对变化率

    [1] 参数
    ----------
    data:
        float, 需要计算变化率的对象数据

    [2] 方法
    ----------
    gradientCal:
        变化率计算

    [3] 返回
    -------
    -/-:
        变化率

    [4] 示例
    --------
    >>> databaseName = 'bearing_pad_temper'
    >>> tableName = '轴承瓦温20200320_20200327_原始数据'
    >>> host = 'localhost'
    >>> port = 3306
    >>> userID = 'root'
    >>> password = '000000'
    >>> obj = mysqlOperator(databaseName=databaseName, tableName=tableName, host=host, port=port, userID=userID,
    >>>                     password=password)
    >>> content = '时间戳,发电机励端轴瓦温度'
    >>> condition = "(时间戳>=\'2020-03-20 16:00:00\') and (时间戳<=\'2020-03-20 20:20:00\')"
    >>> data = obj.selectData(content=content, condition=condition)
    >>> dataRecord = data["发电机励端轴瓦温度"].tolist()
    >>> ratioRecord = []
    >>> _buffer = None
    >>> for i in range(len(dataRecord)):
    >>> 	obj = AxisCentricity_WeightUnbalance_HydraulicUnbalance(buffer=_buffer)
    >>> 	obj.gradientCal(dataRecord[i])
    >>> 	ratioRecord.append(obj.ratio)
    >>> 	_buffer = obj.buffer
    >>> plt.subplot(211)
    >>> plt.plot(dataRecord)
    >>> plt.subplot(212)
    >>> plt.plot(ratioRecord)
    >>> plt.show()

    [5] 备注
    -----
    * 输入为某频幅值时,输出为该频幅值变化率
    * 输入为某频幅值与某频幅值之比时,输出为该频幅值与某幅值之比的变化率

    """

    def __init__(self, **kwargs):
        if ("buffer" in kwargs.keys()) and (kwargs["buffer"]):
            self.buffer = kwargs["buffer"]
        else:
            self.buffer = None
        self.ratio = None

    def gradientCal(self, data: float):
        if not self.buffer:
            self.buffer = data
            self.ratio = 0
        else:
            cache = self.buffer
            self.buffer = data
            self.ratio = data / (cache + INFINITESIMAL)