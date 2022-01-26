import os
import glob
import yaml
import json
from itertools import repeat
from typing import Dict, Optional, List, Union

import click
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_pdf import PdfPages
from quickstats.utils.process_tools import parallel_run
from quickstats.plots.template import draw_atlas_label, format_axis_ticks, parse_transform, draw_hatches, \
                                      draw_sigma_bands, draw_sigma_lines, get_box_dimension, draw_text, centralize_axis
from quickstats.components.numerics import ceildiv, pretty_float
from quickstats.utils.common_utils import json_load

BASE_STYLE = {
    'pull': {
        'marker'     : 'o', 
        'markersize' :  6,
        'ls'         : 'none',
        'color'      : 'k',
        'capsize'    : 4,
        'capthick'   : 2, 
        'linewidth'  : 2
    },
    'one_sigma':{
        'marker'     : None, 
        'markersize' : 0,
        'ls'         : 'none',
        'color'      : 'r',
        'capsize'    : 4,
        'capthick'   : 2, 
        'linewidth'  : 2.5
    },    
    'shade':{
        'hatch' : 'xxxxx', 
        'color' : 'gray', 
        'alpha' : 0.1,
        'fill'  : True
    },
    'legend': {
        'x': 0.48,
        'dx': 0.01,
        'dy': 0.01,
        'fontsize': 15,
        'fontsize_minor': 12,
        'box_width': 0.06,
        'box_height': 0.025,
        'line_width': 0.05
    },
    'sigma_lines':{
        'color'    : 'gray',
        'linestyle': '--'
    },
    'logo':{
        'x': 0.02,
        'fontsize': 25
    },    
    'label':{
        'x': 0.02,
        'dy': 0.03,
        'fontsize': 20
    },
    'figure': {
        'width' : 8,
        'height': 14,
        'dpi'   : 100
    },
    'xaxis' :{
        'labelsize': 15
    },
    'yaxis':{
        'labelsize': 12
    },
    'xaxis_label':{
        'fontsize': 18,
        'loc' : 'right'
    }
}

DEFAULT_STYLE = {
    'prefit_1': {
        'linewidth': 2,
        'edgecolor': '#000155',
        'alpha': 1,
        'hatch': None,
        'fill': False,
    },
    'prefit_2':{
        'linewidth': 2,
        'edgecolor': '#027734',
        'alpha': 1,
        'hatch': None,
        'fill': False,
    },
    'postfit_1':{
        'linewidth': 0,
        'color': '#0094ff',
        'alpha': 1,
        'hatch': None,
        'fill': True,
    },
    'postfit_2':{
        'linewidth': 0,
        'color': "#44ff94",
        'alpha': 1,
        'hatch': None,
        'fill': True,
    }, **BASE_STYLE
}
        
TREX_STYLE = {
    'prefit_1': {
        'linewidth': 2,
        'color': '#00FFFF',
        'edgecolor': '#00FFFF',
        'alpha': 0.6,
        'hatch': None,
        'fill': False,
    },
    'prefit_2':{
        'linewidth': 2,
        'color': '#6495ED',
        'edgecolor': '#6495ED',
        'alpha': 0.6,
        'hatch': None,
        'fill': False,
    },
    'postfit_1':{
        'linewidth': 0,
        'color': '#00FFFF',
        'alpha': 0.6,
        'hatch': None,
        'fill': True,
    },
    'postfit_2':{
        'linewidth': 0,
        'color': "#6495ED",
        'alpha': 0.6,
        'hatch': None,
        'fill': True,
    }, **BASE_STYLE
}

class NPRankingPlot:
    def __init__(self, input_dir:str=None, poi:Optional[str]=None):
        self._data = None
        if input_dir is not None:
            self.load(input_dir, poi=poi)
        
    @property
    def data(self):
        return self._data
    
    @staticmethod
    def _extract_pull_result(file:str, poi:str=None):
        with open(file, 'r') as infile:
                data = json_load(infile)
        result = {}
        nuis_data = data['nuis']
        result['nuis_label']  = nuis_data['nuisance']
        result['nuis_val']    = nuis_data['nuis_hat'] - nuis_data['nuis_nom']
        result['nuis_up']     = nuis_data['nuis_hi']
        result['nuis_down']   = nuis_data['nuis_lo']
        result['nuis_prefit'] = nuis_data['nuis_prefit']
        if poi:
            poi_data = data['pois'].get(poi, None)
            if not poi_data:
                raise ValueError("No impact evaluated for the POI \"{}\" in the file {}".format(poi, file))
            result['poi_hat']      = poi_data['hat']
            result['impact_postfit_up']    = poi_data['up'] 
            result['impact_postfit_down']  = poi_data['down'] 
            result['impact_prefit_up']   = poi_data['up_nom'] 
            result['impact_prefit_down'] = poi_data['down_nom']
        return result
    
    @staticmethod
    def extract_pull_results(input_dir:str, poi:str=None):
        if not os.path.exists(input_dir):
            raise FileNotFoundError('input directory {} does not exist'.format(input_dir))
        if not os.path.isdir(input_dir):
            raise ValueError('{} is not a directory'.format(input_dir))
        input_files = glob.glob(os.path.join(input_dir, "*.json"))
        data = parallel_run(NPRankingPlot._extract_pull_result, input_files, repeat(poi))
        df = pd.DataFrame(data)
        if poi:
            df['impact_postfit_up']   -= df['poi_hat']
            df['impact_postfit_down'] -= df['poi_hat']
            df['impact_prefit_up']    -= df['poi_hat']
            df['impact_prefit_down']  -= df['poi_hat']
            df['impact_postfit_total'] = abs(df['impact_postfit_up']) + abs(df['impact_postfit_down'])
            df['impact_prefit_total']  = abs(df['impact_prefit_up']) + abs(df['impact_prefit_down'])
        return df
    
    def load(self, input_dir:str, poi:Optional[str]=None):
        self._data = self.extract_pull_results(input_dir, poi=poi)
        
    @staticmethod
    def get_processed_data(df, num=None, threshold=None, ranking=True):
        processed_df = df.copy()
        if 'impact_postfit_total' in processed_df:
            if ranking:
                processed_df.sort_values('impact_postfit_total', ascending=False, inplace=True)
            if threshold is not None:
                processed_df = processed_df[processed_df['impact_postfit_total'] >= threshold]            
        if num is not None:
            processed_df = processed_df.head(num)
        processed_df = processed_df.iloc[::-1]
        return processed_df
    
    @staticmethod
    def setup_axis(ax1, ax2, **styles):
        ax2.set_zorder(ax1.get_zorder()-1)
        ax1.patch.set_visible(False)
        ax1.tick_params(axis='y', which='both', left=False, right=False, **styles['yaxis'])
        ax1.tick_params(axis='x', direction="in", **styles['xaxis'])
        ax2.tick_params(axis='x', direction="in", **styles['xaxis'])    
        
    @staticmethod
    def draw_impact_legend(axis, poi:str, impact_type:str, x:float, y:float, 
                           label_1:str, label_2:str, dx:float=0.01, dy:float=0.01,
                           box_width:float=0.06, box_height:float=0.025, **styles):
        """
            Draw legend for prefit/postfit impact.
            x: starting x-position in Axes coordinates
            y: starting y-position in Axes coordinates
        """
        header = '{} Impact on {}:'.format(impact_type.title(), poi)
        fontsize, fontsize_minor = styles['legend']['fontsize'], styles['legend']['fontsize_minor']
        style_type1, style_type2 = styles['{}_1'.format(impact_type)], styles['{}_2'.format(impact_type)]
        text_prefit = axis.text(x, y - dy, header, fontsize=fontsize, transform=axis.transAxes,
                                horizontalalignment='left', verticalalignment='top')
        _, _, ymin, _ = get_box_dimension(text_prefit)
        # y-position of marker and label
        y_marker = ymin - dy - box_height
        y_label  = y_marker + box_height/2
        # draw first marker
        axis.add_patch(Rectangle((x + dx, y_marker), box_width, 
                                 box_height, transform=axis.transAxes, **style_type1))
        # draw label for first marker
        label_box_1 = axis.text(x + 2*dx + box_width, y_label, label_1, 
                                  fontsize=fontsize_minor, transform=axis.transAxes,
                                  horizontalalignment='left',
                                  verticalalignment='center')
        _, x_2, _, _ = get_box_dimension(label_box_1)
        # draw second marker
        axis.add_patch(Rectangle((x_2 + 2*dx, y_marker), box_width, 
                                 box_height, transform=axis.transAxes, **style_type2))
        # draw label for second marker
        label_box_2 = axis.text(x_2 + 3*dx + box_width, y_label, label_2, 
                                  fontsize=fontsize_minor, transform=axis.transAxes,
                                  horizontalalignment='left',
                                  verticalalignment='center')
        return y_marker
    
    @staticmethod
    def draw_legend(axis, poi:str=r"$\mu$", x:float=0.48, y:float=-1.2, show_sigma:bool=True, show_prefit:bool=True,
                    show_postfit:bool=True, correlation:bool=True, **styles):
        """
            Draw legends.
            x: starting x-position in Axes coordinates
            y: starting y-position in Data coordinates
        """
        dx = styles['legend']['dx']
        dy = styles['legend']['dy']
        line_width     = styles['legend']['line_width']
        box_width      = styles['legend']['box_width']
        box_height     = styles['legend']['box_height']
        fontsize       = styles['legend']['fontsize']
        fontsize_minor = styles['legend']['fontsize_minor']
        # starting x-position of pull and one sigma legend markers
        x_marker = x + dx + line_width
        # current y-position
        y_curr  = y
        ########################################################################################
        # draw pull legend
        pull_styles = {k:v for k,v in styles['pull'].items() if 'cap' not in k}
        transform = transforms.blended_transform_factory(axis.transAxes, axis.transData) 
        axis.errorbar(x_marker, y_curr, yerr=None, xerr=line_width, 
                      transform=transform, **pull_styles)
        text_pull = axis.text(x_marker + line_width + 2*dx, y, 'Nuis. Param. Pull', 
                              fontsize=fontsize, transform=transform,
                              horizontalalignment='left',
                              verticalalignment='center')
        #########################################################################################
        
        #########################################################################################
        # draw one sigma legend
        _, _, ymin, ymax = get_box_dimension(text_pull)
        y_curr = ymin
        if show_sigma:
            height = ymax - ymin
            one_sigma_styles = {k:v for k,v in styles['one_sigma'].items() if 'cap' not in k}
            axis.errorbar(x_marker, ymin - height, yerr=None, xerr=line_width, 
                          transform=axis.transAxes, **one_sigma_styles)
            text_sigma = axis.text(x_marker + line_width + 2*dx, ymin - height, '1 standard deviation', 
                                   fontsize=fontsize, transform=axis.transAxes,
                                   horizontalalignment='left',
                                   verticalalignment='center')
            _, _, y_curr, _ = get_box_dimension(text_sigma)
        #########################################################################################
        if correlation:
            prefit_label1 = r"Correlated"
            prefit_label2 = r"Anticorrelated"
            postfit_label1 = r"Correlated"
            postfit_label2 = r"Anticorrelated"
        else:  
            prefit_label1 = r"$\theta = \hat{\theta}+\Delta\theta$"
            prefit_label2 = r"$\theta = \hat{\theta}-\Delta\theta$"
            postfit_label1 = r"$\theta = \hat{\theta}+\Delta\hat{\theta}$"
            postfit_label2 = r"$\theta = \hat{\theta}-\Delta\hat{\theta}$"
        #########################################################################################
        # draw prefit impact legend
        if show_prefit:
            y_curr = NPRankingPlot.draw_impact_legend(axis, poi, "prefit", x, y_curr, prefit_label1, 
                                                      prefit_label2, dx, dy, box_width, box_height, **styles)
        #########################################################################################
        #########################################################################################
        # draw postfit impact legend
        if show_postfit:
            y_curr = NPRankingPlot.draw_impact_legend(axis, poi, "postfit", x, y_curr, postfit_label1, 
                                                      postfit_label2, dx, dy, box_width, box_height, **styles)
        #########################################################################################
        
    @staticmethod
    def plot_pulls(axis, data, height=1.0, show_sigma:bool=True, **styles):
        n = len(data)
        y = np.arange(0, n*height, height)
        axis.errorbar(data['nuis_val'], y, yerr=None, 
                      xerr=[abs(data['nuis_down']), abs(data['nuis_up'])], 
                      zorder=3.1, **styles['pull'])
        if show_sigma:
            axis.errorbar(data['nuis_val'], y, yerr=None, 
                          xerr=[abs(data['nuis_prefit']), abs(data['nuis_prefit'])],
                          zorder=3.0, **styles['one_sigma'])        
        
    @staticmethod
    def plot_impact(axis, data, show_prefit:bool=True, show_postfit:bool=True, correlation:bool=True, onesided:bool=True, 
                    relative:bool=False, height:float=1.0, spacing:float=0., **styles):     
        n = len(data)  
        impact_types = []
        if show_postfit:
            impact_types.append('postfit')
        if show_prefit:
            impact_types.append('prefit')
        if not correlation:
            impact_types = impact_types[::-1]
        for it in impact_types:
            prefix = 'impact_{}'.format(it)
            # retrieve the impact data
            if relative:
                impact_down = data['{}_down'.format(prefix)].values / data['poi_hat'].values
                impact_up = data['{}_up'.format(prefix)].values / data['poi_hat'].values           
            else:
                impact_down = data['{}_down'.format(prefix)].values
                impact_up = data['{}_up'.format(prefix)].values

            if correlation:
                # negative-valued correlated impact 
                neg_type1 = (impact_down <= 0)
                # positive-valued correlated imapact
                pos_type1 = (impact_up >= 0)
                # negative-valued anticorrelated impact
                neg_type2 = ~pos_type1
                # positive-valued anticorrelated impact
                pos_type2 = ~neg_type1
                x_neg_type1 = impact_down[neg_type1]
                x_pos_type1 = impact_up[pos_type1]
                x_neg_type2 = impact_up[neg_type2]
                x_pos_type2 = impact_down[pos_type2]
            else:
                # negative-valued +1 sigma impact
                neg_type1 = impact_up < 0
                # positive-valued +1 sigma impact
                pos_type1 = impact_up > 0
                # negative-valued -1 sigma impact
                neg_type2 = impact_down < 0
                # positive-valued -1 sigma impact
                pos_type2 = impact_down > 0 
                x_neg_type1 = impact_up[neg_type1]
                x_pos_type1 = impact_up[pos_type1]
                x_neg_type2 = impact_down[neg_type2]    
                x_pos_type2 = impact_down[pos_type2]

            style_type1, style_type2 = styles['{}_1'.format(it)], styles['{}_2'.format(it)]
            x = np.zeros(n)
            y_type1 = np.arange(0, n*height, height) - height/2 + spacing/2
            y_type2 = y_type1.copy()
            w = height - spacing
            h = np.full((n), w, dtype=float)
            if onesided:
                all_neg = (impact_down < 0) & (impact_up < 0)
                all_pos = (impact_down > 0) & (impact_up > 0)
                h[all_neg] = w/2
                h[all_pos] = w/2
                # secondary bar
                # put type1 bar above by default and type2 bar below
                y_type1[all_neg] = y_type1[all_neg] + w/2
                y_type1[all_pos] = y_type1[all_pos] + w/2

            # negative-valued type 1
            axis.bar(x_neg_type1, height=h[neg_type1], 
                     width=abs(x_neg_type1), bottom=y_type1[neg_type1], 
                     align='edge', **style_type1)
            # positive-valued type 1
            axis.bar(x[pos_type1], height=h[pos_type1], 
                     width=x_pos_type1, bottom=y_type1[pos_type1], 
                     align='edge', **style_type1)          
            # negative-valued type 2
            axis.bar(x_neg_type2, height=h[neg_type2], 
                     width=abs(x_neg_type2), bottom=y_type2[neg_type2], 
                     align='edge', **style_type2)
            # positive-valued type 2
            axis.bar(x[pos_type2], height=h[pos_type2], 
                     width=x_pos_type2, bottom=y_type2[pos_type2], 
                     align='edge', **style_type2)
            
    @staticmethod
    def draw_np_labels(axis, data, padding:int=7, height:float=1.0):
        n = len(data)
        y_ticks = np.arange(-padding, height*(n+1), height)
        y_ticks_label = np.concatenate((['']*padding, data['nuis_label'], ['']*1))
        axis.set_yticks(y_ticks)
        axis.set_yticklabels(y_ticks_label)
        axis.set_ylim((-padding, n + height/2))
    
    def draw_labels(axis, extra_text:str=None, elumi_label:bool=True, ranking_label:bool=True, height=1.0,
                    energy:float=13, lumi:float=139, status:str='int', r_start:int=0, r_end:int=0, **styles):
        """
            extra_text: extra labels below the ATLAS label, use "//" as newline delimiter
        """
        
        dy            = styles['label']['dy'] 
        x_logo        = styles['logo']['x']
        fontsize_logo = styles['logo']['fontsize']
        
        text_options = {
            'fontsize'  : styles['label']['fontsize'],
        }
        
        extra_texts = []
        
        if extra_text:
            extra_texts.append(extra_texts)
            
        if ranking_label:
            rank_text = 'Rank {} to {}'.format(r_start, r_end)
            extra_texts.append(rank_text)
        
        
        draw_options = {
            'axis': axis,
            'loc': (x_logo, -height),
            'fontsize': fontsize_logo,
            'status': status,
            'extra_text': "//".join(extra_texts),
            'dy': dy,
            'transform_y': 'data',            
            'text_options': text_options,
        }
    
        if not elumi_label:
            draw_options['energy'] = None
            draw_options['lumi'] = None
        else:
            draw_options['energy'] = energy
            draw_options['lumi'] = lumi
          
        draw_atlas_label(**draw_options)
        
    @staticmethod
    def parse_style(style:str):
        if os.path.exists(style):
            return yaml.safe_load(open(style))
        if isinstance(style, str):
            if style.lower() == 'default':
                return DEFAULT_STYLE
            elif style.lower() == 'trex':
                return TREX_STYLE
            else:
                raise ValueError('unknown style: {}'.format(style))
        return DEFAULT_STYLE
    
    @staticmethod
    def _plot(data, show_sigma:bool=True, show_prefit:bool=True, show_postfit:bool=True, sigma_bands:bool=False,
              sigma_lines:bool=True, shade:bool=True, correlation:bool=True, onesided:bool=True, relative:bool=False,
              theta_max:float=2, padding:int=7, height:float=1, spacing:float=0, display_poi:str=r"$\mu$", 
              extra_text:str=None, elumi_label:bool=True, ranking_label:bool=True, energy:str=r"13 TeV", 
              lumi:str=r"139 fb$^{-1}$", status:str='int', r_start:int=1, style:Dict=DEFAULT_STYLE):
        # setup figure and axes
        plt.clf()
        fig_width, fig_height = style['figure']['width'], style['figure']['height']
        fig = plt.figure(figsize=(fig_width, fig_height))
        ax1 = fig.add_subplot(111)
        ax2 = ax1.twiny()
        NPRankingPlot.setup_axis(ax1, ax2, **style)
        ax1.set_xlim((-theta_max, theta_max))
        ax1.set_xlabel(r"$(\hat{\theta}-\theta_0)/\Delta\theta$" , **style['xaxis_label'])
        if relative:
            ax2.set_xlabel(r"$\Delta$ " + display_poi +"/" + display_poi, 
                           **style['xaxis_label'], labelpad=10)
        else:
            ax2.set_xlabel(r"$\Delta$ " + display_poi , **style['xaxis_label'], labelpad=10)
        if sigma_bands:
            shade, show_prefit, show_postfit = False, False, False
        n = len(data)
        NPRankingPlot.plot_impact(ax2, data, show_prefit=show_prefit, show_postfit=show_postfit,
                                  correlation=correlation, onesided=onesided, relative=relative,
                                  height=height, spacing=spacing, **style)
        centralize_axis(ax2, 'x')
        if shade:
            draw_hatches(ax2, n, height=height, **style['shade'])
        NPRankingPlot.plot_pulls(ax1, data, height=height, **style)
        if sigma_bands:
            draw_sigma_bands(ax1, n, height=height)
        if sigma_lines:
            draw_sigma_lines(ax1, n, height=height, **style['sigma_lines'])
        NPRankingPlot.draw_np_labels(ax2, data, padding=padding, height=height)
        format_axis_ticks(ax1, y_axis=False, x_axis_styles=style['xaxis'])
        format_axis_ticks(ax2, y_axis=False, x_axis_styles=style['xaxis'])
        ax2.xaxis.set_ticks_position('top')
        impact_xlim = ax2.get_xlim()
        #if (abs(impact_xlim[0]) + abs(impact_xlim[1])) < 0.05:
        #    ax2.xaxis.set_major_locator(plt.MaxNLocator(3))
        NPRankingPlot.draw_labels(ax1, extra_text=extra_text, height=height, elumi_label=elumi_label,
                                  ranking_label=ranking_label, energy=energy, lumi=lumi, status=status,
                                  r_start=r_start, r_end=r_start + n - 1, **style)
        x_legend = style['legend']['x']
        NPRankingPlot.draw_legend(ax1, display_poi, x=x_legend, y=-1.2*height, show_prefit=show_prefit,
                                  show_postfit=show_postfit, correlation=correlation, **style)
        return fig
    
    def plot(self, show_sigma:bool=True, show_prefit:bool=True, show_postfit:bool=True, sigma_bands:bool=False,
             sigma_lines:bool=True, shade:bool=True, correlation:bool=True, onesided:bool=True, relative:bool=False,
             theta_max:float=2, padding:int=7, height:float=1, spacing:float=0, display_poi:str=r"$\mu$", 
             extra_text:str=None, elumi_label:bool=True, ranking_label:bool=True, energy:str=r"13 TeV", 
             lumi:str=r"139 fb$^{-1}$",
             status:str='int', n_rank=None, rank_per_plot=20, combine_pdf=True, threshold=0, ranking=True, 
             fix_axis_scale=True, outdir="ranking_plots", outname:str='ranking', style:Union[str, Dict]=DEFAULT_STYLE):
        if isinstance(style, str):
            style = self.parse_style(style)
        if self.data is None:
            raise ValueError("no data to process")
        has_impact = any('impact' in i for i in self.data)
        if not has_impact:
            ranking, threshold, show_prefit, show_postfit = False, False, False, False           
        processed_data = self.get_processed_data(self.data, num=n_rank, threshold=threshold, ranking=ranking)
        num_data = len(processed_data)
        if not num_data:
            print("INFO: No data passing threshold. Skipped.")
        n_plot = ceildiv(num_data, rank_per_plot)
        dpi = style['figure']['dpi']
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        if combine_pdf:
            pdf_name = os.path.join(outdir, '{}_rank_{:04d}_to_{:04d}.pdf'.format(outname, 1, num_data))
            pp = PdfPages(pdf_name)
        nominal_xlim = None
        for i in range(n_plot):
            start, end = rank_per_plot*i, rank_per_plot*(i+1)
            data_slice = processed_data[::-1][start:end][::-1]
            fig = self._plot(data_slice, show_sigma=show_sigma, show_prefit=show_prefit, show_postfit=show_postfit, 
                             sigma_bands=sigma_bands, sigma_lines=sigma_lines, shade=shade, correlation=correlation,
                             onesided=onesided, relative=relative, theta_max=theta_max, padding=padding, height=height, 
                             spacing=spacing, display_poi=display_poi, extra_text=extra_text, elumi_label=elumi_label,
                             ranking_label=ranking_label, energy=energy, lumi=lumi, status=status, r_start=start+1, style=style)
            if fix_axis_scale:
                if nominal_xlim is None:
                    nominal_xlim = fig.get_axes()[1].get_xlim()
                else:
                    fig.get_axes()[1].set_xlim(nominal_xlim)
            base_name = os.path.join(outdir, '{}_rank_{:04d}_to_{:04d}'.format(outname, start+1, start+len(data_slice)))
            fig.savefig(base_name+'.eps', bbox_inches='tight')
            fig.savefig(base_name+'.png', dpi=dpi, bbox_inches='tight')
            print('INFO: Saved ranking plot as {}'.format(base_name+'.eps'))
            print('INFO: Saved ranking plot as {}'.format(base_name+'.png'))
            if combine_pdf:
                pp.savefig(fig, bbox_inches='tight')
            else:
                fig.savefig(base_name+'.pdf', dpi=dpi, bbox_inches='tight')
                print('INFO: Saved ranking plot as {}'.format(base_name+'.pdf'))
        if combine_pdf:
            print('INFO: Saved ranking plot as {}'.format(pdf_name))
            pp.close()

