"""
DeepLabCut2.0 Toolbox (deeplabcut.org)
© A. & M. Mathis Labs
https://github.com/AlexEMG/DeepLabCut

Please see AUTHORS for contributors.
https://github.com/AlexEMG/DeepLabCut/blob/master/AUTHORS
Licensed under GNU Lesser General Public License v3.0
"""

import argparse
import os

####################################################
# Dependencies
####################################################
import os.path
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from openlabcluster.utils import auxiliaryfunctions, visualization

def format_axes(axes: plt.Axes):
    font = {
        'family': 'sans-serif',
        'color': 'firebrick',
        'weight': 'normal',
        'size': 16,
    }
    axes_font = {
        'family': 'sans-serif',
        'color': 'black',
        'weight': 'normal',
        'size': 10,
    }

    axes.set_xlabel('Dimension 1' , fontdict=axes_font)
    axes.set_ylabel('Dimension 2' , fontdict=axes_font)
    # figure.axes.tick_params(labelsize=10)
    plt.setp(axes.get_yticklabels(), fontweight="normal", size=10)
    plt.setp(axes.get_xticklabels(), fontweight="normal", size=10)
    axes.set_title(axes.get_title(), fontdict=font)
    axes.set_xlim([-10,20])
    axes.set_ylim([-10,20])

    axes.autoscale()


def Histogram(vector, color, bins, ax=None, linewidth=1.0):
    dvector = np.diff(vector)
    dvector = dvector[np.isfinite(dvector)]
    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111)
    ax.hist(dvector, color=color, histtype="step", bins=bins, linewidth=linewidth)


def PlottingResults(
    tmpfolder,
    Dataframe,
    cfg,
    bodyparts2plot,
    individuals2plot,
    showfigures=False,
    suffix=".png",
    resolution=100,
    linewidth=1.0,
):
    """ Plots poses vs time; pose x vs pose y; histogram of differences and likelihoods."""
    pcutoff = cfg["pcutoff"]
    colors = visualization.get_cmap(len(bodyparts2plot), name=cfg["colormap"])
    alphavalue = cfg["alphavalue"]
    if individuals2plot:
        Dataframe = Dataframe.loc(axis=1)[:, individuals2plot]
    animal_bpts = Dataframe.columns.get_level_values("bodyparts")
    # Pose X vs pose Y
    fig1 = plt.figure(figsize=(8, 6))
    ax1 = fig1.add_subplot(111)
    ax1.set_xlabel("X position in pixels")
    ax1.set_ylabel("Y position in pixels")
    ax1.invert_yaxis()

    # Poses vs time
    fig2 = plt.figure(figsize=(10, 3))
    ax2 = fig2.add_subplot(111)
    ax2.set_xlabel("Frame Index")
    ax2.set_ylabel("X-(dashed) and Y- (solid) position in pixels")

    # Likelihoods
    fig3 = plt.figure(figsize=(10, 3))
    ax3 = fig3.add_subplot(111)
    ax3.set_xlabel("Frame Index")
    ax3.set_ylabel("Likelihood (use to set pcutoff)")

    # Histograms
    fig4 = plt.figure()
    ax4 = fig4.add_subplot(111)
    ax4.set_ylabel("Count")
    ax4.set_xlabel("DeltaX and DeltaY")
    bins = np.linspace(0, np.amax(Dataframe.max()), 100)

    with np.errstate(invalid="ignore"):
        for bpindex, bp in enumerate(bodyparts2plot):
            if (
                bp in animal_bpts
            ):  # Avoid 'unique' bodyparts only present in the 'single' animal
                prob = Dataframe.xs(
                    (bp, "likelihood"), level=(-2, -1), axis=1
                ).values.squeeze()
                mask = prob < pcutoff
                temp_x = np.ma.array(
                    Dataframe.xs((bp, "x"), level=(-2, -1), axis=1).values.squeeze(),
                    mask=mask,
                )
                temp_y = np.ma.array(
                    Dataframe.xs((bp, "y"), level=(-2, -1), axis=1).values.squeeze(),
                    mask=mask,
                )
                ax1.plot(temp_x, temp_y, ".", color=colors(bpindex), alpha=alphavalue)

                ax2.plot(
                    temp_x,
                    "--",
                    color=colors(bpindex),
                    linewidth=linewidth,
                    alpha=alphavalue,
                )
                ax2.plot(
                    temp_y,
                    "-",
                    color=colors(bpindex),
                    linewidth=linewidth,
                    alpha=alphavalue,
                )

                ax3.plot(
                    prob,
                    "-",
                    color=colors(bpindex),
                    linewidth=linewidth,
                    alpha=alphavalue,
                )

                Histogram(temp_x, colors(bpindex), bins, ax4, linewidth=linewidth)
                Histogram(temp_y, colors(bpindex), bins, ax4, linewidth=linewidth)

    sm = plt.cm.ScalarMappable(
        cmap=plt.get_cmap(cfg["colormap"]),
        norm=plt.Normalize(vmin=0, vmax=len(bodyparts2plot) - 1),
    )
    sm._A = []
    for ax in ax1, ax2, ax3, ax4:
        cbar = plt.colorbar(sm, ax=ax, ticks=range(len(bodyparts2plot)))
        cbar.set_ticklabels(bodyparts2plot)

    fig1.savefig(
        os.path.join(tmpfolder, "trajectory" + suffix),
        bbox_inches="tight",
        dpi=resolution,
    )
    fig2.savefig(
        os.path.join(tmpfolder, "plot" + suffix), bbox_inches="tight", dpi=resolution
    )
    fig3.savefig(
        os.path.join(tmpfolder, "plot-likelihood" + suffix),
        bbox_inches="tight",
        dpi=resolution,
    )
    fig4.savefig(
        os.path.join(tmpfolder, "hist" + suffix), bbox_inches="tight", dpi=resolution
    )

    if not showfigures:
        plt.close("all")
    else:
        plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config")
    parser.add_argument("video")
    cli_args = parser.parse_args()
