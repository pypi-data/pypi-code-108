"""
资配指标的更新程序
"""
from WindPy import w
from hbshare.quant.Kevin.asset_allocation.macro_index.currency import Currency, CurrencyShibor
from hbshare.quant.Kevin.asset_allocation.macro_index.credit import Credit
from hbshare.quant.Kevin.asset_allocation.macro_index.inflation import Inflation
from hbshare.quant.Kevin.asset_allocation.macro_index.eco_increase import EconomyIncrease
from hbshare.quant.Kevin.asset_allocation.macro_index.rates_and_price import RatesAndPrice
from hbshare.quant.Kevin.asset_allocation.macro_index.processed_market_index import MarketIndex
from hbshare.quant.Kevin.asset_allocation.macro_index.stock_market import StockValuation
from hbshare.quant.Kevin.asset_allocation.macro_index.stock_cash_flow import StockCashFlow
from hbshare.quant.Kevin.asset_allocation.macro_index.stock_trading import StockTrading
from hbshare.quant.Kevin.asset_allocation.macro_index.stock_cross_section_vol import StockCrossSectionVol
from hbshare.quant.Kevin.asset_allocation.macro_index.stock_time_series_vol import StockTimeSeriesVol
from hbshare.quant.Kevin.asset_allocation.macro_index.stock_trading_cr import TradingCRNCalculator
from hbshare.quant.Kevin.asset_allocation.macro_index.stock_style_momentum import StyleFactorMomentum
from hbshare.quant.Kevin.asset_allocation.macro_index.stock_style_spread import StyleFactorSpread
from hbshare.quant.Kevin.asset_allocation.macro_index.treasury_yield import TreasuryYield
from hbshare.quant.Kevin.asset_allocation.macro_index.bond_trading import BondTrading
from hbshare.quant.Kevin.asset_allocation.macro_index.future_data import FutureMarketIndex, FuturePrice
from hbshare.quant.Kevin.quant_room.IndexActiveStyleAnalyse import EquityIndexStyleCalculator
from hbshare.quant.Kevin.convertible_bond.CBMarketIV import CBMarketIV
from hbshare.quant.Kevin.asset_allocation.macro_index.stock_share_price_index_futures import StockSharePriceIndex

w.start()


def update_weekly(start_date, end_date):
    """
    周度更新宏观数据：mac_curr, mac_curr_shibor, mac_credit, mac_inflation, mac_eco_increase,
                  mac_rates_and_price, mac_market_index
    """
    # 宏观-货币类
    Currency(start_date, end_date).get_construct_result()
    CurrencyShibor(start_date, end_date).get_construct_result()
    # 宏观-信用类
    Credit(start_date, end_date).get_construct_result()
    # 宏观-通胀类
    Inflation(start_date, end_date).get_construct_result()
    # 宏观-经济增长类
    EconomyIncrease(start_date, end_date).get_construct_result()
    # 宏观-汇率和价格类
    RatesAndPrice(start_date, end_date).get_construct_result()
    # 宏观-处理过的指数数据
    MarketIndex(start_date, end_date).get_construct_result()


def update_monthly(start_date, end_date):
    """
    月度更新风格因子动量&离散度
    """
    # 股票风格因子：因子动量 & 因子离散度
    StyleFactorMomentum(start_date, end_date).get_construct_result()
    StyleFactorSpread(start_date, end_date).get_construct_result()
    # 指数风格暴露
    start_date = start_date.replace('-', '')
    end_date = end_date.replace('-', '')
    EquityIndexStyleCalculator(start_date, end_date, benchmark_id='000300').get_construct_result()
    EquityIndexStyleCalculator(start_date, end_date, benchmark_id='000905').get_construct_result()
    EquityIndexStyleCalculator(start_date, end_date, benchmark_id='000852').get_construct_result()


def update_daily(start_date, end_date):
    """
    日度更新股票市场微观数据
    """
    # 股票-PE
    StockValuation(start_date, end_date).get_construct_result()
    # 股票-资金流向
    StockCashFlow(start_date, end_date).get_construct_result()
    # 股票-成交额&换手率
    StockTrading(start_date, end_date).get_construct_result()
    # 股票-截面波动率
    StockCrossSectionVol(start_date, end_date).get_construct_result()
    # 股票-时序波动率
    StockTimeSeriesVol(start_date, end_date).get_construct_result()
    # 股票-成交集中度
    TradingCRNCalculator(start_date, end_date).get_construct_result()
    # 债券-国债收益率
    TreasuryYield(start_date, end_date).get_construct_result()
    # 债券-质押式回购成交量
    BondTrading(start_date, end_date).get_construct_result()
    # 期货商品指数数据
    FutureMarketIndex(start_date, end_date).get_construct_result()
    FuturePrice(start_date, end_date).get_construct_result()
    # 可转债市场隐含波动率
    CBMarketIV(start_date.replace('-', ''), end_date.replace('-', '')).get_construct_result()
    # 基差数据
    StockSharePriceIndex(start_date, end_date).get_construct_result()


if __name__ == '__main__':
    update_daily(start_date='2022-01-26', end_date='2022-01-26')
    # update_monthly('2021-12-10', '2021-12-31')
    # update_weekly(start_date='2021-09-01', end_date='2021-12-31')
