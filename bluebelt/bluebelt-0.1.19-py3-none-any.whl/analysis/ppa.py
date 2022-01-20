# process performance analysis
import copy

import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

import plotly.graph_objects as go

import bluebelt.statistics.std

import bluebelt.analysis.ci as ci
import bluebelt.statistics.hypothesis_testing as hypothesis_testing

import bluebelt.styles.defaults as defaults

import bluebelt.core.helpers
import bluebelt.core.decorators
import bluebelt.styles

# process performance analysis
@bluebelt.core.decorators.class_methods
class Summary():
        
    def __init__(self, series, whis=1.5, **kwargs):

        # check arguments
        if not isinstance(series, pd.Series):
            raise ValueError('series is not a Pandas Series')
        
        self.series = series.dropna()
        self.whis = whis
        self.calculate(whis)
        
    def __str__(self):
        str_mean="mean:"
        str_ci_mean="CI mean:"
        str_std="standard deviation:"
        str_min="minimum"
        str_q1="1st quantile:"
        str_median="median:"
        str_q3="3rd quantile:"
        str_max="maximum"
        str_ci_median="CI median:"
        str_ad_test="Anderson-Darling test"
        
        fill = 32
        return (f'{str_mean:{fill}}{self.mean:1.2f}\n' +
                f'{str_ci_mean:{fill}}{self.ci_mean[0]:1.2f}-{self.ci_mean[1]:1.2f}\n' +
                f'{str_std:{fill}}{self.std:1.2f}\n' +
                f'{str_min:{fill}}{self.min:1.2f}\n' +
                f'{str_q1:{fill}}{self.q1:1.2f}\n' +
                f'{str_median:{fill}}{self.median}\n' +
                f'{str_q3:{fill}}{self.q3:1.2f}\n' +
                f'{str_max:{fill}}{self.max:1.2f}\n' +
                f'{str_ci_median:{fill}}{self.ci_median[0]:1.2f}-{self.ci_median[1]:1.2f}\n' +
                f'{str_ad_test:{fill}}A={self.ad_test.statistic:1.2f}, p-value={self.ad_test.p_value:1.2f}')
                

    def __repr__(self):
        return (f'{self.__class__.__name__}(mean={self.mean:1.1f}, std={self.std:1.1f}, min={self.min:1.1f}, q1={self.q1:1.1f}, median={self.median:1.1f}, q3={self.q3:1.1f}, max={self.max:1.1f})')
    
    def calculate(self, whis=1.5):
        
        self.mean = self.series.mean()
        self.ci_mean = ci.ci_mean(self.series)
        self.std = self.series.std()
        self.min = self.series.min()
        self.q1 = self.series.quantile(q=0.25)
        self.median = self.series.median()
        self.q3 = self.series.quantile(q=0.75)
        self.max = self.series.max()
        self.ci_median = ci.ci_median(self.series)
        self.ad_test = hypothesis_testing.AndersonDarling(self.series)
        self.boxplot_quantiles = bluebelt.core.helpers._get_boxplot_quantiles(whis=whis)# self.get_boxplot_quantiles(whis=whis)
        self.boxplot_outliers = bluebelt.core.helpers._get_boxplot_outliers(whis=whis) #self.get_boxplot_outliers(whis=whis)
        
        
    def get_boxplot_quantiles(self, whis=1.5):
        # get the matplotlib boxplot quantiles
        # sort of direct copy from the matplotlib library

        q1, median, q3 = np.percentile(self.series, [25, 50, 75])

        if np.isscalar(whis):
            iqr = q3 - q1
            loval = q1 - (whis * iqr)
            hival = q3 + (whis * iqr)
        else:
            loval, hival = np.percentile(self.series, sorted(whis))

        # get high extreme
        wiskhi = self.series[self.series <= hival]
        if len(wiskhi) == 0 or np.max(wiskhi) < q3:
            high = q3
        else:
            high = np.max(wiskhi)

        # get low extreme
        wisklo = self.series[self.series >= loval]
        if len(wisklo) == 0 or np.min(wisklo) > q1:
            low = q1
        else:
            low = np.min(wisklo)
        
        return (low, q1, q3, high)

    def get_boxplot_outliers(self, whis=1.5):
        low, q1, q3, high = self.get_boxplot_quantiles(whis=whis)

        return self.series[self.series < low].append(self.series[self.series > high]).values
    
    def plot(self, **kwargs):

        style = kwargs.get('style', bluebelt.styles.paper)
        kwargs.pop('style', None)
        path = kwargs.pop('path', None)

        # prepare figure
        fig = plt.figure(constrained_layout=False, **kwargs)
        gridspec = fig.add_gridspec(nrows=4, ncols=1, height_ratios=[8,3,3,3], wspace=0, hspace=0)
        ax1 = fig.add_subplot(gridspec[0, 0], zorder=50)
        ax2 = fig.add_subplot(gridspec[1, 0], zorder=40)
        ax3 = fig.add_subplot(gridspec[2, 0], zorder=30)
        ax4 = fig.add_subplot(gridspec[3, 0], zorder=20)

        # 1. histogram ############################################
        ax1.hist(self.series, **style.summary.histogram)

        # get current limits
        xlims = ax1.get_xlim()
        ylims = ax1.get_ylim()

        # fit a normal distribution to the data
        norm_mu, norm_std = stats.norm.fit(self.series)
        pdf_x = np.linspace(xlims[0], xlims[1], 100)
        ax1.plot(pdf_x, stats.norm.pdf(pdf_x, norm_mu, norm_std), **style.summary.normal_plot)

        # plot standard deviation
        if (self.mean-self.std) > self.min:
            std_area = np.linspace(self.mean-self.std, self.mean, 100)
            std_line_x = self.mean-self.std
            std_text_x = self.mean-self.std*0.5
        else:
            std_area = np.linspace(self.mean, self.mean+self.std, 100)
            std_line_x = self.mean+self.std
            std_text_x = self.mean+self.std*0.5

        ax1.fill_between(std_area, stats.norm.pdf(std_area, norm_mu, norm_std), 0, **style.summary.std_fill_between)
        
        ax1.axvline(x=self.mean, ymin=0, ymax=1, **style.summary.std_axvline)
        ax1.axvline(x=std_line_x, ymin=0, ymax=1, **style.summary.std_axvline)
        
        ax1.plot((std_line_x, self.mean), (ylims[1]*0.9, ylims[1]*0.9), **style.summary.std_axhline)
        ax1.text(std_text_x, ylims[1]*0.9, r'$\sigma = $'+f'{self.std:1.2f}', **style.summary.std_text)
        
        # plot AD test results
        if self.mean > (self.max + self.min) / 2:
            ad_x = 0.02
            ad_align = 'left'
        else:
            ad_x =  0.98
            ad_align = 'right'

        ad_text = r'$P_{AD, normal}: $'+f'{self.ad_test.p_value:1.4f}'
        
        ax1.text(ad_x, 0.9, ad_text, transform=ax1.transAxes, va='center', ha=ad_align)

        # reset limits
        ax1.set_xlim(xlims)
        ax1.set_ylim(ylims)

        # 2. box plot ############################################
        boxplot = ax2.boxplot(self.series, vert=False, widths=0.3, whis=self.whis)
        
        for box in boxplot['boxes']:
            # add style if any is given
            box.set(**style.summary.boxplot.get('boxes', {}))

        ax2.set_xlim(xlims)
        ax2.set_ylim(0.7,1.7)
        
        ax2_xticks = bluebelt.core.helpers._get_boxplot_quantiles(self.series, whis=1.5)
        ax2.set_xticks(ax2_xticks)
        ax2.xaxis.set_major_formatter(FormatStrFormatter(f'%{bluebelt.core.helpers._format_digits(ax2_xticks, digits=3)}'))
        

        

        #for tick in ax2.get_xticklabels():
        #    tick.set_horizontalalignment('left')

        #######################################################
        # CI for the median
        #######################################################

        ax3.plot([self.ci_median[0], self.ci_median[1]], [1,1], **style.summary.ci_mean_plot)
        ax3.axvline(x=self.ci_median[0], ymin=0.15, ymax=0.45, **style.summary.ci_mean_axvline)
        ax3.axvline(x=self.ci_median[1], ymin=0.15, ymax=0.45, **style.summary.ci_mean_axvline)
        ax3.scatter([self.median],[1], **style.summary.ci_mean_scatter)
        ax3.set_xlim(xlims)
        ax3_xticks = [self.ci_median[0], self.ci_median[1]]
        
        
        ax3.set_ylim(0.7,1.7)
        
        ci_median_x = 0.02 if self.median>(self.max+self.min)/2 else 0.98
        ci_median_align = 'left' if self.median>(self.max+self.min)/2 else 'right'
        
        ax3.text(ci_median_x, 0.1, r'$CI_{median}$', transform=ax3.transAxes, va='bottom', ha=ci_median_align)

        ax3.set_xticks(ax3_xticks)
        ax3.xaxis.set_major_formatter(FormatStrFormatter(f'%{bluebelt.core.helpers._format_digits(ax3_xticks, digits=3)}'))


        #######################################################
        # CI for the mean
        #######################################################

        ax4.plot([self.ci_mean[0], self.ci_mean[1]], [1,1], **style.summary.ci_median_plot)
        ax4.axvline(x=self.ci_mean[0], ymin=0.15, ymax=0.45, **style.summary.ci_median_axvline)
        ax4.axvline(x=self.ci_mean[1], ymin=0.15, ymax=0.45, **style.summary.ci_median_axvline)
        ax4.scatter([self.mean],[1], **style.summary.ci_median_scatter)
        ax4.set_xlim(xlims)
        ax4_xticks = [self.ci_mean[0], self.ci_mean[1]]
        ax4.set_ylim(0.7,1.7)

        ci_mean_x = 0.02 if self.mean>(self.max+self.min)/2 else 0.98
        ci_mean_align = 'left' if self.mean>(self.max+self.min)/2 else 'right'
        
        ax4.text(ci_mean_x, 0.1, r'$CI_{mean}$', transform=ax4.transAxes, va='bottom', ha=ci_mean_align)

        # drop lines
        ax2.axvline(self.mean, ymin=0, ymax=2, **style.summary.drop_axvline)
        ax3.axvline(self.mean, ymin=0, ymax=1.7, **style.summary.drop_axvline)
        ax4.axvline(self.mean, ymin=0.3, ymax=1.7, **style.summary.drop_axvline)
        
        ax2.axvline(self.median, ymin=0, ymax=0.3, **style.summary.drop_axvline)
        ax3.axvline(self.median, ymin=0.3, ymax=1.7, **style.summary.drop_axvline)
        


        ax4.set_xticks(ax4_xticks)
        ax4.xaxis.set_major_formatter(FormatStrFormatter(f'%{bluebelt.core.helpers._format_digits(ax4_xticks, digits=3)}'))

        ax1.set_title(f'graphical summary for {self.series.name}', **style.summary.title)

        ax1.set_yticks([])
        ax2.set_yticks([])
        ax3.set_yticks([])
        ax4.set_yticks([])

        if path:
            plt.savefig(path)
            plt.close()
        else:
            plt.close()
            return fig

@bluebelt.core.decorators.class_methods
class ControlChart():
    
    def __init__(self, series, **kwargs):

        # check arguments
        if not isinstance(series, pd.Series):
            raise ValueError('series is not a Pandas Series')
                
        self.series = series
        self.calculate()
        
    def __str__(self):
        str_mean="mean:"
        str_std="standard deviation:"
        str_ucl="upper control limit:"
        str_lcl=f"lower control limit:"
        str_outlier_count=f"outliers:"

        fill = 32
        return (f'{str_mean:{fill}}{self.mean:1.2f}\n' +
                f'{str_std:{fill}}{self.std:1.2f}\n' +
                f'{str_ucl:{fill}}{self.ucl:1.2f}\n' +
                f'{str_lcl:{fill}}{self.lcl:1.2f}\n' +
                f'{str_outlier_count:{fill}}{self.outlier_count}\n') 

    def __repr__(self):
        return (f'{self.__class__.__name__}(mean={self.mean:1.1f}, std={self.std:1.1f}, UCL={self.ucl:1.1f}, LCL={self.lcl:1.1f}, outlier_count={self.outlier_count:1.0f})')
    
    def calculate(self):
        mean = self.series.mean()
        std = self.series.std()
        ucl = mean + std * 3
        lcl = mean - std * 3
        outliers = self.series[(self.series > ucl) | (self.series < lcl)]
        
        self.mean = mean
        self.std = std
        self.ucl = ucl
        self.lcl = lcl
        self.outliers = outliers
        self.outlier_count = outliers.shape[0]
        
    def plot(self, **kwargs):
        
        style = kwargs.get('style', bluebelt.styles.paper)
        kwargs.pop('style', None)

        path = kwargs.pop('path', None)
        
        fig, ax = plt.subplots(**kwargs)

        # observations
        ax.plot(self.series, **style.control_chart.plot)

        # observations white trail
        ax.plot(self.series, **style.control_chart.plot_background)

        # control limits
        ax.axhline(self.ucl, **style.control_chart.ucl_axhline)
        ax.axhline(self.lcl, **style.control_chart.lcl_axhline)

        ylim = ax.get_ylim() # get limits to set them back later
        xlim = ax.get_xlim()
        
        ax.fill_between(xlim, self.ucl, ylim[1], **style.control_chart.ucl_fill_between)
        ax.fill_between(xlim, self.lcl, ylim[0], **style.control_chart.lcl_fill_between)

        # outliers
        ax.plot(self.outliers, **style.control_chart.outlier_background)
        ax.plot(self.outliers, **style.control_chart.outlier)
        
        # mean
        ax.axhline(self.mean, **style.control_chart.mean_axhline)

        # text boxes for mean, UCL and LCL
        ax.text(xlim[1], self.mean, f' mean = {self.mean:1.2f}', **style.control_chart.mean_text)
        ax.text(xlim[1], self.ucl, f' UCL = {self.ucl:1.2f}', **style.control_chart.ucl_text)
        ax.text(xlim[1], self.lcl, f' LCL = {self.lcl:1.2f}', **style.control_chart.lcl_text)

        # reset limits
        ax.set_ylim(ylim)
        ax.set_xlim(xlim)

        # labels
        ax.set_title(f'control chart of {self.series.name}', **style.control_chart.title)
        #ax.set_xlabel(self.series.index.name)
        ax.set_ylabel('value')

        # set x axis locator
        bluebelt.core.helpers._axisformat(ax, self.series)
        
        plt.gcf().subplots_adjust(right=0.8)

        if path:
            plt.savefig(path)
            plt.close()
        else:
            plt.close()
            return fig
    
    def plotly(self, **kwargs):
        
        layout = go.Layout(
            title=f'control chart of {self.series.name}',    
            plot_bgcolor=f'rgba{defaults.white+(1,)}',
            hovermode="closest",
            xaxis=dict(
                title=self.series.index.name,
                linecolor=f'rgba{defaults.black+(1,)}',
                zeroline=False,
                ticks="outside",
                tickwidth=1,
                tickcolor=f'rgba{defaults.black+(1,)}',
                ticklen=5,
                showgrid=True,
                gridwidth=0.5,
                gridcolor=f'rgba{defaults.light_grey+(1,)}',
                mirror=True,
            ),
            yaxis=dict(
                title="value",
                linecolor=f'rgba{defaults.black+(1,)}',
                zeroline=False,
                ticks="outside",
                tickwidth=1,
                tickcolor=f'rgba{defaults.black+(1,)}',
                ticklen=5,
                showgrid=True,
                gridwidth=0.5,
                gridcolor=f'rgba{defaults.light_grey+(1,)}',
                mirror=True,
            ),
        )
        
        data = [go.Scatter(
                        x=self.outliers.index,
                        y=self.outliers.values,
                        marker=dict(
                            color=f'rgba{defaults.white+(1,)}',
                            line=dict(width=1, color=f'rgba{defaults.black+(1,)}'),
                            size=17,
                        ),
                        mode='markers',
                        showlegend=False,
                        name='outliers'
                    ),
                go.Scatter(
                        x=self.series.index,
                        y=self.series.values,
                        line=dict(
                                width=1,
                                color=f'rgba{defaults.blue+(1,)}',
                            ),
                        marker=dict(
                            color=f'rgba{defaults.black+(1,)}',
                            size=9,
                        ),
                        mode='lines+markers',
                        showlegend=False,
                        name=self.series.name,
                    ),
               ]
    
        fig = go.Figure(data=data, layout=layout)
    
    
        # add mean, UCL and LCL line
        fig.add_shape(
                type="line",
                xref="paper",
                yref="y",
                x0=0,
                y0=self.mean,
                x1=1,
                y1=self.mean,
                line=dict(
                    color=f'rgba{defaults.black+(1,)}',
                    width=1,
                    dash='dash'
                ),
            )
        fig.add_annotation(
            dict(
                xref="paper",
                yref="y",
                x=1,
                y=self.mean,
                text=f'mean = {self.mean:1.2f}',
                showarrow=False,
                align='right',
                bgcolor=f'rgba{defaults.white+(0.5,)}',
            )
        )
        fig.add_shape(
                type="line",
                xref="paper",
                yref="y",
                x0=0,
                y0=self.ucl,
                x1=1,
                y1=self.ucl,
                line=dict(
                    color=f'rgba{defaults.black+(1,)}',
                    width=0.5,
                    dash='dash'
                ),
            )
        fig.add_annotation(
            dict(
                xref="paper",
                yref="y",
                x=1,
                y=self.ucl,
                text=f'UCL = {self.ucl:1.2f}',
                showarrow=False,
                align='right',
                bgcolor=f'rgba{defaults.white+(0.5,)}',
            )
        )
        fig.add_shape(
                type="line",
                xref="paper",
                yref="y",
                x0=0,
                y0=self.lcl,
                x1=1,
                y1=self.lcl,
                line=dict(
                    color=f'rgba{defaults.black+(1,)}',
                    width=0.5,
                    dash='dash'
                ),
            )
        fig.add_annotation(
            dict(
                xref="paper",
                yref="y",
                x=1,
                y=self.lcl,
                text=f'LCL = {self.lcl:1.2f}',
                showarrow=False,
                align='right',
                bgcolor=f'rgba{defaults.white+(0.5,)}',
            )
        )
        # x-ticks to nice datetime format
        if isinstance(self.series.index, pd.DatetimeIndex):
            fig.update_layout(xaxis_tickformat = '%d-%m-%Y')
        
        # set width en height if any

        if 'width' in kwargs and 'height' in kwargs:
            fig.update_layout(width=kwargs.get('width'), height=kwargs.get('height'))

        return fig

@bluebelt.core.decorators.class_methods
class RunChart():
    def __init__(self, series, alpha=0.05):
        
        # check arguments
        if not isinstance(series, pd.Series):
            raise ValueError('series is not a Pandas Series')
        
        self.series = series
        self.alpha = alpha
        
        self.calculate()
        
    def __str__(self):
        
        str_runs_about="runs about the median:"
        str_expected_runs_about="expected runs about the median:"
        str_longest_run_about="longest run about the median:"
        str_clustering=f"clustering (p ≈ {self.p_value_clustering:1.2f}):"
        str_mixtures=f"mixtures (p ≈ {self.p_value_mixtures:1.2f}):"
        
        str_runs_up_or_down="runs up or down:"
        str_expected_runs_up_or_down="expected runs up or down:"
        str_longest_run_up_or_down="longest run up or down:"
        str_trends=f"trends (p ≈ {self.p_value_trends:1.2f}):"
        str_oscillation=f"oscillation (p ≈ {self.p_value_oscillation:1.2f}):"

        fill = 32
        return (f'{str_runs_about:{fill}}{self.runs_about:1.0f}\n' +
                f'{str_expected_runs_about:{fill}}{self.expected_runs_about:1.0f}\n' +
                f'{str_longest_run_about:{fill}}{self.longest_run_about:1.0f}\n' +
                f'{str_clustering:{fill}}{self.clustering}\n' +
                f'{str_mixtures:{fill}}{self.mixtures}\n' +
                f'\n' +
                f'{str_runs_up_or_down:{fill}}{self.runs_up_or_down:1.0f}\n' +
                f'{str_expected_runs_up_or_down:{fill}}{self.expected_runs_up_or_down:1.0f}\n' +
                f'{str_longest_run_up_or_down:{fill}}{self.longest_run_up_or_down:1.0f}\n' +
                f'{str_trends:{fill}}{self.trends}\n' +
                f'{str_oscillation:{fill}}{self.oscillation}')


    def __repr__(self):
        return (f'{self.__class__.__name__}(runs_about={self.runs_about:1.0f}, expected_runs_about={self.expected_runs_about:1.0f}, longest_run_about={self.longest_run_about:1.0f}, runs_up_or_down={self.runs_up_or_down:1.0f}, expected_runs_up_or_down={self.expected_runs_up_or_down:1.0f}, longest_run_up_or_down={self.longest_run_up_or_down:1.0f}, p_value_clustering={self.p_value_clustering:1.2f}, p_value_mixtures={self.p_value_mixtures:1.2f}, p_value_trends={self.p_value_trends:1.2f}, p_value_oscillation={self.p_value_oscillation:1.2f}, clustering={self.clustering}, mixtures={self.mixtures}, trends={self.trends}, oscillation={self.oscillation})')

    def metrics(self):
        str_runs_about="runs about the median:"
        str_expected_runs_about="expected runs about the median:"
        str_longest_run_about="longest run about the median:"
        str_clustering=f"clustering (p ≈ {self.p_value_clustering:1.2f}):"
        str_mixtures=f"mixtures (p ≈ {self.p_value_mixtures:1.2f}):"
        
        str_runs_up_or_down="runs up or down:"
        str_expected_runs_up_or_down="expected runs up or down:"
        str_longest_run_up_or_down="longest run up or down:"
        str_trends=f"trends (p ≈ {self.p_value_trends:1.2f}):"
        str_oscillation=f"oscillation (p ≈ {self.p_value_oscillation:1.2f}):"

        fill = 32
        print( (f'{str_runs_about:{fill}}{self.runs_about:1.0f}\n' +
                f'{str_expected_runs_about:{fill}}{self.expected_runs_about:1.0f}\n' +
                f'{str_longest_run_about:{fill}}{self.longest_run_about:1.0f}\n' +
                f'{str_clustering:{fill}}{self.clustering}\n' +
                f'{str_mixtures:{fill}}{self.mixtures}\n' +
                f'\n' +
                f'{str_runs_up_or_down:{fill}}{self.runs_up_or_down:1.0f}\n' +
                f'{str_expected_runs_up_or_down:{fill}}{self.expected_runs_up_or_down:1.0f}\n' +
                f'{str_longest_run_up_or_down:{fill}}{self.longest_run_up_or_down:1.0f}\n' +
                f'{str_trends:{fill}}{self.trends}\n' +
                f'{str_oscillation:{fill}}{self.oscillation}'))
    
    def calculate(self):
        '''
        The number of runs about the median is the total number of runs above the median and 
        the total number of runs below the median.
        A run about the median is one or more consecutive points on the same side of the center line.
        A run ends when the line that connects the points crosses the center line.
        A new run begins with the next plotted point. 
        A data point equal to the median belongs to the run below the median.

        The number of runs up or down is the total count of upward and downward runs in the series.
        A run up or down ends when the direction changes.


        Clustering, mixtures, trends and oscillation
        A p-value that is less than the specified level of significance indicates clustering, mixtures, trends and/or oscillation
        '''

        median = self.series.median()

        longest_runs_about = [] #pd.Series(dtype=object)[
        longest_runs_up_or_down = [] #pd.Series(dtype=object)

        # runs

        for index, value in self.series.iteritems():

            # runs about the median
            if index == self.series.index[0]: # set above and start the first run
                above = True if value > median else False
                longest_run_about = 1
                run_about_length = 1
                runs_about = 0
            elif (value > median and not above) or (value <= median and above): # new run about
                runs_about += 1 # add an extra run
                above = not above # toggle the above value
                if run_about_length > longest_run_about:
                    longest_run_about = run_about_length
                    longest_runs_about = [self.series.loc[:index].iloc[-(longest_run_about+1):-1]]
                elif run_about_length == longest_run_about:
                    longest_runs_about += [self.series.loc[:index].iloc[-(longest_run_about+1):-1]]
                #longest_run_about = max(longest_run_about, run_about_length)
                run_about_length = 1
            elif index == self.series.index[-1]: # the last value might bring a longest run
                run_about_length += 1
                if run_about_length > longest_run_about:
                    longest_run_about = run_about_length
                    longest_runs_about = [self.series.loc[:index].iloc[-(longest_run_about):]]
                elif run_about_length == longest_run_about:
                    longest_runs_about += [self.series.loc[:index].iloc[-(longest_run_about):]]
            else:
                run_about_length += 1

            # runs up or down
            if index == self.series.index[0]: # set the first value
                previous_value = value
            elif index == self.series.index[1]: # set up and start first run
                up = True if value > previous_value else False
                longest_run_up_or_down = 1
                run_up_or_down_length = 1
                runs_up_or_down = 1
                previous_value = value

            elif (value > previous_value and not up) or (value <= previous_value and up): # new run up or down
                runs_up_or_down += 1 # add an extra run
                up = not up # toggle up
                if run_up_or_down_length > longest_run_up_or_down:
                    longest_run_up_or_down = run_up_or_down_length
                    longest_runs_up_or_down = [self.series.loc[:index].iloc[-(longest_run_up_or_down+1):-1]]
                elif run_up_or_down_length == longest_run_up_or_down:
                    longest_runs_up_or_down += [self.series.loc[:index].iloc[-(longest_run_up_or_down+1):-1]]   
                run_up_or_down_length = 1
                previous_value = value

            elif index == self.series.index[-1]: # the last value might bring a longest run
                run_up_or_down_length += 1
                if run_up_or_down_length > longest_run_up_or_down:
                    longest_run_up_or_down = run_up_or_down_length
                    longest_runs_up_or_down = [self.series.loc[:index].iloc[-(longest_run_up_or_down):]]
                    
                elif run_up_or_down_length == longest_run_up_or_down:
                    longest_runs_up_or_down += [self.series.loc[:index].iloc[-(longest_run_up_or_down):]]

            else:
                run_up_or_down_length += 1
                previous_value = value



        # expected runs
        m = self.series[self.series > self.series.median()].count()
        n = self.series[self.series <= self.series.median()].count()
        N = self.series.count()

        expected_runs_about = 1 + (2 * m * n) / N

        expected_runs_up_or_down = (2 * (m + n) - 1) / 3

        # clustering and mixtures
        p_value_clustering = stats.norm.cdf((runs_about - 1 - ((2 * m * n) / N)) / (((2 * m * n * (2 * m * n - N)) / (N**2 * (N - 1)))**0.5))
        p_value_mixtures = 1 - p_value_clustering

        clustering = True if p_value_clustering < self.alpha else False
        mixtures = True if p_value_mixtures < self.alpha else False

        # trends and oscillation
        p_value_trends = stats.norm.cdf((runs_up_or_down - (2 * N - 1) / 3) / ((16 * N - 29) / 90)**0.5)
        p_value_oscillation = 1 - p_value_trends

        trends = True if p_value_trends < self.alpha else False
        oscillation = True if p_value_oscillation < self.alpha else False
        
        self.runs_about = runs_about
        self.expected_runs_about = expected_runs_about
        self.longest_run_about = longest_run_about
        self.runs_up_or_down = runs_up_or_down
        self.expected_runs_up_or_down = expected_runs_up_or_down
        self.longest_run_up_or_down = longest_run_up_or_down
        self.p_value_clustering = p_value_clustering
        self.p_value_mixtures = p_value_mixtures
        self.p_value_trends = p_value_trends
        self.p_value_oscillation = p_value_oscillation
        self.clustering = clustering
        self.mixtures = mixtures
        self.trends = trends
        self.oscillation = oscillation
        self.longest_runs_about = longest_runs_about
        self.longest_runs_up_or_down = longest_runs_up_or_down
        
    def plot(self, **kwargs):
        
        style = kwargs.get('style', bluebelt.styles.paper)
        kwargs.pop('style', None)

        path = kwargs.pop('path', None)        
        
        fig, ax = plt.subplots(nrows=1, ncols=1, **kwargs)
        
        # observations
        ax.plot(self.series, **style.run_chart.plot)
        

        # longest run(s) about the median and longest run(s) up or down
        ylim = ax.get_ylim() # get ylim to set it back later

        for run in self.longest_runs_about:
            ax.fill_between(run.index, run.values, ylim[0], **style.run_chart.longest_runs_about_fill_between)

        for run in self.longest_runs_up_or_down:
            ax.fill_between(run.index, run.values, ylim[1], **style.run_chart.longest_runs_up_or_down_fill_between)
        
        ax.set_ylim(ylim[0], ylim[1]) # reset ylim

        # mean
        ax.axhline(self.series.median(), zorder=1, **style.run_chart.median_axhline)
        ax.text(ax.get_xlim()[1], self.series.median(), f' median = {self.series.median():1.2f}', **style.run_chart.median_text)

        ax.text(ax.get_xlim()[1], ylim[0], f' longest {"run" if len(self.longest_runs_about)==1 else "runs"}\n about the\n median = {self.longest_run_about}', **style.run_chart.longest_runs_about_text)
        ax.text(ax.get_xlim()[1], ylim[1], f' longest {"run" if len(self.longest_runs_up_or_down)==1 else "runs"}\n up or down = {self.longest_run_up_or_down}', **style.run_chart.longest_runs_up_or_down_text)

        # labels
        ax.set_title(f'run chart of {self.series.name}', **style.run_chart.title)
        #ax.set_xlabel(self.series.index.name)
        ax.set_ylabel('value')

        # set x axis locator
        bluebelt.core.helpers._axisformat(ax, self.series)

        plt.gcf().subplots_adjust(right=0.8)

        if path:
            plt.savefig(path)
            plt.close()
        else:
            plt.close()
            return fig

        
    def plotly(self, **kwargs):
        
        layout = go.Layout(
            title=f'run chart of {self.series.name}',    
            plot_bgcolor=f'rgba{defaults.white+(1,)}',
            hovermode="closest",
            xaxis=dict(
                title=self.series.index.name,
                linecolor=f'rgba{defaults.black+(1,)}',
                zeroline=False,
                ticks="outside",
                tickwidth=1,
                tickcolor=f'rgba{defaults.black+(1,)}',
                ticklen=5,
                showgrid=True,
                gridwidth=0.5,
                gridcolor=f'rgba{defaults.light_grey+(0.2,)}',
                mirror=True,
            ),
            yaxis=dict(
                title="value",
                linecolor=f'rgba{defaults.black+(1,)}',
                zeroline=False,
                ticks="outside",
                tickwidth=1,
                tickcolor=f'rgba{defaults.black+(1,)}',
                ticklen=5,
                showgrid=True,
                gridwidth=0.5,
                gridcolor=f'rgba{defaults.light_grey+(1,)}',
                mirror=True,
            ),
        )
        
        data = []
        
        for idx, trace in enumerate(self.longest_runs_about):
            data.append(go.Scatter(
                x=trace.index,
                y=trace.values,
                line=dict(
                    width=9,
                    color=f'rgba{defaults.red+(0.4,)}',
                ),
                mode='lines',
                name=f'longest {"run" if len(self.longest_runs_about)==1 else "runs"} about the median ({self.longest_run_about})',
                legendgroup="runs_about",
                showlegend=True if idx==0 else False,
            ))

        for idx, trace in enumerate(self.longest_runs_up_or_down):
            data.append(go.Scatter(
                x=trace.index,
                y=trace.values,
                line=dict(
                    width=9,
                    color=f'rgba{defaults.blue+(0.4,)}',
                ),
                mode='lines',
                name=f'longest {"run" if len(self.longest_runs_up_or_down)==1 else "runs"} up or down ({self.longest_run_up_or_down})',
                legendgroup="runs_up_down",
                showlegend=True if idx==0 else False,
            ))


        data.append(go.Scatter(
            x=self.series.index,
            y=self.series.values,
            line=dict(
                    width=1,
                    color=f'rgba{defaults.blue+(1,)}',
                ),
            marker=dict(
                color=f'rgba{defaults.black+(1,)}',
                size=5,
            ),
            mode='lines+markers',
            showlegend=False,
        ))
        
        fig = go.Figure(data=data, layout=layout)

        # legend position
        fig.update_layout(legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ))

    
        # add median line
        fig.add_shape(
                type="line",
                xref="paper",
                yref="y",
                x0=0,
                y0=self.series.median(),
                x1=1,
                y1=self.series.median(),
                line=dict(
                    color=f'rgba{defaults.grey+(1,)}',
                    width=1,
                    dash='dash'
                ),
            )
        fig.add_annotation(
            dict(
                xref="paper",
                yref="y",
                x=1,
                y=self.series.median(),
                text=f'median = {self.series.median():1.2f}',
                showarrow=False,
                align='right',
                bgcolor=f'rgba{defaults.white+(0.5,)}',
            )
        )
        
        # x-ticks to nice datetime format
        if isinstance(self.series.index, pd.DatetimeIndex):
            fig.update_layout(xaxis_tickformat = '%d-%m-%Y')
        
        # set width en height if any
        if 'width' in kwargs and 'height' in kwargs:
            fig.update_layout(width=kwargs.get('width'), height=kwargs.get('height'))

        return fig

@bluebelt.core.decorators.class_methods
class ProcessCapability():
    def __init__(self,
                 series,
                 target=None,
                 usl=None,
                 ub=None,
                 lsl=None,
                 lb=None,
                 subgroups=None,
                 subgroup_size=1,
                 tolerance=6,
                ):
        
        # check arguments
        if not isinstance(series, pd.Series):
            raise ValueError('series is not a Pandas Series')
        
        self.series = series
        self.target = target
        self.usl = usl
        self.lsl = lsl
        self.ub = ub
        self.lb = lb
        self.subgroups = subgroups
        self.subgroup_size = subgroup_size
        self.tolerance = tolerance
        
        # check parameters
        self.check()
        
        self.calculate()
    def test(self):
        return np.power(self.series - self.target, 2)

    def check(self):
        # check if all parameters are ok

        # limits and bounds
        if (self.lb and self.lsl) and self.lb != self.lsl:
            raise ValueError("You can specify a lower bound (lb) or a lower specification limit (lsl) but not both.")
        if (self.ub and self.usl) and self.ub != self.usl:
            raise ValueError("You can specify a upper bound (ub) or a upper specification limit (usl) but not both.")
        
    def calculate(self):
        
        # basic statistics
        self.min = self.series.min()
        self.max = self.series.max()
        self.mean = self.series.mean()
        self.std = self.series.std()
        self.subgroups = _get_subgroups(self.series, subgroups=self.subgroups, subgroup_size=self.subgroup_size)
        self.std_within = bluebelt.statistics.std.StdWithin(self.subgroups).std
        self.size = self.series.size

        self._lsl = self.lb if self.lb is not None else self.lsl if self.lsl is not None else None
        self._usl = self.ub if self.ub is not None else self.usl if self.usl is not None else None
        
        self._lsl_or_min = self.lb if self.lb is not None else self.lsl if self.lsl is not None else self.min
        self._usl_or_max = self.ub if self.ub is not None else self.usl if self.usl is not None else self.max
        
        if (self._usl is not None) and (self._lsl is not None):
            self._midpoint = (self._usl + self._lsl) / 2
        else:
            self._midpoint = self.mean

        # performance
        self.observed_lt_lsl = self.get_observed_lt_lsl()
        self.observed_gt_usl = self.get_observed_gt_usl()
        self.observed_performance = self.get_observed_performance()

        self.expected_lt_lsl_within = self.get_expected_lt_lsl_within()
        self.expected_gt_usl_within = self.get_expected_gt_usl_within()
        self.expected_performance_within = self.get_expected_performance_within()

        self.expected_lt_lsl_overall = self.get_expected_lt_lsl_overall()
        self.expected_gt_usl_overall = self.get_expected_gt_usl_overall()
        self.expected_performance_overall = self.get_expected_performance_overall()
        
        # within capability
        self.cp = self.get_cp()
        self.cpl = self.get_cpl()
        self.cpu = self.get_cpu()
        self.cpk = self.get_cpk()
        self.ccpk = self.get_ccpk()
        
        # overall capability
        self.pp = self.get_pp()
        self.ppl = self.get_ppl()
        self.ppu = self.get_ppu()
        self.ppk = self.get_ppk()
        self.cpm = self.get_cpm()
    
    # performance
    def get_observed_lt_lsl(self):
        return (self.series[self.series < self._lsl].count() / self.size) * 1000000 if self._lsl is not None else 0

    def get_observed_gt_usl(self):
        return (self.series[self.series > self._usl].count() / self.size) * 1000000 if self._usl is not None else 0

    def get_observed_performance(self):
        return self.get_observed_lt_lsl() + self.get_observed_gt_usl()

    def get_expected_lt_lsl_within(self):
        return (1 - stats.norm.cdf((self.mean - self._lsl) / self.std_within, loc=0, scale=1)) * 1000000 if self._lsl is not None else 0

    def get_expected_gt_usl_within(self):
        return (1 - stats.norm.cdf((self._usl - self.mean) / self.std_within, loc=0, scale=1)) * 1000000 if self._usl is not None else 0

    def get_expected_performance_within(self):
        return self.get_expected_lt_lsl_within() + self.get_expected_gt_usl_within()

    def get_expected_lt_lsl_overall(self):
        return (1 - stats.norm.cdf((self.mean - self._lsl) / self.std, loc=0, scale=1)) * 1000000 if self._lsl is not None else 0

    def get_expected_gt_usl_overall(self):
        return (1 - stats.norm.cdf((self._usl - self.mean) / self.std, loc=0, scale=1)) * 1000000 if self._usl is not None else 0

    def get_expected_performance_overall(self):
        return self.get_expected_lt_lsl_overall() + self.get_expected_gt_usl_overall()

    # within capability
    def get_cp(self):
        """
        Cp is a measure of the potential capability of the process. It is calculated by taking the ratio of the specification spread (USL – LSL)
        and the process spread (the tolerance * sigma variation) based on the standard deviation within subgroups.

        Cp = (usl - lsl) / (tolerance * std_within)
        """
        if (self._usl is not None) and (self._lsl is not None):
            return (self._usl - self._lsl) / (self.tolerance * self.std_within)
        else:
            return None

    def get_cpl(self):
        """
        Cpl = (mean - lsl) / ((tolerance / 2) * std_within)
        """
        if self._lsl is not None:
            return (self.mean - self._lsl) / (self.tolerance * 0.5 * self.std_within)
        else:
            return None

    def get_cpu(self):
        """
        Cpu = (usl - mean) / ((tolerance / 2) * std_within)
        """
        if self._usl is not None:
            return (self._usl - self.mean) / (self.tolerance * 0.5 * self.std_within)
        else:
            return None

    def get_cpk(self):
        if (self._usl is not None) and (self._lsl is not None):
            return min(self.get_cpl(), self.get_cpu())
        else:
            return None
    
    def get_ccpk(self):
        # calculate mu
        if self.target is not None:
            mu = self.target
        elif (self._usl is not None) and (self._lsl is not None):
            mu = (self._lsl + self._usl) / 2
        else:
            mu = self.mean

        # calculate ccpk
        if (self._usl is not None) and (self._lsl is not None):
            ccpk = min((self._usl - mu), (mu - self._lsl)) / ((self.tolerance / 2) * self.std_within)
        elif self._usl is not None:
            ccpk = (self._usl - mu) / ((self.tolerance / 2) * self.std_within) 
        elif self._lsl is not None:
            ccpk = (mu - self._lsl) / ((self.tolerance / 2) * self.std_within) 
        else:
            ccpk = None

        return ccpk
    
    # overall capability
    def get_pp(self):
        # Pp = (USL – LSL) / tolerance * sigma
        if (self._usl is not None) and (self._lsl is not None):
            return (self._usl - self._lsl) / (self.tolerance * self.std)
        else:
            return None

    def get_ppl(self):
        if self._lsl is not None:
            return (self.mean - self._lsl) / ((self.tolerance / 2) * self.std)
        else:
            return None

    def get_ppu(self):
        if self._usl is not None:
            return (self._usl - self.mean) / ((self.tolerance / 2) * self.std)
        else:
            return None

    def get_ppk(self):
        if (self._usl is not None) and (self._lsl is not None):
            return min(self.get_ppl(), self.get_ppu())
        else:
            return None

    def get_cpm(self):
        if not self.target:
            return None
        
        elif self._lsl or self._usl:
            if not self._usl:
                # LSL and target only
                numerator = self.target - (self.lb or self.lsl)
                denominator_factor = 0.5
            elif not self._lsl:
                # USL and target only
                numerator = self._usl - self.target
                denominator_factor = 0.5
            elif self.target == (self._lsl + self._usl) / 2:
                numerator = self._usl - self._lsl
                denominator_factor = 1
            else:
                numerator = min(self.target - self._lsl, self._usl - self.target)
                denominator_factor = 0.5
        else:
            return None

        # get subgroups
        subgroups = _get_subgroups(self.series, subgroup_size=5)

        denominator = self.tolerance * ((sum([sum((subgroups[col].dropna()-self.target)**2) for col in subgroups.columns]) / self.series.size)**0.5)

        return numerator / (denominator_factor * denominator)
    
    def __str__(self):
        
        fill = 15
        
        # process data
        digits = f'{bluebelt.core.helpers._format_digits([self.lsl, self.usl, self.target, self.mean, self.std_within, self.std], 6)}'

        str_target = f'{"target":{fill}}{self.target}'
        str_lsl = f'{"LB" if self.lb else "LSL":{fill}}{self._lsl:{digits}}' if self._lsl is not None else ''
        str_usl = f'{"UB" if self.ub else "USL":{fill}}{self._usl:{digits}}' if self._usl is not None else ''
        str_mean = f'{"mean":{fill}}{self.mean:{digits}}'
        str_n = f'{"n":{fill}}{self.size}'
        str_std_within = f'{"std within":{fill}}{self.std_within:{digits}}'
        str_std_overall = f'{"std overall":{fill}}{self.std:{digits}}'
        
        # within capability
        str_cp = f'{"Cp":{fill}}{self.cp:1.2f}' if self.cp is not None else f'{"Cp":{fill}}*'
        str_cpl = f'{"Cpl":{fill}}{self.cpl:1.2f}' if self.cpl is not None else f'{"Cpl":{fill}}*'
        str_cpu = f'{"Cpu":{fill}}{self.cpu:1.2f}' if self.cpu is not None else f'{"Cpu":{fill}}*'
        str_cpk = f'{"Cpk":{fill}}{self.cpk:1.2f}' if self.cpk is not None else f'{"Cpk":{fill}}*'
        str_ccpk = f'{"CCpk":{fill}}{self.ccpk:1.2f}' if self.ccpk is not None else f'{"CCpk":{fill}}*'

        # overall capability
        str_pp = f'{"Pp":{fill}}{self.pp:1.2f}' if self.pp is not None else f'{"Pp":{fill}}*'
        str_ppl = f'{"Ppl":{fill}}{self.ppl:1.2f}' if self.ppl is not None else f'{"Ppl":{fill}}*'
        str_ppu = f'{"Ppu":{fill}}{self.ppu:1.2f}' if self.ppu is not None else f'{"Ppu":{fill}}*'
        str_ppk = f'{"Ppk":{fill}}{self.ppk:1.2f}' if self.ppk is not None else f'{"Ppk":{fill}}*'
        str_cpm = f'{"Cpm":{fill}}{self.cpm:1.2f}' if self.cpm is not None else f'{"Cpm":{fill}}*'

        # performance
        str_observed_lt_lsl = f'{"PPM < LSL":{fill}}{self.observed_lt_lsl:1.0f}'
        str_observed_gt_usl = f'{"PPM > USL":{fill}}{self.observed_gt_usl:1.0f}'
        str_observed_performance = f'{"PPM":{fill}}{self.observed_performance:1.0f} ({self.observed_performance / 10000:1.2f}%)'
        
        str_expected_lt_lsl_within = f'{"PPM < LSL":{fill}}{self.expected_lt_lsl_within:1.0f}'
        str_expected_gt_usl_within = f'{"PPM > USL":{fill}}{self.expected_lt_lsl_within:1.0f}'
        str_expected_performance_within = f'{"PPM":{fill}}{self.expected_performance_within:1.0f} ({self.expected_performance_within / 10000:1.2f}%)'
        
        str_expected_lt_lsl_overall = f'{"PPM < LSL":{fill}}{self.expected_lt_lsl_overall:1.0f}'
        str_expected_gt_usl_overall = f'{"PPM > USL":{fill}}{self.expected_gt_usl_overall:1.0f}'
        str_expected_performance_overall = f'{"PPM":{fill}}{self.expected_performance_overall:1.0f} ({self.expected_performance_overall / 10000:1.2f}%)'
        
        width = 35

        result = (
            f'{"Process Data":{width}}{"Potential Capability":{width}}{"Overall Capability":{width}}\n' +
            f'{str_target:{width}}' + f'{str_cp:{width}}' + f'{str_pp:{width}}' + '\n' +
            f'{str_lsl:{width}}' + f'{str_cpl:{width}}' + f'{str_ppl:{width}}' + '\n' +
            f'{str_usl:{width}}' + f'{str_cpu:{width}}' + f'{str_ppu:{width}}' + '\n' +
            f'{str_mean:{width}}' + f'{str_cpk:{width}}' + f'{str_ppk:{width}}' + '\n' +
            f'{str_n:{width}}' + f'{str_ccpk:{width}}' + f'{str_cpm:{width}}' + '\n' +
            f'{str_std_within:{width}}' + '\n' +
            f'{str_std_overall:{width}}' + '\n' + '\n' +
            f'{"Observed Performance":{width}}{"Expected Performance (Within)":{width}}{"Expected Performance (Overall)":{width}}\n' +
            f'{str_observed_lt_lsl:{width}}' + f'{str_expected_lt_lsl_within:{width}}' + f'{str_expected_lt_lsl_overall:{width}}' + '\n' +
            f'{str_observed_gt_usl:{width}}' + f'{str_expected_gt_usl_within:{width}}' + f'{str_expected_gt_usl_overall:{width}}' + '\n' +
            f'{str_observed_performance:{width}}' + f'{str_expected_performance_within:{width}}' + f'{str_expected_performance_overall:{width}}'
            )
                
        return result

    def __repr__(self):
        target_value = self.target or 'None'

        lsl_text = 'lb' if self.lb is not None else 'lsl'
        lsl_value = self._lsl or 'None'

        usl_text = 'ub' if self.ub is not None else 'usl'
        usl_value = self._usl or 'None'

        
        return (f'{self.__class__.__name__}(n={self.size}, target={target_value}, {lsl_text}={lsl_value}, {usl_text}={usl_value})')
    
    @property
    def result(self):
        print(self)

    def df(self):
        df_md = pd.DataFrame({
            'metric': ["target", "LB" if self.lb else "LSL", "UB" if self.ub else "USL", "% < LSL", "% > USL", "Observed Performance", "Pp", "Ppk"],
            'value': [self.target, self._lsl, self._usl, self.observed_lt_lsl, self.observed_gt_usl, self.observed_performance, self.pp, self.ppk],
            }
        )
        
        return df_md

    def md(self):
        print(self.df().to_markdown(index=False))

        
    def plot(self, **kwargs):
        
        style = kwargs.get('style', bluebelt.styles.paper)
        kwargs.pop('style', None)

        path = kwargs.pop('path', None)

        # get bins
        min_bins = kwargs.pop('min_bins', 10)
        max_bins = kwargs.pop('max_bins', 20)

        histogram_points = [x for x in [self._lsl_or_min, self._usl_or_max, self.target] if x is not None]
        bins = bluebelt.core.helpers._bins(series=self.series, points=histogram_points, min_bins=min_bins, max_bins=max_bins)
        
        def _set_patch_style(patch, style):
            for key in ['facecolor', 'edgecolor', 'linewidth', 'hatch', 'fill']:
                if key in style:
                    eval(f'patch.set_{key}(style.get(key))')
        
        fig, ax = plt.subplots(nrows=1, ncols=1, **kwargs)
        
        # 1. histogram ############################################
        n, bins, patches = ax.hist(self.series, bins=bins, **style.process_capability.histogram)

        for patch in patches:
            # catch patches 

            # LSL
            if self._lsl is not None:

                # < LSL
                if patch.get_x() + patch.get_width() <= self._lsl:
                    patch.set_fill(False)
                    patch.set_hatch('')
                    patch_copy = copy.copy(patch)
                    _set_patch_style(patch_copy, style.process_capability.histogram_fill_out_of_range)
                    ax.add_patch(patch_copy)

                # on LSL
                elif patch.get_x() < self._lsl and patch.get_x() + patch.get_width() > self._lsl:
                    # split patch
                    patch.set_fill(False)
                    patch.set_hatch('')
                    # first half
                    patch_width_1 = self._lsl - patch.get_x()
                    patch_copy = copy.copy(patch)
                    _set_patch_style(patch_copy, style.process_capability.histogram_fill_out_of_range)
                    patch_copy.set_width(patch_width_1)
                    ax.add_patch(patch_copy)
                
                    # second half
                    patch_width_2 = (patch.get_x()+patch.get_width()) - self._lsl
                    patch_copy = copy.copy(patch)
                    _set_patch_style(patch_copy, style.process_capability.histogram_fill_in_range)
                    patch_copy.set_width(patch_width_2)
                    patch_copy.set_x(patch.get_x()+patch_width_1)
                    ax.add_patch(patch_copy)
            
            if self._usl is not None:
                # > USL
                if patch.get_x() >= self._usl:
                    patch.set_fill(False)
                    patch.set_hatch('')
                    patch_copy = copy.copy(patch)
                    _set_patch_style(patch_copy, style.process_capability.histogram_fill_out_of_range)
                    ax.add_patch(patch_copy)

                # on USL
                elif patch.get_x() <= self._usl and patch.get_x() + patch.get_width() > self._usl:
                    # split patch
                    patch.set_fill(False)
                    patch.set_hatch('')
                    # first half
                    patch_width_1 = self._usl - patch.get_x()
                    patch_copy = copy.copy(patch)
                    _set_patch_style(patch_copy, style.process_capability.histogram_fill_in_range)
                    patch_copy.set_width(patch_width_1)
                    ax.add_patch(patch_copy)
                    
                    # second half
                    patch_width_2 = (patch.get_x()+patch.get_width()) - self._usl
                    patch_copy = copy.copy(patch)
                    _set_patch_style(patch_copy, style.process_capability.histogram_fill_out_of_range)
                    patch_copy.set_width(patch_width_2)
                    patch_copy.set_x(patch.get_x()+patch_width_1)
                    ax.add_patch(patch_copy)

        # get current limits
        xlims = ax.get_xlim()
        ylims = ax.get_ylim()

        # fit a normal distribution to the data
        pdf_x = np.linspace(xlims[0], xlims[1], 100)

        # normal plot overall
        ax.plot(pdf_x, stats.norm.pdf(pdf_x, self.mean, self.std), label='overall', **style.process_capability.normal_plot_overall)
        
        # normal plot within
        ax.plot(pdf_x, stats.norm.pdf(pdf_x, self.mean, self.std_within), label='within', **style.process_capability.normal_plot_within)
        
        # target
        if self.target is not None:
            ax.axvline(x=self.target, ymin=0, ymax=1, **style.process_capability.target_axvline)
            ax.text(self.target, ylims[1]*0.9, f'target', **style.process_capability.sl_text)

        # LSL, USL
        if self._lsl is not None:
            ax.axvline(x=self._lsl, ymin=0, ymax=1, **style.process_capability.sl_axvline)
            lsl_text = 'LB' if self.lb is not None else 'LSL'
            ax.text(self._lsl, ylims[1]*0.9, lsl_text, **style.process_capability.sl_text)
        
        if self._usl is not None:
            ax.axvline(x=self._usl, ymin=0, ymax=1, **style.process_capability.sl_axvline)
            usl_text = 'UB' if self.ub is not None else 'USL'
            ax.text(self._usl, ylims[1]*0.9, usl_text, **style.process_capability.sl_text)

        # change xlim if needed
        xlims_min = min(self.min, self._lsl_or_min, self._usl_or_max, (self.target or self.mean))
        xlims_max = max(self.max, self._lsl_or_min, self._usl_or_max, (self.target or self.mean))
        xlims_margin = (xlims_max - xlims_min) * plt.rcParams['axes.xmargin']
        xlims = (xlims_min - xlims_margin, xlims_max + xlims_margin)

        # reset limits
        ax.set_xlim(xlims)
        ax.set_ylim(ylims)

        # set ticks
        ax.set_yticks([])
        
        # labels
        ax.set_title(f'process capability analysis of {self.series.name}', **style.process_capability.title)
        #ax.set_xlabel(self.series.index.name)
        ax.legend(loc='upper right')

        #plt.gcf().subplots_adjust(right=0.8)

        if path:
            plt.savefig(path)
            plt.close()
        else:
            plt.close()
            return fig

def _get_subgroups(series, subgroups=None, subgroup_size=None):
    if subgroups is not None:
        subgroup_size = subgroups.value_counts().max()
        s = pd.Series(index=subgroups, data=series.values)
        groups = [(s[group].append(pd.Series((subgroup_size - len(s[group])) * [np.nan], dtype=float), ignore_index=True)) for group in np.unique(subgroups)]
        return pd.DataFrame(groups).T
    elif subgroup_size is not None:
        series = series.append(pd.Series(((subgroup_size - series.size) % subgroup_size) * [np.NaN], dtype=float), ignore_index=True)
        return pd.DataFrame(series.values.reshape(subgroup_size, int(series.size/subgroup_size)))
    else:
        return series