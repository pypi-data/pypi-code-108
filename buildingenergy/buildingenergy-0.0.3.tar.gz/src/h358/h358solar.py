import matplotlib.pylab as plt
from pandas.plotting import register_matplotlib_converters
import buildingenergy.openweather
import buildingenergy.solar

register_matplotlib_converters()
site_weather_data = buildingenergy.openweather.OpenWeatherMapJsonReader('grenoble_weather2015-2019.json', from_stringdate = '01/01/2019 0:00:00', to_stringdate = '01/01/2020 0:00:00', sea_level_in_meter=330, albedo=.1).site_weather_data
solar_model = buildingenergy.solar.SolarModel(site_weather_data=site_weather_data)
solar_model.plot_heliodon(2015, 'heliodon')
solar_model.plot_solar_cardinal_irradiations()
plt.figure()
phis1 = solar_model.solar_irradiations(slope_in_deg=160, exposure_in_deg=90)
print('energy PV:', sum(phis1['total'])*21*.13/1000,'kWh')
phis2 = solar_model.solar_irradiations(slope_in_deg=160, exposure_in_deg=0)
print('energy PV:', sum(phis2['total'])*12.46*.13/1000, 'kWh')
plt.plot(solar_model._site_weather_data.get('datetime'), phis2['total'])
plt.plot(solar_model._site_weather_data.get('datetime'), phis1['total'])
plt.legend(('sud','ouest'))
#solar_model.plot_angles()
plt.show()
