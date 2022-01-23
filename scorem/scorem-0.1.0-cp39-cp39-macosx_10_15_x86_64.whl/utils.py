from scorem import starHandler
from os import PathLike
from os import path
import scorem_core
import pandas as pd
import numpy as np

#############################
###  create ctfStack
def ctfStack(particlesStarFile: PathLike, outputStackBasename):
    imageNameTag='_rlnImageName'
    imageNames = starHandler.readColumns(particlesStarFile, [imageNameTag])
    
    #CTFParameters ctf_parameters(rlnSphAberration[ii], rlnVoltage[ii], rlnDefocusAngle[ii], rlnDefocusU[ii], rlnDefocusV[ii], rlnAmplitudeContrast[ii], 0, 0);
    version=starHandler.infoStarFile(particlesStarFile)[2]
    if version=="relion_v31":
        parametersFULL = starHandler.readColumns(particlesStarFile, ['_rlnImageName','_rlnDefocusU','_rlnDefocusV','_rlnDefocusAngle','_rlnOpticsGroup','_rlnCtfBfactor', '_rlnPhaseShift'])
        idx=[x for x in range(0, len(parametersFULL))]
        parametersFULL['idx']=idx
        parametersDataOptics = starHandler.dataOptics(particlesStarFile)[['_rlnImagePixelSize','_rlnVoltage','_rlnAmplitudeContrast','_rlnSphericalAberration','_rlnOpticsGroup']]
        ctfParameters =  pd.merge(parametersFULL, parametersDataOptics,  on=['_rlnOpticsGroup']).sort_values(['idx'])
        ctfParameters=ctfParameters.drop(['_rlnOpticsGroup'],axis=1).reindex()
        ctfParameters=ctfParameters.set_index('idx')
        ctfParameters.rename(columns={'_rlnImagePixelSize':'_rlnDetectorPixelSize'},inplace=True)
    else:
        ctfParameters = starHandler.readColumns(particlesStarFile, ['_rlnImageName','_rlnDefocusU','_rlnDefocusV','_rlnDefocusAngle','_rlnDetectorPixelSize','_rlnVoltage','_rlnAmplitudeContrast','_rlnSphericalAberration','_rlnCtfBfactor', '_rlnPhaseShift'])

#    print (ctfParameters)
    tmpLine= (imageNames[imageNameTag][0])
    stackName=tmpLine[tmpLine.find('@')+1:]
    sizeI=scorem_core.sizeMRC(stackName)
    scorem_core.WriteEmptyMRC(outputStackBasename+'.mrcs',sizeI[0],sizeI[1],len(imageNames[imageNameTag]))
    nx=sizeI[0]
    ny=sizeI[1]
    outImageNames = []
    numIterations=len(imageNames[imageNameTag])
    for ii in range(0,len(imageNames[imageNameTag])):
        print('iteration ',ii,' out of ', numIterations,end='\r')
        tmpLine= (imageNames[imageNameTag][ii])
        atPosition=tmpLine.find('@')
        imageNo=int(tmpLine[:atPosition])
        stackName=tmpLine[atPosition+1:]
        #print (ii,' >> ',imageNo,' >> ',imageNames[imageNameTag][ii])
        angpix=ctfParameters.at[ii, '_rlnDetectorPixelSize']
        SphericalAberration=ctfParameters.at[ii, '_rlnSphericalAberration']
        voltage=ctfParameters.at[ii, '_rlnVoltage']
        DefocusAngle=ctfParameters.at[ii, '_rlnDefocusAngle']
        DefocusU=ctfParameters.at[ii, '_rlnDefocusU']
        DefocusV=ctfParameters.at[ii, '_rlnDefocusV']
        AmplitudeContrast=ctfParameters.at[ii, '_rlnAmplitudeContrast']
        Bfac=ctfParameters.at[ii, '_rlnCtfBfactor']
        phase_shift=ctfParameters.at[ii, '_rlnPhaseShift']
        ctfI=scorem_core.CtfCenteredImage(nx,ny,angpix,SphericalAberration,voltage,DefocusAngle,DefocusU,DefocusV,AmplitudeContrast,Bfac,phase_shift)
        ctfI=np.array(ctfI).reshape((sizeI[1], sizeI[0]))
        mapI=np.array(scorem_core.ReadMrcSlice(stackName,imageNo-1))
        mapI=mapI.reshape((sizeI[1], sizeI[0]))
        mapFFT=np.fft.fftshift(np.fft.fft2(mapI))
        mapIFFT=np.real(np.fft.ifft2(np.fft.ifftshift(mapFFT*ctfI))).flatten()
        scorem_core.ReplaceMrcSlice(mapIFFT.tolist(),outputStackBasename+'.mrcs',sizeI[0],sizeI[1],ii)
        outImageNames.append(str(str(ii+1).zfill(7)+'@'+outputStackBasename+'.mrcs'))

#    for ii in range(0,len(outImageNames)):
#        print (outImageNames[ii])

    originalStarDataframe=starHandler.readStar(particlesStarFile)
    originalStarDataframe['_rlnImageName']=outImageNames
    starHandler.writeDataframeToStar(particlesStarFile, outputStackBasename+'.star', originalStarDataframe)


    
    #Phi=starHandler.readColumns(starFileIn, ['_rlnAngleRot'])

#############################
###  Read MRC
def readMRC(mrcFile: PathLike):
    print("read MRC file ", mrcFile)
    if (not path.exists(mrcFile)):
        print ('ERROR: file ',mrcFile,' does not exists')
        return None
    if not mrcFile.endswith('.mrc') or not mrcFile.endswith('.mrcs') or not mrcFile.endswith('.st') or not not mrcFile.endswith('.rawst'):
        print ('ERROR: file ',mrcFile,' does not have a recognized extension. If you sure it is a mrc file, just rename it as .mrc')
        return None

    #if (particlesStarFile.endswith(suffix))
