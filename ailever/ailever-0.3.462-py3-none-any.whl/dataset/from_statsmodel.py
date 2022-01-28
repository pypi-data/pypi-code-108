import statsmodels.api as sm

class Statsmodels_API:
    def macrodata(self, download=False):
        df = sm.datasets.macrodata.load_pandas().data
        if download:
            df.to_csv('macro.csv')
        return df

    def sunspots(self, download=False):
        df = sm.datasets.sunspots.load_pandas().data
        if download:
            df.to_csv('sunspots.csv')
        return df

    def anes96(self, download=False):
        df = sm.datasets.anes96.load_pandas().data
        if download:
            df.to_csv('anes96.csv')
        return df

    def cancer(self, download=False):
        df = sm.datasets.cancer.load_pandas().data
        if download:
            df.to_csv('cancer.csv')
        return df

    def ccard(self, download=False):
        df = sm.datasets.ccard.load_pandas().data
        if download:
            df.to_csv('ccard.csv')
        return df

    def china_smoking(self, download=False):
        df = sm.datasets.china_smoking.load_pandas().data
        if download:
            df.to_csv('china_smoking.csv')
        return df

    def co2(self, download=False):
        df = sm.datasets.co2.load_pandas().data
        if download:
            df.to_csv('co2.csv')
        return df

    def committee(self, download=False):
        df = sm.datasets.committee.load_pandas().data
        if download:
            df.to_csv('committee.csv')
        return df

    def copper(self, download=False):
        df = sm.datasets.copper.load_pandas().data
        if download:
            df.to_csv('copper.csv')
        return df

    def cpunish(self, download=False):
        df = sm.datasets.cpunish.load_pandas().data
        if download:
            df.to_csv('cpunish.csv')
        return df

    def elnino(self, download=False):
        df = sm.datasets.elnino.load_pandas().data
        if download:
            df.to_csv('elnino.csv')
        return df

    def engel(self, download=False):
        df = sm.datasets.engel.load_pandas().data
        if download:
            df.to_csv('engel.csv')
        return df

    def fair(self, download=False):
        df = sm.datasets.fair.load_pandas().data
        if download:
            df.to_csv('fair.csv')
        return df

    def fertility(self, download=False):
        df = sm.datasets.fertility.load_pandas().data
        if download:
            df.to_csv('fertility.csv')
        return df

    def grunfeld(self, download=False):
        df = sm.datasets.grunfeld.load_pandas().data
        if download:
            df.to_csv('frunfeld.csv')
        return df

    def heart(self, download=False):
        df = sm.datasets.heart.load_pandas().data
        if download:
            df.to_csv('heart.csv')
        return df

    def interest_inflation(self, download=False):
        df = sm.datasets.interest_inflation.load_pandas().data
        if download:
            df.to_csv('interest_inflation.csv')
        return df

    def longley(self, download=False):
        df = sm.datasets.longley.load_pandas().data
        if download:
            df.to_csv('longley.csv')
        return df

    def modechoice(self, download=False):
        df = sm.datasets.modechoice.load_pandas().data
        if download:
            df.to_csv('modechoice.csv')
        return df

    def nile(self, download=False):
        df = sm.datasets.nile.load_pandas().data
        if download:
            df.to_csv('nile.csv')
        return df

    def randhie(self, download=False):
        df = sm.datasets.randhie.load_pandas().data
        if download:
            df.to_csv('randhie.csv')
        return df

    def scotland(self, download=False):
        df = sm.datasets.scotland.load_pandas().data
        if download:
            df.to_csv('scotland.csv')
        return df

    def spector(self, download=False):
        df = sm.datasets.spector.load_pandas().data
        if download:
            df.to_csv('spector.csv')
        return df

    def stackloss(self, download=False):
        df = sm.datasets.stackloss.load_pandas().data
        if download:
            df.to_csv('stackloss.csv')
        return df

    def star98(self, download=False):
        df = sm.datasets.star98.load_pandas().data
        if download:
            df.to_csv('star98.csv')
        return df

    def statecrime(self, download=False):
        df = sm.datasets.statecrime.load_pandas().data
        if download:
            df.to_csv('statecrime.csv')
        return df

    def strikes(self, download=False):
        df = sm.datasets.strikes.load_pandas().data
        if download:
            df.to_csv('strikes.csv')
        return df
