#Chek if autoai4ml_ts is available if not then set tslibs
try:
    import ai4ml_ts
except:
    import sys
    from autoai_ts_libs import watfore
    sys.modules['ai4ml_ts'] = watfore
    sys.modules['ai4ml_ts.estimators'] = watfore