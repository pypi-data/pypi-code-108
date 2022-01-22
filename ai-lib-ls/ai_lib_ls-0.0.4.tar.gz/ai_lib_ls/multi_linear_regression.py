"""
*@File    : multi_linear_regression.py
*@Time    :9/9/21 4:01 下午
*author:QauFue ,技术改变未来
*doc ：重要
线性回归,多因子的线性回归
线性分析 ，类似 楼市预测 场景
"""

# 训练数据模型
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from ai_lib_ls.pyhon_machine import ProductionRate
import numpy as np

# 线性回归,多因子的线性回归
class LinearRegressionUtil:
    LR_multi = LinearRegression()

    def fit(self, X_train, y_train):
        self.LR_multi.fit(X_train, y_train)
        return self

    def predict(self, X_test):
        return self.LR_multi.predict(X_test)

    def MSE_R2(self, Y, y2):
        MSE = mean_squared_error(Y, y2)
        R2 = r2_score(Y, y2)
        return [MSE, R2]

    def score(self, LR, X_test, y_test):
        return LR.score(X_test, y_test)

    def multi_fit(self, X_multi, Y):
        self.LR_multi.fit(X_multi, Y)
        y_predict_multi = self.LR_multi.predict(X_multi)
        return self

    def multi_predict(self, test_X):
        return self.LR_multi.predict(test_X)

    def fast_all_fit(self, X_train, y_train, X_test,y_test_true):
        self.LR_multi.fit(X_train, y_train)  # 训练模型没有输出数据
        y_predict = self.LR_multi.predict(X_test)  #预测的结果
        y_predict[y_predict > 0.5] = 1
        y_predict[y_predict < 0.5] = 0
        rate = ProductionRate()
        rate_score = rate.all_score(y_test_true, y_predict)

        print(y_predict)
        print(type(y_predict))
        print(str(rate_score) +'\n' +str(self.LR_multi.score(X_test, y_test_true)))
        print(np.sum(y_predict ==y_test_true) ,len(y_predict))



        return rate_score



