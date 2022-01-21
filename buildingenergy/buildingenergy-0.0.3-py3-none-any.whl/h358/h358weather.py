import buildingenergy.openweather
import matplotlib.pylab as plt
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()
site_weather_data = buildingenergy.openweather.OpenWeatherMapJsonReader('grenoble_weather2015-2019.json', '1/01/2019 0:00:00', '1/01/2020 0:00:00', sea_level_in_meter=330, albedo=.1).site_weather_data
print(site_weather_data.from_stringdate, '>', site_weather_data.to_stringdate)
site_weather_data.day_degrees()
fig, ax = plt.subplots()
plt.plot(site_weather_data.get('stringdate'), site_weather_data.get('temperature'))
ax.set_title('temperature')
ax.axis('tight')
# fig, ax = plt.subplots()
# plt.plot(site_weather_data.get('stringdate'), site_weather_data.get('cloudiness'))
# ax.set_title('cloudiness')
# ax.axis('tight')
# fig, ax = plt.subplots()
# plt.plot(site_weather_data.get('stringdate'), site_weather_data.get('wind_speed'))
# ax.set_title('wind_speed')
# ax.axis('tight')
# fig, ax = plt.subplots()
# plt.plot(site_weather_data.get('stringdate'), site_weather_data.get('humidity'))
# ax.set_title('humidity')
# ax.axis('tight')
plt.show()