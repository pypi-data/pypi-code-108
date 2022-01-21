# -*- coding:utf-8 -*-

import pandas as pd
import numpy as np

class sarindicator:
    """
        SAR技术指标,精度指标限定在了2位小数，需要修正，重大bug
    """

    def __init__(self,
                 high: pd.Series,
                 low: pd.Series,
                 close: pd.Series,
                 period: int = 4,
                 step: float = 0.02,
                 max_step: float = 0.20,
                 fillna: bool = False,
                 decimalcount: int = 4
                 ):
        self._high = high.copy()
        self._low = low.copy()
        self._close = close.copy()
        self._length = self._close.__len__()
        self._period = period - 1
        self._step = step
        self._max_step = max_step  # 步长最大值
        self._fillna = fillna  # 是否填充空值
        self._decimalcount = decimalcount  # 小数精度位数
        self._run()

    def _run(self):
        up_trend = True  # 默认初始是上升趋势
        acceleration_factor = self._step  # 初始加速因子是0.02
        up_trend_high = self._high.iloc[0]  # 初始上升趋势最高值，为第一天的最高
        down_trend_low = self._low.iloc[0]  # 初始下降趋势最低值，为第一天的最低

        self._psar = pd.Series([np.nan] * self._length, index=self._close.index)
        self._psar_up = pd.Series([np.nan] * self._length, index=self._close.index)
        self._psar_down = pd.Series([np.nan] * self._length, index=self._close.index)
        self._psar_indicator = pd.Series([np.nan] * self._length, index=self._close.index)
        self._psar_af = pd.Series([np.nan] * self._length, index=self._close.index)

        for i in range(1, self._length):
            if i < self._period:
                up_trend_high = max(self._high.iloc[i], up_trend_high)
                down_trend_low = min(self._low.iloc[i], down_trend_low)
                continue
            # print(up_trend_high, down_trend_low)

            if up_trend:
                down_trend_low = min(self._low.iloc[i], down_trend_low)

                if np.isnan(self._psar.iloc[i - 1]):  # 如果一开始是空值，上升趋势默认，min最低点
                    self._psar.iloc[i] = down_trend_low
                else:
                    self._psar.iloc[i] = self._psar.iloc[i - 1] + (  # 如果有前值，计算
                            acceleration_factor * (up_trend_high - self._psar.iloc[i - 1])
                    )
                self._psar.iloc[i] = round(self._psar.iloc[i], self._decimalcount)

                if self._psar.iloc[i] > self._low.iloc[i]:  # 上升趋势中SAR大于当前最低点，则翻转
                    up_trend = False  # 表示翻转了
                    self._psar.iloc[i] = up_trend_high  # 上一周期的max最高
                    down_trend_low = self._low.iloc[i]  # 最低值是当前的最低点
                    acceleration_factor = self._step  # 加速因子重置

                else:  # 没有翻转
                    if self._high.iloc[i] > up_trend_high:  # 如果有新高
                        up_trend_high = self._high.iloc[i]  # 更新当前周期内的最高价
                        acceleration_factor = min(  # 更新加速因子
                            acceleration_factor + self._step, self._max_step
                        )
            else:  # 进入下降趋势
                up_trend_high = max(self._high.iloc[i], up_trend_high)

                self._psar.iloc[i] = self._psar.iloc[i - 1] - (  # 如果有前值，计算
                        acceleration_factor * (self._psar.iloc[i - 1] - down_trend_low)
                )
                self._psar.iloc[i] = round(self._psar.iloc[i], self._decimalcount)

                if self._psar.iloc[i] < self._high.iloc[i]:  # 下降趋势中，SAR小于当前最高点，则翻转
                    up_trend = True  # 表示翻转了
                    self._psar.iloc[i] = down_trend_low  # 上一周期的min最低
                    up_trend_high = self._high.iloc[i]  # 最高值是当前的最高点
                    acceleration_factor = self._step  # 加速因子重置

                else:
                    if self._low.iloc[i] < down_trend_low:  # 如果有新低
                        down_trend_low = self._low.iloc[i]  # 更新当前周期内的最低价
                        acceleration_factor = min(  # 更新加速因子
                            acceleration_factor + self._step, self._max_step
                        )

            if up_trend:
                self._psar_up.iloc[i] = 1
                self._psar_indicator.iloc[i] = 1
            else:
                self._psar_down.iloc[i] = 1
                self._psar_indicator.iloc[i] = -1
            self._psar_af.iloc[i] = acceleration_factor

    def psar(self):
        """
        返回SAR数值
        :return:
        """
        return pd.Series(self._psar, name='psar')

    def psar_up(self):
        """
        返回上升趋势
        :return:
        """
        return pd.Series(self._psar_up, name='psar_up')

    def psar_down(self):
        """
        返回下降趋势
        :return:
        """
        return pd.Series(self._psar_down, name='psar_down')

    def psar_indicator(self):
        """
        返回多头和空头
        :return:
        """
        return pd.Series(self._psar_indicator, name='indicator')

    def psar_acceleration_factor(self):
        """
        返回加速因子
        :return:
        """
        return pd.Series(self._psar_af, name='acceleration_factor')
