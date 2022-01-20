import pandas as pd
import numpy as np
import math
import scipy.stats as stats

import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

import bluebelt.analysis.ci
import bluebelt.core.helpers
import bluebelt.styles
import bluebelt.core.decorators

from bluebelt.core.checks import check_kwargs

import warnings

def index():
    df = pd.DataFrame([['discrete', 'discrete', '-', '-', '-', 'chi square test', ''],
                        ['discrete', 'continuous', '-', '-', '-', 'logistic regression', ''],
                        ['continuous', 'discrete', 'mean', '1', 'normal', '1 sample t-test', 'one_sample_t'],
                        ['continuous', 'discrete', 'mean', '1', 'non-normal', '1 sample Wilcoxon test', 'wilcoxon'],
                        ['continuous', 'discrete', 'mean', '2', 'normal', '2 sample t-test', 'two_sample_t'],
                        ['continuous', 'discrete', 'mean', '2', 'non-normal', 'Mann-Whitney test', 'mann_whitney'],
                        ['continuous', 'discrete', 'mean', '>2', 'normal', '1 way Anova', 'anova'],
                        ['continuous', 'discrete', 'mean', '>2', 'non-normal', 'Kruskal-Wallis test', 'kruskal'],
                        ['continuous', 'discrete', 'variance', '2', 'normal', 'F-test', 'f_test'],
                        ['continuous', 'discrete', 'variance', '2', 'non-normal', 'Levene’s test', 'levene'],
                        ['continuous', 'discrete', 'variance', '>2', 'normal', 'Bartlett’s test', 'bartlett'],
                        ['continuous', 'discrete', 'variance', '>2', 'non-normal', 'Levene’s test', 'levene'],
                        ['continuous', 'continuous', '', '-', '-', 'regression', '']],
                    columns=['Y', 'X', 'investigate', '# data groups', 'distribution', 'test', 'bluebelt'])
    print(df.to_string(index=False))

# equal means
@bluebelt.core.decorators.class_methods
class OneSampleT():

    def __init__(self, frame, columns=None, popmean=None, confidence=0.95, alpha=0.05, **kwargs):

        if isinstance(frame, pd.Series):
            frame = pd.DataFrame(frame)
        elif isinstance(columns, str):
            frame = frame[columns]
        elif isinstance(columns, list):
            frame = frame[columns[0]]
        else:
            frame = frame[:,:1]

        # check arguments
        ncols = 1
        check_kwargs(locals())
                        
        self.frame = frame
        self.columms = columns
        self.nrows = frame.shape[0]
        self.ncols = frame.shape[1]
        self.popmean = popmean
        self.confidence = confidence
        self.alpha = alpha
        self.test = "One Sample T"
        self.h0 = f'$H_0: \\bar{{X}} = \\mu$'
        self.calculate(**kwargs)

    def calculate(self, **kwargs):
        self.statistic, self.p_value = stats.ttest_1samp(a=self.frame.iloc[:,0].values, popmean=self.popmean, **kwargs)
        self.ci_mean = [bluebelt.analysis.ci.ci_mean(self.frame.iloc[:,0])]
        self.passed = True if self.p_value > self.alpha else False

    def __str__(self):
        return ""
    
    def __repr__(self):
        return (f'{self.__class__.__name__}(nrows={self.nrows}, ncols={self.ncols}, alpha={self.alpha}, p_value={self.p_value:1.2f}, passed={self.passed})')
    
    def result(self):
        print(self.statistic)
    
    def plot(self, **kwargs):
        return _equal_means_plot(self, **kwargs)

@bluebelt.core.decorators.class_methods
class Wilcoxon():
    """
    Calculate the Wilcoxon signed-rank test.

    The Wilcoxon signed-rank test tests the null hypothesis that two related paired samples come from the same distribution.
    In particular, it tests whether the distribution of the differences x - y is symmetric about zero.
    It is a non-parametric version of the paired T-test.
    This test is performed with the assumption that if a pandas Series is provided the series contains the differences between x and y.
    """
    def __init__(self, frame, columns=None, confidence=0.95, alpha=0.05, **kwargs):

        if isinstance(frame, pd.Series):
            frame = pd.DataFrame(frame)
        elif isinstance(columns, str):
            frame = frame[columns]
        elif isinstance(columns, list):
            frame = frame[columns[:2]]
        else:
            frame = frame[:,:2]

        # check arguments
        ncols = (1, min(frame.shape[1], 2))
        check_kwargs(locals())
        
        self.frame = frame
        self.columms = columns
        self.nrows = self.frame.shape[0]
        self.ncols = self.frame.shape[1]
        self.confidence = confidence
        self.alpha = alpha
        self.test = "Wilcoxon signed-rank test"
        self.h0 = f'difference between the pairs follows a symmetric distribution around zero'
        self.calculate(**kwargs)

    def calculate(self, **kwargs):
        self.array_a = self.frame.iloc[:,0].dropna()
        self.array_b = self.frame.iloc[:,1].dropna() if self.ncols == 2 else None
        self.statistic, self.p_value = stats.wilcoxon(x=self.array_a, y=self.array_b, **kwargs)
        self.passed = True if self.p_value > self.alpha else False

    def __str__(self):
        return ""
    
    def __repr__(self):
        return (f'{self.__class__.__name__}(nrows={self.nrows}, ncols={self.ncols}, alpha={self.alpha}, p_value={self.p_value:1.2f}, passed={self.passed})')
    
    def plot(self, **kwargs):
        return _equal_means_plot(self, **kwargs)

@bluebelt.core.decorators.class_methods
class TwoSampleT():

    def __init__(self, frame, columns=None, related=False, confidence=0.95, alpha=0.05, **kwargs):
        
        if isinstance(columns, list):
            frame = frame[columns[:2]]
        else:
            frame = frame.iloc[:,:2]

        # check arguments
        ncols = 2
        check_kwargs(locals())
        
        self.frame = frame
        self.columms = columns
        self.nrows = self.frame.shape[0]
        self.ncols = self.frame.shape[1]
        self.related = related
        self.confidence = confidence
        self.alpha = alpha
        self.test = "Two Sample T Test"
        self.h0 = bluebelt.core.helpers._get_h0_equal_means(self.frame.columns)
        self.calculate(**kwargs)

    def calculate(self, **kwargs):
        self.array_a = self.frame.iloc[:,0].dropna()
        self.array_b = self.frame.iloc[:,1].dropna()
        
        self.mean_a = self.array_a.mean()
        self.mean_b = self.array_b.mean()
        
        self.max_a = self.array_a.max()
        self.max_b = self.array_b.max()
        
        self.min_a = self.array_a.min()
        self.min_b = self.array_b.min()
        
        self.ci_mean_a = bluebelt.analysis.ci.ci_mean(self.array_a)
        self.ci_mean_b = bluebelt.analysis.ci.ci_mean(self.array_b)

        # related or not
        if self.related:
            statistic, pvalue = stats.ttest_rel(self.array_a, self.array_b, **kwargs)
        else:
            # test equal variance
            equal_var = True if Levene(frame=self.frame, alpha=self.alpha).passed else False
            statistic, pvalue = stats.ttest_ind(self.array_a, self.array_b, equal_var=equal_var, **kwargs)

        self.statistic = statistic
        self.p_value = pvalue
        self.passed = True if self.p_value >= self.alpha else False


    def __str__(self):
        return ""
    
    def __repr__(self):
        return (f'{self.__class__.__name__}(nrows={self.nrows}, ncols={self.ncols}, alpha={self.alpha}, p_value={self.p_value:1.2f}, passed={self.passed})')
    
    def result(self):
        print(self.statistic)
    
    def plot(self, **kwargs):
        return _equal_means_plot(self, **kwargs)

@bluebelt.core.decorators.class_methods
class MannWhitney():
    """
    apply the Mann-Whitney test on a pandas dataframe with the columns as groups to compare
    Returns the scipy Mann-Whitney; statistic, pvalue
    pvalue >= alpha (default 0.05) : columns have equal means
    pvalue < alpha: columns don't have equal means
    """
    
    def __init__(self, frame, columns=None, confidence=0.95, alpha=0.05, **kwargs):
        
        # check arguments
        ncols = 2
        check_kwargs(locals())

        self.frame = frame if columns is None else frame[columns]
        self.columms = columns
        self.nrows = self.frame.shape[0]
        self.ncols = self.frame.shape[1]
        self.confidence = confidence
        self.alpha = alpha
        self.test = 'Mann-Whitney'
        self.h0 = bluebelt.core.helpers._get_h0_equal_means(self.frame.columns)
        self.calculate(**kwargs)

    def calculate(self, **kwargs):
        
        self.statistic, self.p_value = stats.mannwhitneyu(*self.frame.dropna().T.values)
        self.passed = True if self.p_value >= self.alpha else False

    def __repr__(self):
        return (f'{self.__class__.__name__}(nrows={self.nrows}, ncols={self.ncols}, alpha={self.alpha}, p_value={self.p_value:1.2f}, passed={self.passed})')
    
    def plot(self, **kwargs):
        return _equal_means_plot(self, **kwargs)

@bluebelt.core.decorators.class_methods
class Anova():
    """
    apply the one way ANOVA test on a pandas dataframe with the columns as groups to compare
    Returns the scipy F_onewayResult; statistic, pvalue
    pvalue >= alpha (default 0.05) : columns have equal means
    pvalue < alpha: columns don't have equal means
    """
    
    def __init__(self, frame, columns=None, confidence=0.95, alpha=0.05, **kwargs):
        
        # check arguments
        ncols = (2, None)
        check_kwargs(locals())

        self.frame = frame if columns is None else frame[columns]
        self.data_dict = _data_dict(self.frame)
        self.columms = columns
        self.nrows = self.frame.shape[0]
        self.ncols = self.frame.shape[1]
        self.confidence = confidence
        self.alpha = alpha
        self.test = "ANOVA"
        self.h0 = bluebelt.core.helpers._get_h0_equal_means(self.frame.columns)
        self.calculate(**kwargs)

    def calculate(self, **kwargs):
        
        self.statistic, self.p_value = stats.f_oneway(*self.data_dict.values())
        self.passed = True if self.p_value >= self.alpha else False

    def __repr__(self):
        return (f'{self.__class__.__name__}(nrows={self.nrows}, ncols={self.ncols}, alpha={self.alpha}, p_value={self.p_value:1.2f}, passed={self.passed})')
    
    def plot(self, **kwargs):
        return _equal_means_plot(self, **kwargs)

@bluebelt.core.decorators.class_methods
class KruskalWallis():
    """
    apply the Kruskal-Wallis test on a pandas dataframe with the columns as groups to compare
    Returns the scipy KruskalResult; statistic, pvalue
    pvalue >= alpha (default 0.05) : columns have equal means
    pvalue < alpha: columns don't have equal means
    """
    
    def __init__(self, frame, columns=None, confidence=0.95, alpha=0.05, **kwargs):
        
        # check arguments
        ncols = (2, None)
        check_kwargs(locals())


        self.frame = frame if columns is None else frame[columns]
        self.data_dict = _data_dict(self.frame)
        self.columms = columns
        self.nrows = self.frame.shape[0]
        self.ncols = self.frame.shape[1]
        self.confidence = confidence
        self.alpha = alpha
        self.test = 'Kruskal-Wallis'
        self.h0 = bluebelt.core.helpers._get_h0_equal_means(self.frame.columns)
        self.calculate(**kwargs)

    def calculate(self, **kwargs):
        
        self.statistic, self.p_value = stats.kruskal(*self.data_dict.values())
        self.passed = True if self.p_value >= self.alpha else False

    def __repr__(self):
        return (f'{self.__class__.__name__}(nrows={self.nrows}, ncols={self.ncols}, alpha={self.alpha}, p_value={self.p_value:1.2f}, passed={self.passed})')
    
    def plot(self, **kwargs):
        return _equal_means_plot(self, **kwargs)

@bluebelt.core.decorators.class_methods
class EqualMeans():
    """
    Test a dataframe for equal means over the dataframe columns.

    frame: a pandas DataFrame
    columns: string or list of strings with the column names to be tested
    alpha: test threshold

    applies ANOVA or Kruskal-Wallis test

    pvalue >= alpha (default 0.05) : columns have equal means
    pvalue < alpha: columns don't have equal means
    
    """
    
    def __init__(self, frame, columns=None, confidence=0.95, alpha=0.05, **kwargs):
        
       # check arguments
        ncols = (2, None)
        check_kwargs(locals())

        self.frame = frame if columns is None else frame[columns]
        self.columms = columns
        self.nrows = self.frame.shape[0]
        self.ncols = self.frame.shape[1]
        self.confidence = confidence
        self.alpha = alpha
        self.h0 = bluebelt.core.helpers._get_h0_equal_means(self.frame.columns)
        self.calculate(**kwargs)

    def calculate(self, **kwargs):
        
        # test for normal distribution; null hypothesis: values come from a normal distribution
        if NormalDistribution(frame=self.frame, alpha=self.alpha).passed and Levene(frame=self.frame, alpha=self.alpha).passed:
            # all columns in the dataframe come from a normal distribution AND have equal variances
            # do Anova
            test = Anova(frame=self.frame, alpha=self.alpha)
        else:
            # not all columns in the dataframe come from a normal distribution OR have equal variances
            # do Kruskal-Wallis
            test = KruskalWallis(frame=self.frame, alpha=self.alpha)
        
        self.test = test.test
        self.statistic = test.statistic
        self.p_value = test.p_value
        self.passed = True if self.p_value >= self.alpha else False

    def __repr__(self):
        return (f'{self.__class__.__name__}(nrows={self.nrows}, ncols={self.ncols}, alpha={self.alpha}, p_value={self.p_value:1.2f}, passed={self.passed})')
    
    def plot(self, **kwargs):
        return _equal_means_plot(self, **kwargs)

def _equal_means_plot(plot_obj, **kwargs):

    style = kwargs.pop('style', bluebelt.styles.paper)
    path = kwargs.pop('path', None)
    digits = kwargs.pop('digits', 2)
    xlim = kwargs.pop('xlim', None)
    xticks = kwargs.pop('xticks', True)

    # prepare figure
    fig, axes = plt.subplots(nrows=plot_obj.ncols, ncols=1, gridspec_kw={'wspace': 0, 'hspace': 0}, **kwargs)

    for row in range(0, plot_obj.ncols):

        if plot_obj.ncols == 1:
            ax = axes
        else:
            ax = axes[row]
        
        # set right zorder
        ax.set_zorder((plot_obj.ncols-row)*10)
        # get the data
        array = plot_obj.frame.iloc[:,row].dropna()

        # 1. box plot ############################################
        boxplot = ax.boxplot(array, vert=False, widths=0.3, whis=1.5)
        for box in boxplot['boxes']:
            box.set(**style.equal_means_plot.boxplot.get('boxes', {}))
        
        # 2. CI for the mean #####################################
        ci_mean = bluebelt.analysis.ci.ci_mean(array, confidence=plot_obj.confidence)

        ax.plot([ci_mean[0], ci_mean[1]], [1.5,1.5], **style.equal_means_plot.ci_mean_plot)
        ax.axvline(x=ci_mean[0], ymin=9/14, ymax=11/14, **style.equal_means_plot.ci_mean_axvline)
        ax.axvline(x=ci_mean[1], ymin=9/14, ymax=11/14, **style.equal_means_plot.ci_mean_axvline)
        ax.scatter([array.mean()],[1.5], **style.equal_means_plot.ci_mean_scatter)

        ci_area = np.linspace(ci_mean[0], ci_mean[1], 100)
        ax.fill_between(x=(ci_mean[0], ci_mean[1]), y1=0, y2=2, label='CI sample mean', **style.equal_means_plot.ci_fill_between)
        ax.axvline(x=ci_mean[0], ymin=0, ymax=2, **style.equal_means_plot.ci_axvline)
        ax.axvline(x=ci_mean[1], ymin=0, ymax=2, **style.equal_means_plot.ci_axvline)
        
        
        # plot CI values
        ax.text(ci_mean[0], 1.5, f'{ci_mean[0]:1.{digits}f} ', **style.equal_means_plot.text_ci_min)
        ax.text(ci_mean[1], 1.5, f' {ci_mean[1]:1.{digits}f}', **style.equal_means_plot.text_ci_max)

        # plot popmean if it exists
        if hasattr(plot_obj, 'popmean'):
            ax.axvline(plot_obj.popmean, ymin=0, ymax=2, label='population mean', **style.equal_means_plot.popmean_axvline)
        

        # handle xticks
        local_xticks = bluebelt.core.helpers._get_boxplot_quantiles(array, whis=1.5)
        if xticks:
            ax.set_xticks(local_xticks)
            ax.tick_params(axis="x", top=False, direction='in', pad=-18)
            ax.xaxis.set_major_formatter(FormatStrFormatter(f'%1.{digits}f'))
        elif row < plot_obj.ncols - 1: # last row
            ax.set_xticks([])
        

        ax.set_ylim([0.25, 2])
        ax.set_yticklabels([array.name])

        # set title and x limits
        if row == 0:
            xlims = ax.get_xlim()
            ax.set_title(plot_obj.h0 + f'   t={plot_obj.statistic:1.2f} p={plot_obj.p_value:1.2f} ('+r'$H_0$'+f' is {"accepted" if plot_obj.p_value > plot_obj.alpha else "rejected"})', **style.equal_means_plot.title)
            ax.legend(loc='best')
        else:
            xlims = (min(ax.get_xlim()[0], xlims[0]), max(ax.get_xlim()[1], xlims[1]))
        
    # format things
    for row in range(0, plot_obj.ncols):

        if plot_obj.ncols == 1:
            ax = axes
        else:
            ax = axes[row]

        

        if xlim is not None:
            ax.set_xlim(xlim)
        else:
            ax.set_xlim(xlims)
        

    # add suptitle
    fig.suptitle(t=f'{plot_obj.test}', x=fig.subplotpars.left, **style.equal_means_plot.suptitle)

    if path:
        plt.savefig(path)
        plt.close()
    else:
        plt.close()
        return fig

# equal variance
@bluebelt.core.decorators.class_methods
class FTest():
    """
    apply the F-test on a pandas dataframe with the columns as groups to compare
    the F-test is extremely sensitive to non-normality of the two arrays
    pvalue >= 0.05 : columns have equal variances
    pvalue < 0.05: columns don't have equal variances
    """
    
    def __init__(self, frame, columns=None, alpha=0.05, **kwargs):
        
        # check arguments
        ncols = 2
        check_kwargs(locals())
        
        self.frame = frame if columns is None else frame[columns]
        self.columms = columns
        self.array_a = self.frame.iloc[:,0].dropna()
        self.array_b = self.frame.iloc[:,1].dropna()
        self.nrows = self.frame.shape[0]
        self.ncols = self.frame.shape[1]
        self.alpha = alpha
        self.test = 'F-test'
        self.calculate(**kwargs)

    def calculate(self, **kwargs):
        self.statistic = self.array_a.var() / self.array_b.var()
        self.p_value = stats.f.cdf(self.statistic, self.array_a.size-1, self.array_b.size-1)
        self.passed = True if self.p_value >= self.alpha else False

    def __repr__(self):
        return (f'{self.__class__.__name__}(nrows={self.nrows}, ncols={self.ncols}, alpha={self.alpha}, p_value={self.p_value:1.2f}, passed={self.passed})')
    
    def plot(self, **kwargs):
        return _equal_variances_plot(self, **kwargs)

@bluebelt.core.decorators.class_methods
class Levene():
    """
    apply levene's test on a pandas dataframe with the columns as groups to compare
    Returns the scipy LeveneResult; statistic, pvalue
    pvalue >= 0.05 : columns have equal variances
    pvalue < 0.05: columns don't have equal variances
    """
    
    def __init__(self, frame, columns=None, alpha=0.05, **kwargs):
        
        # check arguments
        ncols = (2, None)
        check_kwargs(locals())
        

        self.frame = frame if columns is None else frame[columns]
        self.data_dict = _data_dict(self.frame)
        self.columms = columns
        self.nrows = self.frame.shape[0]
        self.ncols = self.frame.shape[1]
        self.alpha = alpha
        self.test = 'Levene'
        self.calculate(**kwargs)

    def calculate(self, **kwargs):
        self.statistic, self.p_value = stats.levene(*self.data_dict.values())
        self.passed = True if self.p_value >= self.alpha else False
    
    def __repr__(self):
        return (f'{self.__class__.__name__}(nrows={self.nrows}, ncols={self.ncols}, alpha={self.alpha}, p_value={self.p_value:1.2f}, passed={self.passed})')
    
    def plot(self, **kwargs):
        return _equal_variances_plot(self, **kwargs)

@bluebelt.core.decorators.class_methods
class Bartlett():
    """
    apply Bartlett's test on a pandas dataframe with the columns as groups to compare
    Returns the scipy BartlettResult; statistic, pvalue
    pvalue >= 0.05 : columns have equal variances
    pvalue < 0.05: columns don't have equal variances
    """
    
    def __init__(self, frame, columns=None, alpha=0.05, **kwargs):
        
        # check arguments
        ncols = (2,None)
        check_kwargs(locals())
        
        self.frame = frame if columns is None else frame[columns]
        self.data_dict = _data_dict(self.frame)
        self.columms = columns
        self.nrows = self.frame.shape[0]
        self.ncols = self.frame.shape[1]
        self.alpha = alpha
        self.test = 'Bartlett'
        self.calculate(**kwargs)

    def calculate(self, **kwargs):
        self.statistic, self.p_value = stats.bartlett(*self.data_dict.values())
        self.passed = True if self.p_value >= self.alpha else False
    
    def __repr__(self):
        return (f'{self.__class__.__name__}(nrows={self.nrows}, ncols={self.ncols}, alpha={self.alpha}, p_value={self.p_value:1.2f}, passed={self.passed})')
    
    def plot(self, **kwargs):
        return _equal_variances_plot(self, **kwargs)

@bluebelt.core.decorators.class_methods
class EqualVariances():
    """
    Test a dataframe for equal variances over the dataframe columns.

    frame: a pandas DataFrame
    columns: string or list of strings with the column names to be tested
    alpha: test threshold

    applies F-test, Bartlett's or Levene's

    pvalue >= alpha (default 0.05) : columns have equal variances
    pvalue < alpha: columns don't have equal variances
    
    """
    def __init__(self, frame, columns=None, alpha=0.05, **kwargs):
        
        # check arguments
        ncols = (2,None)
        check_kwargs(locals())
        
        self.frame = frame if columns is None else frame[columns]
        self.columms = columns
        self.nrows = self.frame.shape[0]
        self.ncols = self.frame.shape[1]
        self.alpha = alpha
        self.calculate(**kwargs)

    def calculate(self, **kwargs):

        # test for normal distribution; null hypothesis: values come from a normal distribution
        if NormalDistribution(frame=self.frame, alpha=self.alpha).passed:
            # all columns in the dataframe come from a normal distribution
            if self.ncols == 2:
                test = FTest(frame=self.frame, alpha=self.alpha)
            else:
                test = Bartlett(frame=self.frame, alpha=self.alpha)
        else:
            # not all columns in the dataframe come from a normal distribution
            test=Levene(frame=self.frame, alpha=self.alpha)
        
        self.test = test.test
        self.statistic = test.statistic
        self.p_value = test.p_value
        self.passed = True if self.p_value >= self.alpha else False
    
    def __repr__(self):
        return (f'{self.__class__.__name__}(nrows={self.nrows}, ncols={self.ncols}, alpha={self.alpha}, p_value={self.p_value:1.2f}, passed={self.passed})')
    
    def plot(self, **kwargs):
        return _equal_variances_plot(self, **kwargs)

def _equal_variances_plot(plot_obj, **kwargs):

    style = kwargs.pop('style', bluebelt.styles.paper)
    path = kwargs.pop('path', None)
    xlim = kwargs.pop('xlim', None)
    digits = kwargs.pop('digits', 3)
    bins = kwargs.pop('bins', 17)

    # prepare figure
    fig, axes = plt.subplots(nrows=plot_obj.ncols, ncols=1, sharex='col', gridspec_kw={'wspace': 0, 'hspace': 0}, **kwargs)

    for row in range(0, plot_obj.ncols):

        if plot_obj.ncols == 1:
            ax = axes
        else:
            ax = axes[row]
        
        # set right zorder
        ax.set_zorder((plot_obj.ncols-row)*10)
        # get the data
        array = plot_obj.frame.iloc[:,row]

        # calculate bin width
        bin_width = (np.nanmax(plot_obj.frame.values) - np.nanmin(plot_obj.frame.values)) / bins

        # 1. histogram ############################################
        ax.hist(array, bins=np.arange(np.nanmin(plot_obj.frame.values), np.nanmax(plot_obj.frame.values) + bin_width, bin_width), **style.equal_variances_plot.histogram)
        ax.text(0.05, 0.9, array.name, transform=ax.transAxes, **style.equal_variances_plot.text)
        ax.set_yticks([])

        # add xlims to xlims list for formatting
        if row == 0:
            xlims = ax.get_xlim()
            ax.set_title(f't={plot_obj.statistic:1.2f} p={plot_obj.p_value:1.2f} ('+r'$H_0$'+f' is {"accepted" if plot_obj.p_value > plot_obj.alpha else "rejected"})', **style.equal_variances_plot.title)
 
        else:
            xlims = (min(ax.get_xlim()[0], xlims[0]), max(ax.get_xlim()[1], xlims[1]))
        
    # format things
    for row in range(0, plot_obj.ncols):

        if plot_obj.ncols == 1:
            ax = axes
        else:
            ax = axes[row]

        if xlim is not None:
            ax.set_xlim(xlim)
        else:
            ax.set_xlim(xlims)

    # add suptitle
    fig.suptitle(t=f'{plot_obj.test}', x=fig.subplotpars.left, **style.equal_variances_plot.suptitle)
    
    if path:
        plt.savefig(path)
        plt.close()
    else:
        plt.close()
        return fig

# distribution
@bluebelt.core.decorators.class_methods
class AndersonDarling():
    """
    Anderson-Darling test
    
    null hypothesis: x comes from a normal distribution
    
    test all pandas dataframe columns for normal distribution
    input pivoted dataframe
    
    pvalue >= alpha : column values are (all) normally distributed
    pvalue < alpha: column values are not (all) normally distributed
    """
    
    def __init__(self, frame, columns=None, dist='norm', alpha=0.05, **kwargs):
        
        if isinstance(frame, pd.Series):
            frame = pd.DataFrame(frame)
        elif isinstance(columns, (list, str)):
            frame = frame[columns]
        
        # check arguments
        ncols = (1, None)
        check_kwargs(locals())

        self.frame = frame
        self.columns = columns
        self.dist = dist
        self.nrows = self.frame.shape[0]
        self.ncols = self.frame.shape[1]
        self.alpha = alpha
        self.test = "Anderson-Darling"
        self.calculate(**kwargs)

    def calculate(self, **kwargs):
        statistics = {}
        p_values = {}
        passed_values = {}

        statistic = 0
        p_value = 1
        
        for col in self.frame.columns:

            AD, critical_values, significance_level = stats.anderson(self.frame[col].dropna().values, dist=self.dist)
        
            AD_adjusted = AD*(1 + (.75/50) + 2.25/(50**2))
            if AD_adjusted >= .6:
                pval = math.exp(1.2937 - 5.709*AD_adjusted - .0186*(AD_adjusted**2))
            elif AD_adjusted >=.34:
                pval = math.exp(.9177 - 4.279*AD_adjusted - 1.38*(AD_adjusted**2))
            elif AD_adjusted >.2:
                pval = 1 - math.exp(-8.318 + 42.796*AD_adjusted - 59.938*(AD_adjusted**2))
            else:
                pval = 1 - math.exp(-13.436 + 101.14*AD_adjusted - 223.73*(AD_adjusted**2))

            if pval < p_value:
                p_value = pval
                statistic = AD
            
            statistics[col] = AD
            p_values[col] = pval
            passed_values[col] = True if pval >= self.alpha else False

        self.statistics = pd.Series(statistics)
        self.p_values = pd.Series(p_values)
        self.passed_values = pd.Series(passed_values)
        
        self.statistic = statistic
        self.p_value = p_value
        self.passed = True if self.p_value >= self.alpha else False

    def __repr__(self):
        return (f'{self.__class__.__name__}(nrows={self.nrows}, ncols={self.ncols}, alpha={self.alpha}, p_value={self.p_value:1.2f}, passed={self.passed})')
    
    def plot(self, **kwargs):
        return _distribution_plot(self, dist=self.dist, **kwargs)

@bluebelt.core.decorators.class_methods
class DAgostinoPearson():
    """
    D’Agostino-Pearson test
    
    null hypothesis: x comes from a normal distribution
    
    test all pandas dataframe columns for normal distribution
    input pivoted dataframe
    Returns the scipy NormaltestResult; statistic, pvalue for a single column
    Returns the worst scipy NormaltestResult as a tuple; statistic, pvalue for multiple columns
    pvalue >= alpha : column values are (all) normally distributed
    pvalue < alpha: column values are not (all) normally distributed
    """
    
    def __init__(self, frame, columns=None, alpha=0.05, **kwargs):
        
        if isinstance(frame, pd.Series):
            frame = pd.DataFrame(frame)
        elif isinstance(columns, (list, str)):
            frame = frame[columns]
        
        # check arguments
        ncols = (1, None)
        check_kwargs(locals())

        self.frame = frame
        self.columns = columns
        self.dist = 'norm'
        self.nrows = self.frame.shape[0]
        self.ncols = self.frame.shape[1]
        self.alpha = alpha
        self.test = "D’Agostino-Pearson"
        self.calculate(**kwargs)

    def calculate(self, **kwargs):
        statistics = {}
        p_values = {}
        passed_values = {}

        statistic = 0
        p_value = 1
        
        for col in self.frame.columns:
            result = stats.normaltest(self.frame[col].dropna().values)
            if result.pvalue < p_value:
                p_value = result.pvalue
                statistic = result.statistic

            statistics[col] = result.statistic
            p_values[col] = result.pvalue
            passed_values[col] = True if result.pvalue >= self.alpha else False

        self.statistics = pd.Series(statistics)
        self.p_values = pd.Series(p_values)
        self.passed_values = pd.Series(passed_values)

        self.statistic = statistic
        self.p_value = p_value
        self.passed = True if self.p_value >= self.alpha else False

    def __repr__(self):
        return (f'{self.__class__.__name__}(nrows={self.nrows}, ncols={self.ncols}, alpha={self.alpha}, p_value={self.p_value:1.2f}, passed={self.passed})')
    
    def plot(self, **kwargs):
        return _distribution_plot(self, dist='norm', **kwargs)

NormalDistribution = DAgostinoPearson

def _distribution_plot(plot_obj, **kwargs):

    style = kwargs.pop('style', bluebelt.styles.paper)
    path = kwargs.pop('path', None)
    dist = kwargs.pop('dist', 'norm')


    # prepare figure
    ncols = math.ceil(math.sqrt(plot_obj.ncols))
    nrows = math.ceil(plot_obj.ncols/ncols)
    # nrows = math.ceil(math.sqrt(plot_obj.ncols))
    # ncols = math.ceil(plot_obj.nrows/nrows)
    
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, gridspec_kw={'wspace': 0, 'hspace': 0}, **kwargs)

    for row in range(0, nrows):
        for col in range(0, ncols):
            id = col + (ncols * row)

            if nrows == 1:
                if ncols == 1:
                    ax = axes
                else:
                    ax = axes[col]
            else:
                ax = axes[row, col]

                
            # get the data
            if id < plot_obj.ncols:
                array = plot_obj.frame.iloc[:,id].dropna()
                col = plot_obj.frame.columns[id]
                
                # H0 the two distributions are identical, F(x)=G(x)
                parameters = eval("stats."+dist+".fit(array.values)")
                (osm, osr), (slope, intercept, r) = stats.probplot(array, dist=eval("stats."+dist), sparams=parameters, fit=True)

                # plot
                ax.scatter(osm, osr, **style.distribution_plot.scatter)
                ax.plot(osm, osm*slope + intercept, **style.distribution_plot.plot)
                
                ax.text(0.99, 0.01, f'statistic: {plot_obj.statistics[col]:1.2f}\np-value: {plot_obj.p_values[col]:1.2f}', transform=ax.transAxes, **style.distribution_plot.stat_text)
                
                if plot_obj.ncols > 1:
                    ax.text(0.01, 0.99, f'{plot_obj.frame.columns[id]}', transform=ax.transAxes, **style.distribution_plot.array_text)
                
                if id == 0:
                    ax.set_title(f'{plot_obj.test} for {bluebelt.core.helpers._get_distribution(plot_obj.dist)}', **style.distribution_plot.title)
                ax.set_xticks([])
                ax.set_yticks([])
                
                ax.set_ylim(ax.get_xlim())
                
            else:
                ax.axis('off')
            
    # add suptitle
    fig.suptitle(t=f'Probability Plot', x=fig.subplotpars.left, **style.distribution_plot.suptitle)

    if path:
        plt.savefig(path)
        plt.close()
    else:
        plt.close()
        return fig

def _data_dict(frame):
    return {k:v.dropna().values for k, v in frame.items()}