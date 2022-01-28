from auger_ml.algorithms.dnn_base import DeepNeuralNetworkClassifier, DeepNeuralNetworkRegressor


class DNN1LayerClassifier(DeepNeuralNetworkClassifier):
    pass


class DNN2LayerClassifier(DeepNeuralNetworkClassifier):
    pass


class DNN3LayerClassifier(DeepNeuralNetworkClassifier):
    pass


class DNN4LayerClassifier(DeepNeuralNetworkClassifier):
    pass


class DNN1LayerRegressor(DeepNeuralNetworkRegressor):
    pass


class DNN2LayerRegressor(DeepNeuralNetworkRegressor):
    pass


class DNN3LayerRegressor(DeepNeuralNetworkRegressor):
    pass


class DNN4LayerRegressor(DeepNeuralNetworkRegressor):
    pass


if __name__ == "__main__":
    from sklearn.utils.estimator_checks import check_estimator

    check_estimator(DNN1LayerClassifier)
    check_estimator(DNN2LayerClassifier)
    check_estimator(DNN3LayerClassifier)
    check_estimator(DNN4LayerClassifier)
    check_estimator(DNN1LayerRegressor)
    check_estimator(DNN2LayerRegressor)
    check_estimator(DNN3LayerRegressor)
    check_estimator(DNN4LayerRegressor)
