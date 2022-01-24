import pandas as pd


def get_cities():
    df = pd.read_csv("/components/cities.csv")
    return df.to_json(orient='index')
