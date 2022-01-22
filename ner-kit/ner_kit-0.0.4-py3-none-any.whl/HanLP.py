from pyhanlp import *

def get_entity_list_by_hanlp(text,recognize=""):

    ha_model=HanLP.newSegment()
    if recognize=="":
        ha_model = HanLP.newSegment()
    elif recognize=="name":
        # 中国人名识别
        ha_model = HanLP.newSegment().enableNameRecognize(True)
    elif recognize=="place":
        # 地名识别
        ha_model = HanLP.newSegment().enablePlaceRecognize(True)
    elif recognize=="organization":
        # 机构名识别
        ha_model = HanLP.newSegment().enableOrganizationRecognize(True)
    res = ha_model.seg(text)
    return res
