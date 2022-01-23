from os import PathLike
import pandas as pd
from scorem import starHandler
import scorem_core
import numpy as np
#import metrics
import tensorflow as tf
import matplotlib.pyplot as plt
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio

def ParticleVsReprojectionScores(particlesStarFile: PathLike, scoredParticlesStarFile: PathLike, referenceMap: PathLike, referenceMask: PathLike, listScoresTags = "", numViews=[50,200,400], useCTF=False):
    if listScoresTags == "":
        listScoresTags = ['_scorem_CC','_scorem_MI_blur_2','_scorem_CC_firstDerivativeX_1','_scorem_CC_firstDerivativeY_1','_scorem_CC_secondDerivativeX_1','_scorem_CC_secondDerivativeY_1']
    print ('listScoresTags=',listScoresTags)

    mapI=scorem_core.ReadMRC(referenceMap)
    sizeMap=scorem_core.sizeMRC(referenceMap)
    maskI=scorem_core.ReadMRC(referenceMask)
#    sizeMask=scorem_core.sizeMRC(referenceMask)


    version=starHandler.infoStarFile(particlesStarFile)[2]
    if version=="relion_v31":
        coordinatesFULL = starHandler.readColumns(particlesStarFile, ['_rlnRandomSubset','_rlnImageName','_rlnAngleRot','_rlnAngleTilt','_rlnAnglePsi','_rlnOriginXAngst','_rlnOriginYAngst','_rlnOpticsGroup'])
        idx=[x for x in range(0, len(coordinatesFULL))]
        coordinatesFULL['idx']=idx
        coordinatesDataOptics = starHandler.dataOptics(particlesStarFile)[['_rlnOpticsGroup','_rlnImagePixelSize']]
        coordinates =  pd.merge(coordinatesFULL, coordinatesDataOptics,  on=['_rlnOpticsGroup']).sort_values(['idx'])
        coordinates['_rlnOriginX']=coordinates['_rlnOriginXAngst']/coordinates['_rlnImagePixelSize']
        coordinates['_rlnOriginY']=coordinates['_rlnOriginYAngst']/coordinates['_rlnImagePixelSize']
        coordinates=coordinates.drop(['_rlnOpticsGroup'],axis=1).reindex()
        coordinates=coordinates.set_index('idx')
        coordinates=coordinates.drop(['_rlnOriginXAngst','_rlnOriginYAngst'],axis=1)
    else:
        coordinates = starHandler.readColumns(particlesStarFile, ['_rlnRandomSubset','_rlnImageName','_rlnAngleRot','_rlnAngleTilt','_rlnAnglePsi','_rlnOriginX','_rlnOriginY'])

    numIterations=len(coordinates['_rlnImageName'])
    outImageNames = []
    scoresOut = []
    #listScoresTags = ['_scorem_CC','_LRA_rank_linear','_LRA_particle_category']
    for ii in range(0,len(coordinates['_rlnImageName'])):
        print('iteration ',ii,' out of ', numIterations,end='\r')
        #print('iteration ',ii,' out of ', numIterations)
        tmpLine= (coordinates['_rlnImageName'][ii])
        atPosition=tmpLine.find('@')
        imageNo=int(tmpLine[:atPosition])
        stackName=tmpLine[atPosition+1:]
        phi=coordinates.at[ii, '_rlnAngleRot']
        theta=coordinates.at[ii, '_rlnAngleTilt']
        psi=coordinates.at[ii, '_rlnAnglePsi']
        tx=coordinates.at[ii, '_rlnOriginX']
        ty=coordinates.at[ii, '_rlnOriginY']
        outImageNames.append(str(str(ii+1).zfill(7)+'@'+stackName+'.mrcs'))
        I=scorem_core.ReadMrcSlice(stackName,imageNo-1)
        RI=scorem_core.projectMap(mapI,sizeMap[0],sizeMap[1],sizeMap[2],phi,theta,psi,tx,ty,0)
        MI=scorem_core.projectMask(maskI,sizeMap[0],sizeMap[1],sizeMap[2],phi,theta,psi,tx,ty,0,0.5)
        

        tmpScore=[]
        for kk in range(0,len(listScoresTags)):
            comparisonMethod = listScoresTags[kk].split('_')[2] if len(listScoresTags[kk].split('_'))>2 else "CC"
            preprocessingMethod = listScoresTags[kk].split('_')[3] if len(listScoresTags[kk].split('_'))>3 else "unprocessed"
            sigmaBlur = str(listScoresTags[kk].split('_')[4]) if len(listScoresTags[kk].split('_'))>4 else "1"
            #print ( 'comparing methods=',comparisonMethod,' ', preprocessingMethod)
            #print ('comparisonMethod=',comparisonMethod)
            if comparisonMethod=="CC" or comparisonMethod=="MI": 
                #I_fft=np.fft.fft(np.reshape(I,[sizeMap[1],sizeMap[0]]))
                #RI_fft=np.fft.fft(np.reshape(RI,[sizeMap[1],sizeMap[0]]))
                #I_abs_fft=np.abs(I_fft)+0.0000001
                #RI_abs_fft=np.abs(RI_fft)+0.0000001
                #ampAvg=0.5*(I_abs_fft+RI_abs_fft)
                #I_out=np.fft.ifft(I_fft*(ampAvg/I_abs_fft)).real.flatten().tolist()
                #RI_out=np.fft.ifft(RI_fft*(ampAvg/RI_abs_fft)).real.flatten().tolist()
                #tmpScore.append(scorem_core.MaskedImageComparison(I_out, RI_out, MI, sizeMap[0], sizeMap[1], 1,comparisonMethod,preprocessingMethod,sigmaBlur))
                tmpScore.append(scorem_core.MaskedImageComparison(I, RI, MI, sizeMap[0], sizeMap[1], 1,comparisonMethod,preprocessingMethod,sigmaBlur))
            elif comparisonMethod=="SSIM":
                #if preprocessingMethod.lower()=='blur':
                #    RI=scorem_core.derivative(I,float(sigmaBlur),sizeMap[0], sizeMap[1],0)
                #mean1,diff1,mean2,diff2= scorem_core.maskedNormalizeInfo(I,RI,MI,sizeMap[1]*sizeMap[0] )
                #img1 = ((np.array(I,dtype=np.float32)-mean1)/diff1).reshape(sizeMap[1],sizeMap[0])
                #img2 = ((np.array(RI,dtype=np.float32)-mean2)/diff2).reshape(sizeMap[1],sizeMap[0])
                #scoreSSIM=ssim(img1,img2)
                scoreSSIM=scorem_core.MaskedImageComparison(RI, I, MI, sizeMap[0], sizeMap[1], 1,comparisonMethod,preprocessingMethod,sigmaBlur)
                tmpScore.append(scoreSSIM)
                #plt.imshow(img2)
                #plt.show()
            elif comparisonMethod=="PSNR":
                #img1 = ((np.array(I,dtype=np.float32)-mean1)/diff1).reshape(sizeMap[1],sizeMap[0])
                #img_GT = ((np.array(RI,dtype=np.float32)-mean2)/diff2).reshape(sizeMap[1],sizeMap[0])
                #scorePSNR=peak_signal_noise_ratio(img_GT, img1)
                scorePSNR=scorem_core.MaskedImageComparison(RI, I, MI, sizeMap[0], sizeMap[1], 1,comparisonMethod,preprocessingMethod,sigmaBlur)
                tmpScore.append(scorePSNR)
            elif comparisonMethod=="SCI":
                I_fft=np.fft.fft(np.reshape(I,[sizeMap[1],sizeMap[0]]))
                RI_fft=np.fft.fft(np.reshape(RI,[sizeMap[1],sizeMap[0]]))
                I_abs_fft=np.abs(I_fft)+0.0000001
                RI_abs_fft=np.abs(RI_fft)+0.0000001
                ampAvg=0.5*(I_abs_fft+RI_abs_fft)
                I_out=np.fft.ifft(I_fft*(ampAvg/I_abs_fft)).real.flatten().tolist()
                RI_out=np.fft.ifft(RI_fft*(ampAvg/RI_abs_fft)).real.flatten().tolist()

                scoreSCI=scorem_core.MaskedImageComparison(RI_out, I_out, MI, sizeMap[0], sizeMap[1], 1,comparisonMethod,preprocessingMethod,sigmaBlur)
                #scoreSCI=scorem_core.MaskedImageComparison(RI_out, I_out, MI, sizeMap[0], sizeMap[1], 1,comparisonMethod,preprocessingMethod,sigmaBlur)
                tmpScore.append(scoreSCI)



        scoresOut.append(tmpScore)
#       exit(0)
#        print("------------")
#        score=scorem_core.MaskedImageComparison(I, RI, MI, sizeMap[0], sizeMap[1], 1,"CC","unprocessed",1)
#        print ("score=",score)
#        scoresOut.append(score)

#    print (tmpScore.shape)
#    exit(0)
    df_full_scores = pd.DataFrame(data=scoresOut,columns=listScoresTags)
    #print (df_full_scores.head)


#    targetScoreTag=listScoresTags[0]
#    phiListParticle = coordinates['_rlnAngleRot'].tolist()
#    thetaListParticle = coordinates['_rlnAngleTilt'].tolist()
#    scores = df_full_scores[targetScoreTag].tolist()
#    randomSubset = coordinates['_rlnRandomSubset'].tolist()
#    for vvv in range(0,len(numViews)):
#        rankedParticles=scorem_core.EqualizedParticlesRank(phiListParticle,thetaListParticle,scores,randomSubset,numViews[vvv])
#        df_full_scores['_scorem_rank_'+str(numViews[vvv])]=np.array(rankedParticles)
#        listScoresTags.append('_scorem_rank_'+str(numViews[vvv]) )
#        eulerGroup=scorem_core.GetEulerClassGroup(phiListParticle,thetaListParticle,numViews[vvv])
#        df_full_scores['_scorem_EulerGroup_'+str(numViews[vvv]) ]=np.array(eulerGroup)
#        listScoresTags.append('_scorem_EulerGroup_'+str(numViews[vvv]) )

    starHandler.removeColumnsTagsStartingWith(particlesStarFile, scoredParticlesStarFile, "_scorem_")
    starHandler.addDataframeColumns(scoredParticlesStarFile, scoredParticlesStarFile, listScoresTags, df_full_scores)



#    for ii in range(0,len(outImageNames)):
#        print (scoresOut[ii],' >> ',outImageNames[ii])

#        pm=scorem_core.projectMap(map,sizeMap[0],sizeMap[1],sizeMap[2],45,45,0,30,10,0)
#        scorem_core.WriteMRC(pm,"proj.mrc",sizeMap[0],sizeMap[1],1,1)

        #outImageNames.append(str(str(ii+1).zfill(7)+'@'+outputStackBasename+'.mrcs'))
 
 
    #print('try c++')



