import xgboost as xgb
from feature_engine.creation import MathematicalCombination
from sklearn.metrics import accuracy_score
from sklearn.pipeline import Pipeline

from iris_hector_patino.config.core import config

iris_pipeline = Pipeline(
    [
        (
            "full_combination",
            MathematicalCombination(
                variables_to_combine=config.model_config.features_to_combine
            ),
        ),
        (
            "xgb",
            xgb.XGBClassifier(
                n_estimators=config.model_config.n_estimators,
                learning_rate=config.model_config.learning_rate,
                max_depth=config.model_config.max_depth,
                gamma=config.model_config.gamma,
                subsample=config.model_config.subsample,
                objective="multi:softprob",
                eval_metric=accuracy_score,
            ),
        ),
    ]
)
