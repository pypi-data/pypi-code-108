# 著作者：叶凯文
# Author: YE KAIWEN
# 版权归著作者叶凯文所有
# Copyright (c) 2022 YE KAIWEN. All Rights Reserved.

from .StockModelSets import company_modelset

class strict_latest_status_frameset(company_modelset):

    def __init__(self, stockcode,reportdate, minstep, significance, seasonal=False, anneal=None, conservative=False, adjdate=None, ttm=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self, stockcode,reportdate, minstep, significance, seasonal=False, anneal=None, conservative=False, adjdate=None, ttm=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class probable_latest_status_frameset(company_modelset):

    def __init__(self,stockcode,reportdate, minstep, significance, seasonal=False, anneal=None, conservative=False, adjdate=None, ttm=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,stockcode,reportdate, minstep, significance, seasonal=False, anneal=None, conservative=False, adjdate=None, ttm=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class long_range_status_frameset(company_modelset):

    def __init__(self,stockcode,reportdate, significance, seasonal=False, anneal=None, samplerange=None, conservative=False, adjdate=None, ttm=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,stockcode,reportdate, significance, seasonal=False, anneal=None, samplerange=None, conservative=False, adjdate=None, ttm=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class strict_latest_long_range_frameset(company_modelset):

    def __init__(self,stockcode,reportdate, minstep, significance, inertia, seasonal=False, anneal=None, samplerange=None, adjdate=None, ttm=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,stockcode,reportdate, minstep, significance, inertia, seasonal=False, anneal=None, samplerange=None, adjdate=None, ttm=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class probable_latest_long_range_frameset(company_modelset):

    def __init__(self,stockcode,reportdate, minstep, significance, inertia, seasonal=False, anneal=None, samplerange=None, adjdate=None, ttm=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,stockcode,reportdate, minstep, significance, inertia, seasonal=False, anneal=None, samplerange=None, adjdate=None, ttm=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class series_shape_frameset(company_modelset):

    def __init__(self,stockcode,reportdate, significance, seasonal=False, conservative=False, adjdate=None, ttm=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,stockcode,reportdate, significance, seasonal=False, conservative=False, adjdate=None, ttm=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class ma_strict_latest_status_shape_frameset(company_modelset):

    def __init__(self,stockcode,reportdate,mawindow,minstep, significance, seasonal=False, conservative=False, adjdate=None, ttm=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,stockcode,reportdate,mawindow,minstep, significance, seasonal=False, conservative=False, adjdate=None, ttm=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class ma_probable_latest_status_shape_frameset(company_modelset):

    def __init__(self,stockcode,reportdate,mawindow,minstep, significance, seasonal=False, conservative=False, adjdate=None, ttm=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,stockcode,reportdate,mawindow,minstep, significance, seasonal=False, conservative=False, adjdate=None, ttm=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class ma_strict_latest_status_frameset(company_modelset):

    def __init__(self,stockcode,reportdate, mawindow, minstep, seasonal=False, anneal=None, conservative=False, adjdate=None, ttm=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,stockcode,reportdate, mawindow, minstep, seasonal=False, anneal=None, conservative=False, adjdate=None, ttm=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class ma_probable_latest_status_frameset(company_modelset):

    def __init__(self,stockcode,reportdate, mawindow, minstep,significance, seasonal=False, anneal=None, conservative=False, adjdate=None, ttm=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,stockcode,reportdate, mawindow, minstep,significance, seasonal=False, anneal=None, conservative=False, adjdate=None, ttm=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)

class ma_long_range_status_frameset(company_modelset):

    def __init__(self,stockcode,reportdate, mawindow, significance, seasonal=False, anneal=None, samplerange=None, conservative=False, adjdate=None, ttm=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().__init__(mparams)

    def resetparams(self,stockcode,reportdate, mawindow, significance, seasonal=False, anneal=None, samplerange=None, conservative=False, adjdate=None, ttm=False):
        mparams = locals()
        del mparams['self']
        del mparams['__class__']
        super().resetparams(mparams)