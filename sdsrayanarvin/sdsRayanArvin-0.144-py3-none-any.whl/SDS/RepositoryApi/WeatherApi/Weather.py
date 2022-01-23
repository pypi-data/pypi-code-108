from sdsRayanArvin.Dataset import WeatherData
from sdsRayanArvin.Repository import Repository


class Weather(Repository):
    def WeatherOnFarm(self, ID_farm):
        res = self.Request.sendWithToken('GET', 'farm/' + ID_farm)
        return WeatherData(res['success'])
