from typing import Optional, Union, Dict, List, Tuple
import math

import numpy as np

import ROOT

from quickstats.plots import AbstractPlot
from quickstats.plots.template import single_frame, parse_styles
from quickstats.utils.roostats_utils import get_hypotest_data

class TestStatisticDistributionPlot(AbstractPlot):
    
    COLOR_PALLETE = {
        'null': 'b',
        'alt': 'r',
        'null_sec': 'tab:cyan',
        'alt_sec': 'tab:pink'
    }
        
    def __init__(self, result:ROOT.RooStats.HypoTestResult,
                 sec_result:Optional[ROOT.RooStats.HypoTestResult]=None,
                 teststat_str:str=r"\~{q}_{\mu}",
                 sec_teststat_str:str=r"\~{q}_{\mu}",
                 annotate_str:str=r"toys",
                 sec_annotate_str:str=r"toys",
                 color_pallete:Optional[Dict]=None,
                 styles:Optional[Union[Dict, str]]='teststat_dist',
                 analysis_label_options:Optional[Union[Dict, str]]='default'):
        super().__init__(color_pallete=color_pallete, styles=styles,
                         analysis_label_options=analysis_label_options)
        
        self.result = result
        self.data = get_hypotest_data(self.result)
        self.teststat_str = teststat_str
        self.annotate_str = annotate_str
        
        # secondary result (for comparison plot)
        self.sec_result = sec_result
        if self.sec_result is None:
            self.sec_data = None
        else:
            self.sec_data = get_hypotest_data(self.sec_result)
        self.sec_teststat_str = sec_teststat_str
        self.sec_annotate_str = sec_annotate_str
        
        self.asymptotic_mu = None
        self.asymptotic_sigma = None
        
    def draw_distribution(self, ax, data, weight, label:str,
                          color:Optional[str]=None,
                          nbins:int=75, xmax:float=40.):
        n, bins   = np.histogram(data, bins=nbins, range=(0, xmax), 
                                 density=False, weights=weight/weight.sum())
        bin_centers  = 0.5*(bins[1:] + bins[:-1])
        bin_width    = bin_centers[1] - bin_centers[0]
        h = ax.errorbar(bin_centers, n, color=color, xerr=0.5*bin_width, 
                        yerr = (n/weight.sum())**0.5, **self.styles['errorbar'], 
                        label=label, zorder=999)
        return h
    
    @staticmethod
    def get_qmutilde_cdf(qmutilde, mu:float, muprime:float, sigma:float, scale_factor:float=1.):
        mu2 = mu * mu
        sigma2 = sigma * sigma
        mu2oversigma2 = mu2 / sigma2
        if (muprime != mu):
            if (qmutilde < mu2oversigma2):
                value = 0.5 * (1. / np.sqrt(2. * np.pi)) * (1. / np.sqrt(qmutilde)) * \
                        np.exp(-0.5 * np.power(np.sqrt(qmutilde) - (mu - muprime) / sigma, 2))
            else:
                value = 0.5 * sigma * (1. / mu) * (1. / np.sqrt(2. * np.pi)) * \
                        np.exp(-0.5 * np.power((qmutilde - (mu2 - 2 * mu * muprime) / (sigma2)) / (2. * mu / sigma), 2))
        else:
            if (qmutilde < mu2oversigma2):
                value = 0.5 * (1. / np.sqrt(2. * np.pi)) * (1. / np.sqrt(qmutilde)) * \
                        np.exp(-0.5 * qmutilde)
            else:
                value = 0.5 * sigma * (1. / mu) * (1. / np.sqrt(2. * np.pi)) * \
                        np.exp(-0.5 * np.power((qmutilde + mu2oversigma2) / (2. * mu / sigma), 2))
        value *= scale_factor
        return value
    
    def set_asymptotic_params(self, mu:Optional[float]=None, sigma:Optional[float]=None):
        self.asymptotic_mu    = mu
        self.asymptotic_sigma = sigma
    
    def draw_asymptotic(self, ax, xmax:float, nbins:int):
        if (self.asymptotic_mu is None) or (self.asymptotic_sigma is None):
            raise RuntimeError(" mu and sigma values for asymptotic results are not initialized")
        bins = np.linspace(0, xmax, nbins+1)
        bin_centers  = 0.5*(bins[1:] + bins[:-1])
        bin_width    = bin_centers[1] - bin_centers[0]
        mu = self.asymptotic_mu
        sigma = self.asymptotic_sigma
        asym_curve_null = np.array([self.get_qmutilde_cdf(i, mu, mu, sigma, bin_width) for i in bin_centers])
        asym_curve_alt  = np.array([self.get_qmutilde_cdf(i, mu, 0, sigma, bin_width) for i in bin_centers])
        h_asym_null = ax.plot(bin_centers, asym_curve_null, 
                              color=self.color_pallete['null'],
                              label=fr"$f({self.teststat_str}|\mu)$ asymptotic")
        h_asym_alt  = ax.plot(bin_centers, asym_curve_alt, 
                              color=self.color_pallete['alt'],
                              label=fr"$f({self.teststat_str}|0)$ asymptotic")
        return h_asym_null, h_asym_alt

    def draw_annotation(self, ax, data, xmin:float=0.35, ymax:float=0.9):
        null_converged = data['null']['size']
        alt_converged = data['alt']['size']        
        obs_pmu = data['observed']['CLsplusb']
        obs_pmu_err = data['observed']['CLsplusbError']
        obs_pb = 1 - data['observed']['CLb']
        obs_pb_err = data['observed']['CLbError']
        obs_CLs = data['observed']['CLs']
        obs_CLs_err = data['observed']['CLsError']
        exp_pmu = data['expected']['CLsplusb']
        exp_pmu_err = data['expected']['CLsplusbError']
        exp_pb = 1 - data['expected']['CLb']
        exp_pb_err = data['expected']['CLbError']
        exp_CLs = data['expected']['CLs']
        exp_CLs_err = data['expected']['CLsError']
        ax.annotate('\n'.join([fr'     # converged null : {null_converged}',
                    fr'     # converged alt   : {alt_converged}',
                    fr'$p_{{\mu}}^{{obs}}$(toys)    = {obs_pmu:.4f} $\pm$ {obs_pmu_err:.4f}',
                    fr'$p_{{b}}^{{obs}}$(toys)    = {obs_pb:.4f} $\pm$ {obs_pb_err:.4f}',
                    fr'$CL_s^{{obs}}$(toys)  = {obs_CLs:.4f} $\pm$ {obs_CLs_err:.4f}',
                    fr'$p_{{\mu}}^{{exp}}$(toys)    = {exp_pmu:.4f} $\pm$ {exp_pmu_err:.4f}',
                    fr'$p_{{b}}^{{exp}}$(toys)    = {exp_pb:.4f} $\pm$ {exp_pb_err:.4f}',
                    fr'$CL_s^{{exp}}$(toys)  = {exp_CLs:.4f} $\pm$ {exp_CLs_err:.4f}']),
                    (xmin, ymax), xycoords='axes fraction', 
                    horizontalalignment='left', verticalalignment='top',
                    bbox={'facecolor': 'white', 'edgecolor': 'white', 'pad': 5, 'alpha':0.8},
                    **self.styles['annotation'])
        

    def draw_quantiles(self, ax, data, teststat_str:str=r"\~{q}_{\mu}", 
                       linestyle:str='-', ymax:float=0.7):
        qmu_obs = data['observed']['teststat']
        qmu_exp = data['expected']['teststat'][0]
        qmu_exp_n2s = data['expected']['teststat'][-2]
        qmu_exp_n1s = data['expected']['teststat'][-1]
        qmu_exp_p1s = data['expected']['teststat'][1]
        qmu_exp_p2s = data['expected']['teststat'][2]
        h_obs = ax.axvline(qmu_obs, 0, ymax, color='k', linestyle=linestyle,
                           label=fr"${teststat_str}^{{obs}}$")
        h_n2s = ax.axvline(qmu_exp_n2s, 0, ymax, color='#ffcc00', linestyle=linestyle,
                           label=fr"${teststat_str}^{{exp}}(-2\sigma)$", clip_on=False)
        h_n1s = ax.axvline(qmu_exp_n1s, 0, ymax, color='#33ad33', linestyle=linestyle,
                           label=fr"${teststat_str}^{{exp}}(-1\sigma)$")
        h_exp = ax.axvline(qmu_exp, 0, ymax, color='#52ffff', linestyle=linestyle,
                           label=fr"${teststat_str}^{{exp}}$")
        h_p1s = ax.axvline(qmu_exp_p1s, 0, ymax, color='#33ad33', linestyle=linestyle,
                           label=fr"${teststat_str}^{{exp}}(+1\sigma)$")
        h_p2s = ax.axvline(qmu_exp_p2s, 0, ymax, color='#ffcc00', linestyle=linestyle,
                           label=fr"${teststat_str}^{{exp}}(+2\sigma)$")
        # return the plot handles
        return [h_obs, h_n2s, h_n1s, h_exp, h_p1s, h_p2s]
    
    def draw_legends(self, ax, primary_handles, secondary_handles=None, asymptotic_handles=None,
                     leg_loc:Tuple=(1.02, 0.75), sec_leg_loc:Tuple=(1.02, 0.5)):
        handles, labels = ax.get_legend_handles_labels()
        if asymptotic_handles is not None:
            primary_handles += asymptotic_handles
        primary_labels = [labels[handles.index(h)] for h in primary_handles]
        primary_leg = ax.legend(primary_handles, primary_labels, 
                                loc=leg_loc, ncol=2, **self.styles['legend'])
        ax.add_artist(primary_leg)
        
        if secondary_handles is not None:
            secondary_labels = [labels[handles.index(h)] for h in secondary_handles]
            primary_leg = ax.legend(secondary_handles, secondary_labels, 
                                    loc=leg_loc, ncol=2, **self.styles['legend'])
            ax.add_artist(primary_leg)
        
        
    def draw(self, xlabel:str=r"$\~{q}_{\mu}$",
             nbins:int=75, xmax:Optional[float]=None, ymax:float=1e3,
             leg_loc:Tuple=(1.02, 0.7), sec_leg_loc:Tuple=(1.02, 0.45)):
        if self.sec_data is not None:
            annotation_ymax = 0.9
        else:
            annotation_ymax = 0.95
        data_max = max([np.max(self.data['null']['data']), np.max(self.data['alt']['data'])])
        if self.sec_data is not None:
            data_max_sec = max(np.max(self.sec_data['null']['data']), np.max(self.sec_data['alt']['data']))
            data_max = max([data_max, data_max_sec])
        if xmax is None:
            xmax = math.ceil(data_max * 1.1)
        binwidth = xmax / nbins
        ax = self.draw_frame(logy=True)
        ax.set_xlabel(xlabel, **self.styles['xlabel'])
        ax.set_ylabel("Normalized Entries / {:.3f}".format(binwidth), **self.styles['ylabel'])
        
        # draw test statistic distribution for null hypothesis
        h_null = self.draw_distribution(ax, 
                                       self.data['null']['data'],
                                       self.data['null']['weight'],
                                       label=fr"$f({self.teststat_str}|\mu)$ {self.annotate_str}",
                                       color=self.color_pallete['null'],
                                       nbins=nbins, xmax=xmax)
        # draw test statistic distribution for alternative hypothesis
        h_alt = self.draw_distribution(ax, 
                               self.data['alt']['data'],
                               self.data['alt']['weight'],
                               label=fr"$f({self.teststat_str}|0)$ {self.annotate_str}",
                               color=self.color_pallete['alt'],
                               nbins=nbins, xmax=xmax)
        h_quantiles = self.draw_quantiles(ax, self.data, teststat_str=self.teststat_str)
        self.draw_annotation(ax, self.data, xmin=0.4, ymax=annotation_ymax)
        primary_handles = h_quantiles + [h_null, h_alt]
        
        if self.sec_data is not None:
            h_null_sec = self.draw_distribution(ax, 
                                           self.sec_data['null']['data'],
                                           self.sec_data['null']['weight'],
                                           label=fr"$f({self.sec_teststat_str}|\mu)$ {self.sec_annotate_str}",
                                           color=self.color_pallete['null_sec'],
                                           nbins=nbins, xmax=xmax)
            h_alt_sec = self.draw_distribution(ax, 
                                   self.sec_data['alt']['data'],
                                   self.sec_data['alt']['weight'],
                                   label=fr"$f({self.sec_teststat_str}|0)$ {self.sec_annotate_str}",
                                   color=self.color_pallete['alt_sec'],
                                   nbins=nbins, xmax=xmax)
            h_quantiles_sec = self.draw_quantiles(ax, self.sec_data, 
                                                  teststat_str=self.sec_teststat_str,
                                                  linestyle='--')
            self.draw_annotation(ax, self.sec_data, xmin=0.7, ymax=annotation_ymax)
            secondary_handles = h_quantiles_sec + [h_null_sec, h_alt_sec]
            
            ax.annotate(f'${self.teststat_str}$ {self.annotate_str}',
                        (0.45, 0.95), xycoords='axes fraction', verticalalignment='top', 
                        horizontalalignment='left', **self.styles['annotation'])
            ax.annotate(f'${self.sec_teststat_str}$ {self.sec_annotate_str}',
                        (0.75, 0.95), xycoords = 'axes fraction', verticalalignment='top', 
                        horizontalalignment='left', **self.styles['annotation'])
        else:
            secondary_handles = None

        ymin = ax.get_ylim()[0]
        
        # draw test statistic distribution from asymptotic approximation
        if (self.asymptotic_mu is not None) and (self.asymptotic_sigma is not None):
            h_asym_null, h_asym_alt = self.draw_asymptotic(ax, xmax, nbins)
            asymptotic_handles = [h_asym_null[0], h_asym_alt[0]]
        else:
            asymptotic_handles = None
            
        ax.set_xlim([0, xmax])
        ax.set_ylim([ymin, ymax])
        
        self.draw_legends(ax, primary_handles, secondary_handles, asymptotic_handles,
                          leg_loc=leg_loc, sec_leg_loc=sec_leg_loc)
        
        return ax