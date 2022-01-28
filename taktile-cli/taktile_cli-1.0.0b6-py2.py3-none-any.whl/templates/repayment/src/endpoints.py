import joblib
import pandas as pd

from tktl.future import Tktl

# instantiate client
client = Tktl()

# load model
model = joblib.load("assets/model.joblib")

# load reference data
data = pd.read_parquet("assets/loans_test.pqt")
label = "Repaid"
X = data.drop(columns=label)
y = data[label]


# specify transformation
@client.endpoint(profile="binary", X=X, y=y)
def repayment(df):
    pred = model.predict_proba(df)[:, 1]
    return pd.Series(pred)
