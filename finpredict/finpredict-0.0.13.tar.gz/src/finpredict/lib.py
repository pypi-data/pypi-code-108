import pandas_datareader.data as web
from pandas_datareader import wb
import pandas as pd
import numpy as np
import requests


USER_AGENT = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
        " Chrome/91.0.4472.124 Safari/537.36"
    )
}


class FinData:
    def __init__(self):
        self.start = None
        self.end = None
        self.symbol = None
        self.indexes = None
        self.sesh = requests.Session()
        self.sesh.headers.update(USER_AGENT)
        pd.set_option("display.precision", 2)

    @staticmethod
    def _build_df(df):
        df["Date"] = pd.to_datetime(df["DATE"])
        df["Day"] = [i.day for i in df["Date"]]
        df["Month"] = [i.month for i in df["Date"]]
        df["Year"] = [i.year for i in df["Date"]]
        df.drop(["DATE"], axis=1, inplace=True)
        return df

    @staticmethod
    def _build_technical_df(df):
        """
        This static method computes some technical indicators based on the dataframe values
        """
        df["8ema"] = df["Adj Close"].ewm(span=8, adjust=False).mean()
        df["21ema"] = df["Adj Close"].ewm(span=21, adjust=False).mean()
        df["20sma"] = df["Adj Close"].rolling(window=20).mean()
        df["50sma"] = df["Adj Close"].rolling(window=50).mean()
        df["100sma"] = df["Adj Close"].rolling(window=100).mean()
        df["200sma"] = df["Adj Close"].rolling(window=200).mean()
        df["rstd"] = df["Adj Close"].rolling(window=20).std()
        df["bollinger_upper_band"] = df["20sma"] + 2 * df["rstd"]
        df["bollinger_lower_band"] = df["20sma"] - 2 * df["rstd"]
        df["Daily Return"] = df["Adj Close"].pct_change()
        return df

    def get_gdp(self, start, end):
        df = web.DataReader("GDP", "fred", start=start, end=end).reset_index()
        df = self._build_df(df)
        return df

    def get_gdp_rate(self, country, start, end):
        df = (
            wb.download(
                indicator="NY.GDP.MKTP.KD.ZG", country=[country], start=start, end=end
            )
            .reset_index()
            .set_index("year")
        )
        return df

    def get_unemployment(self, start, end):
        df = web.DataReader("UNRATE", "fred", start=start, end=end).reset_index()
        df = self._build_df(df)
        return df

    def get_currencies(self, start, end):
        indexes = ["DEXUSEU", "DEXJPUS", "DEXCHUS"]
        df = (
            web.DataReader(indexes, "fred", start=start, end=end)
            .fillna(method="bfill")
            .reset_index()
        )
        df = self._build_df(df)
        df = df.rename(
            columns={"DEXUSEU": "USD/EU", "DEXJPUS": "USD/YEN", "DEXCHUS": "USD/YUAN"}
        )
        return df

    def get_finance_data(self, start, end):
        indexes = [
            "UNRATE",
            "GDP",
            "FPCPITOTLZGUSA",
            "CPALTT01USM657N",
            "RSAFS",
            "USSTHPI",
            "IEABC",
            "GFDEBTN",
            "FEDFUNDS",
            "PAYEMS",
            "DCOILWTICO",
            "GOLDAMGBD228NLBM",
            "PALLFNFINDEXQ",
        ]
        df = (
            web.DataReader(indexes, "fred", start=start, end=end)
            .fillna(0)
            .reset_index()
        )
        df = self._build_df(df)
        df = df.rename(
            columns={
                "FPCPITOTLZGUSA": "INFLATION",
                "CPALTT01USM657N": "CPI",
                "RSAFS": "AdvanceRetailSales",
                "USSTHPI": "HousePrices",
                "IEABC": "BalanceOnCurrentAccount",
                "GFDEBTN": "TotalPublicDebtInMillion",
                "FEDFUNDS": "EffectiveFederalFundsRate",
                "PAYEMS": "TotalNonfarm",
                "DCOILWTICO": "CrudeOil",
                "GOLDAMGBD228NLBM": "Gold",
                "PALLFNFINDEXQ": "CommoditiesIndex",
            }
        )
        return df

    def get_stock(self, symbol, start, end):
        df = web.DataReader(
            symbol, "yahoo", start=start, end=end, session=self.sesh
        ).reset_index()
        df["Day"] = [i.day for i in df["Date"]]
        df["Month"] = [i.month for i in df["Date"]]
        df["Year"] = [i.year for i in df["Date"]]
        df = self._build_technical_df(df)
        df = df.set_index("Date")
        return df

    @staticmethod
    def get_war_index(start, end):
        """
        War Index is an index based on $ITA.
        iShares U.S. Aerospace & Defense ETF (ITA). This ETF price reflects
        the Index of all defense companies in US.
        """
        sesh = requests.Session()
        sesh.headers.update(USER_AGENT)
        df = web.DataReader("ITA", "yahoo", start=start, end=end, session=sesh)
        return df

    @staticmethod
    def get_covid_stat():
        data = "https://api.covidtracking.com/v1/us/daily.csv"
        df = pd.read_csv(data).reset_index(drop=True)
        df["Date"] = pd.to_datetime(df["date"], format="%Y%m%d")
        df = df.set_index("Date")
        return df

    @staticmethod
    def get_solar_cycle():
        data = "https://services.swpc.noaa.gov/json/solar-cycle/observed-solar-cycle-indices.json"
        df = pd.read_json(data).reset_index(drop=True)
        df["Date"] = pd.to_datetime(df["time-tag"], format="%Y-%m")
        df = df.set_index("Date")
        return df
