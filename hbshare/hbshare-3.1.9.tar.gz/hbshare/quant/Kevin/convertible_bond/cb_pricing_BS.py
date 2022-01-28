"""
可转债定价模型；B-S模型
"""
import numpy as np
import datetime as dt
import time
from scipy.stats import norm


def run_time(func):
    def call_fun(*args, **kwargs):
        start_time = time.time()
        func(*args, **kwargs)
        end_time = time.time()
        print('程序用时：%s秒' % (end_time - start_time))
    return call_fun


def _cashFlowCalc(termCoupon, strMaturityDate, strNowDate):
    """
    @param termCoupon: 票息
    @param strMaturityDate: 到期日
    @param strNowDate: 现在的日期
    """
    dtMaturityDate = dt.datetime.strptime(strMaturityDate, '%Y/%m/%d')
    dtNowDate = dt.datetime.strptime(strNowDate, '%Y/%m/%d')
    numPtmYears = (dtMaturityDate - dtNowDate).days / 365.0

    n = len(termCoupon)
    numDig, numRound = np.modf(numPtmYears)
    numPayment = int(np.min([numRound + 1, n]))

    cashFlow = termCoupon[-numPayment:]
    cashFlowTime = np.arange(numPayment) + numDig

    return cashFlow, cashFlowTime


def _pv(cashFlow, cashFlowTime, r):
    """
    @param cashFlow: 现金流
    @param cashFlowTime: 现金流对应时间
    @param r: 无风险利率
    """
    ret = 0

    for t, cash in enumerate(cashFlow):
        ret += cash / ((1 + r) ** cashFlowTime[t])

    return ret


def bondPrice(termCoupon, strMaturityDate, strNowDate, r):
    cashFlow, cashFlowTime = _cashFlowCalc(termCoupon, strMaturityDate, strNowDate)
    ret = _pv(cashFlow, cashFlowTime, r)

    return ret


def blackScholes(s, x, t, vol, r):
    """
    @param s: 标的股票的现价
    @param x: 执行价格/转股价格
    @param t: 期权到期日，按年计
    @param vol: 股票的标准差
    @param r: 无风险利率
    """
    d1 = (np.log(s / x) + (r + 0.5 * (vol ** 2)) * t) / (vol * np.sqrt(t))
    d2 = d1 - vol * np.sqrt(t)

    ret = s * norm.cdf(d1) - x * np.exp(-r * t) * norm.cdf(d2)

    return ret


def cbPricingBlackScholes(stock, term, now, vol, r, isPrint=True):
    """
    B-S定价模型
    @param stock: 当前股价
    @param term: 转债条款变量
    @param now: 当前日期
    @param vol: 隐含波动率
    @param r: 无风险利率(同等级期限信用债收益率)
    @param isPrint
    """
    straightBondValue = bondPrice(term['Coupon'], term['Maturity'], now, r)

    if isPrint:
        print("B-S模型的债底: {}".format(straightBondValue, '0.2f'))

    s = stock
    x = term['ConvPrice'] * term['Coupon'][-1] / 100.0

    dtMaturityDate = dt.datetime.strptime(term['Maturity'], '%Y/%m/%d')
    dtNowDate = dt.datetime.strptime(now, '%Y/%m/%d')

    t = (dtMaturityDate - dtNowDate).days / 365.0

    call = blackScholes(s, x, t, vol, np.log(1 + r)) * 100.0 / term['ConvPrice']

    if isPrint:
        print("B-S模型的期权部分: {}".format(call, '0.2f'))

    return straightBondValue, call


if __name__ == '__main__':
    # 山鹰转债为例
    term_CB = {
        "ConvPrice": 3.3,
        "Maturity": "2024/11/21",
        "ConvertStart": 5.5,
        "Coupon": [0.4, 0.6, 1.0, 1.5, 2.0, 113],
        "Recall": [5.5, 15, 30, 130],
        "Resell": [2, 30, 30, 70, 103]
    }

    stock_price = 3.62
    bond_value, option_value = cbPricingBlackScholes(stock_price, term_CB, '2021/9/17', 0.01, 0.0258)
    print(bond_value + option_value)