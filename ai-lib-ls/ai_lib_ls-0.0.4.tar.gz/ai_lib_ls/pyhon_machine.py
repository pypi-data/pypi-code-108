"""
*@File    : Uitls.py
*@Time    :8/18/21 4:25 下午
*author:QauFue ,技术改变未来
*doc ： 机器学习封装库
步骤：
*1，数据处理（数据采集+去噪）
*2， 模型训练 （特征提取+模型）
*3，模型评估和优化（MSE、F1.score,AUC+调参）
*4，模型应用 （A/B 测试）
"""
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures
from sklearn.preprocessing import StandardScaler
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix  # 绘制矩阵的内容
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split  # 训练和测试 分数据
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import Ridge
from sklearn.multiclass import OneVsRestClassifier  # 2分类算法扩展到多分类算法 ovr
from sklearn.multiclass import OneVsOneClassifier  # 2分类算法扩展到多分类算法 ovo
from sklearn.linear_model import LogisticRegression  # 逻辑回归，用于分类算法
from sklearn.metrics import precision_score  # 精准率
from sklearn.metrics import recall_score  # 招回率
from sklearn.metrics import f1_score  # f1 同时兼顾 精准率和召回率
from sklearn.metrics import confusion_matrix  # 可以设置精准率的数据值，方便调优精准
from sklearn.metrics import roc_curve  # ROC 用来观察 精准度的
from sklearn.metrics import roc_auc_score  # 用来计算分数 ，评估两个模型的 那个更优
from sklearn.svm import LinearSVC  # SVC  的实际应用
from sklearn.svm import SVC  # 多项式核函数的SVM
from sklearn.svm import LinearSVR  # SVM 思想解决回归问题
from sklearn.tree import DecisionTreeClassifier  # 决策树
from sklearn.tree import DecisionTreeRegressor  # 决策树
from sklearn.ensemble import VotingClassifier  # 集成学习
from sklearn.ensemble import BaggingClassifier  # 集成学习 ，将数据分成若干样本，分别评估数据能力
from sklearn.ensemble import RandomForestClassifier  # 随机森林
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import AdaBoostClassifier  # 若干个样本 逐渐优化算法，优化以前的错误
from sklearn.ensemble import GradientBoostingClassifier  # 若干个样本 ，优化补偿上一个样本
from sklearn.decomposition import PCA
from sklearn.preprocessing import scale

# 集成学习回归问题的相关内容
from sklearn.ensemble import BaggingRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.ensemble import AdaBoostRegressor
from sklearn.ensemble import GradientBoostingRegressor


class LinearUtil():

    def PolynomialRegression(degree):
        return Pipeline([
            ("poly", PolynomialFeatures(degree=degree)),  # 多项式增加特征，
            ("std_scaler", StandardScaler()),  # 数值的均一化
            ("lin_reg", LinearRegression())  # 线性回归
        ])

    # 岭回归
    def RidgeRegression(degree, alpha):
        '''
         使用案例
         ridge1_reg = RidgeRegression(20, 0.001)
         ridge1_reg.fit(X_train, y_train)
         y1_predict = ridge1_reg.predict(X_test)
         mean_squared_error(y_test, y1_predict)
         '''
        return Pipeline([
            ("poly", PolynomialFeatures(degree=degree)),
            ("std_scaler", StandardScaler()),
            ("ridge_reg", Ridge(alpha=alpha))
        ])

    # train：训练数据 ，test:测试数据
    def train_test(self, X, y, random_state=666):  # 将数据分成训练数据 和 测试数据集
        # 返回数据4个 ： X_train, X_test, y_train, y_test
        return train_test_split(X, y, random_state)  # test_size =0.4 相当于40%数据拆分为测试数据

    # 均方根误差
    # y_test： 测试的数据集，y_predict：训练之后的数据
    def mean_squared_error(self, y_test, y_predict):
        return mean_squared_error(y_test, y_predict)

    def getData(self, start, end, cont=100):
        # 随机生成数据；start 开始的数据~ 结束的数据，cont :数据总量，随机
        return np.random.uniform(start, end, size=cont).reshape(-1, 1)

    # 2分类任务,转变多分类任务 ovo
    def OVO(self, X_train, y_train, X_test, y_test):
        ovr = OneVsRestClassifier(LogisticRegression())
        ovr.fit(X_train, y_train)
        ovr.score(X_test, y_test)
        return self

    # 2分类任务,转变多分类任务 ovr
    def OVR(self, X_train, y_train, X_test, y_test):
        ovr = OneVsOneClassifier(LogisticRegression())
        ovr.fit(X_train, y_train)
        ovr.score(X_test, y_test)
        print(ovr.score(X_test, y_test))
        return self


# 混淆矩阵，计算精准率，召回率 3本书10-4
class ProductionRate():
    def all_score(self, y_true, y_predict):
        return [
            f'混淆矩阵 分类准确性：{self.confusion_matrix(y_true, y_predict)}      ',  # 计算混淆矩阵以评估分类的准确性。
            f'精准率:{self.precision_score(y_true, y_predict)}      ',
            f'召回率：{self.recall_score(y_true, y_predict)}      ',
            f'F1 分数:{self.f1_score(y_true, y_predict)}      ',
        ]

    def precision_score(self, y_true, y_predict):
        ''' 精准率：
              y_test:测试数据上y的真实值
              y_predict ：预测的结果值 '''
        return precision_score(y_true, y_predict)

    def recall_score(self, y_true, y_predict):
        ''' 召回率：对数据的预测结果的错误的数据率'''
        return recall_score(y_true, y_predict)

    def f1_score(self, y_true, y_predict):
        '''F1 分数，兼顾召回和 精准率的 综合判断精度'''
        return f1_score(y_true, y_predict)

    def confusion_matrix(self, y_true, y_predict):
        '''
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=666)

        from sklearn.linear_model import LogisticRegression
        log_reg = LogisticRegression()
        log_reg.fit(X_train, y_train)
        y_predict = log_reg.predict(X_test)

        decision_scores = log_reg.decision_function(X_test)

        y_predict = np.array(decision_scores >= 5, dtype='int')  decision_scores:判断条件
        '''

        return confusion_matrix(y_true, y_predict)

    def roc_curve(self, y_test, decision_scores):
        # fprs, tprs, thresholds = roc_curve(y_test, decision_scores)
        # plt.plot(fprs, tprs)
        # plt.show()
        return roc_curve(y_test, decision_scores)

    def roc_auc_score(self, y_test, decision_scores):
        return roc_auc_score(y_test, decision_scores)


class PCAUtil:
    def pca_cheack(self, X_multi):
        data = scale(X_multi.values)  # 标准化，标准化之后就自动根据协方差矩阵进行主成分分析了
        pca = PCA()  # 可以调整主成分个数，n_components = 1
        pca.fit(data)

        return [
            f'输出特征根:{pca.explained_variance_}',
            f'输出解释方差比:{pca.explained_variance_ratio_}',
            f'输出主成分:{pca.components_}'
        ]


class SVCUtil:

    def PolynomialSVC(degree, C=1.0):
        return Pipeline([
            ("poly", PolynomialFeatures(degree=degree)),
            ("std_scaler", StandardScaler()),
            ("linearSVC", LinearSVC(C=C))
        ])

    def PolynomialKernelSVC(degree, C=1.0):
        return Pipeline([
            ("std_scaler", StandardScaler()),
            ("kernelSVC", SVC(kernel="poly", degree=degree, C=C))
        ])

    def svcfit(self, X, y):  # 线性SSVC
        svc = LinearSVC(C=1e9)  # C 越大，越接近直线，越小越曲线
        svc.fit(X, y)

    # SVM 思想解决回归问题
    def StandardLinearSVR(epsilon=0.1):
        # 应用=》
        # svr = StandardLinearSVR()
        # svr.fit(X_train, y_train)
        # svr.score(X_test, y_test)

        return Pipeline([
            ('std_scaler', StandardScaler()),
            ('linearSVR', LinearSVR(epsilon=epsilon))
        ])


# 决策树
class cart_tree:

    def fit(self, X, y):
        dt_clf = DecisionTreeClassifier()
        dt_clf.fit(X, y)

    def fit2(self, X_train, y_train):
        dt_reg = DecisionTreeRegressor()
        dt_reg.fit(X_train, y_train)
        # dt_reg.score(X_test, y_test)


# 集成学习
class newVotingClassifier:

    # hard 少数服从多少 投票方式
    def hard_voting(self, X_train, y_train, X_test, y_test):
        voting_clf = VotingClassifier(estimators=[
            ('log_clf', LogisticRegression()),
            ('svm_clf', SVC()),
            ('dt_clf', DecisionTreeClassifier(random_state=666))],
            voting='hard')  # hard 少数服从多少

        voting_clf.fit(X_train, y_train)
        voting_clf.score(X_test, y_test)

    # 根据 投票的权重进行 分类： 评委 和 观众 投票的票的权重不一样
    def soft_voting(self, X_train, y_train, X_test, y_test):
        voting_clf = VotingClassifier(estimators=[
            ('log_clf', LogisticRegression()),
            ('svm_clf', SVC(probability=True)),
            ('dt_clf', DecisionTreeClassifier(random_state=666))],
            voting='soft')

        voting_clf.fit(X_train, y_train)
        voting_clf.score(X_test, y_test)

    # 集成学习 ，将数据分成若干样本，分别评估数据能力
    def bagging(self, X_train, y_train, X_test, y_test):
        ''':n_estimators :样本模型的数量，分成多少个模型，理论上越大越好 > 2
            max_samples ：每个模型多少个数据
            bootstrap =true 放回取样， flase :不放回取样
            n_jobs=-1 : 并行处理，数据处理结果会快一点
            oob_score=True：  如果有些数据没有取到的数据可以变成测试数据
            max_features=1 ： 特征取样，设置特征数量
        '''
        bagging_clf = BaggingClassifier(DecisionTreeClassifier(),
                                        n_estimators=500, max_samples=100,
                                        bootstrap=True, n_jobs=-1)

        bagging_clf.fit(X_train, y_train)
        bagging_clf.score(X_test, y_test)
        # bagging_clf.oob_score_

    # 随机森林
    def random_forest(self, X_train, y_train):
        ''':max_leaf_nodes :叶子分类的个数
        '''
        rf_clf = RandomForestClassifier(n_estimators=500, oob_score=True, random_state=666, n_jobs=-1)
        rf_clf.fit(X_train, y_train)
        rf_clf.oob_score_

    def et_train(self, X_train, y_train):
        et_clf = ExtraTreesClassifier(n_estimators=500, bootstrap=True, oob_score=True, random_state=666, n_jobs=-1)
        et_clf.fit(X_train, y_train)
        et_clf.oob_score_

    # 数据的样本 优化以前犯得错误
    def ada_boosting(self, X_train, y_train, X_test, y_test):
        ada_clf = AdaBoostClassifier(
            DecisionTreeClassifier(max_depth=2), n_estimators=500)
        ada_clf.fit(X_train, y_train)
        ada_clf.score(X_test, y_test)

    # 数据样本 将上一个的数据样本的补偿
    def gradient_boosting(self, X_train, y_train):
        gb_clf = GradientBoostingClassifier(max_depth=2, n_estimators=30)
        gb_clf.fit(X_train, y_train)


class MatplotlibUtil():

    # 绘制学习曲线
    # 使用方法：plot_learning_curve(LinearRegression(), X_train, X_test, y_train, y_test)
    # plot_learning_curve(PolynomialRegression(degree=2), X_train, X_test, y_train, y_test)
    def plot_learning_curve(algo, X_train, X_test, y_train, y_test):
        train_score = []
        test_score = []
        for i in range(1, len(X_train) + 1):
            algo.fit(X_train[:i], y_train[:i])

            y_train_predict = algo.predict(X_train[:i])
            train_score.append(mean_squared_error(y_train[:i], y_train_predict))

            y_test_predict = algo.predict(X_test)
            test_score.append(mean_squared_error(y_test, y_test_predict))

        plt.plot([i for i in range(1, len(X_train) + 1)],
                 np.sqrt(train_score), label="train")
        plt.plot([i for i in range(1, len(X_train) + 1)],
                 np.sqrt(test_score), label="test")
        plt.legend()
        plt.axis([0, len(X_train) + 1, 0, 4])
        plt.show()

    # 绘制矩阵的图像 ，10-9
    def confusion_matrix(self, y_test, y_predict):
        confusion_matrix(y_test, y_predict)
        cfm = confusion_matrix(y_test, y_predict)
        plt.matshow(cfm, cmap=plt.cm.gray)
        plt.show()


class PyplotUtil():
    def scatter(self, x, y):
        plt.scatter(x, y)
        plt.show()
        return self
