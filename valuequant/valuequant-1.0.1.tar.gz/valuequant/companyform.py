# 著作者：叶凯文
# Author: YE KAIWEN
# 版权归著作者叶凯文所有
# Copyright (c) 2022 YE KAIWEN. All Rights Reserved.

from .VQconnect import VQC
from .commonform import modelcate

def formatmodelparams(mfunc,mparams):
    stockcode=mparams.pop('stockcode')
    dimension=mparams.pop('dimension')
    reportdate=mparams.pop('reportdate')
    adjdate=mparams.pop('adjdate')
    ttm=mparams.pop('ttm')
    return {'stockcode':stockcode,'dimension':dimension,'reportdate':reportdate,'adjdate':adjdate,'ttm':ttm,'mcate':modelcate[mfunc],'mfunc':mfunc,'mparams':mparams}

def formatmodelsetparams(mfunc,mparams):
    stockcode=mparams.pop('stockcode')
    if type(mparams['structure'])==dict:
        structure=mparams.pop('structure')
    else:
        print("structure参数应该是字典类型。")
        return None
    reportdate=mparams.pop('reportdate')
    adjdate = mparams.pop('adjdate')
    ttm = mparams.pop('ttm')
    mfunc=mfunc[:-3]
    return {'stockcode':stockcode,'structure':structure,'reportdate':reportdate,'adjdate':adjdate,'ttm':ttm,'mcate':modelcate[mfunc],'mfunc':mfunc,'mparams':mparams}

def formatframesetparams(mfunc,mparams):
    stockcode=mparams.pop('stockcode')
    reportdate=mparams.pop('reportdate')
    adjdate=mparams.pop('adjdate')
    ttm = mparams.pop('ttm')
    mfunc=mfunc[:-8]+'model'
    return {'stockcode':stockcode,'reportdate':reportdate,'adjdate':adjdate,'ttm':ttm,'mcate':modelcate[mfunc],'mfunc':mfunc,'mparams':mparams}

def getcompanymodel(mfunc,mparams):
    modeltype = mfunc.split('_')[-1]
    if modeltype=='model':
        modeltype='Model'
    elif modeltype=='modelset':
        modeltype='ModelSet'
    elif modeltype=='frameset':
        modeltype='FrameSet'
    else:
        print("非法参数")
        return None
    fparams=globals()['format'+modeltype.lower()+'params'](mfunc,mparams)
    if type(fparams)==dict:
        try:
            params = {'datatype': 'Company', 'modeltype': modeltype, 'restype': 'Model', 'params':fparams}
            return VQC.service(params)
        except:
            print("网络请求出错")
            return None
    else:
        return None

def formatmodelxparams(model,mparams,mfunc):
    if type(model)!=dict:
        return None
    stockcode=mparams.pop('stockcode')
    reportdate=mparams.pop('reportdate')
    adjdate = mparams.pop('adjdate')
    ttm=mparams.pop('ttm')
    return {'model':model,'stockcode':stockcode,'reportdate':reportdate,'adjdate':adjdate,'ttm':ttm,'mcate':modelcate[mfunc]}

def formatmodelsetxparams(modelset,mparams,vparams,mfunc):
    if type(modelset)!=dict:
        return None
    stockcode=mparams.pop('stockcode')
    reportdate=mparams.pop('reportdate')
    adjdate = mparams.pop('adjdate')
    dimension=vparams.pop('dimension')
    ttm=mparams.pop('ttm')
    return {'modelset':modelset,'stockcode':stockcode,'reportdate':reportdate,'dimension':dimension,'adjdate':adjdate,'ttm':ttm,'mcate':modelcate[(mfunc[:-8]+'model')]}

def formatbatchirrparams(fparams,vparams):
    if type(fparams)==dict:
        fparams['startdate']=vparams.pop('startdate')
        fparams['enddate'] = vparams.pop('enddate')
        fparams['pricemode'] = vparams.pop('pricemode')
        fparams['rp'] = vparams.pop('rp')
        return fparams
    else:
        return fparams

def formatunitirrparams(fparams,vparams):
    if type(fparams)==dict:
        fparams['tradedate']=vparams.pop('tradedate')
        fparams['pricemode'] = vparams.pop('pricemode')
        fparams['rp'] = vparams.pop('rp')
        return fparams
    else:
        return None

def formatbatchachieverateparams(fparams,vparams):
    if type(fparams)==dict:
        fparams['startdate']=vparams.pop('startdate')
        fparams['enddate'] = vparams.pop('enddate')
        fparams['pricemode'] = vparams.pop('pricemode')
        fparams['r'] = vparams.pop('r')
        fparams['rp'] = vparams.pop('rp')
        return fparams
    else:
        return None

def formatunitachieverateparams(fparams,vparams):
    if type(fparams)==dict:
        fparams['tradedate']=vparams.pop('tradedate')
        fparams['pricemode'] = vparams.pop('pricemode')
        fparams['r'] = vparams.pop('r')
        fparams['rp'] = vparams.pop('rp')
        return fparams
    else:
        return None

def getcompanyservice(restype,model,mfunc,mparams,vparams):
    modeltype=mfunc.split('_')[-1]
    if modeltype=='model':
        fparams=formatmodelxparams(model=model,mparams=mparams,mfunc=mfunc)
        modeltype='Model'
    elif modeltype in ['modelset','frameset']:
        fparams=formatmodelsetxparams(modelset=model,mparams=mparams,vparams=vparams,mfunc=mfunc)
        modeltype='ModelSet'
    else:
        print("非法参数")
        return None
    fparams=globals()['format'+restype.lower()+'params'](fparams=fparams,vparams=vparams)
    if type(fparams)==dict:
        try:
            params = {'datatype': 'Company', 'modeltype': modeltype, 'restype': restype, 'params':fparams}
            return VQC.service(params)
        except:
            print("网络请求出错")
            return None
    else:
        return None

def getcompanydata(stockcode,reportdate,dimension,adjdate=None,ttm=False):
    fparams=locals()
    try:
        params={'datatype':'StockAdjUnitDimInc','params':fparams}
        return VQC.data(params)
    except:
        print("网络请求出错")
        return None
