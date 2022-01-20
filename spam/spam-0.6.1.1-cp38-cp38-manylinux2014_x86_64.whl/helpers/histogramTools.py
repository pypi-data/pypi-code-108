import matplotlib.pyplot as plt
import numpy


def findHistogramPeaks(image, valley1=20000, valley2=[], phases=2, gaussianFit=False, returnSigma=False, mask=True, showGraph=False, greyRange=[0,65535], bins=256, saveFigPath=None):
    """
    This function finds the peaks of the phases of a greylevel image (16bit or 8bit). The peaks are in greylevel units. Minimum number of Phases is 2 and Maximum is 3.

    Parameters
    -----------

        image : 3D numpy array

        valley1 : float
            An initial guess (arbitrary) greylevel value between peak phase 1 and peak phase 2, where peak phase 1 < valley1 < peak phase 2.

        valley2 : float
            An initial guess (arbitrary) greylevel value between peak phase 2 and peak phase 3, where peak phase 2 < valley2 < peak phase 3.
            If the image has 2 phases, value 2 is [].

        phases : int (2 or 3)
            The phases that exist in the greylevel image.
            Easy way to determine by looking how many peaks the histogram has.

        gaussianFit : bool, optional
            Should the peaks be fitted, or just the bin with the max valu returned?
            Default = True

        returnSigma : bool, optional
            Return a list of standard deviations from Fit?
             Requires gaussianFit=True
             Default= False

        mask: bool
            If image is masked with mask set to 0.

        showGraph: bool, optional
            If True, showing two matplotlib graphs - one corresponding to the histogram as returned in the spam.plotting.greyLevelHistogram and one corresponding to the histogram with the peaks of the phases.
            Default = False

        greyRange : list, optional
            If a 16-bit greylevel image --> greyRange = [0,65535]
            If a 8-bit greylevel image --> greyRange = [0,255]
            Default = [0,65535]

        bins : int, optional
            Default = 256

        saveFigPath : string, optional
            Path to save figure to.
            Default = None

    Returns
    --------
        The peaks of the phases of the image.
    """
    import scipy.optimize
    import spam.plotting.greyLevelHistogram

    def gauss(x,a,mu,sigma, offset):
        return a*numpy.exp(-1*(x-mu)**2/(2*sigma**2))+offset

    def gaussianFitFunction(x1, y1):
        # probably there is a smarter way to guess A instead of 1...
        mu1 = sum(x1 * y1) / sum(y1)
        sigma1 = numpy.sqrt(sum(y1 * (x1 - mu1)**2) / sum(y1))
        popt1,pcov1 = scipy.optimize.curve_fit(gauss, x1, y1, p0=[max(y1),mu1, sigma1, 0],maxfev=1000)
        a1 = popt1[0]
        mu1 = popt1[1]
        s1 = numpy.abs(popt1[2])
        offset1 = popt1[3]
        return a1, mu1, s1, offset1

    if phases == 1 or phases>=4:
        print("spam.helpers.histogramTools.findHistogramPeaks: Need to give me correct number of phases, remember always 2 or 3")
        return

    if phases==3:
        if valley1>=valley2:
            print("spam.helpers.histogramTools.findHistogramPeaks: Need to give me the correct values, where always valley1 < valley2")
            return

    if mask==True:
        image=image.astype(numpy.float)
        image[image==0]=numpy.nan
        reshist = spam.plotting.greyLevelHistogram.plotGreyLevelHistogram(image[numpy.isfinite(image)], greyRange=greyRange, bins=bins)
    else:
        reshist = spam.plotting.greyLevelHistogram.plotGreyLevelHistogram(image, greyRange=greyRange, bins=bins)


    totalCounts = numpy.array(reshist[1])
    totalgreylevel = numpy.array(reshist[0])

    if phases==2:

        greyPhase1= totalgreylevel[totalgreylevel<=valley1]
        countsPhase1 = totalCounts[0:greyPhase1.shape[0]]
        peakPhase1 = greyPhase1[numpy.argmax(countsPhase1)]
        # peakPhase1 = greyPhase1[countsPhase1==countsPhase1.max()]
        greyPhase2= totalgreylevel[totalgreylevel>=valley1]
        countsPhase2 = totalCounts[(bins-greyPhase2.shape[0]):bins]
        peakPhase2 = greyPhase2[numpy.argmax(countsPhase2)]
        # peakPhase2 = greyPhase2[countsPhase2==countsPhase2.max()]

        if gaussianFit:
            try: #Lets try to make the fitting
                #Compute midpoint between two peaks
                midPointGrey = (greyPhase1[numpy.argmax(countsPhase1)] + greyPhase2[numpy.argmax(countsPhase2)] ) / 2
                midPointArg = numpy.argmin(numpy.abs(totalgreylevel - midPointGrey))
                midPointCount = totalCounts[midPointArg]
                #Compute index of peaks on total
                indexPeak1 = numpy.where(totalCounts == countsPhase1.max())
                indexPeak2 = numpy.where(totalCounts == countsPhase2.max())
                #Compute midpoint in Y for subsets
                midPointCount1 = midPointCount + 0.25*(countsPhase1.max() - midPointCount)
                midPointCount2 = midPointCount + 0.25*(countsPhase2.max() - midPointCount)
                #Get new subsets index
                startIndex1 = numpy.argmin(numpy.abs( totalCounts[0:indexPeak1[0][0]]- midPointCount1)) 
                stopIndex1 = numpy.argmin(numpy.abs( totalCounts[indexPeak1[0][0]:midPointArg]- midPointCount1)) + indexPeak1[0][0] +1
                startIndex2 = numpy.argmin(numpy.abs( totalCounts[midPointArg:indexPeak2[0][0]]- midPointCount2)) + midPointArg 
                stopIndex2 = numpy.argmin(numpy.abs( totalCounts[indexPeak2[0][0]:]- midPointCount2)) + indexPeak2[0][0] +1
                a1, peakPhase1, sigmaPhase1, offset1 = gaussianFitFunction(totalgreylevel[startIndex1:stopIndex1], totalCounts[startIndex1:stopIndex1])  
                a2, peakPhase2, sigmaPhase2, offset2 = gaussianFitFunction(totalgreylevel[startIndex2:stopIndex2], totalCounts[startIndex2:stopIndex2])  
                sigmas = numpy.array([sigmaPhase1,sigmaPhase2])
            except:
                print("spam.helpers.histogramTools.findHistogramPeaks: There is not enough data to make the fitting")

        peakPhases = numpy.array([peakPhase1,peakPhase2])


        if showGraph == True:
            fig = plt.figure(1)
            plt.plot(totalgreylevel,totalCounts,label="Histogram")   

            plt.plot(peakPhase1,countsPhase1[countsPhase1==countsPhase1.max()],"ro",label="Peak Phase 1 @ {:5.0f}".format(float(peakPhase1)))
            plt.plot(peakPhase2,countsPhase2[countsPhase2==countsPhase2.max()],"yo",label="Peak Phase 2 @ {:5.0f}".format(float(peakPhase2)))
            plt.xlabel("Greylevel")
            plt.ylabel("Counts")

            if gaussianFit:
                plt.plot(totalgreylevel[startIndex1:stopIndex1], gauss(totalgreylevel[startIndex1:stopIndex1], a1, peakPhase1, sigmaPhase1, offset1), label='Fit 1')
                plt.plot(totalgreylevel[startIndex2:stopIndex2], gauss(totalgreylevel[startIndex2:stopIndex2], a2, peakPhase2, sigmaPhase2, offset2), label='Fit 2')

            plt.legend()
            fig.tight_layout()
            if saveFigPath is not None:
                plt.savefig(saveFigPath)
            else:
                plt.show()

        plt.close()


    if phases==3:
        #if gaussianFit:
        #    print("spam.helpers.findHistogramPeaks(): Three-peak fitting not yet implemented")
        greyPhase1= totalgreylevel[totalgreylevel<=valley1]
        countsPhase1 = totalCounts[0:greyPhase1.shape[0]]
        peakPhase1 = greyPhase1[countsPhase1==countsPhase1.max()]
        if gaussianFit:
            a1, peakPhase1, sigmaPhase1, offset1 = gaussianFitFunction(greyPhase1, countsPhase1)

        greyPhase3= totalgreylevel[totalgreylevel>=valley2]
        countsPhase3 = totalCounts[(bins-greyPhase3.shape[0]):bins]
        peakPhase3 = greyPhase3[countsPhase3==countsPhase3.max()]
        if gaussianFit:
            a3, peakPhase3, sigmaPhase3, offset3 = gaussianFitFunction(greyPhase3, countsPhase3)

        greyPhase2 = totalgreylevel[(totalgreylevel>valley1)&(totalgreylevel<valley2)]
        countsPhase2 = totalCounts[greyPhase1.shape[0]:(bins-greyPhase3.shape[0])]
        peakPhase2 = greyPhase2[countsPhase2==countsPhase2.max()]

        if gaussianFit:
            a2, peakPhase2, sigmaPhase2, offset2 = gaussianFitFunction(greyPhase2, countsPhase2)

        #print("spam.helpers.findHistogramPeaks: The peak of the Phase1 is at {:5.0f} of Greylevel".format(float(peakPhase1)))
        #print("spam.helpers.findHistogramPeaks: The peak of the Phase2 is at {:5.0f} of Greylevel".format(float(peakPhase2)))
        #print("spam.helpers.findHistogramPeaks: The peak of the Phase3 is at {:5.0f} of Greylevel".format(float(peakPhase3)))

        peakPhases = numpy.array([peakPhase1,peakPhase2,peakPhase3])
        if gaussianFit:
            sigmas = numpy.array([sigmaPhase1,sigmaPhase2,sigmaPhase3])

        if showGraph == True:
            fig = plt.figure()
            plt.plot(totalgreylevel,totalCounts,label="Histogram")
            plt.plot(peakPhase1,countsPhase1[countsPhase1==countsPhase1.max()],"ro",label="Peak Phase 1 @ {:5.0f}".format(float(peakPhase1)))
            plt.plot(peakPhase2,countsPhase2[countsPhase2==countsPhase2.max()],"yo",label="Peak Phase 2 @ {:5.0f}".format(float(peakPhase2)))
            plt.plot(peakPhase3,countsPhase3[countsPhase3==countsPhase3.max()],"bo",label="Peak Phase 3 @ {:5.0f}".format(float(peakPhase3)))
            plt.xlabel("Greylevel")
            plt.ylabel("Counts")
            if gaussianFit:
                plt.plot(greyPhase1, gauss(greyPhase1, a1, peakPhase1, sigmaPhase1), label='Fit 1')
                plt.plot(greyPhase2, gauss(greyPhase2, a2, peakPhase2, sigmaPhase2), label='Fit 2')
                plt.plot(greyPhase3, gauss(greyPhase3, a3, peakPhase3, sigmaPhase3), label='Fit 3')
            plt.legend()
            fig.tight_layout()
            plt.show()

    if returnSigma and not gaussianFit:
        print("spam.helpers.histogramTools.findHistogramPeaks: cannot return sigma if fitGaussian is not activated")
    if returnSigma and gaussianFit:
        return peakPhases, sigmas
    else:
        return peakPhases



def histogramNorm(im_Or, twoPeaks, peaksNormed=[0.25, 0.75], cropGreyvalues=[-numpy.inf, numpy.inf]):
    """
    This function normalise the histogram in order to range beween 0 and 1, presenting two peaks at p1 and p2 (p1<p2)


    Parameters
    -----------

        im_Or : 3D numpy array

        twoPeaks : list of two floats
            First and second peak of the original histogram

        peaksNormed : list of two floats, optional
            The desired level for the first and second peak of the normalized histogram.
            Default = [0.25, 0.75]

        cropGreyvalues :  list of two floats, optional
            The limits on the generated normalised values.
            Default = [-numpy.inf, numpy.inf]

    Returns
    --------
        im_Norm : 3D numpy array. Image with grey range between [0,1] and peaks at 0.25 and 0.75


    """
    if len(twoPeaks) != 2:
        print("spam.helpers.histogramTools.histogramTools.histogramNorm: The number of peaks should be 2")
        return
    peak1 = twoPeaks[0]
    peak2 = twoPeaks[1]
    p1 = peaksNormed[0]
    p2 = peaksNormed[1]
    if p1 > p2:
        print("spam.helpers.histogramTools.histogramTools.histogramNorm: p1 should be less than p2")
        return
    if peak1 > peak2:
        print("spam.helpers.histogramTools.histogramTools.histogramNorm: peak1 should be less than peak2")
        return
    #if peaksNormed is None:
    #    peaksNormed = [0.25, 0.75]

    m = (p2-p1)/(peak2 - peak1)
    b = p1 - m*peak1
    im_Norm = m*im_Or + b
    im_Norm[im_Norm<cropGreyvalues[0]]=cropGreyvalues[0]
    im_Norm[im_Norm>cropGreyvalues[1]]=cropGreyvalues[1]

    return im_Norm 

