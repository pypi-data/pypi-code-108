# 著作者：叶凯文
# Author: YE KAIWEN
# 版权归著作者叶凯文所有
# Copyright (c) 2022 YE KAIWEN. All Rights Reserved.

from .VQconnect import VQC

import pandas as pd

datasize=5000
accuracy=4

modelcate={
    'strict_latest_status_model':'Status',
    'probable_latest_status_model':'Status',
    'long_range_status_model':'Status',
    'strict_latest_long_range_model':'Status',
    'probable_latest_long_range_model':'Status',
    'series_shape_model':'Shape',
    'ma_strict_latest_status_shape_model':'Shape',
    'ma_probable_latest_status_shape_model':'Shape',
    'ma_strict_latest_status_model':'Ma',
    'ma_probable_latest_status_model':'Ma',
    'ma_long_range_status_model':'Ma',
}

def formatseries(datalist,startdate,freq):
    if len(datalist)>5000:
        print("上传数据序列长度超过5000。")
        return None
    try:
        series=pd.Series(datalist,index=pd.date_range(start=startdate,freq=freq,periods=len(datalist)))
        if series.dtypes not in [int,float]:
            print("序列元素应为数字类型。")
            return None
        return series.round(accuracy)
    except:
        print("数据出错,请检查序列参数。")
        return None

def formatdataframe(datalist,startdate,freq,datacols):
    try:
        df=pd.DataFrame(datalist,index=pd.date_range(start=startdate,freq=freq,periods=len(datalist)),columns=datacols)
        if (len(df.index)*len(df.columns))>datasize:
            print("上传数据表格元素总数超过5000。")
            return None
        if (((df.dtypes==int).all())|((df.dtypes==float).all()))==False:
            print("数据表格元素应为数字类型。")
            return None
        return df.round(accuracy)
    except:
        print("数据出错,请检查数据表格参数。")
        return None

def seriestoformat(series):
    datalist = series.values.tolist()
    startdate = series.index[0].strftime('%Y-%m-%d')
    freq = series.index.freq.name
    return datalist,startdate,freq

def dftoformat(df):
    datalist = df.values.tolist()
    startdate = df.index[0].strftime('%Y-%m-%d')
    freq = df.index.freq.name
    datacols = df.columns.to_list()
    return datalist,startdate,freq,datacols

def formatmodelparams(mfunc,mparams):
    datalist=mparams.pop('datalist')
    startdate=mparams.pop('startdate')
    freq=mparams.pop('freq')
    series=formatseries(datalist,startdate,freq)
    if type(series)==pd.Series:
        return {'datalist':datalist,'startdate':startdate,'freq':freq,'mcate':modelcate[mfunc],'mfunc':mfunc,'mparams':mparams}
    else:
        return None

def formatmodelsetparams(mfunc,mparams):
    datalist=mparams.pop('datalist')
    startdate=mparams.pop('startdate')
    freq=mparams.pop('freq')
    datacols=mparams.pop('datacols')
    structure=mparams.pop('structure')
    mfunc=mfunc[:-3]
    if type(structure) != dict:
        print('ModelSet结构错误。')
        return None
    df = formatdataframe(datalist, startdate, freq, datacols)
    if type(df)==pd.DataFrame:
        return {'datalist':datalist,'startdate':startdate,'freq':freq,'datacols':datacols,'structure':structure,'mcate':modelcate[mfunc],'mfunc':mfunc,'mparams':mparams}
    else:
        return None

def getcommonmodel(mfunc,mparams):
    modeltype=mfunc.split('_')[-1]
    if modeltype=='model':
        modeltype='Model'
    elif modeltype=='modelset':
        modeltype='ModelSet'
    else:
        print("非法参数")
        return None
    formatparams=globals()['format'+modeltype.lower()+'params'](mfunc,mparams)
    if type(formatparams)==dict:
        try:
            params = {'datatype': 'Common', 'modeltype': modeltype, 'restype': 'Model', 'params':formatparams}
            return VQC.service(params)
        except:
            print("网络请求出错")
            return None
    else:
        print("非法参数")
        return None

def formatmodelxparams(model,mfunc):
    if type(model)==dict:
        return {'model':model,'mcate':modelcate[mfunc]}
    else:
        return None

def formatmodelsetxparams(modelset,mfunc,vparams):
    if type(modelset)==dict:
        return {'modelset':modelset,'mcate':modelcate[(mfunc[:-8]+'model')],'dimension':vparams.pop('dimension')}
    else:
        return None

def formatdimensionparams(fparams,vparams):
    if type(fparams)==dict:
        fparams['dimension']=vparams.pop('dimension')
        return fparams
    else:
        return fparams

def formatforecastparams(fparams,vparams):
    if type(fparams)==dict:
        fparams['t']=vparams.pop('t')
        return fparams
    else:
        return fparams

def formatpvparams(fparams,vparams):
    if type(fparams)==dict:
        fparams['r']=vparams.pop('r')
        return fparams
    else:
        return fparams

def formatbatchirrparams(fparams,vparams):
    if type(fparams)==dict:
        pricelist=vparams.pop('pricelist')
        pricestart=vparams.pop('pricestart')
        pricefreq = vparams.pop('pricefreq')
        series=formatseries(pricelist,pricestart,pricefreq)
        if type(series)==pd.Series:
            fparams['pricelist']=pricelist
            fparams['pricestart'] = pricestart
            fparams['pricefreq'] = pricefreq
            fparams['dcdate'] = vparams.pop('dcdate')
            fparams['rp']=vparams.pop('rp')
            return fparams
        else:
            return None
    else:
        return fparams

def formatunitirrparams(fparams,vparams):
    if type(fparams)==dict:
        fparams['price'] = vparams.pop('price')
        fparams['gap']=vparams.pop('gap')
        fparams['rp']=vparams.pop('rp')
        return fparams
    else:
        return fparams

def formatbatchachieverateparams(fparams,vparams):
    if type(fparams)==dict:
        pricelist=vparams.pop('pricelist')
        pricestart=vparams.pop('pricestart')
        pricefreq = vparams.pop('pricefreq')
        series=formatseries(pricelist,pricestart,pricefreq)
        if type(series)==pd.Series:
            fparams['pricelist']=pricelist
            fparams['pricestart'] = pricestart
            fparams['pricefreq'] = pricefreq
            fparams['r']=vparams.pop('r')
            fparams['dcdate'] = vparams.pop('dcdate')
            fparams['rp'] = vparams.pop('rp')
            return fparams
        else:
            return None
    return fparams

def formatunitachieverateparams(fparams,vparams):
    if type(fparams)==dict:
        fparams['price'] = vparams.pop('price')
        fparams['gap']=vparams.pop('gap')
        fparams['r'] = vparams.pop('r')
        fparams['rp']=vparams.pop('rp')
        return fparams
    else:
        return fparams

def getcommonservice(restype,model,mfunc,vparams):
    modeltype=mfunc.split('_')[-1]
    if modeltype=='model':
        fparams=formatmodelxparams(model=model,mfunc=mfunc)
        modeltype='Model'
    elif modeltype in ['modelset','frameset']:
        fparams=formatmodelsetxparams(modelset=model,mfunc=mfunc,vparams=vparams)
        modeltype='ModelSet'
    else:
        print("非法参数")
        return None
    fparams=globals()['format'+restype.lower()+'params'](fparams=fparams,vparams=vparams)
    if type(fparams)==dict:
        try:
            params = {'datatype': 'Common', 'modeltype': modeltype, 'restype': restype, 'params':fparams}
            return VQC.service(params)
        except:
            print("网络请求出错")
            return None
    else:
        return None
