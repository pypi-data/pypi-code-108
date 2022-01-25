"""
可转债定价模型；Monte-Carlo
"""
import numpy as np
# from cb_pricing_BS import run_time
from hbshare.quant.Kevin.convertible_bond.cb_pricing_BS import _pv
from cb_pricing_Tree import _cashFlowDict


def _monteCarlo(stock, vol, r, numNodes, numToMock=10000):
    """模拟风险中性世界下的股价"""
    arrStock = np.ones([numToMock, numNodes + 1])
    dt = 1 / 250.
    rc = np.log(1 + r)

    arrMock = np.cumprod(
        np.exp((rc - 0.5 * (vol ** 2)) * dt + vol * np.sqrt(dt) * np.random.randn(numToMock, numNodes)), axis=1)

    arrStock[:, 1:] = arrMock
    arrStock *= stock

    return arrStock


def _sliceInMC(array, point, length):

    return array[int(max([0, point - length])): int(point)]


def _isRecall(arr, arrTimeSeries, recall_term):
    logicTime = np.array(arrTimeSeries[:]) < recall_term[0]
    logicPrice = arr[:] > recall_term[-1]

    return 1 if np.sum(1 * logicTime * logicPrice) >= recall_term[1] else 0


def _isResell(arr, arrTimeSeries, resell_term):
    logicTime = np.array(arrTimeSeries[:]) < resell_term[0]
    logicPrice = arr[:] < resell_term[-2]

    return 1 if np.sum(1 * logicTime * logicPrice) >= resell_term[1] else 0


def _processRecall(term, row, i, arrTimeSeries):

    if row[i] > term['Recall'][-1]:
        sliceArr = _sliceInMC(row, i, term['Recall'][2])
        sliceArrTimeSeries = _sliceInMC(arrTimeSeries, i, term['Recall'][2])

        isBeRecall = _isRecall(sliceArr, sliceArrTimeSeries, term['Recall'])

        if isBeRecall:
            thisRowEndTime = i / 250.
            thisRowValue = row[i]
        else:
            thisRowEndTime = None
            thisRowValue = None

        return isBeRecall, thisRowEndTime, thisRowValue
    else:
        return None, None, None


def _processResell(term, row, i, arrTimeSeries):

    if row[i] < term['Resell'][-2]:
        sliceArr = _sliceInMC(row, i, term['Resell'][2])
        sliceArrTimeSeries = _sliceInMC(arrTimeSeries, i, term['Resell'][2])

        isBeResell = _isResell(sliceArr, sliceArrTimeSeries, term['Resell'])

        if isBeResell:
            thisRowEndTime = i / 250.
            thisRowValue = term['Resell'][-1]
        else:
            thisRowEndTime = None
            thisRowValue = None

        return isBeResell, thisRowEndTime, thisRowValue
    else:
        return None, None, None


def _pvCashFlowMC(thisRowEndTime, thisRowValue, dictCF, r):

    cfT, cf = [thisRowEndTime], [thisRowValue]

    for time in dictCF:
        if time / 250.0 < thisRowEndTime:
            cfT.append(time / 250.0)
            cf.append(dictCF[time])

    return _pv(cf, cfT, r)


# @run_time
def cbPricingMC(stock, term, now, vol, r, numToMock=10000, isPrint=True):
    """
    MC定价函数
    @param stock: 当前股价
    @param term: 转债条款变量
    @param now: 当前日期
    @param vol: 隐含波动率
    @param r: 无风险利率(同等级期限信用债收益率)
    @param numToMock: 模拟次数
    @param isPrint
    """
    dictCF = _cashFlowDict(term['Coupon'], term['Maturity'], now)

    numNodes = int(max(dictCF))
    arrTimeSeries = [(numNodes - i) / 250.0 for i in range(numNodes)]

    arrMC = _monteCarlo(stock, vol, r, numNodes, numToMock)

    v = []
    j = 0
    k = 0
    for row in arrMC:
        for i in range(numNodes):
            # 是否触发赎回
            isBeRecall, thisRowEndTime, thisRowValue = _processRecall(term, row, i, arrTimeSeries)

            if isBeRecall:
                j += 1
                thisRowValue *= 100 / term['ConvPrice']
                v.append(_pvCashFlowMC(thisRowEndTime, thisRowValue, dictCF, r))
                break
            # 是否触及回售
            isBeResell, thisRowEndTime, thisRowValue = _processResell(term, row, i, arrTimeSeries)

            if isBeResell:
                k += 1
                thisRowValue *= 100 / term['ConvPrice']
                v.append(_pvCashFlowMC(thisRowEndTime, thisRowValue, dictCF, r))
                break

        else:
            # 整个生命周期都没有触发条款，计算到期价值
            thisRowEndTime = numNodes / 250.
            thisRowValue = np.max([row[-1] * 100 / term['ConvPrice'], term['Coupon'][-1]])

            v.append(_pvCashFlowMC(thisRowEndTime, thisRowValue, dictCF, r))

    if isPrint:
        print("MC模型的可转债价值: {}".format(np.mean(v), '0.2f'))
        # print("赎回路径次数: {}".format(j))
        # print("回售路径次数: {}".format(k))

    return np.mean(v)


if __name__ == '__main__':
    # term_CB = {
    #     "ConvPrice": 14.01,
    #     "Maturity": "2025/12/19",
    #     "ConvertStart": 5.5,
    #     "Coupon": [0.5, 0.8, 1.2, 1.8, 2.5, 118],
    #     "Recall": [5.5, 15, 30, 130],
    #     "Resell": [2, 30, 30, 70, 103]
    # }
    #
    # stock_price = 77.4
    # stock_vol = 0.80047
    # rate = 0.067289
    #
    # now_date = '2020/8/21'

    term_CB = {
        "ConvPrice": 10.66,
        "Maturity": "2021/2/1",
        "ConvertStart": 5.5,
        "Coupon": [0.2, 0.5, 1.0, 1.5, 1.5, 106.6],
        "Recall": [5.5, 15, 30, 130],
        "Resell": [2, 30, 30, 70, 103]
    }

    stock_price = 11.99
    # stock_price = stock_price * 100 / term_CB['ConvPrice']
    stock_vol = 0.7847
    rate = 0.029659

    now_date = '2015/9/22'

    term_CB['Recall'][-1] *= term_CB['ConvPrice'] / 100
    term_CB['Resell'][-2] *= term_CB['ConvPrice'] / 100
    term_CB['Resell'][-1] *= term_CB['ConvPrice'] / 100
    cbPricingMC(stock_price, term_CB, now_date, stock_vol, rate)