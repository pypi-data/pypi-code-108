import pathlib

import joblib
import pandas as pd

from tktl.future import Tktl

# instantiate client
client = Tktl()

# load model
model = joblib.load("assets/model.joblib")

# load reference data path
X = pathlib.Path("assets", "loans_test_X.pqt")
y = pathlib.Path("assets", "loans_test_y.pqt")


# specify transformation
@client.endpoint(profile="binary", X=X, y=y)
def repayment(df):
    pred = model.predict_proba(df)[:, 1]
    return pd.Series(pred)
