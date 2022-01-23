from os import PathLike
import pandas as pd
import numpy as np
# from sklearn.tree import DecisionTreeClassifier
# from sklearn import metrics

# from matplotlib import pyplot
# from sklearn.tree import plot_tre
# from matplotlib.pyplot import figure
import matplotlib.pyplot as plt

####################
#ACCESSORY FUNCTIONS 
# START

#get starfile structure info
def infoStarFile(filename: PathLike):
    MAX_STAR_HEADER_SIZE = 500
    startLabels = 0
    startRawInfo = 0
    header = ""
    with open(filename) as f:
       #content = f.readlines()
       header = f.readlines()[:MAX_STAR_HEADER_SIZE]
    counter_loops = 0
    counter_data_optics = 0
    #search for the last loop_
    for ii in range (0, len(header)):
        tmpStr=header[ii].strip().replace(' ', '').replace('\t', '')
        if len (tmpStr)>0:
           #print (tmpStr)
           if tmpStr.startswith("data_optics"):
               counter_data_optics+=1
           if tmpStr.startswith("loop_"):
               startLabels=ii+1
               counter_loops+=1
           if tmpStr.startswith("_"):
               startRawInfo=ii+2
    version="relion_v30"
    if counter_loops > 1 and counter_data_optics > 0:
        version="relion_v31"
    return startRawInfo,startLabels,version


#get dataOptics info
def dataOptics(filename: PathLike):
    version=infoStarFile(filename)[2]
    if (version=='relion_v30'):
        return
    
    MAX_STAR_HEADER_SIZE = 500
    #search data_optics tag

    header = ""
    with open(filename) as f:
       #content = f.readlines()
       header = f.readlines()[:MAX_STAR_HEADER_SIZE]
    foundDataOptics=False
    foundDataOpticsLoop=False
    dataOpticsTags=[]
    startLabelsIdx=0
    endLabelsIdx=0
    startRawIdx=0
    endRawIdx=0
    for ii in range (0, len(header)):
        tmpStr=header[ii].strip().replace(' ', '').replace('\t', '')
        if len (tmpStr)>0:
           #print (tmpStr)
           if tmpStr.startswith("data_optics"):
               foundDataOptics=True
           if not (foundDataOpticsLoop) and foundDataOptics and tmpStr.startswith("loop_"):
#               startLabelsIdx=ii+1
               foundDataOpticsLoop=True
           if foundDataOpticsLoop and foundDataOptics and tmpStr.startswith("_") and startRawIdx==0:
               dataOpticsTags.append( header[ii].split(" ")[0].strip() )
#               print ( header[ii].split(" ")[0].strip() )
           #if foundDataOpticsLoop and foundDataOptics and tmpStr.startswith("_"):
           #    dataOpticsTags.append( split(" ", header[ii])[0] )
           if foundDataOpticsLoop and foundDataOptics and not(tmpStr.startswith("_")) and startRawIdx == 0 and not(tmpStr.startswith("loop_")):
               startRawIdx=ii
        if startRawIdx > 0 and endRawIdx==0 and len(tmpStr)==0:
            endRawIdx=ii
#    print('startLabelsIdx=',startLabelsIdx,'  endRawIdx=',endRawIdx)
#    print('startRawIdx=',startRawIdx,'  endRawIdx=',endRawIdx)
#    print(dataOpticsTags)

    rows_to_keep = [x for x in range(startRawIdx, endRawIdx)]
    data=pd.read_csv(filename, skiprows = lambda x: x not in rows_to_keep, names=dataOpticsTags, skipinitialspace=True, sep="\s+")
#    print (data['_rlnOpticsGroupName'])
    return (data)

# END
# ACCESSORY FUNCTIONS 
#######################



###########################
#get columns in header file
def header_columns(filename: PathLike):
 """get columns in star file

    Arguments:
        Inputs:
            filename: PathLike
                star file name

        Outputs:
            outVect: float, 1D array
                Unit cell
 """
 startRawInfo,startLabels,version=infoStarFile(filename)
 with open(filename) as f:
    header = f.readlines()[:startRawInfo-1]
 outVect=[]
 for ii in range (startLabels, len(header)):
     tmpStr=header[ii].lstrip().split()
     if len(tmpStr[0])>0:
         outVect.append(tmpStr[0])
 return outVect

###########################
#read one or multiple columns in star file
def readColumns(filename: PathLike, columnsToRead, sortColumnsNameOrder=False):
 #print ("readColumns ", filename)
 header_list = header_columns(filename)
 startRawInfo=infoStarFile(filename)[0]
 df = pd.read_csv(filename, skiprows=startRawInfo-1, names=header_list, usecols=columnsToRead, skipinitialspace=True, sep="\s+")
 if sortColumnsNameOrder: #output of the same order of columnsToRead
  outDf=df[columnsToRead]
 else:
   outDf=df
 return outDf

####################################
#read all columns of the star file
def readStar(filename: PathLike):
 #print ("readColumns ", filename)
 header_list = header_columns(filename)
 startRawInfo=infoStarFile(filename)[0]
 df = pd.read_csv(filename, skiprows=startRawInfo-1, names=header_list,  skipinitialspace=True, sep="\s+")
 return df

def extractColumns(filenameIn: PathLike, filenameOut: PathLike, listColumnsnameToRead ):
 #print ("readColumns ", filenameIn)
 startRawInfo,startLabels,version=infoStarFile(filenameIn)[0]
 pre_header =''
 if startLabels>0:
  with open(filenameIn) as f:
   pre_header = f.readlines()[:startLabels]
 pre_header=''.join(pre_header)
 columns=readColumns(filenameIn, listColumnsnameToRead, sortColumnsNameOrder=True)
 #print (columns.head)
 #print(columns.keys())
 #print(df.columns.tolist())
 for ii in range (0, len(listColumnsnameToRead)):
    pre_header+=str(listColumnsnameToRead[ii])+" #"+str(ii+1)+"\n"
 with open(filenameOut, "w") as fw:
  fw.write(pre_header)
  columns.to_csv(fw, header=False, sep=" ", index = False)
  fw.close()

###############################
#remove selected column (drop function)
def removeColumns(filenameIn: PathLike, filenameOut: PathLike, listColumnsToRemoveNames):
 #print ("removeColumns")
 startRawInfo,startLabels,version=infoStarFile(filenameIn)
 columns=header_columns(filenameIn)
 #get pre-header information
 pre_header =''
 if startLabels>0:
  with open(filenameIn) as f:
   pre_header = f.readlines()[:startLabels]
 pre_header=''.join(pre_header)
 df = pd.read_csv(filenameIn, skiprows=startRawInfo-1, names=columns, skipinitialspace=True, sep="\s+")
 columnsDeletedNames=[]
 mask=np.isin(columns, listColumnsToRemoveNames, invert=True)
 for ii in range(0, len(columns)):
   if mask[ii]:
     columnsDeletedNames.append(columns[ii])
 for ii in range (0, len(columnsDeletedNames)):
     pre_header+=str(columnsDeletedNames[ii])+" #"+str(ii+1)+"\n"
 with open(filenameOut, "w") as fw:
  fw.write(pre_header)
  X=df.drop(listColumnsToRemoveNames, axis='columns', inplace=False)
  X.to_csv(fw, header=False, sep=" ", index = False)
  fw.close()

###############################################################
#remove Columns with a Tags Starting With "StartingWithTags"
def removeColumnsTagsStartingWith(filenameIn: PathLike, filenameOut: PathLike, StartingWithTags):
# print ("removeColumnsTagsStartingWith")
# startRawInfo,startLabels=infoStarFile(filenameIn)
 columns=header_columns(filenameIn)
 columnsToRemove=[]
 for iiObj in columns:
     if iiObj.startswith(StartingWithTags):
         columnsToRemove.append(iiObj)
 removeColumns(filenameIn, filenameOut, columnsToRemove)


#########################
#add columns
def addDataframeColumns(filenameIn: PathLike, filenameOut: PathLike, columnsToAddName, columnToAddContent):
 #print ("addColumns")
 startRawInfo,startLabels,version=infoStarFile(filenameIn)
 columns=header_columns(filenameIn)
 #get pre-header information
 pre_header =''
 if startLabels>0:
  with open(filenameIn) as f:
   pre_header = f.readlines()[:startLabels]
 pre_header=''.join(pre_header)
 df = pd.read_csv(filenameIn, skiprows=startRawInfo-1, names=columns, skipinitialspace=True, sep="\s+")
 columnsAdded=columns
 for ii in range (0, len(columnsAdded)):
     pre_header+=str(columnsAdded[ii])+" #"+str(ii+1)+"\n"
 counter=0
 for kk in range(0,len(columnsToAddName)):
   if str(columnsToAddName[kk]) not in columns :
     pre_header+=str(columnsToAddName[kk])+" #"+str(len(columnsAdded)+1+counter)+"\n"
     counter+=1

 #df=df.drop(columnsToAddName, axis='columns', inplace=True)
 df[columnsToAddName]=columnToAddContent.values
#fullColumns=np.append(columns, columnToAddContent, axis=1)
 with open(filenameOut, "w") as fw:
  fw.write(pre_header)
  #df=df.drop(columns, axis='columns', inplace=False)
  df.to_csv(fw, header=False, sep=" ", index = False)
  fw.close()



#########################
#add columns
def addColumns(filenameIn: PathLike, filenameOut: PathLike, columnToAddName, columnToAddContent):
 #print ("addColumns")
 startRawInfo,startLabels,version=infoStarFile(filenameIn)
 columns=header_columns(filenameIn)
 #get pre-header information
 pre_header =''
 if startLabels>0:
  with open(filenameIn) as f:
   pre_header = f.readlines()[:startLabels]
 pre_header=''.join(pre_header)
 df = pd.read_csv(filenameIn, skiprows=startRawInfo-1, names=columns, skipinitialspace=True, sep="\s+")
 columnsAdded=columns
 for ii in range (0, len(columnsAdded)):
     pre_header+=str(columnsAdded[ii])+" #"+str(ii+1)+"\n"
 for kk in range(0,len(columnToAddName)):
     pre_header+=str(columnToAddName[kk])+" #"+str(len(columnsAdded)+len(columnToAddName)+kk)+"\n"
     df[columnToAddName[kk]]=columnToAddContent[kk]
 with open(filenameOut, "w") as fw:
  fw.write(pre_header)
  df.to_csv(fw, header=False, sep=" ", index = False)
  fw.close()



#################################################
#writeDataframe To Star using a template starfile
def writeDataframeToStar(filenameIn: PathLike, filenameOut: PathLike, dataframe):
 startRawInfo,startLabels,version=infoStarFile(filenameIn)
 #print (df)
 header =''
 if startLabels>0:
  with open(filenameIn) as f:
   header = f.readlines()[:startRawInfo-1]
 header=''.join(header)
 with open(filenameOut, "w") as fw:
  fw.write(header)
  dataframe.to_csv(fw, header=False, sep=" ", index = False)
  fw.close()

#################################################
#writeDataframe To Star without a template starfile
#uses information stored in dataframe 
def writeDataframeToStar_deNovo(dataframe, filenameOut: PathLike):
 header ='data_images\n\nloop_ \n'
 for ii in range(0,len(dataframe.columns)):
    header += str(dataframe.columns[ii])+' #'+str(ii+1)+'\n'
 with open(filenameOut, "w") as fw:
  fw.write(header)
  dataframe.to_csv(fw, header=False, sep=" ", index = False)
  fw.close()


#extract best/worst
def extractBest(filenameIn: PathLike, filenameOut: PathLike, numItems, tagToSelect):
 #print ("selectBest ",numItems)
 header_list = header_columns(filenameIn)
 startRawInfo=infoStarFile(filenameIn)[0]
 df = pd.read_csv(filenameIn, skiprows=startRawInfo-1, names=header_list, skipinitialspace=True, sep="\s+")
 df = df.sort_values([tagToSelect],ascending=True, kind='quicksort').head(numItems)
 df = df.sort_index()
 writeDataframeToStar(filenameIn, filenameOut, df)

def extractWorst(filenameIn: PathLike, filenameOut: PathLike, numItems, tagToSelect):
 #print ("selectWorst ",numItems)
 header_list = header_columns(filenameIn)
 startRawInfo=infoStarFile(filenameIn)[0]
 df = pd.read_csv(filenameIn, skiprows=startRawInfo-1, names=header_list, skipinitialspace=True, sep="\s+")
 df = df.sort_values([tagToSelect],ascending=False, kind='quicksort').head(numItems)
 df = df.sort_index()
 writeDataframeToStar(filenameIn, filenameOut, df)

def extractCategory(filenameIn: PathLike, filenameOut: PathLike, categoryName, categoryValue):
 #print ("extractCategory")
 header_list = header_columns(filenameIn)
 startRawInfo=infoStarFile(filenameIn)[0]
 df = pd.read_csv(filenameIn, skiprows=startRawInfo-1, names=header_list, skipinitialspace=True, sep="\s+")
 df = df.loc[ (df[categoryName].astype(str) == str(categoryValue)) ]
 #df = df.sort_values(['_LRA_CC_unprocessed_simple'],ascending=False, kind='quicksort').head(numItems)
 #df = df.sort_index()
 #_LRA_particle_category
 writeDataframeToStar(filenameIn, filenameOut, df)
 #removeColumns(filenameOut, filenameOut, [categoryName])


def extractImageNameInfo_starFile(InputStarFile: PathLike):
 imageNameTag='_rlnImageName'
 referenceColumns = readColumns(InputStarFile, [imageNameTag])
 listOfDatasets=[]
 listOccurrencesNames=[]
 listImagesIdx=[]
 listOccurrencesNamesIdx=[]
 for ii in range(0,len(referenceColumns[imageNameTag])):
   tmpLine= (referenceColumns[imageNameTag][ii])
   atPosition=tmpLine.find('@')
   imageNo=int(tmpLine[:atPosition])
   stackName=tmpLine[atPosition+1:]
   listOccurrencesNames.append(stackName)
   listImagesIdx.append(imageNo)
   if not(stackName in listOfDatasets):
     listOfDatasets.append(stackName)   
   listOccurrencesNamesIdx.append( listOfDatasets.index(stackName) )
 return listImagesIdx, listOccurrencesNamesIdx, listOfDatasets



################################################
#  SIMPLEST WAY TO MERGE MULTIPLE REFINEMENTS
#  mergeRefinementsWithHighestScore
def mergeRefinements(referenceRefinementStarFile: PathLike, fileNameOut: PathLike, listRefinementFiles, primaryScore='_scorem_SCI__1', refinedTags=['_rlnOriginXAngst','_rlnOriginYAngst','_rlnAngleRot','_rlnAngleTilt','_rlnAnglePsi']):
 df=readColumns(referenceRefinementStarFile, [primaryScore])
 listImagesIdx, listOccurrencesNamesIdx, listOfDatasets=extractImageNameInfo_starFile(referenceRefinementStarFile)

 listDataFilenameIdx=[0]*len(listImagesIdx)
 listDataIdx=[-1]*len(listImagesIdx)
 for kk in range(0,len(listRefinementFiles)):  
  pos1=[-1]*len(listImagesIdx)
  pos1_scores=[-10]*len(listImagesIdx)
  listImagesIdx1, listOccurrencesNamesIdx1, listOfDatasets1=extractImageNameInfo_starFile(listRefinementFiles[kk])
  referenceScores_tmp=readColumns(listRefinementFiles[kk], [primaryScore])
  #print ( kk, ' ->',referenceScore_tmp )
  for ii in range (0, len(listImagesIdx)):
   for jj in range (0, len(listImagesIdx1)):
    if listImagesIdx1[jj]==listImagesIdx[ii] and listOccurrencesNamesIdx1[jj]==listOccurrencesNamesIdx[ii]:
      pos1[ii]=jj
      pos1_scores[ii]=referenceScores_tmp.iloc[jj][primaryScore]
      #print ('ii=',ii,'   jj=',jj, '  => ', referenceScore_tmp.iloc[jj]['_LRA_CC_unprocessed_simple'])
      break
  df[ 'idx_ParameterLine_'+str(kk) ] = pos1
  df[ 'scores_file_'+str(kk) ] = pos1_scores


 for ii in range (0, len(listImagesIdx)):
   #print (ii, '  ==> ',df.iloc[ii])
   listTargetParameterFile=[referenceRefinementStarFile]
   listTargetParameterLine=[ii]
   listScores=[df.iloc[ii][primaryScore]]
#OK   meanTargetEulerId=[df.iloc[ii]['_LRA_CC_unprocessed_simple']]
#OK   varianceTargetEulerId=[df.iloc[ii]['_LRA_CC_unprocessed_simple']]
   #print ('values =')
   for kk in range(0,len(listRefinementFiles)):
     tmp_idx=df.iloc[ii][ 'idx_ParameterLine_'+str(kk) ]
     if tmp_idx >= 0: #other files have other values
       listScores.append(df.iloc[ii][ 'scores_file_'+str(kk) ])
       listTargetParameterFile.append('scores_file_'+str(kk))
       listTargetParameterLine.append(tmp_idx)
   sortedIdx = np.array(listScores).argsort()[::-1]
   #sorted_scores = np.array(listScores)[sortedIdx]
   sorted_filenames = np.array(listTargetParameterFile)[sortedIdx]
   sorted_paramsIdx = np.array(listTargetParameterLine)[sortedIdx]

   #####
   #criterium for selecting the particle:
#   thresholdNumParticles=10
   listDataFilenameIdx[ii]=sorted_filenames[0]
   listDataIdx[ii]=sorted_paramsIdx[0]
   #targetBestParticle=0
   #targetZscore=0
   #for ii in range(0, len(sorted_filenames)):

   ######
   #zscoretest
#   print (ii, '  ==>  eulerID=',eulerId[ii],'    numParticlesPerEuler=',len(sorted_filenames),'    ParticlesEulerId=',countEulerID[eulerIdx],'   density%=',100.0*countEulerID[eulerIdx]/len(listImagesIdx),'   MeanScoreEulerID=',meanScoreEulerID[eulerIdx],'   stdScoreEulerID=',stdScoreEulerID[eulerIdx] )
#   for tt in range(0,len(sorted_filenames)):
#    zscore=0
#    if stdScoreEulerID[eulerIdx]>0:
#      zscore= (sorted_scores[tt]-meanScoreEulerID[eulerIdx])/stdScoreEulerID[eulerIdx]
#    print ('    score=',  sorted_scores[tt],'   zscore=',zscore)
   
   ######

   #print (ii, '  ==> ',listScores, '   list_files=', listTargetParameterFile,'   list_scores=', listScores,'   targetFile=', listDataFilenameIdx[ii],'   targetIdx=', listDataIdx[ii] )
 
 referenceTags=readColumns(referenceRefinementStarFile, refinedTags)
 referenceTagsOut=referenceTags.copy()
 referenceTags['listDataIdx'] = pd.DataFrame(listDataIdx, columns=['listDataIdx'], dtype='int')
 referenceTags['listDataFilenameIdx'] = pd.DataFrame(listDataFilenameIdx, columns=['listDataFilenameIdx'])
 
 #save the file with all the amendments
 for kk in range(0,len(listRefinementFiles)):
   tmpTags=readColumns(listRefinementFiles[kk], refinedTags)
   #listDataFilenameIdx
   #tmp0=(referenceTags.loc[ (referenceTags['listDataFilenameIdx'] == 'scores_file_'+str(kk)) ]['listDataIdx'])
   idx=(referenceTags.loc[ (referenceTags['listDataFilenameIdx'] == 'scores_file_'+str(kk)) ]['listDataIdx'])
   tmpTags=tmpTags.iloc[idx.to_numpy()]
   tmpTags.index=idx.index
   referenceTagsOut.loc[tmpTags.index, :]=tmpTags[:]
   #print ('\n+++++++\n idx=', idx, '\n' ,tmpTags.head)
 del referenceTags
 # writeDataframeToStar_deNovo(referenceTagsOut, 'test.star')
 #print (referenceTagsOut.head)
 fullStar=readStar(referenceRefinementStarFile)
 for obj in refinedTags:
  fullStar[obj]=referenceTagsOut[obj]
 writeDataframeToStar(referenceRefinementStarFile, fileNameOut,fullStar)



################################################
################################################
#  MULTIVARIATE ANALYSIS SVD
#  mergeRefinements
def mergeRefinements_SVD(referenceRefinementStarFile: PathLike, fileNameOut: PathLike, listRefinementFiles,referenceScoresColumnsName, primaryScore='_LRA_CC_unprocessed_simple', minNumOfParticlesPerBin=3, numBins = 10, refinedTags=['_rlnOriginXAngst','_rlnOriginYAngst','_rlnAngleRot','_rlnAngleTilt','_rlnAnglePsi']):
 #print ("refinementsMerge")

 df=readColumns(referenceRefinementStarFile, referenceScoresColumnsName)
 listImagesIdx, listOccurrencesNamesIdx, listOfDatasets=extractImageNameInfo_starFile(referenceRefinementStarFile)

 #get the euler group
 eulerId=[-1]*len(listImagesIdx)
 meanScoreEulerID=[0]*(numBins*numBins)
 stdScoreEulerID=[0]*(numBins*numBins)
 countEulerID=[0]*(numBins*numBins)
 Phi=readColumns(referenceRefinementStarFile, ['_rlnAngleRot'])
 Theta=readColumns(referenceRefinementStarFile, ['_rlnAngleTilt'])
 eulers1=(Phi.to_numpy()).reshape((len(Phi),))*np.pi/180.0
 eulers2=(Theta.to_numpy()).reshape((len(Theta),))*np.pi/180.0
 eulers1=np.mod(eulers1, 2*np.pi)-np.pi
 eulers2=np.mod(eulers2, np.pi)-(np.pi/2.0)
 H, xedges, yedges=np.histogram2d(eulers1,eulers2,numBins, range=[ [-3.1415926535,3.1415926535],[-1.570796,1.570796] ])
 #H = H.T
 #print(H[:])
 for ii in range (0, len(listImagesIdx)):
   digX=np.digitize(eulers1[ii], xedges)-1
   digY=np.digitize(eulers2[ii], yedges)-1
   eulerId[ii]=digX+numBins*digY
 df[ 'euler_ID' ] = eulerId
 #get statistics for each group
 classifierPerGroup=[]#*(numBins*numBins)
 for ii in range( 0, numBins*numBins ):
   counts=(df['euler_ID']==ii).sum()
   countEulerID[ii]=counts
   #print ('\n*****************************\n full=', df.loc[df['euler_ID'] == ii][referenceScoresColumnsName])
   #NOTE: trick to select the best particles from view, and store the scores into a numpy vector
   ID_scores=df.loc[df['euler_ID'] == ii][referenceScoresColumnsName].sort_values(primaryScore,ascending = False).head(minNumOfParticlesPerBin).to_numpy()
   #print ('partial=', ID_scores)
   #print ('training data shape=',np.shape(ID_scores)) 
#   print ('numParameters=',len(referenceScoresColumnsName))
   if counts < minNumOfParticlesPerBin:
     trainedParameters=[ [1]*len(referenceScoresColumnsName) ]
     U1, D1, V1 = np.linalg.svd(np.transpose(trainedParameters, (1,0)), full_matrices=False)
     #print ('U1=',U1)
     classifierPerGroup.append(zip(U1))
   else:
     U1, D1, V1 = np.linalg.svd(np.transpose(ID_scores, (1,0)), full_matrices=False)
     classifierPerGroup.append(zip(U1))
 print ('\n\n******************\nclassifierPerGroup=', len(classifierPerGroup))



   #mean and std for each view
   #if counts > 0:
   # ID_scores=df.loc[df['euler_ID'] == ii]['_LRA_CC_unprocessed_simple'].to_numpy()
   # ID_scores=np.sort( ID_scores)[::-1]
   # meanScoreEulerID[ii]=np.average(ID_scores)
   # stdScoreEulerID[ii]=np.std(ID_scores)
   # ID_scores=np.sort( ID_scores)[::-1]
   # print ('\n\n---------\n',ii,' => ', counts, '  avg=', meanScoreEulerID[ii], '  std=', stdScoreEulerID[ii] )


 #train classifier for each group
 
# plt.imshow(H)
# plt.show()
 
 #inspect the files for refinement
 # and compute for each particle of each file the reference score
 listDataFilenameIdx=[0]*len(listImagesIdx)
 listDataIdx=[-1]*len(listImagesIdx)
 

 for kk in range(0,len(listRefinementFiles)):
  pos1=[-1]*len(listImagesIdx)
  pos1_scores=[-10]*len(listImagesIdx)
  listImagesIdx1, listOccurrencesNamesIdx1, listOfDatasets1=extractImageNameInfo_starFile(listRefinementFiles[kk])
  referenceScores_tmp=readColumns(listRefinementFiles[kk], referenceScoresColumnsName)
  #print ( kk, ' ->',referenceScore_tmp )
  print (' ite ', kk, ' of ', len(listRefinementFiles))
  for ii in range (0, len(listImagesIdx)):
   for jj in range (0, len(listImagesIdx1)):
    if listImagesIdx1[jj]==listImagesIdx[ii] and listOccurrencesNamesIdx1[jj]==listOccurrencesNamesIdx[ii]:
      pos1[ii]=jj
      y=(referenceScores_tmp.iloc[jj][referenceScoresColumnsName]).to_numpy().tolist()
      #print ('ii=',ii,'   multivariateScores=',y,'    data shape=',np.shape(y))
      #unpack U1
      unzippedMatrix=[]
      tmpU1=list(classifierPerGroup[eulerId[ii]])
      #print ('ii=',ii,'     eulerID=',eulerId[ii],'     U1=',tmpU1)
      for mm in range(0, len(tmpU1)):
        unzippedMatrix.append(np.array(tmpU1[mm][0]).tolist())
      U1=np.array(unzippedMatrix)
      #print ('     unzipped  U1=',U1)
      #print ('     type=',type(unzippedMatrix))
      y1=np.matmul(U1,np.matmul(np.transpose(U1),y))
      y1_distance=np.linalg.norm(y-y1)
      #print ('     distance=',y1_distance)
      pos1_scores[ii]=y1_distance
      classifierPerGroup[eulerId[ii]]=zip(U1)

      #pos1_scores[ii]=0
      #y=testParameters[ii]
      #y1=np.matmul(U1,np.matmul(np.transpose(U1),y))
      #y1_distance=np.linalg.norm(y-y1) 
      #pos1_scores[ii]=
      #print ('ii=',ii,'   jj=',jj, '  => ', referenceScore_tmp.iloc[jj]['_LRA_CC_unprocessed_simple'])
      break
  df[ 'idx_ParameterLine_'+str(kk) ] = pos1
  df[ 'scores_file_'+str(kk) ] = pos1_scores
 #print (df['idx_file_0'])
 #select best particles out of options

 for ii in range (0, len(listImagesIdx)):
   #print (ii, '  ==> ',df.iloc[ii])
   listTargetParameterFile=[referenceRefinementStarFile]
   listTargetParameterLine=[ii]
   #compute the score for the original files
   unzippedMatrix=[]
   tmpU1=list(classifierPerGroup[eulerId[ii]])
   for mm in range(0, len(tmpU1)):
     unzippedMatrix.append(np.array(tmpU1[mm][0]).tolist())
   U1=np.array(unzippedMatrix)
   y1=np.matmul(U1,np.matmul(np.transpose(U1),y))
   y1_distance=np.linalg.norm(y-y1)
   listScores=[y1_distance]
   classifierPerGroup[eulerId[ii]]=zip(U1)


#OK   listScores=[df.iloc[ii]['_LRA_CC_unprocessed_simple']]
#OK   listScores=[df.iloc[ii][referenceScoresColumnsName]]
#OK   meanTargetEulerId=[df.iloc[ii]['_LRA_CC_unprocessed_simple']]
#OK   varianceTargetEulerId=[df.iloc[ii]['_LRA_CC_unprocessed_simple']]
   #print ('values =')
   for kk in range(0,len(listRefinementFiles)):
     tmp_idx=df.iloc[ii][ 'idx_ParameterLine_'+str(kk) ]
     if tmp_idx >= 0: #other files have other values
       listScores.append(df.iloc[ii][ 'scores_file_'+str(kk) ])
       listTargetParameterFile.append('scores_file_'+str(kk))
       listTargetParameterLine.append(tmp_idx)

   ##########################################################################
   #NOTE: do not need to sort the score, but to compute the L2 distance using statistic trick
   sortedIdx = np.array(listScores).argsort()[::-1]
   sorted_scores = np.array(listScores)[sortedIdx]
   sorted_filenames = np.array(listTargetParameterFile)[sortedIdx]
   sorted_paramsIdx = np.array(listTargetParameterLine)[sortedIdx]

   #####
   #criterium for selecting the particle:
#   thresholdNumParticles=10
   eulerIdx=eulerId[ii]
   listDataFilenameIdx[ii]=sorted_filenames[0]
   listDataIdx[ii]=sorted_paramsIdx[0]
   #targetBestParticle=0
   #targetZscore=0
   #for ii in range(0, len(sorted_filenames)):

   ######
   #zscoretest
#   print (ii, '  ==>  eulerID=',eulerId[ii],'    numParticlesPerEuler=',len(sorted_filenames),'    ParticlesEulerId=',countEulerID[eulerIdx],'   density%=',100.0*countEulerID[eulerIdx]/len(listImagesIdx),'   MeanScoreEulerID=',meanScoreEulerID[eulerIdx],'   stdScoreEulerID=',stdScoreEulerID[eulerIdx] )
#   for tt in range(0,len(sorted_filenames)):
#    zscore=0
#    if stdScoreEulerID[eulerIdx]>0:
#      zscore= (sorted_scores[tt]-meanScoreEulerID[eulerIdx])/stdScoreEulerID[eulerIdx]
#    print ('    score=',  sorted_scores[tt],'   zscore=',zscore)
  
   ######

   #print (ii, '  ==> ',listScores, '   list_files=', listTargetParameterFile,'   list_scores=', listScores,'   targetFile=', listDataFilenameIdx[ii],'   targetIdx=', listDataIdx[ii] )
 
 referenceTags=readColumns(referenceRefinementStarFile, refinedTags)
 referenceTagsOut=referenceTags.copy()
 referenceTags['listDataIdx'] = pd.DataFrame(listDataIdx, columns=['listDataIdx'], dtype='int')
 referenceTags['listDataFilenameIdx'] = pd.DataFrame(listDataFilenameIdx, columns=['listDataFilenameIdx'])
 
  #save the file with all the amendments
 for kk in range(0,len(listRefinementFiles)):
   tmpTags=readColumns(listRefinementFiles[kk], refinedTags)
   #listDataFilenameIdx
   #tmp0=(referenceTags.loc[ (referenceTags['listDataFilenameIdx'] == 'scores_file_'+str(kk)) ]['listDataIdx'])
   idx=(referenceTags.loc[ (referenceTags['listDataFilenameIdx'] == 'scores_file_'+str(kk)) ]['listDataIdx'])
   tmpTags=tmpTags.iloc[idx.to_numpy()]
   tmpTags.index=idx.index
   referenceTagsOut.loc[tmpTags.index, :]=tmpTags[:]
   #print ('\n+++++++\n idx=', idx, '\n' ,tmpTags.head)
 del referenceTags
 # writeDataframeToStar_deNovo(referenceTagsOut, 'test.star')
 #print (referenceTagsOut.head)
 fullStar=readStar(referenceRefinementStarFile)
 for obj in refinedTags:
  fullStar[obj]=referenceTagsOut[obj]
 writeDataframeToStar(referenceRefinementStarFile, fileNameOut,fullStar)



 #print (df.head)
 #ID_tmp=df.loc[df['euler_ID'] == 61]
 #print ('selection =',ID_tmp.head)
 #print ('COUNT=',ID_tmp['euler_ID'].count)
 #print ("counts=",(df['euler_ID']==61).sum())

