# !/usr/local/bin/python3.9
# /usr/local/bin/python3.9 -m pip install starfile
# python3 -m venv venv
# source venv/bin/activate
# wheel, setuptools and twine
# /usr/local/bin/python3.9 -m pip install wheel
# /usr/local/bin/python3.9 -m pip install setuptools
# /usr/local/bin/python3.9 -m pip install twine


from os import PathLike
from os import system
import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn import metrics
from scorem import starHandler

################################
################################
####  extract best/worst
def random_forest_discriminator(filenameIn: PathLike, outBasename: PathLike, list_training_labels, label_for_bestData, label_for_worstData, numGoodParticlesTraining, numBadParticlesTraining, validationAccuracyThreshold=0.95, numIterations=1):
 print ("setupLearning ")
 list_training_labels.append('category')
 relevant_labels=list(set(list_training_labels) | set([label_for_bestData])  | set([label_for_worstData]) )

 header_list = starHandler.header_columns(filenameIn)
 startRawInfo=starHandler.infoStarFile(filenameIn)[0]
 df = pd.read_csv(filenameIn, skiprows=startRawInfo-1, names=header_list, skipinitialspace=True, sep="\s+")
 df['idx_original'] = df.index
 numParticles=len(df)
 print ("num of particles:",numParticles)


 if (numGoodParticlesTraining + numBadParticlesTraining > numParticles):
     numGoodParticlesTraining=int(numParticles/4)
     numBadParticlesTraining=numGoodParticlesTraining
     print ("Warning, input inconsistency, we had to change the num of good/bad particles to ",numGoodParticlesTraining)


 sizeTraining=int((numGoodParticlesTraining+numBadParticlesTraining)/3)
 #sizeTrainingHalf=int((sizeTraining)/2)
 sizeTesting=int(sizeTraining/4)
 sizeValidation=int(sizeTesting/4)
# accuracyThreshold=0.85
 print ("   sizeTraining=",sizeTraining,"  sizeTesting=",sizeTesting,"  sizeValidation=",sizeValidation)
 
 
 #print("##############")
 #print(df.head)
 #print (np.shape(df))
 #print (len(df))
 #y=np.zeros(len(df))

 sumVector = [0]*numParticles
# sumGoodAttemptsData=pd.DataFrame(data = sumVector, columns = ['sumGoodAttempts'])
# print (sumGoodAttemptsData.head)
 for ite in range(0, numIterations):
    #print('iteration ',ii,' out of ', numIterations,end='\r')
    df['category']=np.array([str('UNDEFINED')]*len(df))
    df = df.sort_values([label_for_worstData],ascending=True, kind='quicksort').reset_index(drop=True)
    for ii in range(0, len(df) ):
        if ii<numBadParticlesTraining:
            df.at[ii, 'category']='BAD'

    df = df.sort_values([label_for_bestData],ascending=True, kind='quicksort').reset_index(drop=True)
    for ii in range(0, len(df['category']) ):
        if ii<numGoodParticlesTraining:
            df.at[ii, 'category']='GOOD'

    df = df.sort_values(['idx_original'], ascending=True, kind='quicksort').reset_index(drop=True)
    # print(df.head)
    
    #subset_good=df.loc[ (df['category'] == 'GOOD') ]
#    print ( "undefined particles=",(df['category']=='UNDEFINED').sum() )
#    print ( "Training: GOOD particles=",(df['category']=='GOOD').sum() ,"   BAD particles=",(df['category']=='BAD').sum() )
    numUnsuccesfulAttempts=0
    while (df['category']=='UNDEFINED').sum()>0:
        #validationSubset=subset_good.sample(n = sizeValidation)[list_training_labels]
        validationSubset=df.loc[ (df['category'] == 'GOOD') | (df['category'] == 'BAD')].sample(n = sizeValidation)[list_training_labels]
        training_full=df.loc[ (df['category'] == 'GOOD') | (df['category'] == 'BAD')].drop(validationSubset.index)[list_training_labels]
        
        #print("-------------- validationSubset:")
        #print (validationSubset.head)
        #print("-------------- training_full:")
        #print (training_full.head)
        
        ytrain=training_full['category']
        Xtrain=training_full.drop(['category'], axis='columns', inplace=False)
        #print("#################  ytrain:")
        #print (ytrain.head)
        #print("----------------- Xtrain:")
        #print (training_full.head)
        
        #return
        model = DecisionTreeClassifier(criterion='gini', splitter='random',max_depth=3,min_samples_leaf=2)
        model.fit(Xtrain, ytrain)
        #print(df.get_feature_names())
        ytrain_model=model.predict(Xtrain)
        accuracy_current=metrics.accuracy_score(ytrain_model,ytrain)
        if accuracy_current>validationAccuracyThreshold:
            #print(" Validated accuracy of Decision Tree:", metrics.accuracy_score(ytrain_model,ytrain))
            Xtest=df.loc[ (df['category'] == 'UNDEFINED') ][list_training_labels].drop(['category'], axis='columns', inplace=False)
            if len(Xtest) > sizeTesting:
                Xtest=Xtest.sample(n = sizeTesting)
            tmpIdx=Xtest.index
            ytest_model=model.predict(Xtest)
            numClassfiedGood=0
            numClassfiedBad=0
            for ii in range(0, len(tmpIdx) ):
                    df.at[tmpIdx[ii], 'category']=ytest_model[ii]
                    if ytest_model[ii]=='GOOD':
                        numClassfiedGood=numClassfiedGood+1
                    if ytest_model[ii]=='BAD':
                        numClassfiedBad=numClassfiedBad+1
            #print ("counts=",(df['category']=='UNDEFINED').sum())
            #print ("classified good/bad=",numClassfiedGood,'  ',numClassfiedBad,'  numAttempts=',numUnsuccesfulAttempts)
            #print ("     (remaining particles to classify=", (df['category']=='UNDEFINED').sum(),')' )
            numUnsuccesfulAttempts=0
        else:
            numUnsuccesfulAttempts+=1 
    print ( 'final result: ite',ite,'  GOOD particles=',(df['category']=='GOOD').sum(), 'BAD particles=',(df['category']=='BAD').sum() )
    for hh in range (0, numParticles):
        if df.loc[hh, 'category']=='GOOD':
            sumVector[hh]+=1
    #print (df['category'])
 #sumVector=np.divide(sumVector,ite)
 
# print ('sumVector=',sumVector)
# print ('sum good=',np.sum(sumVector))
# print ('numIterations=',numIterations)

 sumVectorTmp=[0]*numParticles

 for uu in range(0, numIterations):
    for hh in range (0, numParticles):
        sumVectorTmp[hh] = 1 if sumVector[hh] > uu  else 0
        df.loc[hh, 'category']='GOOD' if sumVector[hh] > uu  else 'BAD'
    
    print("len(df['category'])=",len(df['category']))
    print("len(df['idx_original'])=",len(df['idx_original']))
    print('filenameIn=',filenameIn)
    #starHandler.addColumns(filenameIn, outBasename+'_tmp_'+str(uu)+'.star', ['category'], df['category'].to_numpy() )
    starHandler.addColumns(filenameIn, 'eccolo.star', ['category'], df['category'].to_numpy() )

    return
    starHandler.extractCategory( outBasename+'_tmp_'+str(uu)+'.star',  outBasename+'_refine_'+str(uu)+'_good.star',  '_scorem_particle_category', 'GOOD')
    starHandler.extractCategory( outBasename+'_tmp_'+str(uu)+'.star',  outBasename+'_refine_'+str(uu)+'_bad.star',  '_scorem_particle_category', 'BAD')
    print ('threshold=',uu,'sum good/bad=',np.sum(sumVectorTmp),' / ', numParticles-np.sum(sumVectorTmp) )
 return
 for uu in range(0, numIterations):
    for hh in range (0, numParticles):
        sumVectorTmp[hh] = 1 if sumVector[hh] > uu  else 0
        df.loc[hh, 'category']='GOOD' if sumVector[hh] > uu  else 'BAD'
    starHandler.addColumns(filenameIn, 'tmp_'+str(uu)+'.star', ['_LRA_particle_category'], df['category'])
    starHandler.extractCategory( 'tmp_'+str(uu)+'.star',  'refine_'+str(uu)+'_good.star',  '_LRA_particle_category', 'GOOD')
    starHandler.extractCategory( 'tmp_'+str(uu)+'.star',  'refine_'+str(uu)+'_bad.star',  '_LRA_particle_category', 'BAD')
    executeString='~/software/relion_19_june2021/relion/build/bin/relion_reconstruct --i '+'refine_'+str(uu)+'_good.star --o '+' refine_'+str(uu)+'_good_recH1.mrc --subset 1 --ctf &'
    executeString+='~/software/relion_19_june2021/relion/build/bin/relion_reconstruct --i '+'refine_'+str(uu)+'_good.star --o '+' refine_'+str(uu)+'_good_recH2.mrc --subset 2  --ctf ;'
    executeString+='~/software/relion_19_june2021/relion/build/bin/relion_reconstruct --i '+'refine_'+str(uu)+'_bad.star --o '+' refine_'+str(uu)+'_bad_recH1.mrc --subset 1  --ctf &'
    executeString+='~/software/relion_19_june2021/relion/build/bin/relion_reconstruct --i '+'refine_'+str(uu)+'_bad.star --o '+' refine_'+str(uu)+'_bad_recH2.mrc --subset 2  --ctf ; '
    executeString+='~/software/relion_19_june2021/relion/build/bin/relion_postprocess --i '+' refine_'+str(uu)+'_good_recH1.mrc  --i2 '+ ' refine_'+str(uu)+'_good_recH2.mrc  --angpix 1.350 --locres --o refine_'+str(uu)+'_good &'
    executeString+='~/software/relion_19_june2021/relion/build/bin/relion_postprocess --i '+' refine_'+str(uu)+'_bad_recH1.mrc  --i2 '+ ' refine_'+str(uu)+'_bad_recH2.mrc  --angpix 1.350 --locres --o refine_'+str(uu)+'_bad '
    system(executeString)
    #print ('sumVectorTmp=',sumVectorTmp)
    print ('threshold=',uu,'sum good/bad=',np.sum(sumVectorTmp),' / ', numParticles-np.sum(sumVectorTmp) )



# for hh in range (0, numParticles):
#     sumVectorTmp[hh] = 1 if sumVector[hh] > 1.0  else 0
# print ('sumVectorTmp=',sumVectorTmp)
# print ('sum good tmp=',np.sum(sumVectorTmp))

# for hh in range (0, numParticles):
#     sumVectorTmp[hh] = 1 if sumVector[hh] > 2.0  else 0
# print ('sumVectorTmp=',sumVectorTmp)
# print ('sum good tmp=',np.sum(sumVectorTmp))


# sumVectorTmp = np.minimum(3, sumVector)
# print ('sum good tmp=',np.sum(sumVectorTmp))

 #print ('sumVector=',sumVector)
 #print ('threshold=',ite/2.0)


#.loc[0].iat[3]
#    sumGoodAttemptsData

# addColumns(filenameIn, "tmp.star", ["_LRA_particle_category"], df['category'])
 #extractCategory( "tmp.star",  "tmp_good.star",  '_LRA_particle_category', 'GOOD')
 #extractCategory( "tmp.star",  "tmp_bad.star",  "_LRA_particle_category", "BAD")
 #print (df)
 #ytrain_model=model.predict(Xtrain)
 #ytrain=
 #model.fit(Xtrain, ytrain)
# print("--------------")
# for ii in range(0, len(df) ):
#  print (df['idx_original'][ii])
# print(df.head)
# for col in df.columns:
#    print(col)

# df_best = df.sort_values(['_LRA_rank_linear'],ascending=True, kind='quicksort').head(numItems)

# print (np.shape(df['category']))




################################
################################
####  extract best/worst
def random_forest_discriminator2(filenameIn: PathLike, basenameOut: PathLike, relevant_labels, numGoodParticlesTraining, numBadParticlesTraining, validationAccuracyThreshold=0.95, numIterations=1):
 print ("setupLearning ")
 header_list = starHandler.header_columns(filenameIn)
 startRawInfo=starHandler.infoStarFile(filenameIn)[0]
 df = pd.read_csv(filenameIn, skiprows=startRawInfo-1, names=header_list, skipinitialspace=True, sep="\s+")
 df['idx_original'] = df.index
 numParticles=len(df)
 print ("num of particles:",numParticles)


 if (numGoodParticlesTraining + numBadParticlesTraining > numParticles):
     numGoodParticlesTraining=int(numParticles/4)
     numBadParticlesTraining=numGoodParticlesTraining
     print ("Warning, input inconsistency, we had to change the num of good/bad particles to ",numGoodParticlesTraining)

 
 sizeTraining=int((numGoodParticlesTraining+numBadParticlesTraining)/4)
 #sizeTrainingHalf=int((sizeTraining)/2)
 sizeTesting=int(sizeTraining/2)
 sizeValidation=int(sizeTesting/4)
# accuracyThreshold=0.85
 print ("   sizeTraining=",sizeTraining,"  sizeTesting=",sizeTesting,"  sizeValidation=",sizeValidation)
 print ("   validationAccuracyThreshold=",validationAccuracyThreshold)

 
 #print("##############")
 #print(df.head)
 #print (np.shape(df))
 #print (len(df))
 #y=np.zeros(len(df))

 sumVector = [0]*numParticles
# sumGoodAttemptsData=pd.DataFrame(data = sumVector, columns = ['sumGoodAttempts'])
# print (sumGoodAttemptsData.head)

 for ite in range(0, numIterations):
    df['category']=np.array([str('UNDEFINED')]*len(df))
    df = df.sort_values(['_LRA_CC_unprocessed_simple'],ascending=True, kind='quicksort').reset_index(drop=True)
    for ii in range(0, len(df) ):
        if ii<numBadParticlesTraining:
            df.at[ii, 'category']='BAD_GT'

    df = df.sort_values(['_LRA_rank_linear'],ascending=True, kind='quicksort').reset_index(drop=True)
    for ii in range(0, len(df['category']) ):
        if ii<numGoodParticlesTraining:
            df.at[ii, 'category']='GOOD_GT'

    df = df.sort_values(['idx_original'], ascending=True, kind='quicksort').reset_index(drop=True)
    # print(df.head)
    
    #subset_good=df.loc[ (df['category'] == 'GOOD') ]
    print ( "undefined particles=",(df['category']=='UNDEFINED').sum() )
    print ( "Training: GOOD particles=",(df['category']=='GOOD_GT').sum() ,"   BAD particles=",(df['category']=='BAD_GT').sum() )
    numUnsuccesfulAttempts=0
    while (df['category']=='UNDEFINED').sum()>0:
        #print('numPriorUndefined=',(df['category']=='UNDEFINED').sum() )
        #validationSubset=subset_good.sample(n = sizeValidation)[relevant_labels]
        validationSubset=df.loc[ (df['category'] == 'GOOD_GT') | (df['category'] == 'BAD_GT')].sample(n = sizeValidation)[relevant_labels]
        training_full=df.loc[ (df['category'] == 'GOOD_GT') | (df['category'] == 'BAD_GT')].drop(validationSubset.index)[relevant_labels]
        
        
        #print("-------------- validationSubset:")
        #print (validationSubset.head)
        #print("-------------- training_full:")
        #print (training_full.head)
        
        ytrain=training_full['category']
        Xtrain=training_full.drop(['category'], axis='columns', inplace=False)
        #print("#################  ytrain:")
        #print (ytrain.head)
        #print("----------------- Xtrain:")
        #print (training_full.head)
        
        #return
        model = DecisionTreeClassifier(criterion='gini', splitter='random',max_depth=2,min_samples_leaf=2)
        model.fit(Xtrain, ytrain)
        #print(df.get_feature_names())
        ytrain_model=model.predict(Xtrain)
        accuracy_current=metrics.accuracy_score(ytrain_model,ytrain)
        if accuracy_current>validationAccuracyThreshold:
            #print(" Validated accuracy of Decision Tree:", metrics.accuracy_score(ytrain_model,ytrain))
            Xtest=df.loc[ (df['category'] == 'UNDEFINED') ][relevant_labels].drop(['category'], axis='columns', inplace=False)
            if len(Xtest) > sizeTesting:
                Xtest=Xtest.sample(n = sizeTesting)
            tmpIdx=Xtest.index
            ytest_model=model.predict(Xtest)
            numClassfiedGood=0
            numClassfiedBad=0
            for ii in range(0, len(tmpIdx) ):
                    
                    if ytest_model[ii]=='GOOD_GT':
                        numClassfiedGood=numClassfiedGood+1
                        df.at[tmpIdx[ii], 'category']='GOOD'
                    if ytest_model[ii]=='BAD_GT':
                        numClassfiedBad=numClassfiedBad+1
                        df.at[tmpIdx[ii], 'category']='BAD'
            #print ("counts=",(df['category']=='UNDEFINED').sum())
            #print ("classified good/bad=",numClassfiedGood,'  ',numClassfiedBad,'  numAttempts=',numUnsuccesfulAttempts)
            #print ("     (remaining particles to classify=", (df['category']=='UNDEFINED').sum(),')' )
            numUnsuccesfulAttempts=0
        else:
            numUnsuccesfulAttempts+=1 
        #print('unsucc=',numUnsuccesfulAttempts,'   num Post Undefined=',(df['category']=='UNDEFINED').sum(), '  accuracy=',accuracy_current )
    print ( 'final result: ite',ite,'  GOOD particles=',(df['category']=='GOOD').sum(), 'BAD particles=',(df['category']=='BAD').sum() )
    for hh in range (0, numParticles):
        if df.loc[hh, 'category']=='GOOD' or df.loc[hh, 'category']=='GOOD_GT':
            sumVector[hh]+=1
    #print (df['category'])
 #sumVector=np.divide(sumVector,ite)
 
# print ('sumVector=',sumVector)
# print ('sum good=',np.sum(sumVector))
# print ('numIterations=',numIterations)

 sumVectorTmp=[0]*numParticles

 for uu in range(0, numIterations):
    for hh in range (0, numParticles):
        sumVectorTmp[hh] = 1 if sumVector[hh] > uu  else 0
        df.loc[hh, 'category']='GOOD' if sumVector[hh] > uu  else 'BAD'
    starHandler.addColumns(filenameIn, 'tmp_'+str(uu)+'.star', ['_LRA_particle_category'], df['category'] )
    starHandler.extractCategory( 'tmp_'+str(uu)+'.star',  'refine_'+str(uu)+'_good.star',  '_LRA_particle_category', 'GOOD' )
    starHandler.extractCategory( 'tmp_'+str(uu)+'.star',  'refine_'+str(uu)+'_bad.star',  '_LRA_particle_category', 'BAD' )
    print ( 'threshold=',uu,'sum good/bad=',np.sum(sumVectorTmp),' / ', numParticles-np.sum(sumVectorTmp) )
 return
 for uu in range(0, numIterations):
    for hh in range (0, numParticles):
        sumVectorTmp[hh] = 1 if sumVector[hh] > uu  else 0
        df.loc[hh, 'category']='GOOD' if sumVector[hh] > uu  else 'BAD'
    starHandler.addColumns(filenameIn, 'tmp_'+str(uu)+'.star', ['_LRA_particle_category'], df['category'])
    starHandler.extractCategory( 'tmp_'+str(uu)+'.star',  'refine_'+str(uu)+'_good.star',  '_LRA_particle_category', 'GOOD')
    starHandler.extractCategory( 'tmp_'+str(uu)+'.star',  'refine_'+str(uu)+'_bad.star',  '_LRA_particle_category', 'BAD')
    executeString='~/software/relion_19_june2021/relion/build/bin/relion_reconstruct --i '+'refine_'+str(uu)+'_good.star --o '+' refine_'+str(uu)+'_good_recH1.mrc --subset 1 --ctf &'
    executeString+='~/software/relion_19_june2021/relion/build/bin/relion_reconstruct --i '+'refine_'+str(uu)+'_good.star --o '+' refine_'+str(uu)+'_good_recH2.mrc --subset 2  --ctf ;'
    executeString+='~/software/relion_19_june2021/relion/build/bin/relion_reconstruct --i '+'refine_'+str(uu)+'_bad.star --o '+' refine_'+str(uu)+'_bad_recH1.mrc --subset 1  --ctf &'
    executeString+='~/software/relion_19_june2021/relion/build/bin/relion_reconstruct --i '+'refine_'+str(uu)+'_bad.star --o '+' refine_'+str(uu)+'_bad_recH2.mrc --subset 2  --ctf ; '
    executeString+='~/software/relion_19_june2021/relion/build/bin/relion_postprocess --i '+' refine_'+str(uu)+'_good_recH1.mrc  --i2 '+ ' refine_'+str(uu)+'_good_recH2.mrc  --angpix 1.350 --locres --o refine_'+str(uu)+'_good &'
    executeString+='~/software/relion_19_june2021/relion/build/bin/relion_postprocess --i '+' refine_'+str(uu)+'_bad_recH1.mrc  --i2 '+ ' refine_'+str(uu)+'_bad_recH2.mrc  --angpix 1.350 --locres --o refine_'+str(uu)+'_bad '
    system(executeString)
    #print ('sumVectorTmp=',sumVectorTmp)
    print ('threshold=',uu,'sum good/bad=',np.sum(sumVectorTmp),' / ', numParticles-np.sum(sumVectorTmp) )



# for hh in range (0, numParticles):
#     sumVectorTmp[hh] = 1 if sumVector[hh] > 1.0  else 0
# print ('sumVectorTmp=',sumVectorTmp)
# print ('sum good tmp=',np.sum(sumVectorTmp))

# for hh in range (0, numParticles):
#     sumVectorTmp[hh] = 1 if sumVector[hh] > 2.0  else 0
# print ('sumVectorTmp=',sumVectorTmp)
# print ('sum good tmp=',np.sum(sumVectorTmp))


# sumVectorTmp = np.minimum(3, sumVector)
# print ('sum good tmp=',np.sum(sumVectorTmp))

 #print ('sumVector=',sumVector)
 #print ('threshold=',ite/2.0)


#.loc[0].iat[3]
#    sumGoodAttemptsData

# addColumns(filenameIn, "tmp.star", ["_LRA_particle_category"], df['category'])
 #extractCategory( "tmp.star",  "tmp_good.star",  '_LRA_particle_category', 'GOOD')
 #extractCategory( "tmp.star",  "tmp_bad.star",  "_LRA_particle_category", "BAD")
 #print (df)
 #ytrain_model=model.predict(Xtrain)
 #ytrain=
 #model.fit(Xtrain, ytrain)
# print("--------------")
# for ii in range(0, len(df) ):
#  print (df['idx_original'][ii])
# print(df.head)
# for col in df.columns:
#    print(col)

# df_best = df.sort_values(['_LRA_rank_linear'],ascending=True, kind='quicksort').head(numItems)

# print (np.shape(df['category']))
