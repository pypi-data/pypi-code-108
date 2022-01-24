import pandas as pd


def get_wards():
    df = pd.read_csv("/components/wards.csv")
    return df.to_json(orient='index')
