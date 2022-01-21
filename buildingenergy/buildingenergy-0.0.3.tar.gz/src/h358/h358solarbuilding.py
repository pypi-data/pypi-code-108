import matplotlib.pyplot
import buildingenergy.openweather
import buildingenergy.solarbuilding
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()
site_weather_data = buildingenergy.openweather.OpenWeatherMapJsonReader('grenoble_weather2015-2019.json', from_stringdate = "1/01/2019 0:00:00", to_stringdate = "1/01/2020 0:00:00",  sea_level_in_meter=330, albedo=.1).site_weather_data
solar_mask = buildingenergy.solarbuilding.WindowMask((-86, 60), (20, 68))
officeH358 = buildingenergy.solarbuilding.Building(site_weather_data)
officeH358.add_window('main', surface=2, exposure_in_deg=-13, slope_in_deg=90, solar_factor=0.85, window_mask=solar_mask)
officeH358.generate_xls('officeH358', heat_temperature_reference=21, cool_temperature_reference=26)

solar_gains_with_mask, _ = officeH358.solar_gain
print('total_solar_gain with mask in kWh:', sum(solar_gains_with_mask)/1000)
officeH358_nomask = buildingenergy.solarbuilding.Building(site_weather_data)
officeH358_nomask.add_window('main', surface=2, exposure_in_deg=0, slope_in_deg=90, solar_factor=0.85, window_mask=None)
solar_gains_without_mask, _ = officeH358_nomask.solar_gain
print('total_solar_gain without mask in kWh:', sum(solar_gains_without_mask)/1000)
fig, ax = matplotlib.pyplot.subplots()
matplotlib.pyplot.plot(officeH358_nomask.datetimes, solar_gains_without_mask)
matplotlib.pyplot.plot(officeH358.datetimes, solar_gains_with_mask)
ax.set_title('solar gain in Wh')
ax.legend(('no mask', 'mask'))
ax.axis('tight')
ax.grid()
matplotlib.pyplot.show()