"""
可转债定价模型；二叉树模型
"""
import numpy as np
# from cb_pricing_BS import run_time
from hbshare.quant.Kevin.convertible_bond.cb_pricing_BS import _cashFlowCalc


def _cashFlowDict(termCoupon, strMaturityDate, strNowDate):
    cashFlow, cashFlowTime = _cashFlowCalc(termCoupon, strMaturityDate, strNowDate)
    dictCF = {}
    for i, cash in enumerate(cashFlow):
        dictCF[round(cashFlowTime[i] * 250)] = cash

    return dictCF


def cashFlowGenerator(dictCF, tDate):
    return dictCF[tDate] if tDate in dictCF else 0


def _underlyingTree(s, u, d, numNodes):
    """
    生成股价树
    """
    arrTree = np.zeros([numNodes, numNodes])
    arrTree[0, 0] = s

    for i in range(numNodes):
        for j in range(i + 1):
            arrTree[j, i] = s * (u ** (i - j)) * (d ** j)

    return arrTree


def _calcOptionTree(dictCF, arrTree, x, p_u, p_d, r, convertStart=5.5):
    """
    在已有树的情况下，倒算转债价值
    """
    numNodes = int(max(dictCF))

    arrVal = np.zeros_like(arrTree)
    arrVal[:, -1] = list(map(lambda y: max([x, y]), arrTree[:, -1]))

    r = np.log(1 + r)

    for i in range(numNodes - 2, -1, -1):
        cf = cashFlowGenerator(dictCF, i)

        for j in range(i + 1):
            if i / 250.0 <= convertStart:
                arrVal[j, i] = max(
                    [np.exp(-r / 250.0) * (p_u * arrVal[j, i + 1] + p_d * arrVal[j + 1, i + 1]) + cf, arrTree[j, i]])
            else:
                arrTree[j, i] = np.exp(-r / 250.0) * (p_u * arrVal[j, i + 1] + p_d * arrVal[j + 1, i + 1]) + cf

    return arrVal


def binomialTree(dictCF, s, x, vol, r, convertStart=5.5):
    """
    利用二叉树倒算转债价值
    @param dictCF: 现金流，票息
    @param s: 标的股票的现价
    @param x: 执行价格/转股价格
    @param vol: 股票的标准差
    @param r: 无风险利率
    @param convertStart: 期限
    @return:
    """
    numNodes = max(dictCF)
    u = np.exp(vol * np.sqrt(1 / 250.))
    d = 1 / u
    arrTree = _underlyingTree(s, u, d, int(numNodes))

    rc = np.log(1 + r)
    p_u = (np.exp(rc / 250.0) - d) / (u - d)
    p_d = 1 - p_u

    arrVal = _calcOptionTree(dictCF, arrTree, x, p_u, p_d, r, convertStart)

    return arrVal[0, 0]


# @run_time
def cbPricingTree(stock, term, now, vol, r, isPrint=True):
    """
    二叉树定价函数
    @param stock: 当前股价
    @param term: 转债条款变量
    @param now: 当前日期
    @param vol: 隐含波动率
    @param r: 无风险利率(同等级期限信用债收益率)
    @param isPrint
    """
    dictCF = _cashFlowDict(term['Coupon'], term['Maturity'], now)

    s = stock / term['ConvPrice'] * 100
    x = term['Coupon'][-1]
    convertstart = term['ConvertStart']

    ret = binomialTree(dictCF, s, x, vol, r, convertstart)

    if isPrint:
        print("二叉树模型估算的可转债价值: {}".format(ret, '0.2f'))

    return ret


if __name__ == '__main__':
    term_CB = {
        "ConvPrice": 100,
        "Maturity": "2022/3/10",
        "ConvertStart": 5.5,
        "Coupon": [0.3, 0.5, 0.8, 1.3, 1.5, 108],
        "Recall": [5.5, 15, 30, 130],
        "Resell": [2, 30, 30, 70, 103]
    }

    stock_price = 115.0
    stock_vol = 0.258672
    rate = 0.038

    now_date = '2019/6/16'

    cbPricingTree(stock_price, term_CB, now_date, stock_vol, rate)