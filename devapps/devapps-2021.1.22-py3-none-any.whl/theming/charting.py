"""
Some functions for creating simple value charts.

Currently only one, not yet very generalized but might be already now
of some use, expecially when it's about measuring timings.
Not very performant, nested loops.

Might add other charts later.


The current one mode makes this:

< snip >

    Total Run Times

 pool_new
  parallel_poolsize_1: ||||||||||||||||||| (0.43)
  serial             : ||||||||||||||||||| (0.44)
  parallel_big_pool  : |||||||||| (0.24)
  serial_no_pool     : ||||||||||||||||||||||||||||||||||||| (0.84)
     (1 tick is 0.023)

 pool_established
  parallel_poolsize_1: |||||||||||||||||| (0.42)
  serial             : ||||||||||||||||||| (0.44)
  parallel_big_pool  : | (0.031)
  serial_no_pool     : ||||||||||||||||||||||||||||||||||||| (0.85)
     (1 tick is 0.023)
======================================================================
    Average Run Times

 pool_new
  parallel_poolsize_1: ||||||||||||||||||||||||||||||||||| (0.01)
  serial             : |||||||||||||||||||||||||||||||||||| (0.011)
  parallel_big_pool  : ||||||||||||||||||||||||||||||||||||| (0.011)
  serial_no_pool     : |||||||||||||||||||||||||||||||||| (0.01)
     (1 tick is 0.00029)

 pool_established
  parallel_poolsize_1: |||||||||||||||||||||||||||||||||| (0.01)
  serial             : |||||||||||||||||||||||||||||||||||| (0.011)
  parallel_big_pool  : ||||||||||||||||||||||||||||||||||||| (0.011)
  serial_no_pool     : |||||||||||||||||||||||||||||||||| (0.01)
     (1 tick is 0.0003)
======================================================================
< / snip >

out of this:

< snip >

{'pool_established': {'parallel_big_pool': (0.031485795974731445,
                                            0.011009448766708374),
                      'parallel_poolsize_1': (0.42257595062255859,
                                              0.010400831699371338),
                      'serial': (0.43528890609741211, 0.010847651958465576),
                      'serial_no_pool': (0.84693813323974609,
                                         0.010381799936294556)},
 'pool_new': {'parallel_big_pool': (0.24394702911376953,
                                    0.010902762413024902),
              'parallel_poolsize_1': (0.43367099761962891,
                                      0.010407018661499023),
              'serial': (0.44476079940795898, 0.010810500383377076),
              'serial_no_pool': (0.84292483329772949, 0.010311901569366455)}}
< /snip >

via this command:

from theming.charting import bar_chart
print bar_chart(my_map, mode ='0:Vals,1:Main',  val_descr_list = ['\tTotal Run Times', '\tAverage Run Times'])


"""


def get_val_str(val):
    """ return the value as double precision string with max len 7 """
    if val > 10 and val < 1000000:
        return int(val)
    return '%.2g' % val


def normalize_vals(v, max_width, show_vals=1):
    """
    Normalize the values to a given width.
    """
    # normalize to this length:
    if show_vals:
        show_vals = 7
    else:
        show_vals = 0
    max_val_normalized = max_width - show_vals
    mv = max(v)
    tick_val = mv / float(max_val_normalized)
    ret = []
    for val in v:
        s = get_val_str(val)
        ret.append((val, int(val / tick_val), s))
    return ret, tick_val, get_val_str(tick_val)


def bar_chart(
    m,
    out_fmt='ascii',
    mode=None,
    show_vals=1,
    val_descr_list=None,
    symbol='|',
    legendwidth='auto',
    chart_width=70,
):
    """
        Creates ascii charts of python objects like maps or lists
        on the console
        """
    if mode == '0:Vals,1:Main':
        # if m like: {'Main1': {'V1': [1,3,2]}, 'V2':[5, 1, 1], ...}
        # we will draw sth like:
        """
            Value 1:
                Main1
                -----
                V1: | (1)
                V2: ||||| (5)
                (...)
            Value 2:
                Main1
                -----
                V1: ||| (3)
            (...)
            """
        assert len(symbol) == 1
        if legendwidth == 'auto':
            legendwidth = 0
            for l in m.values()[0].keys():
                kl = len(l)
                if kl > legendwidth:
                    legendwidth = kl

        if not val_descr_list:
            val_descr_list = []
            # check out the length of values (3 in the example):
            vals = len(m.values()[0].values()[0])
            for i in range(0, vals):
                val_descr_list.append('Value %s' % i)

        # the chart is built into this variable:
        res = ''
        v_index = -1

        # now loop through the first display hirarchy:
        for vd in val_descr_list:
            # in this loop we show that value of the value lists:
            v_index += 1

            res += '=' * chart_width + '\n'
            # print value description:
            res += vd + '\n'

            for k, v in m.items():
                val_list = []
                for vt in v.values():
                    try:
                        val_list.append(vt[v_index])
                    except:
                        raise ValueError(
                            'value count is not matching for row %s \
                                    of series %s, index is %s'
                            % (str(vt), v, v_index)
                        )
                width = chart_width - legendwidth - 7
                if not show_vals:
                    # don't show ' ()':
                    width = width + 3
                normalized, tickval, tick_fmt = normalize_vals(
                    val_list, width, show_vals=show_vals
                )

                res += '\n ' + k + '\n'
                # k like 'Main1', v like {'V1': [1,3,4], 'V2': ...}
                ind = -1
                for k1, v1 in v.items():
                    legend = (k1 + ' ' * 100)[:legendwidth] + ': '
                    ind += 1
                    val, ticks, v_disp = normalized[ind]
                    v_disp = ' (%s)' % v_disp
                    # k1 like V1
                    if not show_vals:
                        v_disp = ''
                    res += '  ' + legend + symbol * ticks + '%s\n' % v_disp
                res += '     (1 tick is %s)\n' % tick_fmt
        return res + '=' * chart_width

    raise NotImplemented


if __name__ == '__main__':

    print(normalize_vals([0.1, 34, 2], 70))
    print(normalize_vals([1, 39879709784, 0.000000078782], 70, '%.5e'))
    print('\n\n\n')
    print('Chart test')

    from pprint import pprint

    m = {
        'FirstSeries': {'test1': [1.12312, 0.001, 123123], 'test2': [23, 3434, 4545]},
        'SecondSeries': {
            'test1': [1, 2, 12342430.240],
            'test2': [23234240.001, 123123, 2],
        },
    }
    print('map to chart is:')
    pprint(m)

    print('\n\nDefault arguments\n')
    print(bar_chart(m, mode='0:Vals,1:Main'))
    print('\n' * 5)
    print('\n\nMore complex arguments\n')
    print(
        bar_chart(
            m,
            symbol='*',
            mode='0:Vals,1:Main',
            val_descr_list=['Condition 1', 'Condition 2', 'Condition 3'],
            show_vals=1,
            chart_width=50,
        )
    )
    print('\n\nNo values, width 80')
    print(
        bar_chart(
            m,
            symbol='*',
            mode='0:Vals,1:Main',
            val_descr_list=['Condition 1', 'Condition 2', 'Condition 3'],
            show_vals=None,
            chart_width=80,
        )
    )
