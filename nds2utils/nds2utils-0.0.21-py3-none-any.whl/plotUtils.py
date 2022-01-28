import os, sys, time
import numpy as np
import matplotlib as mpl
mpl.rcParams.update({'text.usetex': False,
                     'figure.figsize': (12, 9),
                     'font.family': 'serif',
                     'lines.linewidth': 2.5,
                     'font.size': 16,
                     'xtick.labelsize': 'large',
                     'ytick.labelsize': 'large',
                     'legend.fancybox': True,
                     'legend.fontsize': 12,
                     'legend.framealpha': 0.7,
                     'legend.handletextpad': 0.5,
                     'legend.labelspacing': 0.2,
                     'legend.loc': 'best',
                     'savefig.dpi': 80,
                     'pdf.compression': 9})
mpl.use('TKAgg') # To fix: somehow allow the user to user whatever interactive backend they want
import matplotlib.pyplot as plt

from .dataUtils import linear_log_ASD

# Convenience
def quick_ASD_grab(dataDict, chan, calibrated=True):
    '''
    Inputs:
    dataDict = data dictionary structure containing chanA PSD
    chan     = str. channel name we want to grab ASD from
    Output:
    ff = frequency vector in Hz
    ASD = amplitude spectral density of chan   = sqrt( <|chan|^2> )
    Returned as tuple = (ff, ASD)
    '''
    ff = dataDict[chan]['ff']
    ASD = dataDict[chan]['ASD']

    if calibrated:
        if 'calASD' in dataDict[chan].keys():
            ASD = dataDict[chan]['calASD']

    return ff, ASD

def quick_PSD_grab(dataDict, chan, calibrated=True):
    '''
    Inputs:
    dataDict = data dictionary structure containing chanA PSD
    chan     = str. channel name we want to grab ASD from
    Output:
    ff = frequency vector in Hz
    PSD = power spectral density of chan   = <|chan|^2>
    Returned as tuple = (ff, PSD)
    '''
    ff = dataDict[chan]['ff']
    PSD = dataDict[chan]['PSD']

    if calibrated:
        if 'calPSD' in dataDict[chan].keys():
            PSD = dataDict[chan]['calPSD']

    return ff, PSD

def quick_CSD_grab(dataDict, chanA, chanB, calibrated=True):
    '''
    Inputs:
    dataDict = data dictionary structure containing chanB * chanA CSD
    chanA    = str. channel name we want for channel A, the non-conjugated channel
    chanB    = str. channel name we want for channel B, the conjugated channel
    Output:
    ff = frequency vector in Hz
    CSD = cross spectral density of chanA and chanB = <chanB^*|chanA>
    Returned as tuple = (ff, CSD)
    '''
    ff = dataDict[chanB][chanA]['ff']
    CSD = dataDict[chanB][chanA]['CSD']

    if calibrated:
        if 'calCSD' in dataDict[chanB][chanA].keys():
            TF = dataDict[chanB][chanA]['calCSD']

    return ff, CSD

def quick_TF_grab(dataDict, chanA, chanB, calibrated=True):
    '''
    Inputs:
    dataDict   = data dictionary structure containing chanB / chanA TF
    chanA      = str. channel name we want for channel A, the input channel
    chanB      = str. channel name we want for channel B, the output channel
    calibrated = bool. returns a calibrated TF if possible. Default is true.
    Output:
    ff = frequency vector in Hz
    TF = transfer function from chanA to chanB = B/A
    coh = power coherence of A and B = |CSD|^2/(PSD_A * PSD_B)
    Returned as tuple = (ff, TF, coh)
    '''
    ff = dataDict[chanB][chanA]['ff']
    TF = dataDict[chanB][chanA]['TF']
    coh = dataDict[chanB][chanA]['coh']

    if calibrated:
        if 'calTF' in dataDict[chanB][chanA].keys():
            TF = dataDict[chanB][chanA]['calTF']

    return ff, TF, coh

# Quick plotting
def bode(ff,
         TF,
         label='TF',
         title='Transfer Function',
         units='cts/cts',
         xlims=None,
         ylims=None,
         logbin=False,
         num_points=1000,
         fig=None ):
    '''
    Plots a very simple bode plot.
    Run plt.ion() before for convenience.

    Inputs:
    ff     = frequency vector in Hz.
    TF     = array of complex numbers.  Represents the tranfer function for the bode plot.
    label  = str.  Legend label for the TF.  Default is 'TF'.
    title  = str.  Title of the figure.
    units  = str. Units for the y-axis.  Default is cts/cts.
    xlims  = array containing two floats.  x-axis limits on the plot.  Default is None.
    ylims  = array containing two floats.  y-axis limits on the plot.  Default is None.
    logbin      = bool.  If True, logbins the ASDs.  Default is False.
    num_points  = int.  If logbin == True, logbins using this number of points.  Default is 1000.
    fig    = matplotlib figure object upon which to make the plot.

    Output:
    fig = matplotlib figure object.
    '''
    newFig = False
    if xlims == None:
        xlims = [ff[1], ff[-1]]
    if fig == None:
        newFig = True
        fig = plt.figure(figsize=(16,12))
        s1 = fig.add_subplot(211)
        s2 = fig.add_subplot(212)
    else:
        s1 = fig.get_axes()[0]
        s2 = fig.get_axes()[1]

    if logbin:
        logf_low = ff[1]
        logf_high = ff[-1]
        fflog = np.logspace(np.log10(logf_low), np.log10(logf_high), num_points)
        _, plotTFreal = linear_log_ASD(fflog, ff, np.real(TF))
        _, plotTFimag = linear_log_ASD(fflog, ff, np.imag(TF))
        plotTF = plotTFreal + 1j* plotTFimag
        #plotff, plotcoh = linear_log_ASD(fflog, ff, coh)
    else:
        plotff = ff
        plotTF = TF
        #plotcoh = coh

    s1.loglog(plotff, np.abs(plotTF), label=label)
    s2.semilogx(plotff, 180/np.pi*np.angle(plotTF))

    if newFig == True:
        s1.set_title(title)
        s2.set_yticks([-180, -90, 0, 90, 180])

        s1.set_xlim(xlims)
        s2.set_xlim(xlims)
        if ylims is not None:
            s1.set_ylim(ylims)

        s1.set_ylabel('Magnitude [%s]'%units)
        s2.set_ylabel('Phase [degrees]')
        s2.set_xlabel('Frequency [Hz]')

        s1.grid(which='major', ls='-')
        s2.grid(which='major', ls='-')
        s1.grid(which='minor', ls='--')
        s2.grid(which='minor', ls='--')

    s1.legend()
    plt.tight_layout()
    fig = make_legend_interactive(fig)
    plt.show()
    return fig

def bode_coh(ff,
             TF,
             coh,
             label='TF',
             title='Transfer Function',
             units='cts/cts',
             xlims=None,
             ylims=None,
             logbin=False,
             num_points=1000,
             fig=None ):
    '''
    Plots a very simple bode plot, with coherence.
    Run plt.ion() before for convenience.

    Inputs:
    ff     = frequency vector in Hz.
    TF     = array of complex numbers.  Represents the tranfer function for the bode plot.
    coh    = array of real numbers.  Represents the power coherence between the two channels.
    label  = str.  Legend label for the TF.  Default is 'TF'.
    title  = str.  Title of the figure.
    units  = str. Units for the y-axis.  Default is cts/cts.
    xlims  = array containing two floats.  x-axis limits on the plot.  Default is None.
    ylims  = array containing two floats.  y-axis limits on the plot.  Default is None.
    logbin      = bool.  If True, logbins the ASDs.  Default is False.
    num_points  = int.  If logbin == True, logbins using this number of points.  Default is 1000.
    fig    = matplotlib figure object upon which to make the plot.

    Output:
    fig = matplotlib figure object.
    '''
    newFig = False
    if xlims == None:
        xlims = [ff[1], ff[-1]]
    if fig == None:
        newFig = True
        fig = plt.figure(figsize=(16,12))
        s1 = fig.add_subplot(311)
        s2 = fig.add_subplot(312)
        s3 = fig.add_subplot(313)
    else:
        s1 = fig.get_axes()[0]
        s2 = fig.get_axes()[1]
        s3 = fig.get_axes()[2]

    if logbin:
        logf_low = ff[1]
        logf_high = ff[-1]
        fflog = np.logspace(np.log10(logf_low), np.log10(logf_high), num_points)
        _, plotTFreal = linear_log_ASD(fflog, ff, np.real(TF))
        _, plotTFimag = linear_log_ASD(fflog, ff, np.imag(TF))
        plotTF = plotTFreal + 1j* plotTFimag
        plotff, plotcoh = linear_log_ASD(fflog, ff, coh)
    else:
        plotff = ff
        plotTF = TF
        plotcoh = coh

    s1.loglog(plotff, np.abs(plotTF), label=label)
    s2.semilogx(plotff, 180/np.pi*np.angle(plotTF))
    s3.semilogx(plotff, plotcoh)

    if newFig == True:
        s1.set_title(title)
        s2.set_yticks([-180, -90, 0, 90, 180])

        s1.set_xlim(xlims)
        s2.set_xlim(xlims)
        s3.set_xlim(xlims)
        if ylims is not None:
            s1.set_ylim(ylims)

        s1.set_ylabel('Magnitude [%s]'%units)
        s2.set_ylabel('Phase [degrees]')
        s3.set_ylabel('Power Coherence')
        s3.set_xlabel('Frequency [Hz]')

        s1.grid(which='major', ls='-')
        s2.grid(which='major', ls='-')
        s3.grid(which='major', ls='-')
        s1.grid(which='minor', ls='--')
        s2.grid(which='minor', ls='--')
        s3.grid(which='minor', ls='--')

    s1.legend()
    plt.tight_layout()
    fig = make_legend_interactive(fig)
    plt.show()
    return fig

def bodes(ffs,
          TFs,
          labels=None,
          title='Transfer Function',
          units='cts/cts',
          xlims=None,
          ylims=None,
          logbin=False,
          num_points=1000,
          fig=None ):
    '''
    Plots a very simple bode plot for multiple TFs.
    Run plt.ion() before for convenience.

    Inputs:
    ffs    = vertically stacked frequency vectors in Hz.
             Use ffs = np.vstack((ff_1, ff_2, ..., ff_N)).
    TFs    = vertically stacked arrays of complex numbers.
             Represents the tranfer functions for the bode plot.
             Use TFs = np.vstack((TF_1, TF_2, ..., TF_N)).
    labels = str.  Legend labels for the TFs.  Default is None.
    title  = str.  Title of the figure.
    units  = str. Units for the magnitude y-axis.  Default is cts.
    xlims  = array containing two floats.  x-axis limits on the plot.  Default is None.
    ylims  = array containing two floats.  y-axis limits on the plot.  Default is None.
    logbin      = bool.  If True, logbins the ASDs.  Default is False.
    num_points  = int.  If logbin == True, logbins using this number of points.  Default is 1000.
    fig    = matplotlib figure object upon which to make the plot.

    Output:
    fig = matplotlib figure object.
    '''
    newFig = False
    if xlims == None:
        xlims = [ffs[0][1], ffs[0][-1]]
    if fig == None:
        newFig = True
        fig = plt.figure(figsize=(16,12))
        s1 = fig.add_subplot(211)
        s2 = fig.add_subplot(212)
    else:
        s1 = fig.get_axes()[0]
        s2 = fig.get_axes()[1]

    for ii, ff, TF in zip(np.arange(len(ffs)), ffs, TFs):
        if labels is not None:
            label = labels[ii]
        else:
            label = 'TF {}'.format(ii)

        if logbin:
            logf_low = ff[1]
            logf_high = ff[-1]
            fflog = np.logspace(np.log10(logf_low), np.log10(logf_high), num_points)
            _, plotTFreal = linear_log_ASD(fflog, ff, np.real(TF))
            _, plotTFimag = linear_log_ASD(fflog, ff, np.imag(TF))
            plotTF = plotTFreal + 1j* plotTFimag
            #plotff, plotcoh = linear_log_ASD(fflog, ff, coh)
        else:
            plotff = ff
            plotTF = TF
            #plotcoh = coh

        s1.loglog(plotff, np.abs(plotTF), label=label)
        s2.semilogx(plotff, 180/np.pi*np.angle(plotTF))

    if newFig == True:
        s1.set_title(title)
        s2.set_yticks([-180, -90, 0, 90, 180])

        s1.set_xlim(xlims)
        s2.set_xlim(xlims)
        if ylims is not None:
            s1.set_ylim(ylims)

        s1.set_ylabel('Magnitude [%s]'%units)
        s2.set_ylabel('Phase [degrees]')
        s2.set_xlabel('Frequency [Hz]')

        s1.grid(which='major', ls='-')
        s2.grid(which='major', ls='-')
        s1.grid(which='minor', ls='--')
        s2.grid(which='minor', ls='--')

    s1.legend()
    plt.tight_layout()
    fig = make_legend_interactive(fig)
    plt.show()
    return fig

def bodes_coh(ffs,
              TFs,
              cohs,
              labels=None,
              title='Transfer Function',
              units='cts/cts',
              xlims=None,
              ylims=None,
              logbin=False,
              num_points=1000,
              fig=None ):
    '''
    Plots a very simple bode plot for multiple TFs.
    Run plt.ion() before for convenience.

    Inputs:
    ffs    = vertically stacked frequency vectors in Hz.
             Use ffs = np.vstack((ff_1, ff_2, ..., ff_N)).
    TFs    = vertically stacked arrays of complex numbers.
             Represents the tranfer functions for the bode plot.
             Use TFs = np.vstack((TF_1, TF_2, ..., TF_N)).
    cohs   = vertically stacked power coherence vectors.
             Use cohs = np.vstack((coh_1, coh_2, ..., coh_N)).
    labels = str.  Legend labels for the TFs.  Default is None.
    title  = str.  Title of the figure.
    units  = str. Units for the magnitude y-axis.  Default is cts/cts.
    xlims  = array containing two floats.  x-axis limits on the plot.  Default is None.
    ylims  = array containing two floats.  y-axis limits on the plot.  Default is None.
    logbin      = bool.  If True, logbins the ASDs.  Default is False.
    num_points  = int.  If logbin == True, logbins using this number of points.  Default is 1000.
    fig    = matplotlib figure object upon which to make the plot.

    Output:
    fig = matplotlib figure object.
    '''
    newFig = False
    if xlims == None:
        xlims = [ffs[0][1], ffs[0][-1]]
    if fig == None:
        newFig = True
        fig = plt.figure(figsize=(16,12))
        s1 = fig.add_subplot(311)
        s2 = fig.add_subplot(312)
        s3 = fig.add_subplot(313)
    else:
        s1 = fig.get_axes()[0]
        s2 = fig.get_axes()[1]
        s3 = fig.get_axes()[2]

    for ii, ff, TF, coh in zip(np.arange(len(ffs)), ffs, TFs, cohs):
        if labels is not None:
            label = labels[ii]
        else:
            label = '{}'.format(ii)

        if logbin:
            logf_low = ff[1]
            logf_high = ff[-1]
            fflog = np.logspace(np.log10(logf_low), np.log10(logf_high), num_points)
            _, plotTFreal = linear_log_ASD(fflog, ff, np.real(TF))
            _, plotTFimag = linear_log_ASD(fflog, ff, np.imag(TF))
            plotTF = plotTFreal + 1j* plotTFimag
            plotff, plotcoh = linear_log_ASD(fflog, ff, coh)
        else:
            plotff = ff
            plotTF = TF
            plotcoh = coh

        s1.loglog(plotff, np.abs(plotTF), label=label)
        s2.semilogx(plotff, 180/np.pi*np.angle(plotTF))
        s3.semilogx(plotff, plotcoh)

    if newFig == True:
        s1.set_title(title)
        s2.set_yticks([-180, -90, 0, 90, 180])

        s1.set_xlim(xlims)
        s2.set_xlim(xlims)
        s3.set_xlim(xlims)
        if ylims is not None:
            s1.set_ylim(ylims)

        s1.set_ylabel('Magnitude [%s]'%units)
        s2.set_ylabel('Phase [degrees]')
        s3.set_ylabel('Coherent Power')
        s3.set_xlabel('Frequency [Hz]')

        s1.grid(which='major', ls='-')
        s2.grid(which='major', ls='-')
        s3.grid(which='major', ls='-')
        s1.grid(which='minor', ls='--')
        s2.grid(which='minor', ls='--')
        s3.grid(which='minor', ls='--')

    s1.legend()
    plt.tight_layout()
    fig = make_legend_interactive(fig)
    plt.show()
    return fig

def plot_ASDs(dataDict,
              plot_chans=None,
              label=None,
              title='Spectra',
              units='cts',
              xlims=None,
              ylims=None,
              cal_applied=True,
              logbin=False,
              num_points=1000,
              fig=None):
    '''
    Plots the ASDs in a dataDict from getPSDs() output.
    Automatically plots calibrated ASDs if available.
    Use plt.ion() for convenience.

    Inputs:
    dataDict    = data dictionary structure containing ASDs
    plot_chans  = array of channel names corresponding to the channels you want plotted.
                  If None, all channels are plotted.  Default is None.
    label       = str.  Tag on the end of the legend label for each plotted channel name.  Default is None.
    title       = str.  Title of the figure.
    units       = str. Units for the y-axis numerator (denominator is always rtHz).  Default is cts.
    xlims       = array containing two floats.  x-axis limits on the plot.  Default is None.
    ylims       = array containing two floats.  y-axis limits on the plot.  Default is None.
    cal_applied = bool.  If True, plots calibrated ASDs where possible.  Default is True.
    logbin      = bool.  If True, logbins the ASDs.  Default is False.
    num_points  = int.  If logbin == True, logbins using this number of points.  Default is 1000.
    fig         = matplotlib figure object upon which to make the plot.

    Output:
    fig = matplotlib figure object
    '''

    if np.sum(plot_chans == None):
        plot_chans = np.array(list(dataDict.keys()))

    newFig = False
    if fig is None:
        newFig = True
        fig = plt.figure(figsize=(16,12))
    else:
        axes = fig.gca()
        lines = axes.lines

    channels = dataDict.keys()
    for ii, chan in enumerate(channels):
        if chan not in plot_chans:
            continue

        alpha = 1.0
        ls = '-'
        if ii >= 30:
            alpha = 0.5
            ls = '--'
        elif ii >= 20:
            alpha = 1
            ls = '--'
        elif ii >= 10:
            alpha = 0.5
        #print chan
        ff = dataDict[chan]['ff']
        ASD = dataDict[chan]['ASD']

        if xlims == None:
            xlims = [ff[1], ff[-1]]

        if label == None:
            full_label = chan.replace('_', ' ')
        else:
            full_label = '{} {}'.format(chan.replace('_', ' '), label)

        if 'calFunc' in dataDict[chan].keys() and cal_applied==True:
            units = dataDict[chan]['calUnits']
            full_label = '{} [{}'.format(full_label, units) + r'/$\sqrt{\mathrm{Hz}}]$'
            calFunc = dataDict[chan]['calFunc']
            plotASD = ASD * np.abs(calFunc(ff))
        else:
            plotASD = ASD

        if logbin:
            logf_low = ff[1]
            logf_high = ff[-1]
            fflog = np.logspace(np.log10(logf_low), np.log10(logf_high), num_points)
            plotff, plotASD = linear_log_ASD(fflog, ff, plotASD)
        else:
            plotff = ff

        plt.loglog(plotff, plotASD, alpha=alpha, ls=ls, label=full_label)

    if xlims is not None:
        plt.xlim(xlims)
    if ylims is not None:
        plt.ylim(ylims)

    if newFig:
        plt.grid(which='major', ls='-')
        plt.grid(which='minor', ls='--')
        plt.title('{} - {}'.format(title, time.strftime('%b %d, %Y')))
        plt.xlabel('Frequency [Hz]')
        plt.ylabel('ASD [$\mathrm{%s}/\sqrt{\mathrm{Hz}}$]'%units)

    plt.legend()

    plt.tight_layout()
    fig = make_legend_interactive(fig)
    plt.show()
    return fig

def compare_ASDs(dataDict1,
                 dataDict2,
                 plot_chans=None,
                 label1=None,
                 label2=None,
                 title='Spectra',
                 units='cts',
                 xlims=None,
                 ylims=None,
                 cal_applied=True,
                 logbin=False,
                 num_points=1000,
                 fig=None):
    '''
    Plots the ASDs in dataDict1 and dataDict2 for quick comparison at two different times.
    Automatically plots calibrated ASDs if available.
    Use plt.ion() for convenience.

    Inputs:
    dataDict    = data dictionary structure containing ASDs
    plot_chans  = array of channel names corresponding to the channels you want plotted.
                  If None, all channels are plotted.  Default is None.
    label1  = str.  Tag on the end of the legend label for channels in dataDict1.  Default is None.
    label2  = str.  Tag on the end of the legend label for channels in dataDict2.  Default is None.
    title       = str.  Title of the figure.
    units       = str. Units for the y-axis numerator (denominator is always rtHz).  Default is cts.
    xlims       = array containing two floats.  x-axis limits on the plot.  Default is None.
    ylims       = array containing two floats.  y-axis limits on the plot.  Default is None.
    cal_applied = bool.  If True, plots calibrated ASDs where possible.  Default is True.
    logbin      = bool.  If True, logbins the ASDs.  Default is False.
    num_points  = int.  If logbin == True, logbins using this number of points.  Default is 1000.
    fig         = matplotlib figure object upon which to make the plot.

    Output:
    fig = matplotlib figure object
    '''

    if np.sum(plot_chans == None):
        plot_chans = np.array(list(dataDict1.keys()))

    newFig = False
    if fig is None:
        newFig = True
        fig = plt.figure(figsize=(16,12))
    else:
        axes = fig.gca()
        lines = axes.lines

    channels = dataDict1.keys()
    for ii, chan in enumerate(channels):
        if chan not in plot_chans:
            continue
        #print chan
        ff1  = dataDict1[chan]['ff']
        ASD1 = dataDict1[chan]['ASD']
        ff2  = dataDict2[chan]['ff']
        ASD2 = dataDict2[chan]['ASD']

        if xlims == None:
            xlims = [ff1[1], ff1[-1]]

        if label1 == None:
            full_label1 = chan.replace('_', ' ')
        else:
            full_label1 = '{} {}'.format(chan.replace('_', ' '), label1)
        if label2 == None:
            full_label2 = chan.replace('_', ' ')
        else:
            full_label2 = '{} {}'.format(chan.replace('_', ' '), label2)

        if 'calFunc' in dataDict1[chan].keys() and cal_applied==True:
            units = dataDict1[chan]['calUnits']
            full_label1 = '{} [{}/'.format(full_label1, units) + r'$\sqrt{\mathrm{Hz}}]$'
            calFunc = dataDict1[chan]['calFunc']
            plotASD1 = ASD1 * np.abs(calFunc(ff1))
        else:
            plotASD1 = ASD1

        if 'calFunc' in dataDict2[chan].keys() and cal_applied==True:
            units = dataDict2[chan]['calUnits']
            full_label2 = '{} [{}/'.format(full_label2, units) + r'$\sqrt{\mathrm{Hz}}]$'
            calFunc = dataDict2[chan]['calFunc']
            plotASD2 = ASD2 * np.abs(calFunc(ff2))
        else:
            plotASD2 = ASD2

        if logbin:
            logf_low = ff1[1]
            logf_high = ff1[-1]
            fflog = np.logspace(np.log10(logf_low), np.log10(logf_high), num_points)
            plotff1, plotASD1 = linear_log_ASD(fflog, ff1, plotASD1)
            plotff2, plotASD2 = linear_log_ASD(fflog, ff2, plotASD2)
        else:
            plotff1 = ff1
            plotff2 = ff2

        l1, = plt.loglog(plotff1, plotASD1, alpha=0.5, label=full_label1)
        l2, = plt.loglog(plotff2, plotASD2, color=l1.get_color(), label=full_label2)

    if xlims is not None:
        plt.xlim(xlims)
    if ylims is not None:
        plt.ylim(ylims)

    if newFig:
        plt.grid()
        plt.grid(which='minor', ls='--')
        plt.title('{} - {}'.format(title, time.strftime('%b %d, %Y')))
        plt.xlabel('Frequency [Hz]')
        plt.ylabel('ASD [$\mathrm{%s}/\sqrt{\mathrm{Hz}}$]'%units)

    plt.legend()

    plt.tight_layout()
    fig = make_legend_interactive(fig)
    plt.show()
    return fig

def plot_TF(dataDict,
            chanA,
            chanB,
            label=None,
            title='Spectra',
            units='cts/cts',
            xlims=None,
            ylims=None,
            cal_applied=True,
            logbin=False,
            num_points=1000,
            fig=None):
    '''
    Plots all the TFs in a data dictionary, always using chanA as the A channel for the TF.
    Will plot TF 1 = chanB1/chanA, TF 2 = chanB2/chanA, etc.
    Automatically plots calibrated TFs if available.
    Use plt.ion() for convenience.

    Inputs:
    dataDict    = data dictionary structure containing TFs
    chanA       = str. channel to be used as the A channel.  Must be a key in the above data dictionary.
    chanB       = str. channel to be used as the B channel.  Must be a key in the above data dictionary.
    plot_chans  = array of channel names corresponding to the channels you want plotted.
                  If None, all channels are plotted.  Default is None.
    label       = str.  Tag on the end of the legend label for each plotted channel name.  Default is None.
    title       = str.  Title of the figure.
    units       = str. Units for the y-axis numerator (denominator is always rtHz).  Default is cts/cts.
    xlims       = array containing two floats.  x-axis limits on the plot.  Default is None.
    ylims       = array containing two floats.  y-axis limits on the plot.  Default is None.
    cal_applied = bool.  If True, plots calibrated ASDs where possible.  Default is True.
    logbin      = bool.  If True, logbins the ASDs.  Default is False.
    num_points  = int.  If logbin == True, logbins using this number of points.  Default is 1000.
    fig         = matplotlib figure object upon which to make the plot.

    Output:
    fig = matplotlib figure object
    '''
    ff, TF, coh = quick_TF_grab(dataDict, chanA, chanB, calibrated=cal_applied)
    fig = bode_coh( ff,
                    TF,
                    coh,
                    label=label,
                    title=title,
                    units=units,
                    xlims=xlims,
                    ylims=ylims,
                    logbin=logbin,
                    num_points=num_points,
                    fig=fig )
    return fig


def plot_TFs_A(dataDict,
               chanA,
               plot_chans=None,
               label=None,
               title='Spectra',
               units='cts/cts',
               xlims=None,
               ylims=None,
               cal_applied=True,
               logbin=False,
               num_points=1000,
               num_figs=1,
               fig=None):
    '''
    Plots all the TFs in a data dictionary, always using chanA as the A channel for the TF.
    Will plot TF 1 = chanB1/chanA, TF 2 = chanB2/chanA, etc.
    Automatically plots calibrated TFs if available.
    Use plt.ion() for convenience.

    Inputs:
    dataDict    = data dictionary structure containing TFs
    chanA       = str. channel to be always be used as the A channel.  Must be a key in the above data dictionary.
    plot_chans  = array of channel names corresponding to the channels you want plotted.
                  If None, all channels are plotted.  Default is None.
    label       = str.  Tag on the end of the legend label for each plotted channel name.  Default is None.
    title       = str.  Title of the figure.
    units       = str. Units for the y-axis numerator (denominator is always rtHz).  Default is cts.
    xlims       = array containing two floats.  x-axis limits on the plot.  Default is None.
    ylims       = array containing two floats.  y-axis limits on the plot.  Default is None.
    cal_applied = bool.  If True, plots calibrated ASDs where possible.  Default is True.
    logbin      = bool.  If True, logbins the ASDs.  Default is False.
    num_points  = int.  If logbin == True, logbins using this number of points.  Default is 1000.
    num_figs    = int.  Chooses the number of figures to plot the TF and coherence.  Can be 1, 2, or 3.  Default is 1.
    fig         = matplotlib figure object (or tuple of figs in order, if num_figs > 1) upon which to make the plot.

    Output:
    fig = matplotlib figure object
    '''

    if np.sum(plot_chans == None):
        plot_chans = np.array(list(dataDict.keys()))

    newFig = False
    if fig is None:
        newFig = True
        if num_figs == 1:
            fig, (s1, s2, s3) = plt.subplots(3)
        elif num_figs == 2:
            fig1, (s1, s2) = plt.subplots(2)
            fig2, (s3) = plt.subplots(1)
        elif num_figs == 3:
            fig1, (s1) = plt.subplots(1)
            fig2, (s2) = plt.subplots(1)
            fig3, (s3) = plt.subplots(1)
        else:
            print()
            print('Invalid number of figures given! (num_figs = {})'.format(num_figs))
            print('Using one figure')
            fig, (s1, s2, s3) = plt.subplots(3)
    else:
        if num_figs == 1:
            s1, s2, s3 = fig.get_axes()
        elif num_figs == 2:
            s1, s2 = fig[0].get_axes()
            s3 = fig[1].get_axes()
        elif num_figs == 3:
            s1 = fig[0].get_axes()
            s2 = fig[1].get_axes()
            s3 = fig[2].get_axes()

    channels = dataDict.keys()
    for ii, chanB in enumerate(channels):
        if chanA == chanB:
            continue
        if chanB not in plot_chans:
            continue

        ff, TF, coh = quick_TF_grab(dataDict, chanA, chanB, calibrated=cal_applied)

        alpha = 1.0
        ls = '-'
        if ii >= 30:
            alpha = 0.5
            ls = '--'
        elif ii >= 20:
            alpha = 1
            ls = '--'
        elif ii >= 10:
            alpha = 0.5

        full_label = '{chanB}/A TF'.format(chanB=chanB)
        if cal_applied and 'calTF' in dataDict[chanB][chanA].keys():
            unitsA = 'cts'
            unitsB = 'cts'
            if 'calUnits' in dataDict[chanA].keys():
                unitsA = dataDict[chanA]['calUnits']
            if 'calUnits' in dataDict[chanB].keys():
                unitsB = dataDict[chanB]['calUnits']
            full_label = '{full_label} [{B}/{A}]'.format(full_label=full_label, B=unitsB, A=unitsA)
        if not label == None:
            full_label = '{full_label} {tag}'.format(full_label=full_label, tag=label)

        if logbin:
            logf_low = ff[1]
            logf_high = ff[-1]
            fflog = np.logspace(np.log10(logf_low), np.log10(logf_high), num_points)
            _, plotTFreal = linear_log_ASD(fflog, ff, np.real(TF))
            _, plotTFimag = linear_log_ASD(fflog, ff, np.imag(TF))
            plotTF = plotTFreal + 1j* plotTFimag
            plotff, plotcoh = linear_log_ASD(fflog, ff, coh)
        else:
            plotff = ff
            plotTF = TF
            plotcoh = coh

        s1.loglog(plotff, np.abs(plotTF), ls=ls, alpha=alpha, label=full_label)
        s2.semilogx(plotff, 180/np.pi*np.angle(plotTF), ls=ls, alpha=alpha, label=full_label)
        s3.semilogx(plotff, plotcoh, ls=ls, alpha=alpha, label=full_label)

    if title == None:
        full_title = 'TFs for A = {chanA}'.format(chanA=chanA)
    else:
        full_title = '{user_title}\nA = {chanA}'.format(user_title=title, chanA=chanA)

    if newFig == True:
        s2.set_yticks([-180, -90, 0, 90, 180])

        s1.set_xlim(xlims)
        s2.set_xlim(xlims)
        s3.set_xlim(xlims)
        if ylims is not None:
            s1.set_ylim(ylims)

        s1.set_ylabel('Magnitude [%s]'%units)
        s2.set_ylabel('Phase [degrees]')
        s3.set_ylabel('Coherent Power')

        if num_figs == 1:
            s1.set_title(full_title)
            s3.set_xlabel('Frequency [Hz]')
        elif num_figs == 2:
            s1.set_title(full_title)
            s2.set_xlabel('Frequency [Hz]')
            s3.set_title(full_title)
            s3.set_xlabel('Frequency [Hz]')
        elif num_figs == 3:
            s1.set_title(full_title)
            s1.set_xlabel('Frequency [Hz]')
            s2.set_title(full_title)
            s2.set_xlabel('Frequency [Hz]')
            s3.set_title(full_title)
            s3.set_xlabel('Frequency [Hz]')

        s1.grid(which='major', ls='-')
        s2.grid(which='major', ls='-')
        s3.grid(which='major', ls='-')
        s1.grid(which='minor', ls='--')
        s2.grid(which='minor', ls='--')
        s3.grid(which='minor', ls='--')

    if num_figs == 1:
        s1.legend(fontsize=12)
        fig.tight_layout()
        fig = make_legend_interactive(fig)
        fig_return = fig
    elif num_figs == 2:
        s1.legend(fontsize=12)
        s3.legend(fontsize=12)
        fig1.tight_layout()
        fig2.tight_layout()
        fig1 = make_legend_interactive(fig1)
        fig2 = make_legend_interactive(fig2)
        fig_return = (fig1, fig2)
    elif num_figs == 3:
        s1.legend(fontsize=12)
        s2.legend(fontsize=12)
        s3.legend(fontsize=12)
        fig1.tight_layout()
        fig2.tight_layout()
        fig3.tight_layout()
        fig1 = make_legend_interactive(fig1)
        fig2 = make_legend_interactive(fig2)
        fig3 = make_legend_interactive(fig3)
        fig_return = (fig1, fig2, fig3)
    # plt.tight_layout()
    plt.show()
    return fig_return

def plot_TFs_B(dataDict,
               chanB,
               plot_chans=None,
               label=None,
               title='Spectra',
               units='cts',
               xlims=None,
               ylims=None,
               cal_applied=True,
               logbin=False,
               num_points=1000,
               num_figs=1,
               fig=None):
    '''
    Plots all the TFs in a data dictionary, always using chanB as the B channel for the TF.
    Will plot TF 1 = chanB/chanA1, TF 2 = chanB/chanA2, etc.
    Automatically plots calibrated TFs if available.
    Use plt.ion() for convenience.

    Inputs:
    dataDict    = data dictionary structure containing TFs
    chanB       = str. channel to be always be used as the B channel.  Must be a key in the above data dictionary.
    plot_chans  = array of channel names corresponding to the channels you want plotted.
                  If None, all channels are plotted.  Default is None.
    label       = str.  Tag on the end of the legend label for each plotted channel name.  Default is None.
    title       = str.  Title of the figure.
    units       = str. Units for the y-axis numerator (denominator is always rtHz).  Default is cts.
    xlims       = array containing two floats.  x-axis limits on the plot.  Default is None.
    ylims       = array containing two floats.  y-axis limits on the plot.  Default is None.
    cal_applied = bool.  If True, plots calibrated ASDs where possible.  Default is True.
    logbin      = bool.  If True, logbins the ASDs.  Default is False.
    num_points  = int.  If logbin == True, logbins using this number of points.  Default is 1000.
    fig         = matplotlib figure object (or tuple of figs in order, if num_figs > 1) upon which to make the plot.

    Output:
    fig = matplotlib figure object
    '''

    if np.sum(plot_chans == None):
        plot_chans = np.array(list(dataDict.keys()))

    newFig = False
    if fig is None:
        newFig = True
        if num_figs == 1:
            fig, (s1, s2, s3) = plt.subplots(3)
        elif num_figs == 2:
            fig1, (s1, s2) = plt.subplots(2)
            fig2, (s3) = plt.subplots(1)
        elif num_figs == 3:
            fig1, (s1) = plt.subplots(1)
            fig2, (s2) = plt.subplots(1)
            fig3, (s3) = plt.subplots(1)
        else:
            print()
            print('Invalid number of figures given! (num_figs = {})'.format(num_figs))
            print('Using one figure')
            fig, (s1, s2, s3) = plt.subplots(3)
    else:
        if num_figs == 1:
            s1, s2, s3 = fig.get_axes()
        elif num_figs == 2:
            s1, s2 = fig[0].get_axes()
            s3 = fig[1].get_axes()
        elif num_figs == 3:
            s1 = fig[0].get_axes()
            s2 = fig[1].get_axes()
            s3 = fig[2].get_axes()

    channels = dataDict.keys()
    for ii, chanA in enumerate(channels):
        if chanA == chanB:
            continue
        if chanA not in plot_chans:
            continue

        ff, TF, coh = quick_TF_grab(dataDict, chanA, chanB, calibrated=cal_applied)

        alpha = 1.0
        ls = '-'
        if ii >= 30:
            alpha = 0.5
            ls = '--'
        elif ii >= 20:
            alpha = 1
            ls = '--'
        elif ii >= 10:
            alpha = 0.5

        full_label = 'B/{chanA} TF'.format(chanA=chanA)
        if cal_applied and 'calTF' in dataDict[chanB][chanA].keys():
            unitsA = 'cts'
            unitsB = 'cts'
            if 'calUnits' in dataDict[chanA].keys():
                unitsA = dataDict[chanA]['calUnits']
            if 'calUnits' in dataDict[chanB].keys():
                unitsB = dataDict[chanB]['calUnits']
            full_label = '{full_label} [{B}/{A}]'.format(full_label=full_label, B=unitsB, A=unitsA)
        if not label == None:
            full_label = '{full_label} {tag}'.format(full_label=full_label, tag=label)

        if logbin:
            logf_low = ff[1]
            logf_high = ff[-1]
            fflog = np.logspace(np.log10(logf_low), np.log10(logf_high), num_points)
            _, plotTFreal = linear_log_ASD(fflog, ff, np.real(TF))
            _, plotTFimag = linear_log_ASD(fflog, ff, np.imag(TF))
            plotTF = plotTFreal + 1j* plotTFimag
            plotff, plotcoh = linear_log_ASD(fflog, ff, coh)
        else:
            plotff = ff
            plotTF = TF
            plotcoh = coh

        s1.loglog(plotff, np.abs(plotTF), ls=ls, alpha=alpha, label=full_label)
        s2.semilogx(plotff, 180/np.pi*np.angle(plotTF), ls=ls, alpha=alpha, label=full_label)
        s3.semilogx(plotff, plotcoh, ls=ls, alpha=alpha, label=full_label)

    if title == None:
        full_title = 'TFs for B = {chanB}'.format(chanB=chanB)
    else:
        full_title = '{user_title}\nB = {chanB}'.format(user_title=title, chanB=chanB)

    if newFig == True:
        s2.set_yticks([-180, -90, 0, 90, 180])

        s1.set_xlim(xlims)
        s2.set_xlim(xlims)
        s3.set_xlim(xlims)
        if ylims is not None:
            s1.set_ylim(ylims)

        s1.set_ylabel('Magnitude [%s]'%units)
        s2.set_ylabel('Phase [degrees]')
        s3.set_ylabel('Coherent Power')

        if num_figs == 1:
            s1.set_title(full_title)
            s3.set_xlabel('Frequency [Hz]')
        elif num_figs == 2:
            s1.set_title(full_title)
            s2.set_xlabel('Frequency [Hz]')
            s3.set_title(full_title)
            s3.set_xlabel('Frequency [Hz]')
        elif num_figs == 3:
            s1.set_title(full_title)
            s1.set_xlabel('Frequency [Hz]')
            s2.set_title(full_title)
            s2.set_xlabel('Frequency [Hz]')
            s3.set_title(full_title)
            s3.set_xlabel('Frequency [Hz]')

        s1.grid(which='major', ls='-')
        s2.grid(which='major', ls='-')
        s3.grid(which='major', ls='-')
        s1.grid(which='minor', ls='--')
        s2.grid(which='minor', ls='--')
        s3.grid(which='minor', ls='--')

    if num_figs == 1:
        s1.legend(fontsize=12)
        fig.tight_layout()
        fig = make_legend_interactive(fig)
        fig_return = fig
    elif num_figs == 2:
        s1.legend(fontsize=12)
        s3.legend(fontsize=12)
        fig1.tight_layout()
        fig2.tight_layout()
        fig1 = make_legend_interactive(fig1)
        fig2 = make_legend_interactive(fig2)
        fig_return = (fig1, fig2)
    elif num_figs == 3:
        s1.legend(fontsize=12)
        s2.legend(fontsize=12)
        s3.legend(fontsize=12)
        fig1.tight_layout()
        fig2.tight_layout()
        fig3.tight_layout()
        fig1 = make_legend_interactive(fig1)
        fig2 = make_legend_interactive(fig2)
        fig3 = make_legend_interactive(fig3)
        fig_return = (fig1, fig2, fig3)
    # plt.tight_layout()
    plt.show()
    return fig_return

def plot_raw_data(dataDict,
                  seconds=1,
                  downsample=1,
                  title='Raw Data',
                  units='cts',
                  fig=None ):
    '''
    Plots the time series data in a dataDict.
    Be careful that you plot only a resonable amount of seconds, 1 second will plot 16384 data points per channel.
    If you really want the whole data, set seconds=None.
    Use plt.ion() for convenience.

    Inputs:
    dataDict   = data dictionary structure containing raw data.
    seconds    = float.  Number of seconds of data to plot.  Default is 1 second.
                 Be careful not to plot too much without downsampling, this can make the plot slow.
    downsample = int.  Ratio at which to downsample the data.  Default is 1.
                 For example, downsample=2 will remove every other data point.
    title      = str.  Title of the figure.
    units      = str. Units for the y-axis.  Default is cts.
    fig        = matplotlib figure object upon which to make the plot.

    Output:
    fig = matplotlib figure object

    ### Example ###

    import numpy as np
    import nds2utils
    import nds2utils.dataUtils as du
    import nds2utils.plotUtils as pu

    channels = np.array(['H1:CAL-DELTAL_EXTERNAL_DQ', 'H1:PSL-ISS_SECONDLOOP_RIN_OUTER_OUT_DQ'])
    gps_start = 1256805122
    gps_stop  = 1256805222
    binwidth = 1.0 # Hz
    overlap = 0.25
    dataDict = du.getCSDs(channels, gps_start, gps_stop, binwidth, overlap)

    import matplotlib.pyplot as plt
    plt.ion()
    fig = pu.plot_raw_data(dataDict, seconds=12.3, downsample=2**10)

    '''
    newFig = False
    if fig is None:
        newFig = True
        fig = plt.figure(figsize=(16,12))
    else:
        axes = fig.gca()
        lines = axes.lines
    #print(newFig)

    channels = list(dataDict.keys())
    subplots = np.array([])
    for ii, chan in enumerate(channels):
        #print chan
        fs = dataDict[chan]['fs']
        if seconds == None:
            index = -1
        else:
            index = int(seconds * fs)

        # Get the correct amount of time
        # times = dataDict[chan]['times'][:index]
        times = np.arange(len(dataDict[chan]['data']))/float( dataDict[chan]['fs'] )
        times = times[:index]
        data = dataDict[chan]['data'][:index]

        # Downsample the plotted data
        times = times[::downsample]
        data = data[::downsample]

        label = chan.replace('_', ' ')

        ss = fig.add_subplot(len(channels), 1, ii+1)
        ss.plot(times, data, label=label)
        subplots = np.append(subplots, ss)

    if newFig:
        for ss in subplots:
            ss.grid(which='major', ls='-')
            ss.grid(which='minor', ls='--')
            ss.set_ylabel('Raw Data [%s]'%units)
            ss.legend()
        subplots[0].set_title('{} - {}'.format(title, time.strftime('%b %d, %Y')))
        subplots[-1].set_xlabel('Time [s]')

    plt.tight_layout()
    fig = make_legend_interactive(fig)
    plt.show()
    return fig

def make_legend_interactive(fig):
    '''
    Takes in a figure, finds the lines drawn on the plot, and makes them togglable from the legend.
    Must be done before plt.show() is run, it seems...
    Taken from https://matplotlib.org/examples/event_handling/legend_picking.html

    Inputs:
    fig = matplotlib figure object.

    Output:
    fig = same matplotlib figure object, this time with a clickable legend which toggles that line visible or not.
    '''
    ss = fig.get_axes()
    legends = np.array([])
    for s in ss:
        if s.get_legend() is not None:
            legends = np.append(legends, s.get_legend())

    num_legends = len(legends)
    lined = {}
    if num_legends == 1: # If there's only one legend, then we want all subplots to be turned on/off with each click
        leg = legends[0]
        leglines = leg.get_lines()

        for ii, legline in enumerate(leglines):
            legline.set_picker(5)  # 5 pts tolerance
            temp_lines = np.array([])
            for jj, s in enumerate(ss):
                try:
                    temp_lines = np.append(temp_lines, s.lines[ii])
                except IndexError:
                    continue # do nothing
                    #print('No line {ii} on subplot {jj}'.format(ii=ii, jj=jj))
            lined[legline] = temp_lines
    else: # if there's multiple legends, then we want each legend to correspond only to it's own subplot
        for s in ss:
            leg = s.get_legend()
            leglines = leg.get_lines()
            for ii, legline in enumerate(leglines):
                legline.set_picker(5)  # 5 pts tolerance
                lined[legline] = np.array([s.lines[ii]])

    # num_axes = len(ss)
    # s1 = ss[0]  # Assume that the legend is always on the first subplot here
    # leg = s1.legend()
    #
    # if num_axes == 1:
    #     lines = np.vstack((ss[0].lines))
    # elif num_axes == 2:
    #     lines = np.vstack((ss[0].lines, ss[1].lines)).T
    # elif num_axes == 3:
    #     lines = np.vstack((ss[0].lines, ss[1].lines, ss[2].lines)).T
    #
    # lined = {}
    # for legline, origlines in zip(leg.get_lines(), lines):
    #
    #     lined[legline] = origlines

    def onpick(event):
        # on the pick event, find the orig line corresponding to the
        # legend proxy line, and toggle the visibility
        legline = event.artist
        origlines = lined[legline]
        for origline in origlines:
            vis = not origline.get_visible()
            origline.set_visible(vis)
        # Change the alpha on the line in the legend so we can see what lines
        # have been toggled
        alpha = origline.get_alpha()
        if vis:
            legline.set_alpha(alpha)
        else:
            legline.set_alpha(0.1)
        fig.canvas.draw()

    fig.canvas.mpl_connect('pick_event', onpick)

    return fig
