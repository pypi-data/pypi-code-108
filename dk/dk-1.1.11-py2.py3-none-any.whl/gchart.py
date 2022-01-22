from __future__ import print_function

import math
from dk.html import html

# documentation: http://code.google.com/apis/chart/


def dataval(v):
    if int(v) == v:
        return str(v)
    return '%.1f' % round(v, 1)


def data_list(ch, *lst):
    return ch.join(dataval(v) for v in lst)


########################################################################
#  Chart

class Chart(object):
    def __init__(self, size, **kw):
        self.params = kw
        x, y = size
        self.chart_size(x, y)

    def chart_size(self, x, y):
        assert x * y < 300000
        assert x <= 1000
        assert y <= 1000
        self.params['chs'] = '%dx%d' % (x, y)

    def dataval(self, v):
        if int(v) == v:
            return str(v)
        return '%.1f' % round(v, 1)

    def __setitem__(self, k, v):
        self.params[k] = v


########################################################################
#  DataSeries


class DataSeries(object):
    def __init__(self, data, **kw):
        self.data = data
        self.thickness = kw.get('thickness', 1)
        self.length = kw.get('length', 1)
        self.gap = kw.get('gap', 0)
        self.color = kw.get('color', '00A000')
        self.kw = kw

    def dataval(self, v):
        r = self.kw.get('round', 0)
        if r == 1:
            if int(v) == v:
                return str(v)
            return '%.1f' % v
        rv = round(v)
        return str(int(rv))

    @property
    def linestyle(self):
        return data_list(',', self.thickness, self.length, self.gap)

    @property
    def _xseries(self):
        return [x for x, _y in self.data]

    @property
    def xseries(self):
        return map(self.dataval, self._xseries)

    @property
    def _yseries(self):
        return [y for _x, y in self.data]

    @property
    def yseries(self):
        return map(self.dataval, self._yseries)

    @property
    def legend(self):
        return self.kw.get('legend', '')

    @property
    def dataseries(self):
        return ','.join(self.xseries) + '|' + ','.join(self.yseries)

    @property
    def xrange(self):
        if 'xrange' in self.kw:
            return self.kw['xrange']
        return min(self._xseries), max(self._xseries)

    @property
    def yrange(self):
        if 'yrange' in self.kw:
            return self.kw['yrange']
        return min(self._yseries), max(self._yseries)

    @property
    def scale(self):
        return '%s,%s,%s,%s' % (self.xrange + self.yrange)


########################################################################
#  XYLineChart

class XYLineChart(Chart):
    def __init__(self, size):
        super(XYLineChart, self).__init__(size, cht='lxy', chxt='x,y')
        self.data = []
        self.params['chf'] = 'c,lg,45,ffffff,0,76a4fb,0.75|bg,s,EFEFEF'

    def __iadd__(self, dataseries):
        self.data.append(dataseries)
        return self

    def __str__(self):
        self.params['chd'] = 't:' + '|'.join(d.dataseries for d in self.data)
        self.params['chco'] = ','.join(d.color for d in self.data)
        self.params['chls'] = '|'.join(d.linestyle for d in self.data)
        self.params['chds'] = ','.join(d.scale for d in self.data)

        # self.params['chdl'] = '|'.join(d.legend for d in self.data if d.legend)
        self.params['chxt'] = 'x,y'
        self.params['chxl'] = '0:|%s|1:|%s|' % (
            '|'.join(map(str, range(53)[::2])),
            '|'.join(map(str, range(70)[::10])),
            )
        self.params['chg'] = '7.7,14.3'
        self.params['chm'] = 'o,cfffdf,0,-1,7,0'

        x = self.data[0]
        print(x.xrange)
        print(x.yrange)

        src = 'http://chart.apis.google.com/chart?'
        src += '&'.join('%s=%s' % x for x in self.params.items())
        print("LENGTH:", len(src))
        return str(html.img(src=src))

#     def set_chart_data_scale(self):
#         def minmax(s):
#             s = list(s)
#             return self.dataval(min(s)), self.dataval(max(s))

#         def series_data(s):
#             x = '%s,%s' % minmax(x for x,y in s)
#             y = '%s,%s' % minmax(y for x,y in s)
#             return x + ',' + y
#         self.params['chds'] = ','.join(series_data(s) for s in self.data)


class GChart(object):
    def __init__(self, data):
        self._data = []
        self.add_data(data)
        self.params = {}

    def add_data(self, data):
        assert len(data) > 0
        if len(data[0]) == 1:
            data = enumerate(data)
        self._data.append(list(data))

    def ____(self, comment):
        self.xvals = [x for x, y in self._data]
        self.yvals = [y for x, y in self._data]

    def chart_size(self, x, y):
        assert x * y < 300000
        assert x <= 1000
        assert y <= 1000
        self.params['chs'] = '%dx%d' % (x, y)

    def chart_type(self, t):
        self.params['cht'] = {
            'line': 'lc',
            'xyline': 'lxy',
            'sparkline': 'ls',
            'bar': 'bvs',
            'bar-horizontal': 'bhs',
            'bar-vertical': 'bvs',
            'group': 'bvg',
            'group-horizontal': 'bhg',
            'group-vertical': 'bvg',
            'pie': 'p',
            'pie-3d': 'p3',
            'venn': 'v',
            'scatter': 's',
            'radar': 'r',
            'radar-spline': 'rs',
            'map': 't',
            'google-o-meter': 'gom',
        }.get(t, t)

    def format_data(self):
        return ','.join('%.2f' % float(d) for d in self.yvals)

    def data_range(self):
        low = min(self.yvals)
        high = max(self.yvals)
        return '%.1f,%.1f' % (low, high)

    def _xaxis_vals(self):
        return '|' + '|'.join('%d' % v for v in self.xvals) + '|'

    def _yaxis_vals(self):
        start = int(math.floor(min(self.yvals)))
        start = 0
        end = int(math.ceil(max(self.yvals)))
        step = int(round((end - start) / 7.0))
        return '|' + '|'.join(str(n) for n in range(start, end, step)) + '|'

    def axis_labels(self):
        return '0:' + self._xaxis_vals() + '1:' + self._yaxis_vals()

    def grid_lines(self, x, y):
        self.params['chg'] = '%d,%d' % (x, y)

    def axes_range(self):
        xaxis = '0,%.1f,%.1f' % (min(self.xvals), max(self.xvals))
        yaxis = '1,%.1f,%.1f' % (min(self.yvals), max(self.yvals))
        print('|'.join([xaxis, yaxis]))
        return '|'.join([xaxis, yaxis])

    def html(self):
        params = {
            'chd': 't:' + self.format_data(),
            # 'chds': self.data_range(),                 # data scale
            'chds': '0,100',
            'chxt': 'x,y',                               # axis definition
            # 'chxr': self.axes_range(),                 # axis range
            'chxl': self.axis_labels(),                  # axis labels
            # 'chg': '%d,10' % (100.0/len(self.xvals)),  # grid lines
        }
        params.update(self.params)
        src = 'http://chart.apis.google.com/chart?' + '&'.join('%s=%s' % x for x in params.items())
        return html.img(src=src)

    def __str__(self):
        return str(self.html())

    def __setitem__(self, k, v):
        self.params[k] = v


if __name__ == "__main__":
    gc = GChart(enumerate([1, 3, 9, 6, 34, 2, 34, 45, 43, 23, 34, 42, 25]))
    gc['cht'] = 'lc'
    gc['chs'] = '700x350'
    gc['chf'] = 'c,lg,45,ffffff,0,76a4fb,0.75|bg,s,EFEFEF'
    print(gc)
