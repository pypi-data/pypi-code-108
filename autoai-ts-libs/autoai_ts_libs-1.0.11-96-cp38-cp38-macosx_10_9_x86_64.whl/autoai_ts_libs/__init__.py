#import autoai_ts_libs as dummy_ai4ml_ts
#import sys
#if  not 'ai4ml_ts' in sys.modules:
#    sys.modules['ai4ml_ts'] = dummy_ai4ml_ts
try:
    import ai4ml_ts
except:
    import sys
    from autoai_ts_libs import watfore
    #sys.modules['ai4ml_ts'] = autoai_ts_libs
    sys.modules['ai4ml_ts.estimators'] = watfore

#     from autoai_ts_libs import watfore
#     sys.modules['ai4ml_ts'] = watfore
#     sys.modules['ai4ml_ts.estimators'] = watfore