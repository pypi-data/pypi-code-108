#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 11:25:44 2020

@author: benjamin
"""

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import scipy.spatial as ssp

# Customize matplotlib
matplotlib.rcParams.update({'text.usetex': True,
                            'text.latex.preamble': '\\usepackage{tipa}'})
FONT_SIZE = 20
def set_ticks(fs=FONT_SIZE):
    plt.xticks(fontsize=fs)
    plt.yticks(fontsize=fs)

def special_characters(x):
    y = x
    y = y.replace("x", "\\textipa{@}")
    y = y.replace("#", "\#")
    y = y.replace("_", "\_")
    #y = y.replace("~", "\~")
    y = y.replace("Z", "\\textipa{Z}")
    y = y.replace("S", "\\textipa{S}")
    y = y.replace("O", "\\textipa{O}")
    y = y.replace("^", "\\textipa{2}")
    y = y.replace("I", "\\textipa{I}")
       
    if "~" in y:
       y = y.replace("~", "")
       y = "\\textipa{\~" + y + "}"
    return y

def plot_segmentation(ax, lbl, inst, limy):
    for k in range(len(lbl)):
        ax.plot(inst[k,1] * np.ones((2,1)), limy,
             linestyle='--', color=[ 0, 0.498, 0 ], linewidth=1)
        plt.text(np.mean(inst[k,:]), limy[1], special_characters(lbl[k]),
            color=[ 0, 0.498, 0 ], fontsize=20, fontweight='bold',
            horizontalalignment='center', verticalalignment='top')

def extents(f):
    delta = f[1] - f[0]
    return [f[0] - delta / 2, f[-1] + delta / 2]

def plot_tf(freq, tf, sl=None, hf=None):

    if hf is None:
        h_out = plt.figure()
    else:
        # h_out = plt.figure(hf)
        plt.figure(hf.number)
        h_out = hf
    
    if sl is not None or len(tf.squeeze().shape) == 1:        
        if sl is not None:
            tf = tf[:, sl]
        plt.semilogy(freq, abs(tf))
        plt.xlabel('Frequency (Hz)', fontsize=FONT_SIZE, fontweight='bold')
        plt.ylabel('Transfer function', fontsize=FONT_SIZE, fontweight='bold')
        set_ticks()

    return h_out

def plot_spec(Pxx, tsp, fsp, dyn, tvec, signal, lbl, inst,
              pitch_plot, pitch_time_points, pitch_values,
              formant_plot, formants_time, formants_freq):

    pmax = np.max(Pxx)
    pmaxmclim = pmax-dyn

    fig_handle = plt.figure()
    gs = fig_handle.add_gridspec(3, 1)
    ax1 = fig_handle.add_subplot(gs[:2, 0])
    ax1.set_title('Spectrogram', fontsize=FONT_SIZE, fontweight='bold')
    plt.imshow(Pxx, aspect='auto', interpolation='none',
               extent=extents(tsp)+extents(fsp), origin='lower',
               clim=(pmaxmclim,pmax), cmap="gray_r")
    plt.ylabel('Frequency (Hz)', fontsize=FONT_SIZE, fontweight='bold')
    plt.xlabel('Time (s)', fontsize=FONT_SIZE, fontweight='bold')
    plt.xlim([0, max(tvec)])
    set_ticks()
    if lbl is not None:
        plot_segmentation(ax1, lbl[0], inst[0], [0, max(fsp)])
    if pitch_plot:
        ax1.plot(pitch_time_points, pitch_values, color='b', linewidth=3)
    if formant_plot:
        ax1.plot(formants_time, formants_freq, linewidth=2)
    # plt.show()
    # plt.ion()

    ax2 = fig_handle.add_subplot(gs[-1, 0], sharex=ax1)
    ax2.set_title('Signal', fontsize=FONT_SIZE, fontweight='bold')

    plt.plot(tvec, signal)
    plt.xlabel('Time (s)', fontsize=FONT_SIZE, fontweight='bold')
    plt.xlim([0, max(tvec)])
    miny = min(signal) * 1.1
    maxy = max(signal) * 1.1
    if lbl is not None:
        plot_segmentation(ax2, lbl[0], inst[0], [ -1e3,1e3 ])
    plt.ylim([miny, maxy])
    set_ticks()
    return fig_handle

def freq_plot(freq, Pxx, dyn):

    max_Pxx = np.max(abs(Pxx))
    fig_handle = plt.figure()
    plt.plot(freq, 10*np.log10(np.abs(Pxx)))
    plt.ylabel('Spectrum (dB)', fontsize=FONT_SIZE, fontweight='bold')
    plt.xlabel('Frequency (Hz)', fontsize=FONT_SIZE, fontweight='bold')
    plt.ylim([10*np.log10(np.abs(max_Pxx))-dyn, 10*np.log10(np.abs(max_Pxx))])
    plt.xlim([0, max(freq)])
    set_ticks()

    return fig_handle

def vowel_space(fk, n1=1, n2=2, h=None, k_plot=None):

    n = [n1-1, n2-1]
    convHull = ssp.ConvexHull(fk[n,:].T)

    if h is None:
        h = plt.figure()
        ax1 = plt.subplot(111)
    elif k_plot is not None:
        ax1 = plt.subplot(4, 4, k_plot)
    elif k_plot is None:
        ax1 = plt.subplot(111)

    plt.figure(h.number)
    ax1.plot(fk[n1-1, :], fk[n2-1, :], '.')
    # ax1.plot(fk[n1-1, convHull.simplices[:, 0]],
    #          fk[n2-1, convHull.simplices[:,1]], 'r')
    for simplex in convHull.simplices:
        ax1.plot(fk[n1-1, simplex], fk[n2-1, simplex],
                 'r', linewidth=2)
    plt.ylabel('$F' + str(n2) +'$', fontsize=FONT_SIZE, fontweight='bold')
    plt.xlabel('$F' + str(n1) +'$', fontsize=FONT_SIZE, fontweight='bold')
    set_ticks()
    ax1.set_title('$F' + str(n1) +'-F' + str(n2) + '$ space',
                  fontsize=FONT_SIZE, fontweight='bold')

    return h, ax1

def plot_area(xval, yval, hf=None):

    if hf is None:
        h_out = plt.figure()
    else:
        h_out = hf
        plt.figure(hf.number)
    plt.plot(xval, yval)
    plt.xlabel('Distance from input (cm)', fontsize=FONT_SIZE, fontweight='bold')
    plt.ylabel('Area (cm\\textsuperscript{2})', fontsize=FONT_SIZE, fontweight='bold')
    set_ticks()
    
    return h_out

def pitch_plot(tp, y_pitch, y_contour, spl_tp, spl_v, parent=None):

    h = plt.figure()
    ax = h.add_subplot(111)
    plt.plot(tp, y_pitch)
    plt.plot(tp, y_contour)

    plt.xlabel('Time (s)', fontsize=FONT_SIZE, fontweight='bold')
    plt.ylabel('Pitch (Hz)', fontsize=FONT_SIZE, fontweight='bold')
    set_ticks()
    if spl_tp is not None:
        plt.plot(spl_tp, spl_v)
        
    if parent is not None:
        if parent.phonetic_labels is not None:
            lbl = parent.phonetic_labels[0]
            inst = parent.phonetic_instants[0]
            limy = [0, np.max(np.abs(y_pitch))]
            plot_segmentation(ax, lbl, inst, limy)

    return h

def contour_plot(tvec, y, tp, yI, parent=None):

    h = plt.figure()
    ax = h.add_subplot(111)
    plt.plot(tvec, y)
    plt.plot(tp, yI)
    plt.xlabel('Time (s)', fontsize=FONT_SIZE, fontweight='bold')
    plt.ylabel('Intensity (Lin)', fontsize=FONT_SIZE, fontweight='bold')
    set_ticks()
    if parent is not None:
        if parent.phonetic_labels is not None:
            lbl = parent.phonetic_labels[0]
            inst = parent.phonetic_instants[0]
            limy = [-np.max(np.abs(y)), np.max(np.abs(y))]
            plot_segmentation(ax, lbl, inst, limy)
            
    return h

def addplot(ax, tvec, y, color='r', lst='solid', lnw=2):
    ax.plot(tvec, y, color=color, linestyle=lst, linewidth=lnw)

def subplot_param(subax, tvec, y, lbl, inst, limy,
                  title, ylabel, xlabel=None, limx=None, ax_share=None):

    if ax_share is None:
        ax = plt.subplot(subax)
    else:
        ax = plt.subplot(subax, sharex=ax_share)
    ax.plot(tvec, y, linewidth=2)
    plt.title(title, fontsize=FONT_SIZE, fontweight='bold')
    plt.ylabel(ylabel, fontsize=FONT_SIZE, fontweight='bold')
    set_ticks()
    if xlabel is not None:
        plt.xlabel(xlabel, fontsize=FONT_SIZE, fontweight='bold')
    miny = min([min(y) * 1.1, 0])
    maxy = min([limy[1], max(y) * 1.1])

    plot_segmentation(ax, lbl, inst, [miny, maxy])
    plt.ylim([miny, maxy])
    if plt.xlim is not None:
        plt.xlim(limx)

    return ax

def formantspace(objForm, subax, h=None, clr='b', order=1):

    if h is None:
        h = openfig()
    else:
        plt.figure(h.number)
    k_iter = 0

    for k1 in range(4):
        h, axTmp = pdfplot(objForm.stats[k1], n1=(k1+1),
                          subax=k1*5+1, hf=h, clr=clr)
        if order == 1:
            for k2 in range(k1):
                if k1 != k2:
                    h, axTmp = vowel_space(objForm.frequency, n1=(k2+1), n2=(k1+1),
                                  h=h, k_plot=subax[k_iter])
                    # ax.append(axTmp)
                    k_iter += 1
        else:
            for k2 in range(k1+1, 4):
                if k1 != k2:
                    h, axTmp = vowel_space(objForm.frequency, n1=(k1+1), n2=(k2+1),
                                  h=h, k_plot=subax[k_iter])
                    # ax.append(axTmp)
                    k_iter += 1

    return h

def hull_plot(fk, n1=1, n2=2, h=None, k_plot=None, clr='b'):
    
    n = [n1-1, n2-1]
    convHull = ssp.ConvexHull(fk[n,:].T)

    if h is None:
        h = plt.figure()
        ax1 = plt.subplot(111)
    elif k_plot is not None:
        ax1 = plt.subplot(3, 3, k_plot)
    elif k_plot is None:
        ax1 = plt.subplot(111)

    plt.figure(h.number)
    for simplex in convHull.simplices:
        ax1.plot(fk[n1-1, simplex], fk[n2-1, simplex],
                 color=clr, linewidth=2)
    plt.ylabel('$F' + str(n2) +'$', fontsize=FONT_SIZE, fontweight='bold')
    plt.xlabel('$F' + str(n1) +'$', fontsize=FONT_SIZE, fontweight='bold')
    ax1.set_title('$F' + str(n1) +'-F' + str(n2) + '$ space',
                  fontsize=FONT_SIZE, fontweight='bold')

    return convHull.area

def hull_compare(objForm_1, objForm_2):
    
    h = openfig()
    k_iter = 1
    a_1 = []
    a_2 = []
    for k1 in range(4):
        for k2 in range(k1):
            if k1 != k2:
                a_1.append(hull_plot(objForm_1.frequency, n1=(k2+1), n2=(k1+1),
                              h=h, k_plot=k_iter))
                a_2.append(hull_plot(objForm_2.frequency, n1=(k2+1), n2=(k1+1),
                              h=h, k_plot=k_iter, clr='r')) 
                k_iter += 1
            
    barWidth = 0.4
    axTmp = plt.subplot(3,1,3)
    r1 = range(6)
    r2 = [x + barWidth for x in r1]
    axTmp.bar(r1, a_1, color='b', width = barWidth)
    axTmp.bar(r2, a_2, color='r', width = barWidth)
    plt.xticks([r + barWidth / 2 for r in range(6)],
                      ['$F_1-F_2$', '$F_1-F_3$', '$F_1-F_4$', 
                       '$F_2-F_3$', '$F_2-F_4$', '$F_3-F_4$'])
    plt.ylabel('Hull area (Hz\\textsuperscript{2})')

def pdfplot(x, n1, subax=None, hf=None, clr='b'):

    if hf is None:
        h_out = plt.figure()
    else:
        h_out = hf
        plt.figure(hf.number)

    if subax is not None:
        ax = plt.subplot(4,4,subax)
    else:
        ax = plt.subplot(111)
    ax.plot(x.bins[:-1], x.pdf, linewidth=2, color=clr)
    plt.ylabel('PDF($F_' + str(n1) + '$)', fontsize=FONT_SIZE, fontweight='bold')
    plt.xlabel('$F_' + str(n1) + '$ (Hz)', fontsize=FONT_SIZE, fontweight='bold')

    return h_out, ax

def formant_stats(objForm, obj2compare=None, label=None):

    h = openfig()
    barWidth = 0.4
    ylbl = ['Mean (Hz)', 'Variance (Hz\\textsuperscript{2})', 
            'Skewness', 'Kurtosis']

    for k in range(4):
        ax = plt.subplot(5,4,k+1)
        if obj2compare is not None:
            ax.boxplot([objForm.stats[k].samples, obj2compare.stats[k].samples],
                       notch=True)
        else:
            ax.boxplot(objForm.stats[k].samples, notch=True)
        plt.ylabel('$F_' + str(k+1) + '$ (Hz)', fontsize=FONT_SIZE, fontweight='bold')
        if label is not None:
            plt.gca().xaxis.set_ticklabels(label)
    for k1 in range(4):
        momTmp = []
        momTmp_2 = []
        for k2 in range(4):
            momTmp.append(objForm.stats[k2].moments[k1])
            if obj2compare is not None:
                momTmp_2.append(obj2compare.stats[k2].moments[k1])
        axTmp = plt.subplot(5,1,k1+2)
        r1 = range(4)
        axTmp.bar(r1, momTmp, color='b', width = barWidth)
        if obj2compare is not None:
            r2 = [x + barWidth for x in r1]
            axTmp.bar(r2, momTmp_2, color='r', width = barWidth)
        plt.xticks([r + barWidth / 2 for r in range(4)],
                      ['$F_1$', '$F_2$', '$F_3$', '$F_4$'])
        plt.ylabel(ylbl[k1])


    return h

def openfig():
    return plt.figure()