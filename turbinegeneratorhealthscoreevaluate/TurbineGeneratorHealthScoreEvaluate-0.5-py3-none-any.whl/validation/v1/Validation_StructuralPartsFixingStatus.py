import datetime as dt
import pandas as pd
import numpy as np

from commonMethods_zhaozl_green.toolbox.Method_mysqlOperator import mysqlOperator
from TurbineGeneratorHealthScoreEvaluate.toolbox.v1.Method_StructuralPartsFixingStatus import StructuralPartsFixingStatus


def main():
    databaseName = 'bearing_pad_temper'
    tableName = '轴承瓦温20200320_20200327_原始数据'
    host = 'localhost'
    port = 3306
    userID = 'root'
    password = '000000'
    obj = mysqlOperator(databaseName=databaseName, tableName=tableName, host=host, port=port, userID=userID,
               password = password)
    content = '时间戳,有功功率,汽机润滑油压'
    condition = "(时间戳>=\'2020-03-20 16:00:00\') and (时间戳<=\'2020-03-24 20:20:00\')"
    data = obj.selectData(content=content, condition=condition)
    tsRecord = list(map(str, data["时间戳"].tolist()))
    for i in range(len(tsRecord)):
        tsRecord[i] = (dt.datetime.strptime(tsRecord[i], "%Y-%m-%d %H:%M:%S") + dt.timedelta(days=675)).strftime("%Y-%m-%d %H:%M:%S")
    powerRecord = data["有功功率"].tolist()
    vibAmpRecord = data["汽机润滑油压"].tolist()
    thermalStabilityRecord = [item==1 for item in np.ones_like(vibAmpRecord).tolist()]
    ratioRecord = []
    _powerCache, _vibAmpCache, _tsCache = [], [], []
    _bufferCache = pd.DataFrame([], columns=["time", "power", "vibAmp"])
    for i in range(len(data)):
        obj = StructuralPartsFixingStatus(powerUpperLimit=600, powerLowerLimit=400, buffer=_bufferCache)
        obj.update(powerRecord[i], thermalStabilityRecord[i], vibAmpRecord[i], tsRecord[i])
        _bufferCache = obj._buffer
        [print(obj.vibAmpAverage) if obj.vibAmpAverage else None]


if __name__ == '__main__':
    main()



