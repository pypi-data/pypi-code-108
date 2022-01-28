import numpy as np
import pandas as pd
from commonMethods_zhaozl_green.toolbox.Method_mysqlOperator import mysqlOperator
from TurbineGeneratorHealthScoreEvaluate.toolbox.v1.Method_AirCoolerHeatExchangeEfficiency import AirCoolerHeatExchangeEfficiency
import matplotlib.pyplot as plt


def main():
	# ===== 数据调用 ===== #
	databaseName = 'bearing_pad_temper'
	tableName = '轴承瓦温20200320_20200327_原始数据'
	host = 'localhost'
	port = 3306
	userID = 'root'
	password = '000000'
	obj = mysqlOperator(databaseName=databaseName, tableName=tableName, host=host, port=port, userID=userID,
	                    password=password)
	content = '发电机励端轴瓦温度,发电机汽端轴瓦温度,发电机9轴承回油温度,发电机10轴承回油温度,发电机励端轴瓦温度,发电机汽端轴瓦温度,发电机9轴承回油温度,发电机10轴承回油温度,有功功率'
	condition = "(时间戳>=\'2020-03-20 16:00:00\') and (时间戳<=\'2020-03-20 20:00:00\')"
	data = obj.selectData(content=content, condition=condition)
	data.columns = ["热风温度1", "热风温度2", "冷风温度1", "冷风温度2", "热水温度1", "热水温度2", "冷水温度1", "冷水温度2", "有功功率"]
	for item in data:
		if "热" in item:
			data[item] = pd.Series((data[item].values.tolist() + np.random.rand(1, len(data[item]))).flatten())

	efficiencyIndexRecorder = []
	windTemperDiffRecorder = []
	waterTemperDiffRecorder = []
	apparentPowerRecordCache = []
	for i in range(len(data)):
		effObj = AirCoolerHeatExchangeEfficiency(apparentPowerRecord=apparentPowerRecordCache)
		effObj.update_and_determine(coldWaterTempers=data[["冷水温度1", "冷水温度2"]].iloc[i, :].tolist(),
		                            warmWaterTempers=data[["热水温度1", "热水温度2"]].iloc[i, :].tolist(),
		                            coldWindTempers=data[["冷风温度1", "冷风温度2"]].iloc[i, :].tolist(),
		                            warmWindTempers=data[["热风温度1", "热风温度2"]].iloc[i, :].tolist(),
		                            apparentPower=data[["有功功率"]].iloc[i, :].values)
		apparentPowerRecordCache = effObj._apparentPowerRecord
		windTemperDiffRecorder.append(effObj._windTemperDiff)
		waterTemperDiffRecorder.append(effObj._waterTemperDiff)
		efficiencyIndexRecorder.append(effObj.efficiencyIndex)

	plt.plot(windTemperDiffRecorder, "b:")
	plt.plot(waterTemperDiffRecorder, "g:")
	plt.twinx()
	plt.plot(efficiencyIndexRecorder, "r")
	plt.show()


if __name__ == '__main__':
	main()
