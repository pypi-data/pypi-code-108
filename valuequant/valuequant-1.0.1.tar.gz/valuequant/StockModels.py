# 著作者：叶凯文
# Author: YE KAIWEN
# 版权归著作者叶凯文所有
# Copyright (c) 2022 YE KAIWEN. All Rights Reserved.

import pandas as pd

from .commonform import getcommonservice,seriestoformat
from .companyform import getcompanymodel,getcompanyservice,getcompanydata

AFREQS={'3-31':'A-MAR','6-30':'A-JUN','9-30':'A-SEP','2-31':'A-DEC'}

class company_model:

    def __init__(self,mparams):
        if mparams['adjdate']:
            pass
        else:
            mparams['adjdate']=mparams['reportdate']
        self._mparams = mparams
        self.__getmodel()

    def resetparams(self,mparams):
        self._mparams=mparams
        if hasattr(self,'_model'):
            del self._model
        if hasattr(self,'_fit'):
            del self._fit
        if hasattr(self,'_incdata'):
            del self._incdata
        self.__getmodel()

    def __getmodel(self):
        res=getcompanymodel(mfunc=type(self).__name__,mparams=self._mparams.copy())
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
            if self._mparams['ttm']:
                fit = pd.Series(self._fit, index=pd.date_range(end=self._mparams['reportdate'], freq=AFREQS[self._mparams['reportdate'][-4:]], periods=len(self._fit)))
            else:
                fit=pd.Series(self._fit,index=pd.date_range(end=self._mparams['reportdate'],freq='Q-DEC',periods=len(self._fit)))
            if 'step' in self._model.keys():
                return fit[-self._model['step']:].dropna()
            else:
                return fit
        else:
            return None

    def __getservice(self,restype,vparams):
        if hasattr(self,'_model')==False:
            self.__getmodel()
        if hasattr(self,'_model'):
            res = getcommonservice(restype=restype, model=self._model,mfunc=type(self).__name__, vparams=vparams)
            return res
        else:
            return None

    def forecast(self,t):
        if self._mparams['ttm']:
            inx = pd.date_range(start=self._mparams['reportdate'], freq=AFREQS[self._mparams['reportdate'][-4:]], periods=(1 + t))
        else:
            inx=pd.date_range(start=self._mparams['reportdate'],freq='Q-DEC',periods=(1+t))
        fore=self.__getservice(restype='Forecast',vparams={'t':t})
        if type(fore)==list:
            return pd.Series(fore,index=inx[-t:])
        else:
            return None

    def pv(self,r):
        return self.__getservice(restype='PV',vparams={'r':r})

    def __getdcdate(self):
        if self._mparams['ttm']:
            return pd.date_range(start=self._mparams['reportdate'], freq=AFREQS[self._mparams['reportdate'][-4:]], periods=2)[-1]
        else:
            return pd.date_range(start=self._mparams['reportdate'],freq='Q-DEC',periods=2)[-1]

    def __getrp(self):
        if self._mparams['ttm']:
            return 360
        elif self._mparams['seasonal']:
            return 360
        else:
            return 90

    def irr(self,price,tradedate):
        return self.__getservice(restype='UnitIRR',vparams={'price':price,'rp':self.__getrp(),'gap':(self.__getdcdate()-pd.to_datetime(tradedate)).days})

    def batchirr(self,priceseries):
        vparams = {}
        vparams['pricelist'], vparams['pricestart'], vparams['pricefreq'] = seriestoformat(priceseries)
        vparams['dcdate']=self.__getdcdate().strftime('%Y-%m-%d')
        vparams['rp'] = self.__getrp()
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

    def __gettradeservice(self,restype,vparams):
        if hasattr(self,'_model')==False:
            self.__getmodel()
        if hasattr(self,'_model'):
            res = getcompanyservice(restype=restype, model=self._model,mparams=self._mparams.copy(), mfunc=type(self).__name__, vparams=vparams)
            return res
        else:
            return None

    def irr_trade(self,pricemode,tradedate):
        vparams=locals()
        del vparams['self']
        vparams['rp'] = self.__getrp()
        return self.__gettradeservice(restype='UnitIRR',vparams=vparams)

    def batchirr_trade(self,pricemode,startdate,enddate):
        vparams=locals()
        del vparams['self']
        vparams['rp'] = self.__getrp()
        res=self.__gettradeservice(restype='BatchIRR',vparams=vparams)
        if type(res)==dict:
            df=pd.DataFrame()
            df['IRRs']=pd.Series(res['IRRs'])
            df['errors']=pd.Series(res['errors'])
            return df
        else:
            return None

    def achieverate_trade(self,pricemode,tradedate,r):
        vparams=locals()
        del vparams['self']
        vparams['rp'] = self.__getrp()
        return self.__gettradeservice(restype='UnitAchieverate',vparams=vparams)

    def batchachieverate_trade(self,pricemode,startdate,enddate,r):
        vparams=locals()
        del vparams['self']
        vparams['rp'] = self.__getrp()
        res=self.__gettradeservice(restype='BatchAchieverate',vparams=vparams)
        if type(res)==dict:
            return pd.Series(res)
        else:
            return None

    def __getincdata(self):
        res=getcompanydata(stockcode=self._mparams['stockcode'],reportdate=self._mparams['reportdate'],dimension=self._mparams['dimension'],adjdate=self._mparams['adjdate'],ttm=self._mparams['ttm'])
        if type(res)==dict:
            data = pd.Series(res)
            data.index = pd.to_datetime(data.index)
            self._incdata=data

    def incdata(self):
        if hasattr(self,'_incdata')==False:
            self.__getincdata()
        if hasattr(self,'_incdata'):
            return self._incdata
        else:
            return None

class strict_latest_status_model(company_model):

    def __init__(self,stockcode,dimension,reportdate,minstep,significance,seasonal=False,anneal=None,conservative=False,adjdate=None, ttm=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,stockcode,dimension,reportdate,minstep,significance,seasonal=False,anneal=None,conservative=False,adjdate=None, ttm=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class probable_latest_status_model(company_model):

    def __init__(self,stockcode,dimension,reportdate,minstep,significance,seasonal=False,anneal=None,conservative=False,adjdate=None, ttm=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,stockcode,dimension,reportdate,minstep,significance,seasonal=False,anneal=None,conservative=False,adjdate=None, ttm=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class long_range_status_model(company_model):

    def __init__(self,stockcode,dimension,reportdate,significance,seasonal=False,anneal=None,samplerange=None,conservative=False,adjdate=None, ttm=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,stockcode,dimension,reportdate,significance,seasonal=False,anneal=None,samplerange=None,conservative=False,adjdate=None, ttm=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class strict_latest_long_range_model(company_model):

    def __init__(self,stockcode,dimension,reportdate,minstep,significance,inertia,seasonal=False,anneal=None,samplerange=None,adjdate=None, ttm=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self, stockcode,dimension,reportdate,minstep,significance,inertia,seasonal=False,anneal=None,samplerange=None,adjdate=None, ttm=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class probable_latest_long_range_model(company_model):

    def __init__(self,stockcode,dimension,reportdate,minstep,significance,inertia,seasonal=False,anneal=None,samplerange=None,adjdate=None, ttm=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,stockcode,dimension,reportdate,minstep,significance,inertia,seasonal=False,anneal=None,samplerange=None,adjdate=None, ttm=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class series_shape_model(company_model):

    def __init__(self,stockcode,dimension,reportdate,significance,seasonal=False,conservative=False,adjdate=None, ttm=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,stockcode,dimension,reportdate,significance,seasonal=False,conservative=False,adjdate=None, ttm=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class ma_strict_latest_status_shape_model(company_model):

    def __init__(self,stockcode,dimension,reportdate,mawindow,minstep,significance,seasonal=False,conservative=False,adjdate=None, ttm=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,stockcode,dimension,reportdate,mawindow,minstep,significance,seasonal=False,conservative=False,adjdate=None, ttm=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class ma_probable_latest_status_shape_model(company_model):

    def __init__(self,stockcode,dimension,reportdate,mawindow,minstep,significance,seasonal=False,conservative=False,adjdate=None, ttm=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,stockcode,dimension,reportdate,mawindow,minstep,significance,seasonal=False,conservative=False,adjdate=None, ttm=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class ma_strict_latest_status_model(company_model):

    def __init__(self,stockcode,dimension,reportdate,mawindow,minstep,seasonal=False,anneal=None,conservative=False,adjdate=None, ttm=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,stockcode,dimension,reportdate,mawindow,minstep,seasonal=False,anneal=None,conservative=False,adjdate=None, ttm=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class ma_probable_latest_status_model(company_model):

    def __init__(self,stockcode,dimension,reportdate,mawindow,minstep,significance,seasonal=False,anneal=None,conservative=False,adjdate=None, ttm=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,stockcode,dimension,reportdate,mawindow,minstep,significance,seasonal=False,anneal=None,conservative=False,adjdate=None, ttm=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class ma_long_range_status_model(company_model):

    def __init__(self,stockcode,dimension,reportdate,mawindow,significance,seasonal=False,anneal=None,samplerange=None,conservative=False,adjdate=None, ttm=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,stockcode,dimension,reportdate,mawindow,significance,seasonal=False,anneal=None,samplerange=None,conservative=False,adjdate=None, ttm=False):
        mparams=locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)