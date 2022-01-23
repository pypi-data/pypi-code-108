try:
    # framework is running
    from .startup_choice import *
except ImportError as _excp:
    # class is imported by itself
    if (
        'attempted relative import with no known parent package' in str(_excp)
        or 'No module named \'omfit_classes\'' in str(_excp)
        or "No module named '__main__.startup_choice'" in str(_excp)
    ):
        from startup_choice import *
    else:
        raise


from omfit_classes.omfit_hdf5 import dict2hdf5, OMFIThdf5

import weakref
from matplotlib.pyplot import *
from matplotlib import pyplot

__all__ = ['figures_dmp', 'OMFITdmp']

# ----------------
# Data Managment Plan
# ----------------

patch_plot_functions = [
    'acorr',
    #'add_artist',
    #'add_callback',
    #'add_collection',
    #'add_container',
    #'add_image',
    #'add_line',
    #'add_patch',
    #'add_table',
    #'aname',
    'angle_spectrum',
    'annotate',
    #'apply_aspect',
    'arrow',
    #'autoscale',
    #'autoscale_view',
    #'axes',
    #'axes_downsample',
    'axhline',
    'axhspan',
    'axis',
    'axvline',
    'axvspan',
    'bar',
    'barbs',
    'barh',
    'boxplot',
    'broken_barh',
    'bxp',
    #'can_pan',
    #'can_zoom',
    #'cla', #<-------
    'clabel',
    #'clear', #<------
    'cohere',
    #'contains',
    #'contains_point',
    'contour',
    'contourf',
    #'convert_xunits',
    #'convert_yunits',
    'csd',
    #'drag_pan',
    #'draw',
    #'draw_artist',
    #'end_pan',
    'errorbar',
    'eventplot',
    'fill',
    'fill_between',
    'fill_betweenx',
    #'findobj',
    #'format_coord',
    #'format_cursor_data',
    #'format_xdata',
    #'format_ydata',
    #'grid', #<-------
    #'has_data',
    #'have_units',
    'hexbin',
    'hist',
    'hist2d',
    #'hitlist',
    'hlines',
    #'hold',
    'imshow',
    #'in_axes',
    #'invert_xaxis',
    #'invert_yaxis',
    #'is_figure_set',
    #'is_transform_set',
    #'ishold',
    'legend',
    #'locator_params',
    'loglog',
    'magnitude_spectrum',
    #'margins',
    'matshow',
    #'minorticks_off',
    #'minorticks_on',
    #'mouseover',
    #'name',
    #'pchanged',
    'pcolor',
    'pcolorfast',
    'pcolormesh',
    'phase_spectrum',
    #'pick',
    #'pickable',
    'pie',
    'plot',
    'plot_date',
    #'properties',
    'psd',
    'quiver',
    'quiverkey',
    #'redraw_in_frame',
    #'relim',
    #'remove', #<-------
    #'remove_callback',
    'reset_position',
    'scatter',
    'semilogx',
    'semilogy',
    #'set',
    'specgram',
    'spy',
    'stackplot',
    #'stale',
    #'start_pan',
    'stem',
    'step',
    'sticky_edges',
    'streamplot',
    'table',
    'text',
    #'tick_params',
    #'ticklabel_format',
    'tricontour',
    'tricontourf',
    'tripcolor',
    'triplot',
    #'twinx',
    #'twiny',
    #'update',
    #'update_datalim',
    #'update_datalim_bounds',
    #'update_datalim_numerix',
    #'update_from',
    #'use_sticky_edges',
    'violin',
    'violinplot',
    'vlines',
    'xaxis_date',
    #'xaxis_inverted',
    'xcorr',
    'yaxis_date',
    #'yaxis_inverted',
    #'zorder'
] + [
    #'set_adjustable',
    #'set_agg_filter',
    'set_alpha',
    #'set_anchor',
    #'set_animated',
    #'set_aspect',
    #'set_autoscale_on',
    #'set_autoscalex_on',
    #'set_autoscaley_on',
    #'set_axes',
    #'set_axes_locator',
    #'set_axis_bgcolor',
    #'set_axis_off',
    #'set_axis_on',
    #'set_axisbelow',
    #'set_clip_box',
    #'set_clip_on',
    #'set_clip_path',
    #'set_color_cycle',
    #'set_contains',
    #'set_cursor_props',
    #'set_downsampling',
    #'set_facecolor',
    #'set_fc',
    #'set_figure',
    #'set_frame_on',
    #'set_gid',
    #'set_label',
    #'set_navigate',
    #'set_navigate_mode',
    #'set_path_effects',
    #'set_picker',
    #'set_position',
    #'set_prop_cycle',
    #'set_rasterization_zorder',
    #'set_rasterized',
    #'set_sketch_params',
    #'set_snap',
    'set_title',
    #'set_transform',
    #'set_url',
    #'set_visible',
    #'set_xbound',
    'set_xlabel',
    #'set_xlim',
    #'set_xmargin',
    'set_xscale',
    'set_xticklabels',
    'set_xticks',
    #'set_ybound',
    'set_ylabel',
    #'set_ylim',
    #'set_ymargin',
    'set_yscale',
    'set_yticklabels',
    'set_yticks',
    #'set_zorder'
]


def _tr(self):
    for item in self:
        if 'data' in self[item]:
            data = self[item]['data']
            if isinstance(data, str) and data == '_None':
                data = None
            self[item] = data
        else:
            _tr(self[item])

    return self


class OMFITdmp(SortedDict, OMFITobject):
    """
    Class to satisfy DoE Data Managment Plan that requires the data used in a publication figure to be made available
    """

    def __init__(self, filename, *args, **kw):
        # this is when loading from HDF5 object
        if isinstance(filename, str):
            OMFITobject.__init__(self, filename, *args, **kw)
            SortedDict.__init__(self)
            self.dynaLoad = True
        else:
            # this is when creating object from matplotlib figure
            num = getattr(filename, 'number', filename.get_label())
            OMFITobject.__init__(self, 'Figure_%s.h5' % num, *args, **kw)
            SortedDict.__init__(self)
            self.from_fig(filename)

    def from_fig(self, fig):
        """
        Populate object and file from matplotlib figure

        :param fig: matplotlib figure

        :return: self
        """
        self.clear()
        self.dynaLoad = False
        for ai, ax in enumerate(fig.get_axes()):
            if id(ax) in figures_dmp:
                self['axes_%d' % id(ax)] = axp = copy.copy(figures_dmp[id(ax)]['DATA'])
                self['axes_%d' % id(ax)].append({'func': 'ax.set_xlim', 'args': [ax.get_xlim()]})
                self['axes_%d' % id(ax)].append({'func': 'ax.set_ylim', 'args': [ax.get_ylim()]})
                tmp = ax.get_position().get_points().flatten().tolist()
                tmp = tmp[:2] + [tmp[2] - tmp[0]] + [tmp[3] - tmp[1]]
                self['axes_%d' % id(ax)].insert(0, {'func': 'fig.add_axes', 'args': [tmp]})
        self.save()
        return self

    def load(self):
        self.clear()
        tmp = OMFIThdf5(self.filename, noCopyToCWD=True)['DATA']
        for ax in tmp:
            self[ax] = []
            for step in sorted(tmp[ax], key=lambda x: int(x.split('_')[1])):
                self[ax].append(_tr(tmp[ax][step]))
                self[ax][-1]['args'] = list(self[ax][-1]['args'].values())

    def plot(self):
        """
        generate plot based on dictionary content

        :return: matplotlib Figure handle
        """
        from omfit_classes.utils_plot import image

        fig = pyplot.gcf()
        for ax in self:
            for step in self[ax]:
                func = b2s(step['func'])
                if func == 'fig.add_axes':
                    ax = fig.add_axes(*step.get('args', []), **step.get('kwargs', {}))
                else:
                    eval(func)(*step.get('args', []), **step.get('kwargs', {}))
        return fig

    def save(self):
        """
        writes ditionary to HDF5
        """
        dictin = {}
        for ax in self:
            dictin['axes_%d' % id(ax)] = tmp = {'step_%d' % k: copy.copy(v) for k, v in enumerate(self[ax])}
            for step in list(tmp.values()):
                step['args'] = {'%d' % k: copy.copy(v) for k, v in enumerate(step['args'])}
        return dict2hdf5(self.filename, {'DATA': dictin}, compression=9)

    def script(self):
        """
        :return: string with Python script to reproduce the figure (with DATA!)
        """
        txt = ['# auto-generated OMFIT data management plan plotting script', '']
        txt.append('fig = pyplot.gcf()')
        txt.append('')
        for k, ax in enumerate(self):
            if len(self) > 1:
                comment = 'AXES %d' % k
                txt.append('# ' + comment)
            for step in self[ax]:
                args_txt = ','.join(map(repr, step.get('args', [])))
                kw_txt = keyword_arguments(step.get('kwargs', {}))
                if step['func'] == 'fig.add_axes':
                    txt.append("ax = fig.add_axes(%s)" % ','.join([_f for _f in [args_txt, kw_txt] if _f]))
                else:
                    txt.append("%s(%s)" % (step['func'], ','.join([_f for _f in [args_txt, kw_txt] if _f])))
            txt.append('')
        return '\n'.join(txt)

    def OMFITpythonPlot(self, filename):
        """
        generate OMFITpythonPlot script from figure (with DATA!)

        :param filename: filename for OMFITpythonPlot script

        :return: OMFITpythonPlot object
        """
        from omfit_classes.omfit_python import OMFITpythonPlot

        return OMFITpythonPlot(filename, fromString=self.script())


figures_dmp = {}
originals = {}
subs = {}

mpl_dump_enable = [True]

# storage function that is used by the @dump_function_usage decorator
def mpl_dump(dumpDict):
    if not mpl_dump_enable[0]:
        return
    # store data information on a per axis basis
    ax = dumpDict['args'][0]
    if id(ax) not in figures_dmp:
        figures_dmp[id(ax)] = {}
    figures_dmp[id(ax)]['weakref'] = weakref.ref(ax)
    figures_dmp[id(ax)].setdefault('DATA', [])
    figures_dmp[id(ax)]['DATA'].append(dumpDict)
    if figures_dmp[id(ax)]['DATA'][-1]['func'].startswith('_omfit_dmp_'):
        figures_dmp[id(ax)]['DATA'][-1]['func'] = 'ax.' + re.sub('^_omfit_dmp_', '', figures_dmp[id(ax)]['DATA'][-1]['func'])
    figures_dmp[id(ax)]['DATA'][-1]['args'] = list(figures_dmp[id(ax)]['DATA'][-1]['args'][1:])
    # cleanup data from old figures
    for item in list(figures_dmp.keys()):
        if figures_dmp[item]['weakref']() is None:
            del figures_dmp[item]


from matplotlib.axes import Axes

# monkey patching of matplotlib.Axes function to track arguments passed
for function_name in patch_plot_functions:
    for package in ['Axes']:
        if hasattr(eval(package), function_name) and (package, function_name) not in originals:
            originals[package, function_name] = getattr(eval(package), function_name)
            subs.setdefault(id(originals[package, function_name]), []).append((package, function_name))
for sub in subs:
    for k, (package, function_name) in enumerate(subs[sub]):
        if k == 0:
            exec(
                '''
@dump_function_usage(mpl_dump)
def _omfit_dmp_{function_name}(*args,**kw):
    #print('{function_name}')
    return originals['{package}','{function_name}'](*args,**kw)
_omfit_dmp_{function_name}.__doc__=originals['{package}','{function_name}'].__doc__
'''.format(
                    function_name=function_name, package=package
                )
            )
        setattr(eval(package), function_name, eval('_omfit_dmp_' + function_name))

############################################
if '__main__' == __name__:
    test_classes_main_header()

    tmp = OMFITdmp(OMFITsrc + '/../samples/DIII-D_1_journal_XXXX_FigXX.h5')
    print(tmp)
