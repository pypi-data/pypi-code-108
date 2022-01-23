from os import PathLike
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# from sklearn.tree import DecisionTreeClassifier
# from sklearn import metrics
from scorem import starHandler


def occupancyPlot(starFileIn: PathLike, numBins):
 Phi=starHandler.readColumns(starFileIn, ['_rlnAngleRot'])
 Theta=starHandler.readColumns(starFileIn, ['_rlnAngleTilt'])
 eulers1=(Phi.to_numpy()).reshape((len(Phi),))*np.pi/180.0
 eulers2=(Theta.to_numpy()).reshape((len(Theta),))*np.pi/180.0
 eulers1=np.mod(eulers1, 2*np.pi)-np.pi
 eulers2=np.mod(eulers2, np.pi)-(np.pi/2.0)
 H, xedges, yedges=np.histogram2d(eulers1,eulers2,numBins, range=[ [-3.1415926535,3.1415926535],[-1.570796,1.570796] ])
 histValues = np.flip(np.sort(H.ravel()))
 
 fig, axs = plt.subplots(2)
 fig.suptitle('Occupancy Plots')
 axs[0].plot(histValues)
 axs[1].imshow(H)
 plt.show()



def resolutionPlot(scoringFileBest: PathLike, scoringFileWorst: PathLike = None):
 print ("resolutionPlot")
 tableBestScoring=pd.read_csv(scoringFileBest)
 resolutionBest=tableBestScoring['meanBestLocalResolution']
 particles=tableBestScoring['#numParticles']
 tableWorstScoring=None
 if scoringFileWorst:
  tableWorstScoring=pd.read_csv(scoringFileWorst)
  resolutionWorst=tableWorstScoring['meanWorstLocalResolution']
  legend=['Best Ranked Submaps','Worst Scored Submaps']
 else:
  legend=['resolutions']
 plt.plot( particles, resolutionBest,linewidth=3, color='green')
 if scoringFileWorst:
  plt.plot( particles, resolutionWorst, linewidth=3, color='red')
 plt.grid(True)
 plt.legend(legend,loc='best')
 #legend.append('Descending Ranking Order')
 plt.xlabel('Number of Sorted Particle from which a sub-map is reconstructed')
 plt.ylabel('Mean Local Resolution (A)')
 #plt.ylim([4, 23])
 plt.show()


def plotEulerHist(Phi, Theta, titlePlot, maxValue, numBins, outImage: PathLike = None, toShow=True):
    #Phi=Phi.astype(np.float)
    #Theta=Theta.astype(np.float)
    eulers1=(Phi.to_numpy()).reshape((len(Phi),))*np.pi/180.0
    eulers2=(Theta.to_numpy()).reshape((len(Theta),))*np.pi/180.0
    eulers1=np.mod(eulers1, 2*np.pi)-np.pi
    eulers2=np.mod(eulers2, np.pi)-(np.pi/2.0)

    #Get number of particles
    #tot=len(open(tmp,'r').readlines())
    #
    #numBins=80
    H, xedges, yedges=np.histogram2d(eulers1,eulers2,numBins, range=[ [-3.1415926535,3.1415926535],[-1.570796,1.570796] ])
    #print (xedges, '  ' ,yedges)

    #nominator, _, _ = np.histogram2d(eulers1,eulers2,bins=[xedges,yedges], weights=verification)
    #result = nominator / denominator
    #https://stackoverflow.com/questions/24917685/find-mean-bin-values-using-histogram2d-python


    #print (xedges)
    #print (yedges)
    #print (type(H))
    #print (sys.getsizeof(H[1]))
    #print (H[1])
    #for jj in range (0,len(H,0)):
    #    for ii in range (0,len(H,1)):
    #        print (H[jj][ii])
    #print (H)
    #return
    H = H.T
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111, title='pcolormesh: actual edges',aspect='equal', projection="mollweide")
    ax.tick_params(axis='x', direction='out', length=6, width=4, colors='w', grid_color='w', grid_alpha=0.5, label1On=False)
    X, Y = np.meshgrid(xedges, yedges)
    #pcm = ax.pcolormesh(X, Y, H, cmap='afmhot',vmin=minValue, vmax=maxValue)
    pcm = ax.pcolormesh(X, Y, H, cmap='RdBu_r',vmin=-1, vmax=maxValue)
     


    #colormaps https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html
    fig.colorbar(pcm, ax=ax, extend='both')
    ax.grid(color='w', linestyle=':', linewidth=1)
    ax.set_title(titlePlot, pad=20, fontweight="bold")
    plt.xlabel("Rot Angles ($\phi$)", fontweight="bold")
    plt.ylabel("Tilt Angles ($\\theta$)", fontweight="bold")
    if outImage:
        plt.savefig(outImage)
    if toShow:
        plt.show()
    #copy/paste multiple images in one
    #https://note.nkmk.me/en/python-pillow-paste/

