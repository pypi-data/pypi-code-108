from enum import Enum


class RegressorType(str, Enum):
    RANDOMFOREST = "RandomForest"
    MARTINGALE = "Martingale"
    VBLINREG = "VBLinReg"
    MONDRIANFOREST = "MondrianForest"
    XGBOOST = "XGBoost"

    def __str__(self) -> str:
        return str(self.value)
