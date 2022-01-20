FIRST_NEWARE_DATA_TABLE = 'main_first_table'
SECOND_NEWARE_DATA_TABLE = 'main_second_table'
FIRST_NEWARE_AUX_TABLE = 'aux_first_table'
SECOND_NEWARE_AUX_TABLE = 'aux_second_table'

NW_VOLTAGE = 'test_vol'
NW_CURRENT = 'test_cur'
NW_TEMP = 'test_tmp'
NW_AUX_CHANNEL = 'auxchl_id'
NW_STEP_RANGE = 'cur_step_range'
NW_TIMESTAMP = 'test_time'
NW_DATESTAMP = 'test_atime'
NW_CAP_CHG = 'test_capchg'
NW_CAP_DCHG = 'test_capdchg'
NW_ENGY_CHG = 'test_engchg'
NW_ENGY_DCHG = 'test_engdchg'

NW_SEQ = 'seq_id'
NW_IP = 'ip'
NW_DEVICE = 'dev_uid'
NW_UNIT = 'unit_id'
NW_CHANNEL = 'chl_id'
NW_TEST = 'test_id'
NW_CYCLE = 'cycle'
NW_STEP = 'step_id'
NW_STEP_TYPE = 'step_type'

NW_CACHE_CAP_CHG = 'cap_chg'
NW_CACHE_CAP_DCHG = 'cap_dchg'
NW_CACHE_ENGY_CHG = 'engy_chg'
NW_CACHE_ENGY_DCHG = 'engy_dchg'
NW_CACHE_CC_RATIO = 'cc_ratio'
NW_CACHE_CC_CAP_RATIO = 'cc_cap_ratio'
NW_CACHE_OCV_DRP_CHG = 'ocv_drop_chg'
NW_CACHE_OCV_DRP_DCHG = 'ocv_drop_dchg'
NW_CACHE_V_MIN = 'v_min'
NW_CACHE_V_MAX = 'v_max'
NW_CACHE_R_CHG = 'r_chg'
NW_CACHE_R_DCHG = 'r_dchg'
NW_CACHE_DUR = 'duration'

NW_CACHE_MERGED_COLUMNS = [
    NW_CYCLE, NW_CACHE_CAP_CHG, NW_CACHE_CAP_DCHG, NW_CACHE_ENGY_CHG, NW_CACHE_ENGY_DCHG,
    NW_CACHE_CC_RATIO, NW_CACHE_CC_CAP_RATIO, NW_CACHE_OCV_DRP_CHG, NW_CACHE_OCV_DRP_DCHG,
    NW_CACHE_V_MIN, NW_CACHE_V_MAX, NW_CACHE_R_CHG, NW_CACHE_R_DCHG, NW_CACHE_DUR
]

NW_DATA_SIGNIFICANT_COLUMNS = [
    NW_UNIT, NW_CHANNEL, NW_TEST, NW_SEQ, NW_CYCLE, NW_STEP, NW_STEP_TYPE, 
    NW_TIMESTAMP, NW_VOLTAGE, NW_CURRENT, NW_STEP_RANGE, NW_DATESTAMP,
    NW_CAP_CHG, NW_CAP_DCHG, NW_ENGY_CHG, NW_ENGY_DCHG
]

NW_AUX_SIGNIFICANT_COLUMNS = [NW_AUX_CHANNEL, NW_TEMP]

NW_CACHE_CYCLE_SEQ = 'cycle_end_seq'

NW_CHANNEL_GROUP = 'auxchl_'

PREV_SUFFIX = '_prev'

CACHE_CONNECTION_KWARG = 'cache_connection'
TTL_KWARG = 'ttl'

OUTLIER_STD_COEFFECIENT = 3