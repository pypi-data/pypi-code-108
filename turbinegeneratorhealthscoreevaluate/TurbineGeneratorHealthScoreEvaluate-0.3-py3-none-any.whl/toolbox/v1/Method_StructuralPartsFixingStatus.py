import datetime as dt

import pandas as pd


class StructuralPartsFixingStatus:
    def __init__(self, **kwargs):
        """
        结构件固定情况判断

        [1] 参数
        ----------
        powerUpperLimit:
            float,视在功率下限,MVA
        powerLowerLimit:
            float,视在功率上限,MVA
        processingClock:
            float,每日进行处理的时刻,默认00:00:00
        buffer:
            dataframe,缓存,默认pd.DataFrame([], columns=["time", "power", "vibAmp"])

        [2] 方法
        ----------
        update:
            记录新数据更新缓存,在指定的时间计算前日的通频振幅均值

        [3] 返回
        -------
        vibAmpAverage:
            近一日通频振幅均值,{"timeRange": 进行均值计算的时间范围, "value": 均值, "timestamp": 当前时间戳}

        [4] 示例
        --------
        >>> databaseName = 'bearing_pad_temper'
        >>> tableName = '轴承瓦温20200320_20200327_原始数据'
        >>> host = 'localhost'
        >>> port = 3306
        >>> userID = 'root'
        >>> password = '000000'
        >>> obj = mysqlOperator(databaseName=databaseName, tableName=tableName, host=host, port=port, userID=userID,
        >>>            password = password)
        >>> content = '时间戳,有功功率,汽机润滑油压'
        >>> condition = "(时间戳>=\'2020-03-20 16:00:00\') and (时间戳<=\'2020-03-24 20:20:00\')"
        >>> data = obj.selectData(content=content, condition=condition)
        >>> tsRecord = list(map(str, data["时间戳"].tolist()))
        >>> for i in range(len(tsRecord)):
        >>>     tsRecord[i] = (dt.datetime.strptime(tsRecord[i], "%Y-%m-%d %H:%M:%S") + dt.timedelta(days=675)).strftime("%Y-%m-%d %H:%M:%S")
        >>> powerRecord = data["有功功率"].tolist()
        >>> vibAmpRecord = data["汽机润滑油压"].tolist()
        >>> thermalStabilityRecord = [item==1 for item in np.ones_like(vibAmpRecord).tolist()]
        >>> ratioRecord = []
        >>> _powerCache, _vibAmpCache, _tsCache = [], [], []
        >>> _bufferCache = pd.DataFrame([], columns=["time", "power", "vibAmp"])
        >>> for i in range(len(data)):
        >>>     obj = StructuralPartsFixingStatus(powerUpperLimit=600, powerLowerLimit=400, buffer=_bufferCache)
        >>>     obj.update(powerRecord[i], thermalStabilityRecord[i], vibAmpRecord[i], tsRecord[i])
        >>>     _bufferCache = obj._buffer
        >>>     [print(obj.vibAmpAverage) if obj.vibAmpAverage else None]
        """
        keys = kwargs.keys()
        # ===== 外部参数 ===== #
        self.powerUpperLimit = 195 if "powerUpperLimit" not in keys else kwargs["powerUpperLimit"]
        self.powerLowerLimit = 185 if "powerLowerLimit" not in keys else kwargs["powerLowerLimit"]
        self.runAtClock = "00:00:00" if "processingClock" not in keys else kwargs["processingClock"]
        # ===== 内部、输出参数 ===== #
        self._buffer = kwargs["buffer"] if ("buffer" in keys)and(len(kwargs["buffer"]) != 0) else pd.DataFrame([], columns=["time", "power", "vibAmp"])
        # ===== 输出参数 ===== #
        self.vibAmpAverage = None

    def update(self, power: float, thermalStability: bool, vibAmp: float, ts: str):
        """
        记录新数据更新缓存,在指定的时间计算前日的通频振幅均值

        :param power: float,视在功率,MVA
        :param thermalStability: bool,是否为热稳定状态
        :param vibAmp: float,振动通频幅值
        :param ts: str,当前参与刷新的样本的时间戳,%Y-%m-%d %H:%M:%S
        :return: None
        """
        powerEligible = self.powerLowerLimit<=power<=self.powerUpperLimit
        thermalStabilityEligible = thermalStability == True
        if powerEligible and thermalStabilityEligible:
            _sample = {"power": power, "vibAmp": vibAmp, "time": ts}
            self._buffer = self._buffer.append(_sample, ignore_index=True)

        tsStrpClock = dt.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        if len(self._buffer) >= 2:
            lastEpochClockTo = (tsStrpClock - dt.timedelta(days=1)).strftime("%Y-%m-%d {TIME}").replace("{TIME}", self.runAtClock)
            clockFrom = tsStrpClock.strftime("%Y-%m-%d {TIME}").replace("{TIME}", self.runAtClock)
            clockTo = (tsStrpClock + dt.timedelta(days=1)).strftime("%Y-%m-%d {TIME}").replace("{TIME}", self.runAtClock)
            selectedDF_wait2Update = self._buffer.where((self._buffer["time"]<=clockTo)&(self._buffer["time"]>=clockFrom)).dropna().reset_index(drop=True)
            if len(selectedDF_wait2Update) == 1:
                clockFrom_lastEpoch = (tsStrpClock - dt.timedelta(days=1)).strftime("%Y-%m-%d {TIME}").replace("{TIME}", self.runAtClock)
                clockTo_lastEpoch = tsStrpClock.strftime("%Y-%m-%d {TIME}").replace("{TIME}",self.runAtClock)
                selectedDF_wait2Cal = self._buffer.where((self._buffer["time"] <= clockTo_lastEpoch) & (self._buffer["time"] >= clockFrom_lastEpoch)).dropna().reset_index(drop=True)
                self._buffer = selectedDF_wait2Update
                self.vibAmpAverage = {"timeRange": f"{clockFrom_lastEpoch}~{clockTo_lastEpoch}", "value": selectedDF_wait2Cal["vibAmp"].mean(), "timestamp": ts}
