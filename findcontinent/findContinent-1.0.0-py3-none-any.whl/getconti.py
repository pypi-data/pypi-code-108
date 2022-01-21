import pandas as pd
import os

class getConti:
    def __init__(self):
        self.path = os.path.dirname(os.path.abspath(__file__))
        print(self.path)
        self.CountryDictionary = {}
        self.readdata()
    def readdata(self):
        cols = ["Continent", "Country"]
        df = pd.read_csv(str(self.path)+"/datasource/Continents_to_CountryNames.csv", usecols=cols)
        country = df["Country"].tolist()
        continent = df["Continent"].tolist()
        self.CountryDictionary = dict(zip(country, continent))
        

    def getContinent(self,country):

        try:
            return self.CountryDictionary[country.title()]
        except:
            return "Unknown"

    def getContinents(self, countryList):
        continents = []
        for country in countryList:
            continents.append(self.getContinent(country))
        return continents
    
    def getContinentDictionary(self, countryList):
        continents = {}
        for country in countryList:
            continents[country] = self.getContinent(country)
        return continents

