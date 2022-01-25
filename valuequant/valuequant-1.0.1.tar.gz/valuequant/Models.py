# 著作者：叶凯文
# Author: YE KAIWEN
# 版权归著作者叶凯文所有
# Copyright (c) 2022 YE KAIWEN. All Rights Reserved.

import pandas as pd

from .commonform import getcommonmodel,getcommonservice,seriestoformat

class common_model:

    def __init__(self,mparams):
        mparams['series']=mparams['series'].sort_index(ascending=True)
        mparams['datalist'],mparams['startdate'],mparams['freq']=seriestoformat(mparams['series'])
        self._data=mparams['series']
        del mparams['series']
        self._mparams=mparams
        self.__getmodel()

    def resetparams(self,mparams):
        mparams['series']=mparams['series'].sort_index(ascending=True)
        mparams['datalist'],mparams['startdate'],mparams['freq']=seriestoformat(mparams['series'])
        self._data=mparams['series']
        del mparams['series']
        self._mparams=mparams
        if hasattr(self,'_model'):
            del self._model
        if hasattr(self,'_fit'):
            del self._fit
        self.__getmodel()

    def __getmodel(self):
        res=getcommonmodel(mfunc=type(self).__name__,mparams=self._mparams.copy())
        if type(res)==dict:
            self._model=res['model']
            self._fit=res['fit']

    def model(self):
        if hasattr(self, '_model')==False:
            self.__getmodel()
        if hasattr(self,'_model'):
            return self._model
        else:
            return None

    def fit(self):
        if hasattr(self,'_fit')==False:
            self.__getmodel()
        if hasattr(self,'_fit'):
            inx=pd.date_range(start=self._mparams['startdate'],freq=self._mparams['freq'],periods=len(self._mparams['datalist']))
            if 'step' in self._model.keys():
                return pd.Series(self._fit[-self._model['step']:],index=inx[-self._model['step']:]).dropna()
            else:
                return pd.Series(self._fit, index=inx[-len(self._fit):]).dropna()
        else:
            return None

    def __getservice(self,restype,vparams):
        if hasattr(self,'_model')==False:
            self.__getmodel()
        if hasattr(self,'_model'):
            res = getcommonservice(restype=restype, model=self._model, mfunc=type(self).__name__, vparams=vparams)
            return res
        else:
            return None

    def forecast(self,t):
        inx=pd.date_range(start=self._mparams['startdate'],freq=self._mparams['freq'],periods=(len(self._mparams['datalist'])+t))
        fore=self.__getservice(restype='Forecast',vparams={'t':t})
        if type(fore)==list:
            return pd.Series(fore,index=inx[-t:])
        else:
            return None

    def pv(self,r):
        return self.__getservice(restype='PV',vparams={'r':r})

    def __getdcdate(self):
        return pd.date_range(start=self._mparams['startdate'],freq=self._mparams['freq'],periods=(len(self._mparams['datalist'])+1))[-1]

    def __getrp(self):
        if self._mparams['seasonal']:
            return 360
        else:
            return int(360/len(pd.date_range(start='2022-01-01',end='2022-12-31',freq=self._mparams['freq'])))

    def irr(self,price,tradedate):
        return self.__getservice(restype='UnitIRR',vparams={'price':price,'rp':self.__getrp(),'gap':(self.__getdcdate()-pd.to_datetime(tradedate)).days})

    def batchirr(self,priceseries):
        vparams={}
        vparams['pricelist'], vparams['pricestart'], vparams['pricefreq']=seriestoformat(priceseries)
        vparams['dcdate']=self.__getdcdate().strftime('%Y-%m-%d')
        vparams['rp']=self.__getrp()
        res=self.__getservice(restype='BatchIRR', vparams=vparams)
        if type(res)==dict:
            df=pd.DataFrame()
            df['IRRs']=pd.Series(res['IRRs'],index=priceseries.index)
            df['errors']=pd.Series(res['errors'],index=priceseries.index)
            return df
        else:
            return None

    def achieverate(self,price,r,tradedate):
        return self.__getservice(restype='UnitAchieverate',vparams={'price':price,'r':r,'rp':self.__getrp(),'gap':(self.__getdcdate()-pd.to_datetime(tradedate)).days})

    def batchachieverate(self,priceseries,r):
        vparams = {}
        vparams['pricelist'], vparams['pricestart'], vparams['pricefreq'] = seriestoformat(priceseries)
        vparams['r']=r
        vparams['dcdate']=self.__getdcdate().strftime('%Y-%m-%d')
        vparams['rp'] = self.__getrp()
        res=self.__getservice(restype='BatchAchieverate', vparams=vparams)
        if type(res)==list:
            return pd.Series(res,index=priceseries.index)
        else:
            return None

    def data(self):
        return self._data

class strict_latest_status_model(common_model):

    def __init__(self,series,minstep,significance,seasonal=False,anneal=None,conservative=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,series,minstep,significance,seasonal=False,anneal=None,conservative=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class probable_latest_status_model(common_model):

    def __init__(self,series,minstep,significance,seasonal=False,anneal=None,conservative=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,series,minstep,significance,seasonal=False,anneal=None,conservative=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class long_range_status_model(common_model):

    def __init__(self,series,significance,seasonal=False,anneal=None,samplerange=None,conservative=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,series,significance,seasonal=False,anneal=None,samplerange=None,conservative=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class strict_latest_long_range_model(common_model):

    def __init__(self,series,minstep,significance,inertia,seasonal=False,anneal=None,samplerange=None):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,series,minstep,significance,inertia,seasonal=False,anneal=None,samplerange=None):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class probable_latest_long_range_model(common_model):

    def __init__(self,series,minstep,significance,inertia,seasonal=False,anneal=None,samplerange=None):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,series,minstep,significance,inertia,seasonal=False,anneal=None,samplerange=None):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class series_shape_model(common_model):

    def __init__(self,series,significance,seasonal=False,conservative=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,series,significance,seasonal=False,conservative=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class ma_strict_latest_status_shape_model(common_model):

    def __init__(self,series,mawindow,minstep,significance,seasonal=False,conservative=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,series,mawindow,minstep,significance,seasonal=False,conservative=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class ma_probable_latest_status_shape_model(common_model):

    def __init__(self,series,mawindow,minstep,significance,seasonal=False,conservative=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,series,mawindow,minstep,significance,seasonal=False,conservative=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class ma_strict_latest_status_model(common_model):

    def __init__(self,series,mawindow,minstep,seasonal=False,anneal=None,conservative=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,series,mawindow,minstep,seasonal=False,anneal=None,conservative=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class ma_probable_latest_status_model(common_model):

    def __init__(self,series,mawindow,minstep,significance,seasonal=False,anneal=None,conservative=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,series,mawindow,minstep,significance,seasonal=False,anneal=None,conservative=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class ma_long_range_status_model(common_model):

    def __init__(self,series,mawindow,significance,seasonal=False,anneal=None,samplerange=None,conservative=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,series,mawindow,significance,seasonal=False,anneal=None,samplerange=None,conservative=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

