# -*- coding:utf-8 -*-

import pandas as pd
import numpy as np


class quantify_xoenmap:
    '''
        用于日内分时图交易信号

    '''

    # 初始化
    def __init__(self, decimaldigitcount:int=3):
        self.df = None
        self.data = {}
        self.A1 = None
        self.A2 = None
        self.Exceeds = None
        self.A1X = None
        self.loaded = False
        self.H1 = None
        self.L1 = None
        self.P1 = None

        # ----------------------计算精度---------------------------
        self.decimaldigitcount = decimaldigitcount


        # ------------------------------------------------------

        # -----------------------zig函数参数区----------------------
        self.ZIG_STATE_START = 0
        self.ZIG_STATE_RISE = 1
        self.ZIG_STATE_FALL = 2
        # --------------------------------------------------------


    # ---------------------------0级函数------------------------------------------
    def RD(self, N, D: int = 3):
        # 防止不同交易对或股票的计量精度
        if self.decimaldigitcount <= 0:
            self.decimaldigitcount = 17
            D = self.decimaldigitcount
        else:
            D = self.decimaldigitcount
        return np.round(N, D)  # 四舍五入取3位小数

    def RET(self, S, N=1):
        return np.array(S)[-N]  # 返回序列倒数第N个值,默认返回最后一个

    def ABS(self, S):
        return np.abs(S)  # 返回N的绝对值

    def MAX(self, S1, S2):
        return np.maximum(S1, S2)  # 序列max

    def MIN(self, S1, S2):
        return np.minimum(S1, S2)  # 序列min

    def MA(self, S, N):  # 求序列的N日平均值，返回序列
        return pd.Series(S).rolling(N).mean().values

    def REF(self, S, N=1):  # 对序列整体下移动N,返回序列(shift后会产生NAN)
        return pd.Series(S).shift(N).values

    def DIFF(self, S, N=1):  # 前一个值减后一个值,前面会产生nan
        return pd.Series(S).diff(N)  # np.diff(S)直接删除nan，会少一行

    def STD(self, S, N):  # 求序列的N日标准差，返回序列
        return pd.Series(S).rolling(N).std(ddof=0).values

    def IF(self, S_BOOL, S_TRUE, S_FALSE):  # 序列布尔判断 return=S_TRUE if S_BOOL==True  else  S_FALSE
        return np.where(S_BOOL, S_TRUE, S_FALSE)

    def SUM(self, S, N):  # 对序列求N天累计和，返回序列    N=0对序列所有依次求和
        return pd.Series(S).rolling(N).sum().values if N > 0 else pd.Series(S).cumsum()

    def HHV(self, S, N):  # HHV(C, 5)  # 最近5天收盘最高价
        return pd.Series(S).rolling(N).max().values

    def LLV(self, S, N):  # LLV(C, 5)  # 最近5天收盘最低价
        return pd.Series(S).rolling(N).min().values

    def EMA(self, S, N):  # 指数移动平均,为了精度 S>4*N  EMA至少需要120周期     alpha=2/(span+1)
        return pd.Series(S).ewm(span=N, adjust=False).mean().values

    def SMA(self, S, N, M=1):  # 中国式的SMA,至少需要120周期才精确 (雪球180周期)    alpha=1/(1+com)
        return pd.Series(S).ewm(com=N - M, adjust=True).mean().values

    def AVEDEV(self, S, N):  # 平均绝对偏差  (序列与其平均值的绝对差的平均值)
        return pd.Series(S).rolling(N).apply(lambda x: (np.abs(x - x.mean())).mean()).values

    def SLOPE(self, S, N, RS=False):  # 返S序列N周期回线性回归斜率 (默认只返回斜率,不返回整个直线序列)
        M = pd.Series(S[-N:]);
        poly = np.polyfit(M.index, M.values, deg=1);
        Y = np.polyval(poly, M.index);
        if RS: return Y[1] - Y[0], Y
        return Y[1] - Y[0]

    # ------------------   1级：应用层函数(通过0级核心函数实现） ----------------------------------
    def COUNT(self, S_BOOL, N):  # COUNT(CLOSE>O, N):  最近N天满足S_BOO的天数  True的天数
        return self.SUM(S_BOOL, N)

    def EVERY(self, S_BOOL, N):  # EVERY(CLOSE>O, 5)   最近N天是否都是True
        R = self.SUM(S_BOOL, N)
        return self.IF(R == N, True, False)

    def LAST(self, S_BOOL, A, B):  # 从前A日到前B日一直满足S_BOOL条件
        if A < B: A = B  # 要求A>B    例：LAST(CLOSE>OPEN,5,3)  5天前到3天前是否都收阳线
        return S_BOOL[-A:-B].sum() == (A - B)  # 返回单个布尔值

    def EXIST(self, S_BOOL, N=5):  # EXIST(CLOSE>3010, N=5)  n日内是否存在一天大于3000点
        R = self.SUM(S_BOOL, N)
        return self.IF(R > 0, True, False)

    def BARSLAST(self, S_BOOL):  # 上一次条件成立到当前的周期
        M = np.argwhere(S_BOOL);  # BARSLAST(CLOSE/REF(CLOSE)>=1.1) 上一次涨停到今天的天数
        return len(S_BOOL) - int(M[-1]) - 1 if M.size > 0 else -1

    def FORCAST(self, S, N):  # 返S序列N周期回线性回归后的预测值
        K, Y = self.SLOPE(S, N, RS=True)
        return Y[-1] + K

    def CROSS(self, S1, S2):  # 判断向上金叉穿越 CROSS(MA(C,5),MA(C,10))     判断向下死叉穿越 CROSS(MA(C,10),MA(C,5))
        CROSS_BOOL = self.IF(S1 > S2, True, False)
        return (self.COUNT(CROSS_BOOL > 0, 2) == 1) * CROSS_BOOL  # 上穿：昨天0 今天1   下穿：昨天1 今天0

    # ------------------   2级：技术指标函数(全部通过0级，1级函数实现） ------------------------------
    def ER(self, CLOSE, N=10):
        """
            “EfficiencyRatio效率比值” 概念是美国交易员 Perry J. Kaufman 佩里·考夫曼 提出的，是一种趋势强度的衡量
        :param CLOSE:
        :param N:
        :return:
        """
        return self.ABS(CLOSE - self.REF(CLOSE, N)) \
               / self.SUM(self.ABS(CLOSE - self.REF(CLOSE, 1)), N)

    def AMA(self, CLOSE, N=10, pow1=2, pow2=30):

        '''
            kama indicator 自适应移动平均线AMA
        '''

        ''' accepts pandas dataframe of prices '''

        ER = self.ER(CLOSE, N)
        FASTSC = 2 / (pow1 + 1)  # 快速系数
        SLOWSC = 2 / (pow2 + 1)  # 慢速系数
        SSC = ER * (FASTSC - SLOWSC) + SLOWSC  # 光滑系数
        CONSTANT = SSC * SSC  # 常量
        # print(CONSTANT)
        # AMA = CONSTANT * CLOSE + (1 - CONSTANT) * AMA[i - 1]
        nn = len(CLOSE)

        # AMA[i] = AMA[i - 1] + SSC[i] x（价格[i]–AMA[i - 1]）
        # 其中AMAi为当前AMA的数值，AMAi - 1为前一周期AMA的数值。

        answer = np.zeros(nn)
        first_value = True
        for i in range(nn):

            if CONSTANT.values[i] != CONSTANT.values[i]:
                answer[i] = np.nan
            else:
                if first_value:
                    answer[i] = CLOSE.values[i]
                    first_value = False
                else:
                    answer[i] = answer[i - 1] + CONSTANT.values[i] * (CLOSE.values[i] - answer[i - 1])

            # print("i:{},CONSTANT:{}, CLOSE:{},answer:{}".format(i, CONSTANT.values[i], CLOSE.values[i],answer[i]))
        # print(answer)
        return answer, CONSTANT

    def MACD(self, CLOSE, SHORT=12, LONG=26, M=9):  # EMA的关系，S取120日，和雪球小数点2位相同
        DIF = self.EMA(CLOSE, SHORT) - self.EMA(CLOSE, LONG);
        DEA = self.EMA(DIF, M);
        MACD = (DIF - DEA) * 2
        return self.RD(DIF), self.RD(DEA), self.RD(MACD)

    def KDJ(self, CLOSE, HIGH, LOW, N=9, M1=3, M2=3):  # KDJ指标
        RSV = (CLOSE - self.LLV(LOW, N)) / (self.HHV(HIGH, N) - self.LLV(LOW, N)) * 100
        K = self.EMA(RSV, (M1 * 2 - 1));
        D = self.EMA(K, (M2 * 2 - 1));
        J = K * 3 - D * 2
        return K, D, J

    def RSI(self, CLOSE, N=24):  # RSI指标,和通达信小数点2位相同
        DIF = CLOSE - self.REF(CLOSE, 1)
        return self.RD(self.SMA(self.MAX(DIF, 0), N) / self.SMA(self.ABS(DIF), N) * 100)

    def WR(self, CLOSE, HIGH, LOW, N=10, N1=6):  # W&R 威廉指标
        WR = (self.HHV(HIGH, N) - CLOSE) / (self.HHV(HIGH, N) - self.LLV(LOW, N)) * 100
        WR1 = (self.HHV(HIGH, N1) - CLOSE) / (self.HHV(HIGH, N1) - self.LLV(LOW, N1)) * 100
        return self.RD(WR), self.RD(WR1)

    def BIAS(self, CLOSE, L1=6, L2=12, L3=24):  # BIAS乖离率
        BIAS1 = (CLOSE - self.MA(CLOSE, L1)) / self.MA(CLOSE, L1) * 100
        BIAS2 = (CLOSE - self.MA(CLOSE, L2)) / self.MA(CLOSE, L2) * 100
        BIAS3 = (CLOSE - self.MA(CLOSE, L3)) / self.MA(CLOSE, L3) * 100
        return self.RD(BIAS1), self.RD(BIAS2), self.RD(BIAS3)

    def BOLL(self, CLOSE, N=20, P=2):  # BOLL指标，布林带
        MID = self.MA(CLOSE, N);
        UPPER = MID + self.STD(CLOSE, N) * P
        LOWER = MID - self.STD(CLOSE, N) * P
        return self.RD(UPPER), self.RD(MID), self.RD(LOWER)

    def PSY(self, CLOSE, N=12, M=6):
        PSY = self.COUNT(CLOSE > self.REF(CLOSE, 1), N) / N * 100
        PSYMA = self.MA(PSY, M)
        return self.RD(PSY), self.RD(PSYMA)

    def CCI(self, CLOSE, HIGH, LOW, N=14):
        TP = (HIGH + LOW + CLOSE) / 3
        return (TP - self.MA(TP, N)) / (0.015 * self.AVEDEV(TP, N))

    def ATR(self, CLOSE, HIGH, LOW, N=20):  # 真实波动N日平均值
        TR = self.MAX(self.MAX((HIGH - LOW), self.ABS(self.REF(CLOSE, 1) - HIGH)), self.ABS(self.REF(CLOSE, 1) - LOW))
        return self.MA(TR, N)

    def BBI(self, CLOSE, M1=3, M2=6, M3=12, M4=20):  # BBI多空指标
        return (self.MA(CLOSE, M1) + self.MA(CLOSE, M2) + self.MA(CLOSE, M3) + self.MA(CLOSE, M4)) / 4

    def DMI(self, CLOSE, HIGH, LOW, M1=14, M2=6):  # 动向指标：结果和同花顺，通达信完全一致
        TR = self.SUM(
            self.MAX(self.MAX(HIGH - LOW, self.ABS(HIGH - self.REF(CLOSE, 1))), self.ABS(LOW - self.REF(CLOSE, 1))), M1)
        HD = HIGH - self.REF(HIGH, 1);
        LD = self.REF(LOW, 1) - LOW
        DMP = self.SUM(self.IF((HD > 0) & (HD > LD), HD, 0), M1)
        DMM = self.SUM(self.IF((LD > 0) & (LD > HD), LD, 0), M1)
        PDI = DMP * 100 / TR;
        MDI = DMM * 100 / TR
        ADX = self.MA(self.ABS(MDI - PDI) / (PDI + MDI) * 100, M2)
        ADXR = (ADX + self.REF(ADX, M2)) / 2
        return PDI, MDI, ADX, ADXR

    def TAQ(self, HIGH, LOW, N):  # 唐安奇通道(海龟)交易指标，大道至简，能穿越牛熊
        UP = self.HHV(HIGH, N);
        DOWN = self.LLV(LOW, N);
        MID = (UP + DOWN) / 2
        return UP, MID, DOWN

    def KTN(self, CLOSE, HIGH, LOW, N=20, M=10):  # 肯特纳交易通道, N选20日，ATR选10日
        MID = self.EMA((HIGH + LOW + CLOSE) / 3, N)
        ATRN = self.ATR(CLOSE, HIGH, LOW, M)
        UPPER = MID + 2 * ATRN;
        LOWER = MID - 2 * ATRN
        return UPPER, MID, LOWER

    def TRIX(self, CLOSE, M1=12, M2=20):  # 三重指数平滑平均线
        TR = self.EMA(self.EMA(self.EMA(CLOSE, M1), M1), M1)
        TRIX = (TR - self.REF(TR, 1)) / self.REF(TR, 1) * 100
        TRMA = self.MA(TRIX, M2)
        return TRIX, TRMA

    def VR(self, CLOSE, VOL, M1=26):  # VR容量比率
        LC = self.REF(CLOSE, 1)
        return self.SUM(self.IF(CLOSE > LC, VOL, 0), M1) / self.SUM(self.IF(CLOSE <= LC, VOL, 0), M1) * 100

    def EMV(self, HIGH, LOW, VOL, N=14, M=9):  # 简易波动指标
        VOLUME = self.MA(VOL, N) / VOL;
        MID = 100 * (HIGH + LOW - self.REF(HIGH + LOW, 1)) / (HIGH + LOW)
        EMV = self.MA(MID * VOLUME * (HIGH - LOW) / self.MA(HIGH - LOW, N), N);
        MAEMV = self.MA(EMV, M)
        return EMV, MAEMV

    def DPO(self, CLOSE, M1=20, M2=10, M3=6):  # 区间震荡线
        DPO = CLOSE - self.REF(self.MA(CLOSE, M1), M2);
        MADPO = self.MA(DPO, M3)
        return DPO, MADPO

    def BRAR(self, OPEN, CLOSE, HIGH, LOW, M1=26):  # BRAR-ARBR 情绪指标
        AR = self.SUM(HIGH - OPEN, M1) / self.SUM(OPEN - LOW, M1) * 100
        BR = self.SUM(self.MAX(0, HIGH - self.REF(CLOSE, 1)), M1) / self.SUM(self.MAX(0, self.REF(CLOSE, 1) - LOW),
                                                                             M1) * 100
        return AR, BR

    def DMA(self, CLOSE, N1=10, N2=50, M=10):  # 平行线差指标
        DIF = self.MA(CLOSE, N1) - self.MA(CLOSE, N2);
        DIFMA = self.MA(DIF, M)
        return DIF, DIFMA

    def MTM(self, CLOSE, N=12, M=6):  # 动量指标
        MTM = CLOSE - self.REF(CLOSE, N);
        MTMMA = self.MA(MTM, M)
        return MTM, MTMMA

    def MASS(self, HIGH, LOW, N1=9, N2=25, M=6):  # 梅斯线
        MASS = self.SUM(self.MA(HIGH - LOW, N1) / self.MA(self.MA(HIGH - LOW, N1), N1), N2)
        MA_MASS = self.MA(MASS, M)
        return MASS, MA_MASS

    def ROC(self, CLOSE, N=12, M=6):  # 变动率指标
        ROC = 100 * (CLOSE - self.REF(CLOSE, N)) / self.REF(CLOSE, N);
        MAROC = self.MA(ROC, M)
        return ROC, MAROC

    def EXPMA(self, CLOSE, N1=12, N2=50):  # EMA指数平均数指标
        return self.EMA(CLOSE, N1), self.EMA(CLOSE, N2);

    def OBV(self, CLOSE, VOL):  # 能量潮指标
        return self.SUM(self.IF(CLOSE > self.REF(CLOSE, 1), VOL, self.IF(CLOSE < self.REF(CLOSE, 1), -VOL, 0)),
                        0) / 10000

    def MFI(self, CLOSE, HIGH, LOW, VOL, N=14):  # MFI指标是成交量的RSI指标
        TYP = (HIGH + LOW + CLOSE) / 3
        V1 = self.SUM(self.IF(TYP > self.REF(TYP, 1), TYP * VOL, 0), N) / self.SUM(
            self.IF(TYP < self.REF(TYP, 1), TYP * VOL, 0), N)
        return 100 - (100 / (1 + V1))

    def ASI(self, OPEN, CLOSE, HIGH, LOW, M1=26, M2=10):  # 振动升降指标
        LC = self.REF(CLOSE, 1);
        AA = self.ABS(HIGH - LC);
        BB = self.ABS(LOW - LC);
        CC = self.ABS(HIGH - self.REF(LOW, 1));
        DD = self.ABS(LC - self.REF(OPEN, 1));
        R = self.IF((AA > BB) & (AA > CC), AA + BB / 2 + DD / 4,
                    self.IF((BB > CC) & (BB > AA), BB + AA / 2 + DD / 4, CC + DD / 4));
        X = (CLOSE - LC + (CLOSE - OPEN) / 2 + LC - self.REF(OPEN, 1));
        SI = 16 * X / R * self.MAX(AA, BB);
        ASI = self.SUM(SI, M1);
        ASIT = self.MA(ASI, M2);
        return ASI, ASIT

    def LONGCROSS(self, a, b, n):
        """
        两条线维持一定周期后交叉
        LONGCROSS(A,B,N)表示A在N周期内都小于B，本周期从下方向上穿过B时返回1，否则返回0。
        :param a:
        :param b:
        :param n:
        :return:
        """
        if not isinstance(a, pd.Series):
            arr = []
            counter = 0
            while counter < b.size:
                arr.append(a)
                counter += 1
            a = pd.Series(arr)
            a.index = b.index

        if not isinstance(b, pd.Series):
            arr = []
            counter = 0
            while counter < a.size:
                arr.append(b)
                counter += 1
            b = pd.Series(arr)
            b.index = a.index
        # return self.EVERY((self.REF(a, 1) < self.REF(b, 1)), n) & (a > b)
        return pd.Series(self.EVERY((self.REF(a, 1) < self.REF(b, 1)), n) & self.CROSS(a, b))

    # @profile
    def ZIG(self, df, x=0.01, n=2, digitcount: int = 3):
        """
        转向函数
            算法问题：如果最后两个点的间距小于x的话，应该再最后一个点之前加入一个极值点作为新拐点插入
        :param df: 数据
        :param x: 转向比例
        :return:
        """
        # ts.set_token("此处放入tushare的token！！！")
        # pro = ts.pro_api()
        # df = pro.daily(ts_code="603297.SH")
        # print(list(df["close"]))
        # df = ts.get_hist_data('000069')
        # df = df[::-1]
        # 获取股票交易数据的Tushare的使用方法 - 蜗牛爬行ing - 博客园
        # https://www.cnblogs.com/DreamRJF/p/8660630.html
        # posted on 2018-03-28 15:18 蜗牛爬行ing

        # df = ts.get_k_data('000069')
        # df = ts.get_k_data('600535')
        # df = ts.get_k_data('512040')  # 富国国信价值 etf 基金
        # df = ts.get_h_data('000051', index=True)   # 上证180等权指数 index 参数必须指定为True
        # df = ts.get_k_data('000051', index=True, start='2011-01-01')  # 上证180等权指数 index 参数必须指定为True

        # df = ts.get_h_data('399106', index=True)   # index 参数必须指定为True
        # df = ts.get_h_data('399106', index=True) #深圳综合指数
        # df = ts.get_k_data('399106', index=True) #深圳综合指数
        # df = ts.get_k_data('931052', index=True) # 中证国信价值指数， 不支持的指数
        # df = ts.get_k_data('hs300')   # 支持主要的几个股票指数的历史行情
        # 股票代码，即6位数字代码，或者指数代码
        # （sh=上证指数 sz=深圳成指 hs300=沪深300指数
        # sz50=上证50 zxb=中小板 cyb=创业板）

        # df = df.reset_index(drop=True)
        # df = df.iloc[-100:]
        # x = 0.055
        # 精度保持统一
        df["maN"] = self.RD(df["CLOSE"].values,
                            digitcount)  # self.RD( self.MA(df["CLOSE"].values, n),digitcount)  # df["CLOSE"].values
        maN = df["maN"]  # df["CLOSE"].values

        # # 补充移动平均后前一个nan
        for i in range(0, n - 1):
            maN[i] = round(df["CLOSE"].values[i], digitcount)

        k = maN  # df["CLOSE"].values
        # print(k[-1])
        # 拷贝一份，用最后一个bar的C来替换k的最后一个值
        # 原来是LOW，LOW不一定是最新的价格，用(O+C+H+L)/4来替代，可以使最后一个数值变得稳定一些
        # k[-1] = round(
        #     (df['CLOSE'].values[-1] + df['OPEN'].values[-1] + df['LOW'].values[-1] + df['HIGH'].values[-1]) / 4,
        #     digitcount)

        # df['C'].values[-1]       df['LOW'].values[-1]
        # k[-1] = round(df['C'].values[-1],digitcount)
        # print(k[-1])
        # d = df["trade_date"]
        d = df["time"].values
        # d = df.index
        # print(k)
        # print(d)
        # 循环前的变量初始化
        # 端点 候选点 扫描点 端点列表 拐点线列表 趋势状态
        peer_i = 0
        candidate_i = None
        scan_i = 0
        peers = [0]
        z = np.zeros(len(k))
        state = self.ZIG_STATE_START
        while True:
            # print(peers)
            scan_i += 1
            if scan_i == len(k) - 1:
                # 扫描到尾部
                if candidate_i is None:
                    peer_i = scan_i
                    peers.append(peer_i)
                else:
                    if state == self.ZIG_STATE_RISE:
                        if k[scan_i] >= k[candidate_i]:
                            peer_i = scan_i
                            peers.append(peer_i)
                        else:
                            peer_i = candidate_i
                            peers.append(peer_i)
                            peer_i = scan_i
                            peers.append(peer_i)
                    elif state == self.ZIG_STATE_FALL:
                        if k[scan_i] <= k[candidate_i]:
                            peer_i = scan_i
                            peers.append(peer_i)
                        else:
                            peer_i = candidate_i
                            peers.append(peer_i)
                            peer_i = scan_i
                            peers.append(peer_i)
                break

            if state == self.ZIG_STATE_START:
                if k[scan_i] >= k[peer_i] * (1 + x):
                    candidate_i = scan_i
                    state = self.ZIG_STATE_RISE
                elif k[scan_i] <= k[peer_i] * (1 - x):
                    candidate_i = scan_i
                    state = self.ZIG_STATE_FALL
            elif state == self.ZIG_STATE_RISE:
                if k[scan_i] >= k[candidate_i]:
                    candidate_i = scan_i
                elif k[scan_i] <= k[candidate_i] * (1 - x):
                    peer_i = candidate_i
                    peers.append(peer_i)
                    state = self.ZIG_STATE_FALL
                    candidate_i = scan_i
            elif state == self.ZIG_STATE_FALL:
                if k[scan_i] <= k[candidate_i]:
                    candidate_i = scan_i
                elif k[scan_i] >= k[candidate_i] * (1 + x):
                    peer_i = candidate_i
                    peers.append(peer_i)
                    state = self.ZIG_STATE_RISE
                    candidate_i = scan_i

        # 线性插值， 计算出zig的值
        for i in range(len(peers) - 1):
            peer_start_i = peers[i]
            peer_end_i = peers[i + 1]
            start_value = k[peer_start_i]
            end_value = k[peer_end_i]
            a = (end_value - start_value) / (peer_end_i - peer_start_i)  # 斜率
            for j in range(peer_end_i - peer_start_i + 1):
                z[j + peer_start_i] = round(start_value + a * j, digitcount)

        # print(u'...转向点的阀值、个数、位置和日期...')
        # print(x, len(peers))
        # print(peers)

        dates = [str(d[i]).split('.')[0] + 'Z' for i in peers]
        # print(dates)
        closes = [round(k[i], digitcount) for i in peers]
        # print(closes)
        # print("closes[-1]:{},closes[-2]:{}".format(closes[-1], closes[-2]))
        # print("dates[-1]:{},dates[-2]:{}".format(dates[-1], dates[-2]))
        # 如果最后2个节点的变化率小于x
        # if abs((closes[-1]-closes[-2]))/closes[-2]<x:
        #     start = datetime.strptime(str(dates[-2]).split('.')[0], "%Y-%m-%dT%H:%M:%SZ")
        #     end = datetime.strptime(str(dates[-1]).split('.')[0], "%Y-%m-%dT%H:%M:%SZ")
        #     start = pd.Timestamp(start, unit='ns')
        #     start = start.tz_localize('utc')
        #     end = pd.Timestamp(end, unit='ns')
        #     end = end.tz_localize('utc')
        #     #
        #     # df = df.loc[(df['time'] >= morning_start)]
        #
        #     # INDEX_DF = INDEX_DF.loc[((INDEX_DF['time'] >= morning_start) & (INDEX_DF['time'] <= morning_end))
        #     #                         | ((INDEX_DF['time'] >= afternoon_start) & (INDEX_DF['time'] <= afternoon_end))]
        #     #
        #     tmpklines = pd.DataFrame()
        #     tmpklines = df.loc[(df['time'] >= start) & (df['time'] <= end)]
        #
        #     #如果[-1]>[-2],涨势
        #     if closes[-1]>closes[-2]:
        #         #取区间内的最大值
        #         maxvalue = tmpklines['maN'].max()
        #         # print(maxvalue)
        #         if round(maxvalue,digitcount)!=closes[-1]:
        #             tmpklines = df.loc[df['maN'] == maxvalue, :]
        #             maxindex = 999
        #             maxvalue = round(maxvalue,digitcount)
        #             maxdate = str(tmpklines['time'].values[-1]).split('.')[0]+'Z'
        #             peers.insert(-1,maxindex )
        #             closes.insert(-1,maxvalue )
        #             dates.insert(-1,maxdate )
        #             # print("maxindex:{},maxvalue:{},maxdate:{}".format(maxindex,maxvalue,str(maxdate)))
        #     # 如果[-1]<[-2],跌势
        #     else:
        #         #取区间内的最小值
        #         minvalue = tmpklines['maN'].min()
        #         if round(minvalue,digitcount) != closes[-1]:
        #             tmpklines = df.loc[df['maN'] == minvalue,:]
        #             minindex = 999
        #             minvalue = round(minvalue, digitcount)
        #             mindate =str( tmpklines['time'].values[-1]).split('.')[0]+'Z'
        #             peers.insert(-1,minindex )
        #             closes.insert(-1,minvalue )
        #             dates.insert(-1,mindate )
        #             # print("minindex:{},minvalue:{},mindate:{}".format(minindex,minvalue, mindate))
        #

        # print(z)
        return closes, dates, peers, z
        # print([k[i] for i in peers])
        # print(list(k))
        # print(list(z))

    def ATR_TREND(self, df, period, ohlc=['OPEN', 'HIGH', 'LOW', 'CLOSE']):
        """
        Function to compute Average True Range (ATR)

        Args :
            df : Pandas DataFrame which contains ['date', 'open', 'high', 'low', 'close', 'volume'] columns
            period : Integer indicates the period of computation in terms of number of candles
            ohlc: List defining OHLC Column names (default ['Open', 'High', 'Low', 'Close'])

        Returns :
            df : Pandas DataFrame with new columns added for
                True Range (TR)
                ATR (ATR_$period)
        """
        atr = 'ATR_' + str(period)

        # Compute true range only if it is not computed and stored earlier in the df
        if not 'TR' in df.columns:
            df['h-l'] = df[ohlc[1]] - df[ohlc[2]]
            df['h-yc'] = abs(df[ohlc[1]] - df[ohlc[3]].shift())
            df['l-yc'] = abs(df[ohlc[2]] - df[ohlc[3]].shift())

            df['TR'] = df[['h-l', 'h-yc', 'l-yc']].max(axis=1)

            df.drop(['h-l', 'h-yc', 'l-yc'], inplace=True, axis=1)

        # Compute EMA of true range using ATR formula after ignoring first row
        # EMA(df, 'TR', atr, period, alpha=True)

        df[atr] = self.EMA(df['TR'], period)
        return df

    def SuperTrend(self, df, period, multiplier, ohlc=['OPEN', 'HIGH', 'LOW', 'CLOSE']):
        """
        Function to compute SuperTrend

        Args :
            df : Pandas DataFrame which contains ['date', 'open', 'high', 'low', 'close', 'volume'] columns
            period : Integer indicates the period of computation in terms of number of candles
            multiplier : Integer indicates value to multiply the ATR
            ohlc: List defining OHLC Column names (default ['Open', 'High', 'Low', 'Close'])

        Returns :
            df : Pandas DataFrame with new columns added for
                True Range (TR), ATR (ATR_$period)
                SuperTrend (ST_$period_$multiplier)
                SuperTrend Direction (STX_$period_$multiplier)
        """

        self.ATR_TREND(df, period, ohlc=ohlc)
        atr = 'ATR_' + str(period)
        st = 'ST_' + str(period) + '_' + str(multiplier)
        stx = 'STX_' + str(period) + '_' + str(multiplier)

        """
        SuperTrend Algorithm :

            BASIC UPPERBAND = (HIGH + LOW) / 2 + Multiplier * ATR
            BASIC LOWERBAND = (HIGH + LOW) / 2 - Multiplier * ATR

            FINAL UPPERBAND = IF( (Current BASICUPPERBAND < Previous FINAL UPPERBAND) or (Previous Close > Previous FINAL UPPERBAND))
                                THEN (Current BASIC UPPERBAND) ELSE Previous FINALUPPERBAND)
            FINAL LOWERBAND = IF( (Current BASIC LOWERBAND > Previous FINAL LOWERBAND) or (Previous Close < Previous FINAL LOWERBAND)) 
                                THEN (Current BASIC LOWERBAND) ELSE Previous FINAL LOWERBAND)

            SUPERTREND = IF((Previous SUPERTREND = Previous FINAL UPPERBAND) and (Current Close <= Current FINAL UPPERBAND)) THEN
                            Current FINAL UPPERBAND
                        ELSE
                            IF((Previous SUPERTREND = Previous FINAL UPPERBAND) and (Current Close > Current FINAL UPPERBAND)) THEN
                                Current FINAL LOWERBAND
                            ELSE
                                IF((Previous SUPERTREND = Previous FINAL LOWERBAND) and (Current Close >= Current FINAL LOWERBAND)) THEN
                                    Current FINAL LOWERBAND
                                ELSE
                                    IF((Previous SUPERTREND = Previous FINAL LOWERBAND) and (Current Close < Current FINAL LOWERBAND)) THEN
                                        Current FINAL UPPERBAND
        """

        # Compute basic upper and lower bands
        df['basic_ub'] = (df[ohlc[1]] + df[ohlc[2]]) / 2 + multiplier * df[atr]
        df['basic_lb'] = (df[ohlc[1]] + df[ohlc[2]]) / 2 - multiplier * df[atr]

        # Compute final upper and lower bands
        df['final_ub'] = 0.00
        df['final_lb'] = 0.00
        for i in range(period, len(df)):
            df['final_ub'].iat[i] = df['basic_ub'].iat[i] if df['basic_ub'].iat[i] < df['final_ub'].iat[i - 1] or \
                                                             df[ohlc[3]].iat[i - 1] > df['final_ub'].iat[i - 1] else \
                df['final_ub'].iat[i - 1]
            df['final_lb'].iat[i] = df['basic_lb'].iat[i] if df['basic_lb'].iat[i] > df['final_lb'].iat[i - 1] or \
                                                             df[ohlc[3]].iat[i - 1] < df['final_lb'].iat[i - 1] else \
                df['final_lb'].iat[i - 1]

        # Set the Supertrend value
        df[st] = 0.00
        for i in range(period, len(df)):
            df[st].iat[i] = df['final_ub'].iat[i] if df[st].iat[i - 1] == df['final_ub'].iat[i - 1] and \
                                                     df[ohlc[3]].iat[i] <= df['final_ub'].iat[i] else \
                df['final_lb'].iat[i] if df[st].iat[i - 1] == df['final_ub'].iat[i - 1] and df[ohlc[3]].iat[i] > \
                                         df['final_ub'].iat[i] else \
                    df['final_lb'].iat[i] if df[st].iat[i - 1] == df['final_lb'].iat[i - 1] and df[ohlc[3]].iat[
                        i] >= df['final_lb'].iat[i] else \
                        df['final_ub'].iat[i] if df[st].iat[i - 1] == df['final_lb'].iat[i - 1] and df[ohlc[3]].iat[
                            i] < df['final_lb'].iat[i] else 0.00

        # Mark the trend direction up/down
        df[stx] = np.where((df[st] > 0.00), np.where((df[ohlc[3]] < df[st]), 'down', 'up'), np.NaN)

        # Remove basic and final bands from the columns
        df.drop(['basic_ub', 'basic_lb', 'final_ub', 'final_lb'], inplace=True, axis=1)

        df.fillna(0, inplace=True)

        return df


