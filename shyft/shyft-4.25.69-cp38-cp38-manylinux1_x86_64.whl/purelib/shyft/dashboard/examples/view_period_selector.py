import shyft.time_series as sa
import numpy as np

from bokeh.layouts import column
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.io import curdoc
from bokeh.models.formatters import DatetimeTickFormatter

from shyft.dashboard.time_series.tools.view_time_axis_tools import ViewPeriodSelector


cal = sa.Calendar()
start = sa.utctime_now()
end = start + cal.YEAR*5

fig = figure(x_range=(start*1000, end*1000), y_range=(0, 10), width=1422, tools=['pan', 'wheel_zoom'],
             active_drag="pan")
fig.title.text = "Time period selection tool"

n = 100
t = np.linspace(start*1000, end*1000, n)
f1 = 2
f2 = 5
vals = np.sin(2.*np.pi*f1*t) + np.random.randn(n)*0.8 + np.cos(2.*np.pi*f2*t) + 3

data = ColumnDataSource(dict(x=t, y=vals))
fig.line(x='x', y='y', source=data)
# tax = DatetimeTickFormatter(years=['%Y'], months=['%d.%b %Y'], days=['%d.%b\n%Y'])
tax = DatetimeTickFormatter()
tax.microseconds = ['%fus']
tax.milliseconds = ['%3Nms', '%S.%3Ns']
tax.seconds = ['%Ss']
tax.minsec = [':%M:%S']
tax.minutes = [':%M', '%Mm']
tax.hourmin = ['%H:%M']
# tax.hours = ['%Hh', '%H:%M']
tax.hours = ['%d.%b %H:%M']
# tax.days = ['%a-w%V-%g', '%x']  # day-w<isoweek>-<isoyear>
tax.days = ['%d.%b.%Y']  # dd.mmm.yyyy
# tax.months = ['%d/%m/%Y', '%d%b%Y']
tax.months = ['%d%b%Y']
tax.years = ['%m/%Y']


fig.xaxis.formatter = tax

fig.x_range.start = (start + cal.YEAR*4)*1000
fig.x_range.end = end*1000

view_period_selector = ViewPeriodSelector()
view_period_selector.add_to_figure(figure=fig)


doc = curdoc()
doc.add_root(column(view_period_selector.layout, fig))
curdoc().title = "Period_selector"
