# 著作者：叶凯文
# Author: YE KAIWEN
# 版权归著作者叶凯文所有
# Copyright (c) 2022 YE KAIWEN. All Rights Reserved.

import pandas as pd

from .commonform import getcommonmodel,getcommonservice,dftoformat,seriestoformat

class common_modelset:

    def __init__(self,mparams):
        mparams['df']=mparams['df'].sort_index(ascending=True)
        mparams['datalist'],mparams['startdate'],mparams['freq'],mparams['datacols']=dftoformat(mparams['df'])
        self._data=mparams['df']
        del mparams['df']
        self._mparams = mparams
        self.__getmodelset()

    def resetparams(self,mparams):
        mparams['df']=mparams['df'].sort_index(ascending=True)
        mparams['datalist'],mparams['startdate'],mparams['freq'],mparams['datacols']=dftoformat(mparams['df'])
        self._data=mparams['df']
        del mparams['df']
        self._mparams = mparams
        if hasattr(self,'_modelset'):
            del self._modelset
        if hasattr(self,'_fitset'):
            del self._fitset
        self.__getmodelset()

    def __getmodelset(self):
        res=getcommonmodel(mfunc=type(self).__name__,mparams=self._mparams.copy())
        if type(res)==dict:
            self._modelset=res['modelset']
            self._fitset=res['fitset']

    def modelset(self):
        if hasattr(self, '_modelset')==False:
            self.__getmodelset()
        if hasattr(self,'_modelset'):
            return self._modelset
        else:
            return None

    def fit(self,dimension):
        if hasattr(self,'_fitset')==False:
            self.__getmodelset()
        if hasattr(self, '_fitset'):
            inx=pd.date_range(start=self._mparams['startdate'],freq=self._mparams['freq'],periods=len(self._mparams['datalist']))
            if 'model' in self._modelset[dimension].keys():
                if 'step' in self._modelset[dimension]['model'].keys():
                    return pd.Series(self._fitset[dimension][-self._modelset[dimension]['model']['step']:],index=inx[-self._modelset[dimension]['model']['step']:]).dropna()
            return pd.Series(self._fitset[dimension], index=inx[-len(self._fitset[dimension]):]).dropna()
        else:
            return None

    def __getservice(self,restype,vparams):
        if hasattr(self,'_modelset')==False:
            self.__getmodelset()
        if hasattr(self,'_modelset'):
            res = getcommonservice(restype=restype, model=self._modelset, mfunc=type(self).__name__, vparams=vparams)
            return res
        else:
            return None

    def forecast(self,dimension,t):
        inx = pd.date_range(start=self._mparams['startdate'], freq=self._mparams['freq'], periods=(len(self._mparams['datalist']) + t))
        fore=self.__getservice(restype='Forecast',vparams={'t':t,'dimension':dimension})
        if type(fore)==list:
            return pd.Series(fore,index=inx[-t:])
        else:
            return None

    def pv(self,dimension,r):
        return self.__getservice(restype='PV',vparams={'r':r,'dimension':dimension})

    def __getdcdate(self):
        return pd.date_range(start=self._mparams['startdate'],freq=self._mparams['freq'],periods=(len(self._mparams['datalist'])+1))[-1]

    def __getrp(self):
        if self._mparams['seasonal']:
            return 360
        else:
            return int(360 / len(pd.date_range(start='2022-01-01', end='2022-12-31', freq=self._mparams['freq'])))

    def irr(self,dimension,price,tradedate):
        return self.__getservice(restype='UnitIRR',vparams={'price':price,'dimension':dimension,'rp':self.__getrp(),'gap':(self.__getdcdate()-pd.to_datetime(tradedate)).days})

    def batchirr(self,dimension,priceseries):
        vparams = {}
        vparams['pricelist'], vparams['pricestart'], vparams['pricefreq'] = seriestoformat(priceseries)
        vparams['dimension']=dimension
        vparams['dcdate']=self.__getdcdate().strftime('%Y-%m-%d')
        vparams['rp'] = self.__getrp()
        res=self.__getservice(restype='BatchIRR', vparams=vparams)
        if type(res) == dict:
            df = pd.DataFrame()
            df['IRRs'] = pd.Series(res['IRRs'],index=priceseries.index)
            df['errors'] = pd.Series(res['errors'],index=priceseries.index)
            return df
        else:
            return None

    def achieverate(self,dimension,price,r,tradedate):
        return self.__getservice(restype='UnitAchieverate',vparams={'price':price,'r':r,'rp':self.__getrp(),'dimension':dimension,'gap':(self.__getdcdate()-pd.to_datetime(tradedate)).days})

    def batchachieverate(self,dimension,priceseries,r):
        vparams = {}
        vparams['pricelist'], vparams['pricestart'], vparams['pricefreq'] = seriestoformat(priceseries)
        vparams['dimension']=dimension
        vparams['r']=r
        vparams['dcdate']=self.__getdcdate().strftime('%Y-%m-%d')
        vparams['rp'] = self.__getrp()
        res=self.__getservice(restype='BatchAchieverate', vparams=vparams)
        if type(res)==list:
            return pd.Series(res,index=priceseries.index)
        else:
            return None

    def data(self,dimension):
        return self._data[dimension]

class strict_latest_status_modelset(common_modelset):

    def __init__(self,df,structure,minstep,significance,seasonal=False,anneal=None,conservative=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,df,structure,minstep,significance,seasonal=False,anneal=None,conservative=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class probable_latest_status_modelset(common_modelset):

    def __init__(self,df,structure,minstep,significance,seasonal=False,anneal=None,conservative=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,df,structure,minstep,significance,seasonal=False,anneal=None,conservative=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class long_range_status_modelset(common_modelset):

    def __init__(self,df,structure,significance,seasonal=False,anneal=None,samplerange=None,conservative=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,df,structure,significance,seasonal=False,anneal=None,samplerange=None,conservative=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class strict_latest_long_range_modelset(common_modelset):

    def __init__(self,df,structure,minstep,significance,inertia,seasonal=False,anneal=None,samplerange=None):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,df,structure,minstep,significance,inertia,seasonal=False,anneal=None,samplerange=None):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class probable_latest_long_range_modelset(common_modelset):

    def __init__(self,df,structure,minstep,significance,inertia,seasonal=False,anneal=None,samplerange=None):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,df,structure,minstep,significance,inertia,seasonal=False,anneal=None,samplerange=None):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class series_shape_modelset(common_modelset):

    def __init__(self,df,structure,significance,seasonal=False,conservative=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,df,structure,significance,seasonal=False,conservative=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class ma_strict_latest_status_shape_modelset(common_modelset):

    def __init__(self,df,structure,mawindow,minstep,significance,seasonal=False,conservative=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,df,structure,mawindow,minstep,significance,seasonal=False,conservative=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class ma_probable_latest_status_shape_modelset(common_modelset):

    def __init__(self,df,structure,mawindow,minstep,significance,seasonal=False,conservative=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,df,structure,mawindow,minstep,significance,seasonal=False,conservative=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class ma_strict_latest_status_modelset(common_modelset):

    def __init__(self,df,structure,mawindow,minstep,seasonal=False,anneal=None,conservative=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,df,structure,mawindow,minstep,seasonal=False,anneal=None,conservative=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class ma_probable_latest_status_modelset(common_modelset):

    def __init__(self,df,structure,mawindow,minstep,significance,seasonal=False,anneal=None,conservative=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,df,structure,mawindow,minstep,significance,seasonal=False,anneal=None,conservative=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class ma_long_range_status_modelset(common_modelset):

    def __init__(self,df,structure,mawindow,significance,seasonal=False,anneal=None,samplerange=None,conservative=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,df,structure,mawindow,significance,seasonal=False,anneal=None,samplerange=None,conservative=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)
