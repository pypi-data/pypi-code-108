"""avgper 과 yieldgap 계산
"""
import math
from db_hj3415 import mongo
from eval_hj3415 import eval
from util_hj3415 import utils

import logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(levelname)s: [%(name)s] %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.WARNING)


def avg_per() -> float:
    # 가중조화평균으로 평균 per 산출 mi db에 저장
    per_r_cap_all = []
    cap_all = []
    eval_list = eval.make_today_eval_df().to_dict('records')
    for data in eval_list:
        # eval data: {'code': '111870', '종목명': 'KH 일렉트론', '주가': 1070, 'PER': -2.28, 'PBR': 0.96,
        # '시가총액': 103300000000, 'RED': -11055.0, '주주수익률': -7.13, '이익지표': -0.30426, 'ROIC': -40.31,
        # 'ROE': 0.0, 'PFCF': -7.7, 'PCR': nan}
        logger.debug(f'eval data: {data}')
        if math.isnan(data['PER']) or data['PER'] == 0:
            continue
        if math.isnan(data['시가총액']):
            continue
        cap_all.append(data['시가총액'])
        per_r_cap_all.append((1 / data['PER']) * data['시가총액'])
    logger.debug(f'Count cap_all :{len(cap_all)}')
    logger.debug(f'Count per_r_cap_all : {len(per_r_cap_all)}')
    try:
        return round(sum(cap_all) / sum(per_r_cap_all), 2)
    except ZeroDivisionError:
        return float('nan')


def yield_gap(avg_per: float) -> float:
    # 장고에서 사용할 yield gap, mi db에 저장
    date, gbond3y = mongo.MI(index='gbond3y').get_recent()
    if math.isnan(avg_per) or avg_per == 0:
        return float('nan')
    else:
        yield_share = (1 / avg_per) * 100
        yield_gap = round(yield_share - utils.to_float(gbond3y), 2)
        logger.debug(f"Date - {date}, gbond3y - {gbond3y}, yield_gap - {yield_gap}")
        return yield_gap
