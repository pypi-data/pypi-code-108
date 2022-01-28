#!/usr/bin/python
# coding:utf-8
import pandas as pd
import numpy as np


def xs_weight(data):
    pos_long = sum(data['POS'] == 1)
    pos_short = sum(data['POS'] == -1)
    data['WEIGHT'] = data['POS'].apply(
        lambda x: 0.5 / pos_long if x == 1 else (0.5 / pos_short if x == -1 else 0)
    )
    return data


def ts_weight(data):
    if sum(data['POS'] != 0) > 0:
        data['WEIGHT'] = 1 / sum(data['POS'] != 0)
    else:
        data['WEIGHT'] = 0

    return data


def ts_pos(data, direction=1):
    data['POS'] = data['FACTORVALUE'] / data['FACTORVALUE'].abs() * direction
    data = data[~np.isnan(data['POS'])].reset_index(drop=True)
    return data


def xs_pos(data, direction=1, quantile=50):
    # data = data[~np.isnan(data['FACTORVALUE'])].reset_index(drop=True)
    quantile_p = data['FACTORVALUE'].quantile(quantile / 100)
    quantile_n = data['FACTORVALUE'].quantile(1 - quantile / 100)
    data['POS'] = data['FACTORVALUE'].apply(
        lambda x: direction if x > quantile_p else (-direction if x < quantile_n else np.nan)
    )
    data = data[~np.isnan(data['POS'])].reset_index(drop=True)
    return data


def tsmom(start_date, direction=1, **kwargs):
    data = kwargs['data']
    liq_days = kwargs['liq_days']
    data['UCODE'] = data['EXCHANGE'].apply(lambda x: str(x)) + data['PCODE'].apply(lambda x: str(x))
    calendar = data['TDATE'].drop_duplicates().tolist()

    window_days = kwargs['window_days']

    if direction == 1:
        index_name = 'tsmom_d' + str(window_days)
    else:
        index_name = 'tsrev_d' + str(window_days)

    start_index = calendar.index(np.array(calendar)[np.array(calendar) >= start_date][0])

    positions = pd.DataFrame()
    for i in range(start_index, len(calendar) - 1):
        t_date = calendar[i]
        lookback_date = calendar[i - window_days]
        data_t = data[
            np.array(data['TDATE'] == t_date) & np.array(data['VOL'] > kwargs['min_volume'])
            ][['TDATE', 'EXCHANGE', 'PCODE', 'UCODE', 'CLOSE']]

        data_liq = data[
            data['TDATE'] == calendar[i - liq_days]
            ][['UCODE']]

        data_t = pd.merge(data_liq, data_t, on='UCODE', how='inner')

        data_lookback = data[data['TDATE'] == lookback_date][['TDATE', 'UCODE', 'CLOSE']]

        data_t = pd.merge(
            data_t[['EXCHANGE', 'PCODE', 'UCODE', 'CLOSE']],
            data_lookback[['UCODE', 'CLOSE']].rename(columns={'CLOSE': 'CLOSE0'}),
            on='UCODE', how='left'
        )

        data_t['FACTORVALUE'] = data_t['CLOSE'] / data_t['CLOSE0'] - 1
        # data_t['POS'] = data_t['FACTORVALUE'] / data_t['FACTORVALUE'].abs() * direction
        # data_t['POS'] = data_t['POS'].fillna(0)
        data_t = ts_pos(data_t, direction=direction)

        data_tomorrow = data[np.array(data['TDATE'] == calendar[i + 1])]

        data_t = pd.merge(
            data_t, data_tomorrow[['UCODE', 'CLOSE']].rename(columns={'CLOSE': 'CLOSE1'}),
            on='UCODE', how='left'
        )

        data_t['RETURN'] = (data_t['CLOSE1'] / data_t['CLOSE'] - 1)

        data_t['TDATE'] = calendar[i + 1]
        data_t['FACTOR'] = index_name

        data_t = ts_weight(data_t)

        positions = pd.concat([positions, data_t])
        print(index_name + ', ' + t_date.strftime('%Y-%m-%d') + ', ' + str(sum(data_t['POS'] != 0)))
    if len(positions) == 0:
        return
    positions['WEIGHT'] = positions['WEIGHT'] * 100
    positions['RETURN'] = positions['RETURN'] * 100
    positions['FACTORVALUE'] = positions['FACTORVALUE'] * 100
    return positions.reset_index(drop=True)


def tsrev(start_date, **kwargs):
    return tsmom(start_date=start_date, direction=-1, **kwargs)


def tswr(start_date, price_field='CLOSE', lag=1, **kwargs):
    # 根据前一日仓单数据计算
    # 当日收盘价开平仓
    data = kwargs['data']
    data_wr = kwargs['data_wr']
    liq_days = kwargs['liq_days']
    data['UCODE'] = data['EXCHANGE'].apply(lambda x: str(x)) + data['PCODE'].apply(lambda x: str(x))
    data_wr['UCODE'] = data_wr['EXCHANGE'].apply(lambda x: str(int(x))) + data_wr['PCODE'].apply(lambda x: str(int(x)))

    calendar = data['TDATE'].drop_duplicates().tolist()

    window_days = kwargs['window_days']
    index_name = 'tswr_d' + str(window_days)

    start_index = calendar.index(np.array(calendar)[np.array(calendar) >= start_date][0])

    positions = pd.DataFrame()
    for i in range(start_index, len(calendar) - 1):
        t_date = calendar[i]
        data_wr_0 = data_wr[data_wr['TDATE'] == calendar[i - lag - window_days]][['UCODE', 'PNAME', 'WRQCURRENT']]
        data_wr_t = data_wr[data_wr['TDATE'] == calendar[i - lag]][['UCODE', 'WRQCURRENT']]

        data_wr_range = pd.merge(
            data_wr_0.rename(columns={'WRQCURRENT': 'WR0'}),
            data_wr_t.rename(columns={'WRQCURRENT': 'WR1'}),
            on='UCODE', how='left'
        )
        data_wr_range['FACTORVALUE'] = data_wr_range['WR1'] - data_wr_range['WR0']
        # data_wr_range['POS'] = data_wr_range['FACTORVALUE'] / data_wr_range['FACTORVALUE'].abs() * -1
        # data_wr_range['POS'] = data_wr_range['POS'].fillna(0)
        data_wr_range = ts_pos(data=data_wr_range, direction=-1)

        data_t = data[
            np.array(data['TDATE'] == t_date)
            & np.array(data['VOL'] > kwargs['min_volume'])
            ][['TDATE', 'EXCHANGE', 'PCODE', 'UCODE', price_field]]

        data_liq = data[
            data['TDATE'] == calendar[i - liq_days]
        ][['UCODE']]

        data_t = pd.merge(data_liq, data_t, on='UCODE', how='inner')

        data_tomorrow = data[
            np.array(data['TDATE'] == calendar[i + 1])
        ][['TDATE', 'EXCHANGE', 'PCODE', 'UCODE', price_field]]

        data_t = pd.merge(data_t[['UCODE', price_field]], data_wr_range, on='UCODE', how='inner')

        data_t = pd.merge(
            data_t.rename(columns={price_field: 'CLOSE'}),
            data_tomorrow.rename(columns={price_field: 'CLOSE1'}),
            on='UCODE', how='left'
        )

        data_t['RETURN'] = (data_t['CLOSE1'] / data_t['CLOSE'] - 1)

        data_t['TDATE'] = calendar[i + 1]
        data_t['FACTOR'] = index_name
        data_t = ts_weight(data_t)
        positions = pd.concat([positions, data_t])
        print(index_name + ', ' + t_date.strftime('%Y-%m-%d') + ', ' + str(sum(data_t['POS'] != 0)))
    if len(positions) == 0:
        return
    positions['WEIGHT'] = positions['WEIGHT'] * 100
    positions['RETURN'] = positions['RETURN'] * 100
    positions = positions[
        ['TDATE', 'EXCHANGE', 'PCODE', 'UCODE', 'CLOSE', 'CLOSE1', 'POS', 'RETURN', 'FACTORVALUE', 'FACTOR', 'WEIGHT']
    ].reset_index(drop=True)
    return positions


def carry(start_date, **kwargs):
    data = kwargs['data']
    liq_days = kwargs['liq_days']
    data['UCODE'] = data['EXCHANGE'].apply(lambda x: str(x)) + data['PCODE'].apply(lambda x: str(x))
    calendar = data['TDATE'].drop_duplicates().tolist()

    window_days = kwargs['window_days']
    quantile = kwargs['quantile']
    index_name = 'carry_d' + str(window_days) + '_q' + str(quantile)

    start_index = calendar.index(np.array(calendar)[np.array(calendar) >= start_date][0])

    positions = pd.DataFrame()
    for i in range(start_index, len(calendar) - 1):
        t_date = calendar[i]
        lookback_date = calendar[i - window_days]
        data_ry = data[
            np.array(data['TDATE'] <= t_date)
            & np.array(data['TDATE'] > lookback_date)
            ].groupby('UCODE').mean().reset_index()[['UCODE', 'RY']]
        data_t = data[
            np.array(data['TDATE'] == t_date)
            & np.array(data['VOL'] > kwargs['min_volume'])
            ]

        data_liq = data[
            data['TDATE'] == calendar[i - liq_days]
            ][['UCODE']]

        data_t = pd.merge(data_liq, data_t, on='UCODE', how='inner')

        data_t = pd.merge(data_t.rename(columns={'RY': 'RY0'}), data_ry, on='UCODE')
        data_t = data_t.rename(columns={'RY': 'FACTORVALUE'})
        data_tomorrow = data[
            np.array(data['TDATE'] == calendar[i + 1])
        ]

        # quantile_p = data_t['RY'].quantile(quantile / 100)
        # quantile_n = data_t['RY'].quantile(1 - quantile / 100)
        # data_t['POS'] = data_t['RY'].apply(lambda x: 1 if x > quantile_p else (-1 if x < quantile_n else 0))
        data_t = xs_pos(data=data_t, quantile=quantile)

        data_t = pd.merge(
            data_t, data_tomorrow[['UCODE', 'CLOSE']].rename(columns={'CLOSE': 'CLOSE1'}), on='UCODE', how='left'
        )
        data_t['RETURN'] = (data_t['CLOSE1'] / data_t['CLOSE'] - 1)
        data_t = xs_weight(data_t)
        pos = data_t

        pos['TDATE'] = calendar[i + 1]
        pos['FACTOR'] = index_name

        positions = pd.concat([positions, pos])
        print(index_name + ', ' + t_date.strftime('%Y-%m-%d') + ', ' + str(sum(data_t['POS'] != 0)))
    if len(positions) == 0:
        return

    positions['WEIGHT'] = positions['WEIGHT'] * 100
    positions['RETURN'] = positions['RETURN'] * 100
    positions['FACTORVALUE'] = positions['FACTORVALUE'] * 100
    return positions[
        ['TDATE', 'EXCHANGE', 'PCODE', 'UCODE', 'CLOSE', 'CLOSE1', 'POS', 'RETURN', 'FACTORVALUE', 'FACTOR', 'WEIGHT']
    ].reset_index(drop=True)


def tsbasismom(start_date, **kwargs):
    data = kwargs['data']
    liq_days = kwargs['liq_days']
    data['UCODE'] = data['EXCHANGE'].apply(lambda x: str(x)) + data['PCODE'].apply(lambda x: str(x))
    calendar = data['TDATE'].drop_duplicates().tolist()

    window_days = kwargs['window_days']
    index_name = 'tsbasismom_d' + str(window_days)

    start_index = calendar.index(np.array(calendar)[np.array(calendar) >= start_date][0])

    positions = pd.DataFrame()
    for i in range(start_index, len(calendar) - 1):
        t_date = calendar[i]
        lookback_date = calendar[i - window_days]

        data_t = data[
            np.array(data['TDATE'] == t_date)
            & np.array(data['VOL'] > kwargs['min_volume'])
            ][['TDATE', 'EXCHANGE', 'PCODE', 'UCODE', 'CCODE', 'CCODE2', ]]

        data_liq = data[
            data['TDATE'] == calendar[i - liq_days]
            ][['UCODE']]

        data_t = pd.merge(data_liq, data_t, on='UCODE', how='inner')

        data_t_1 = kwargs['data_raw'][kwargs['data_raw']['TDATE'] == lookback_date]

        data_t = data_t.merge(
            kwargs['data_raw'][['TDATE', 'CCODE', 'CLOSE', 'LDATE']].rename(
                columns={
                    # 'CLOSE': 'CLOSE1t0',
                    'LDATE': 'LDATE1',
                }
            ),
            on=['TDATE', 'CCODE'],
            how='left'
        ).merge(
            kwargs['data_raw'][['TDATE', 'CCODE', 'CLOSE', 'LDATE']].rename(
                columns={
                    'CLOSE': 'CLOSE2t0',
                    'CCODE': 'CCODE2',
                    'LDATE': 'LDATE2',
                }
            ),
            on=['TDATE', 'CCODE2'],
            how='left'
        ).merge(
            data_t_1[['CCODE', 'CLOSE']].rename(
                columns={
                    'CLOSE': 'CLOSE1t1'
                }
            ),
            on=['CCODE'],
            how='left'
        ).merge(
            data_t_1[['CCODE', 'CLOSE']].rename(
                columns={
                    'CLOSE': 'CLOSE2t1',
                    'CCODE': 'CCODE2'
                }
            ),
            on=['CCODE2'],
            how='left'
        )

        data_t = data_t.drop_duplicates(subset=['UCODE'], keep='last')
        data_t['return1'] = (data_t['CLOSE'] - data_t['CLOSE1t1']) / data_t['CLOSE1t1']
        data_t['return2'] = (data_t['CLOSE2t0'] - data_t['CLOSE2t1']) / data_t['CLOSE2t1']
        data_t['FACTORVALUE'] = (
                                        data_t['return1'] - data_t['return2']
                                ) * (data_t['LDATE2'] - data_t['LDATE1']).apply(lambda x: x.days)

        # data_t['POS'] = data_t['FACTORVALUE'] / abs(data_t['FACTORVALUE'])
        # data_t = data_t[~np.isnan(data_t['POS'])].reset_index(drop=True)
        data_t = ts_pos(data_t)

        data_tomorrow = kwargs['data_raw'][
            np.array(kwargs['data_raw']['TDATE'] == calendar[i + 1])
        ]
        data_tomorrow = data_tomorrow.drop_duplicates(subset=['CCODE'], keep='last')
        data_t = pd.merge(
            data_t, data_tomorrow[['CCODE', 'CLOSE']].rename(columns={'CLOSE': 'CLOSE1'}), on='CCODE', how='left'
        )
        data_t['RETURN'] = (data_t['CLOSE1'] / data_t['CLOSE'] - 1)
        data_t = ts_weight(data_t)
        pos = data_t[
            ['TDATE', 'EXCHANGE', 'PCODE', 'UCODE', 'CLOSE', 'POS', 'FACTORVALUE', 'CLOSE1', 'RETURN', 'WEIGHT']
        ].copy()

        pos['TDATE'] = calendar[i + 1]
        pos['FACTOR'] = index_name

        positions = pd.concat([positions, pos])
        print(index_name + ', ' + t_date.strftime('%Y-%m-%d') + ', ' + str(sum(data_t['POS'] != 0)))
    if len(positions) == 0:
        return

    positions['WEIGHT'] = positions['WEIGHT'] * 100
    positions['RETURN'] = positions['RETURN'] * 100
    positions['FACTORVALUE'] = positions['FACTORVALUE'] * 100
    return positions[
        ['TDATE', 'EXCHANGE', 'PCODE', 'UCODE', 'CLOSE', 'CLOSE1', 'POS', 'RETURN', 'FACTORVALUE', 'FACTOR', 'WEIGHT']
    ].reset_index(drop=True)


def xsbasismom(start_date, **kwargs):
    data = kwargs['data']
    liq_days = kwargs['liq_days']
    data['UCODE'] = data['EXCHANGE'].apply(lambda x: str(x)) + data['PCODE'].apply(lambda x: str(x))
    calendar = data['TDATE'].drop_duplicates().tolist()

    window_days = kwargs['window_days']
    quantile = kwargs['quantile']
    index_name = 'xsbasismom_d' + str(window_days) + '_q' + str(quantile)

    start_index = calendar.index(np.array(calendar)[np.array(calendar) >= start_date][0])

    positions = pd.DataFrame()
    for i in range(start_index, len(calendar) - 1):
        t_date = calendar[i]
        lookback_date = calendar[i - window_days]

        data_t = data[
            np.array(data['TDATE'] == t_date)
            & np.array(data['VOL'] > kwargs['min_volume'])
            ][['TDATE', 'EXCHANGE', 'PCODE', 'UCODE', 'CCODE', 'CCODE2', ]]

        data_liq = data[
            data['TDATE'] == calendar[i - liq_days]
            ][['UCODE']]

        data_t = pd.merge(data_liq, data_t, on='UCODE', how='inner')

        data_t_1 = kwargs['data_raw'][kwargs['data_raw']['TDATE'] == lookback_date]

        data_t = data_t.merge(
            kwargs['data_raw'][['TDATE', 'CCODE', 'CLOSE', 'LDATE']].rename(
                columns={
                    # 'CLOSE': 'CLOSE1t0',
                    'LDATE': 'LDATE1',
                }
            ),
            on=['TDATE', 'CCODE'],
            how='left'
        ).merge(
            kwargs['data_raw'][['TDATE', 'CCODE', 'CLOSE', 'LDATE']].rename(
                columns={
                    'CLOSE': 'CLOSE2t0',
                    'CCODE': 'CCODE2',
                    'LDATE': 'LDATE2',
                }
            ),
            on=['TDATE', 'CCODE2'],
            how='left'
        ).merge(
            data_t_1[['CCODE', 'CLOSE']].rename(
                columns={
                    'CLOSE': 'CLOSE1t1'
                }
            ),
            on=['CCODE'],
            how='left'
        ).merge(
            data_t_1[['CCODE', 'CLOSE']].rename(
                columns={
                    'CLOSE': 'CLOSE2t1',
                    'CCODE': 'CCODE2'
                }
            ),
            on=['CCODE2'],
            how='left'
        )

        data_t = data_t.drop_duplicates(subset=['UCODE'], keep='last')
        data_t['return1'] = (data_t['CLOSE'] - data_t['CLOSE1t1']) / data_t['CLOSE1t1']
        data_t['return2'] = (data_t['CLOSE2t0'] - data_t['CLOSE2t1']) / data_t['CLOSE2t1']
        data_t['FACTORVALUE'] = (
                                        data_t['return1'] - data_t['return2']
                                ) * (data_t['LDATE2'] - data_t['LDATE1']).apply(lambda x: x.days)
        data_t = data_t[~np.isinf(data_t['FACTORVALUE'])].reset_index(drop=True)

        # data_t['POS'] = data_t['FACTORVALUE'] / abs(data_t['FACTORVALUE'])
        # data_t = data_t[~np.isnan(data_t['POS'])].reset_index(drop=True)
        data_t = xs_pos(data_t, quantile=quantile)

        data_tomorrow = kwargs['data_raw'][
            np.array(kwargs['data_raw']['TDATE'] == calendar[i + 1])
        ]
        data_tomorrow = data_tomorrow.drop_duplicates(subset=['CCODE'], keep='last')
        data_t = pd.merge(
            data_t, data_tomorrow[['CCODE', 'CLOSE']].rename(columns={'CLOSE': 'CLOSE1'}), on='CCODE', how='left'
        )
        data_t['RETURN'] = (data_t['CLOSE1'] / data_t['CLOSE'] - 1)
        data_t = xs_weight(data_t)
        pos = data_t[
            ['TDATE', 'EXCHANGE', 'PCODE', 'UCODE', 'CLOSE', 'POS', 'FACTORVALUE', 'CLOSE1', 'RETURN', 'WEIGHT']
        ].copy()

        pos['TDATE'] = calendar[i + 1]
        pos['FACTOR'] = index_name

        positions = pd.concat([positions, pos])
        print(index_name + ', ' + t_date.strftime('%Y-%m-%d') + ', ' + str(sum(data_t['POS'] != 0)))
    if len(positions) == 0:
        return

    positions['WEIGHT'] = positions['WEIGHT'] * 100
    positions['RETURN'] = positions['RETURN'] * 100
    positions['FACTORVALUE'] = positions['FACTORVALUE'] * 100
    return positions[
        ['TDATE', 'EXCHANGE', 'PCODE', 'UCODE', 'CLOSE', 'CLOSE1', 'POS', 'RETURN', 'FACTORVALUE', 'FACTOR', 'WEIGHT']
    ].reset_index(drop=True)


def xsmom(start_date, direction=1, **kwargs):
    data = kwargs['data']
    liq_days = kwargs['liq_days']
    data['UCODE'] = data['EXCHANGE'].apply(lambda x: str(x)) + data['PCODE'].apply(lambda x: str(x))
    calendar = data['TDATE'].drop_duplicates().tolist()

    window_days = kwargs['window_days']
    quantile = kwargs['quantile']

    if direction == 1:
        index_name = 'xsmom_d' + str(window_days) + '_q' + str(quantile)
    else:
        index_name = 'xsrev_d' + str(window_days) + '_q' + str(quantile)

    start_index = calendar.index(np.array(calendar)[np.array(calendar) >= start_date][0])

    positions = pd.DataFrame()

    for i in range(start_index, len(calendar) - 1):
        t_date = calendar[i]
        lookback_date = calendar[i - window_days]
        data_t = data[
            np.array(data['TDATE'] == t_date) & np.array(data['VOL'] > kwargs['min_volume'])
            ][['TDATE', 'EXCHANGE', 'PCODE', 'UCODE', 'CLOSE']]
        data_lookback = data[data['TDATE'] == lookback_date][['TDATE', 'UCODE', 'CLOSE']]
        data_tomorrow = data[
            np.array(data['TDATE'] == calendar[i + 1])
        ]

        data_liq = data[
            data['TDATE'] == calendar[i - liq_days]
            ][['UCODE']]

        data_t = pd.merge(data_liq, data_t, on='UCODE', how='inner')

        data_t = pd.merge(
            data_t[['EXCHANGE', 'PCODE', 'UCODE', 'CLOSE']],
            data_lookback[['UCODE', 'CLOSE']].rename(columns={'CLOSE': 'CLOSE0'}),
            on='UCODE', how='left'
        )
        data_t['FACTORVALUE'] = data_t['CLOSE'] / data_t['CLOSE0'] - 1

        data_t = xs_pos(data=data_t, direction=direction, quantile=quantile)
        data_t = pd.merge(
            data_t, data_tomorrow[['UCODE', 'CLOSE']].rename(columns={'CLOSE': 'CLOSE1'}), on='UCODE', how='left'
        )
        data_t['RETURN'] = (data_t['CLOSE1'] / data_t['CLOSE'] - 1)
        data_t = xs_weight(data_t)
        pos = data_t

        pos['TDATE'] = calendar[i + 1]
        pos['FACTOR'] = index_name
        positions = pd.concat([positions, pos])
        print(index_name + ', ' + t_date.strftime('%Y-%m-%d') + ', ' + str(sum(data_t['POS'] != 0)))
    if len(positions) == 0:
        return
    positions['WEIGHT'] = positions['WEIGHT'] * 100
    positions['RETURN'] = positions['RETURN'] * 100
    positions['FACTORVALUE'] = positions['FACTORVALUE'] * 100
    return positions.reset_index(drop=True)


def xsrev(start_date, **kwargs):
    return xsmom(start_date=start_date, direction=-1, **kwargs)


def xswr(start_date, price_field='CLOSE', lag=1, **kwargs):
    # 根据前一日仓单数据计算
    # 当日收盘价开平仓
    data = kwargs['data']
    data_wr = kwargs['data_wr']
    liq_days = kwargs['liq_days']
    data['UCODE'] = data['EXCHANGE'].apply(lambda x: str(x)) + data['PCODE'].apply(lambda x: str(x))
    data_wr['UCODE'] = data_wr['EXCHANGE'].apply(lambda x: str(int(x))) + data_wr['PCODE'].apply(lambda x: str(int(x)))

    calendar = data['TDATE'].drop_duplicates().tolist()

    window_days = kwargs['window_days']
    quantile = kwargs['quantile']
    index_name = 'xswr_d' + str(window_days) + '_q' + str(quantile)

    start_index = calendar.index(np.array(calendar)[np.array(calendar) >= start_date][0])

    positions = pd.DataFrame()
    for i in range(start_index, len(calendar) - 1):
        t_date = calendar[i]
        data_wr_0 = data_wr[data_wr['TDATE'] == calendar[i - lag - window_days]][['UCODE', 'PNAME', 'WRQCURRENT']]
        data_wr_t = data_wr[data_wr['TDATE'] == calendar[i - lag]][['UCODE', 'WRQCURRENT']]

        data_wr_range = pd.merge(
            data_wr_0.rename(columns={'WRQCURRENT': 'WR0'}),
            data_wr_t.rename(columns={'WRQCURRENT': 'WR1'}),
            on='UCODE', how='left'
        )
        data_wr_range['FACTORVALUE'] = (
            data_wr_range[data_wr_range['WR0'] > 0]['WR1'] / data_wr_range[data_wr_range['WR0'] > 0]['WR0'] - 1
        )

        # quantile_p = data_wr_range['FACTORVALUE'].quantile(quantile / 100)
        # quantile_n = data_wr_range['FACTORVALUE'].quantile(1 - quantile / 100)
        # data_wr_range['POS'] = data_wr_range['FACTORVALUE'].apply(
        #     lambda x: -1 if x > quantile_p else (1 if x < quantile_n else 0)
        # )
        data_wr_range = xs_pos(data=data_wr_range, direction=-1, quantile=quantile)

        # data_wr_range['POS'] = data_wr_range['POS'].fillna(0)

        data_t = data[
            np.array(data['TDATE'] == t_date) & np.array(data['VOL'] > kwargs['min_volume'])
            ][['TDATE', 'EXCHANGE', 'PCODE', 'UCODE', price_field]]

        data_liq = data[
            data['TDATE'] == calendar[i - liq_days]
            ][['UCODE']]

        data_t = pd.merge(data_liq, data_t, on='UCODE', how='inner')

        data_tomorrow = data[
            np.array(data['TDATE'] == calendar[i + 1])
        ][['TDATE', 'EXCHANGE', 'PCODE', 'UCODE', price_field]]

        data_t = pd.merge(data_t[['UCODE', price_field]], data_wr_range, on='UCODE', how='inner')

        data_t = pd.merge(
            data_t.rename(columns={price_field: 'CLOSE'}),
            data_tomorrow.rename(columns={price_field: 'CLOSE1'}),
            on='UCODE', how='left'
        )

        data_t['RETURN'] = (data_t['CLOSE1'] / data_t['CLOSE'] - 1)

        data_t['TDATE'] = calendar[i + 1]
        data_t['FACTOR'] = index_name
        data_t = xs_weight(data_t)
        positions = pd.concat([positions, data_t])
        print(index_name + ', ' + t_date.strftime('%Y-%m-%d') + ', ' + str(sum(data_t['POS'] != 0)))
    if len(positions) == 0:
        return
    positions['WEIGHT'] = positions['WEIGHT'] * 100
    positions['RETURN'] = positions['RETURN'] * 100
    positions = positions[
        ['TDATE', 'EXCHANGE', 'PCODE', 'UCODE', 'CLOSE', 'CLOSE1', 'POS', 'RETURN', 'FACTORVALUE', 'FACTOR', 'WEIGHT']
    ].reset_index(drop=True)
    return positions


# n日净持仓
# 净头寸区间总和为正做多
def mr(start_date, price_field='CLOSE', lag=1, **kwargs):
    data = kwargs['data']
    data_mr = kwargs['data_mr']
    liq_days = kwargs['liq_days']
    data['UCODE'] = data['EXCHANGE'].apply(lambda x: str(x)) + data['PCODE'].apply(lambda x: str(x))
    data_mr['UCODE'] = data_mr['EXCHANGE'].apply(lambda x: str(x)) + data_mr['PCODE'].apply(lambda x: str(x))

    calendar = data['TDATE'].drop_duplicates().tolist()

    window_days = kwargs['window_days']
    index_name = 'mr_d' + str(window_days)

    start_index = calendar.index(np.array(calendar)[np.array(calendar) >= start_date][0])

    positions = pd.DataFrame()
    for i in range(start_index, len(calendar) - 1):
        t_date = calendar[i]

        data_mr_t = data_mr[
            np.array(data_mr['TDATE'] >= calendar[i - lag - window_days])
            & np.array(data_mr['TDATE'] <= calendar[i - lag])
            ].groupby(by=['UCODE']).sum()[['MR']].reset_index()
        data_mr_range = data_mr_t

        data_mr_range['FACTORVALUE'] = data_mr_range['MR']
        # data_mr_range['POS'] = data_mr_range['FACTORVALUE'] / data_mr_range['FACTORVALUE'].abs()
        # data_mr_range['POS'] = data_mr_range['POS'].fillna(0)
        data_mr_range = ts_pos(data=data_mr_range)
        data_t = data[
            np.array(data['TDATE'] == t_date) & np.array(data['VOL'] > kwargs['min_volume'])
            ][['TDATE', 'EXCHANGE', 'PCODE', 'UCODE', price_field]]

        data_liq = data[
            data['TDATE'] == calendar[i - liq_days]
            ][['UCODE']]

        data_t = pd.merge(data_liq, data_t, on='UCODE', how='inner')

        data_tomorrow = data[
            np.array(data['TDATE'] == calendar[i + 1])
        ][['TDATE', 'EXCHANGE', 'PCODE', 'UCODE', price_field]]

        data_t = pd.merge(data_t[['UCODE', price_field]], data_mr_range, on='UCODE', how='inner')

        data_t = pd.merge(
            data_t.rename(columns={price_field: 'CLOSE'}),
            data_tomorrow.rename(columns={price_field: 'CLOSE1'}),
            on='UCODE', how='left'
        )

        data_t['RETURN'] = (data_t['CLOSE1'] / data_t['CLOSE'] - 1) #* data_t['POS']

        # index_all.append(index_all[-1] * (1 + data_t['RETURN'].mean()))
        data_t['TDATE'] = calendar[i + 1]
        data_t['FACTOR'] = index_name
        data_t = ts_weight(data_t)
        positions = pd.concat([positions, data_t])
        print(index_name + ', ' + t_date.strftime('%Y-%m-%d') + ', ' + str(sum(data_t['POS'] != 0)))
    if len(positions) == 0:
        return
    positions['WEIGHT'] = positions['WEIGHT'] * 100
    positions['RETURN'] = positions['RETURN'] * 100
    # positions['FACTORVALUE'] = positions['FACTORVALUE'] * 100
    return positions[
        ['TDATE', 'EXCHANGE', 'PCODE', 'UCODE', 'CLOSE', 'CLOSE1', 'POS', 'RETURN', 'FACTORVALUE', 'FACTOR', 'WEIGHT']
    ].reset_index(drop=True)


# n日净持仓变化
# 净头寸时序增加做多
def tsmr(start_date, price_field='CLOSE', lag=1, **kwargs):
    data = kwargs['data']
    data_mr = kwargs['data_mr']
    liq_days = kwargs['liq_days']
    data['UCODE'] = data['EXCHANGE'].apply(lambda x: str(x)) + data['PCODE'].apply(lambda x: str(x))
    data_mr['UCODE'] = data_mr['EXCHANGE'].apply(lambda x: str(x)) + data_mr['PCODE'].apply(lambda x: str(x))

    calendar = data['TDATE'].drop_duplicates().tolist()

    window_days = kwargs['window_days']
    index_name = 'tsmr_d' + str(window_days)

    start_index = calendar.index(np.array(calendar)[np.array(calendar) >= start_date][0])

    positions = pd.DataFrame()
    for i in range(start_index, len(calendar) - 1):
        t_date = calendar[i]
        data_mr_0 = data_mr[
            data_mr['TDATE'] == calendar[i - lag - window_days]
        ].groupby(by=['UCODE']).sum()[['MR']].reset_index()
        data_mr_t = data_mr[
            data_mr['TDATE'] == calendar[i - lag]
        ].groupby(by=['UCODE']).sum()[['MR']].reset_index()

        data_mr_range = pd.merge(
            data_mr_0.rename(columns={'MR': 'MR0'}),
            data_mr_t.rename(columns={'MR': 'MR1'}),
            on='UCODE', how='left'
        )
        data_mr_range['FACTORVALUE'] = data_mr_range['MR1'] - data_mr_range['MR0']
        # data_mr_range['POS'] = data_mr_range['FACTORVALUE'] / data_mr_range['FACTORVALUE'].abs()
        # data_mr_range['POS'] = data_mr_range['POS'].fillna(0)
        data_mr_range = ts_pos(data=data_mr_range)

        data_t = data[
            np.array(data['TDATE'] == t_date) & np.array(data['VOL'] > kwargs['min_volume'])
            ][['TDATE', 'EXCHANGE', 'PCODE', 'UCODE', price_field]]

        data_liq = data[
            data['TDATE'] == calendar[i - liq_days]
            ][['UCODE']]

        data_t = pd.merge(data_liq, data_t, on='UCODE', how='inner')

        data_tomorrow = data[
            np.array(data['TDATE'] == calendar[i + 1])
        ][['TDATE', 'EXCHANGE', 'PCODE', 'UCODE', price_field]]

        data_t = pd.merge(data_t[['UCODE', price_field]], data_mr_range, on='UCODE', how='inner')

        data_t = pd.merge(
            data_t.rename(columns={price_field: 'CLOSE'}),
            data_tomorrow.rename(columns={price_field: 'CLOSE1'}),
            on='UCODE', how='left'
        )

        data_t['RETURN'] = (data_t['CLOSE1'] / data_t['CLOSE'] - 1) #* data_t['POS']

        # index_all.append(index_all[-1] * (1 + data_t['RETURN'].mean()))
        data_t['TDATE'] = calendar[i + 1]
        data_t['FACTOR'] = index_name
        data_t = ts_weight(data_t)
        positions = pd.concat([positions, data_t])
        print(index_name + ', ' + t_date.strftime('%Y-%m-%d') + ', ' + str(sum(data_t['POS'] != 0)))
    if len(positions) == 0:
        return
    positions['WEIGHT'] = positions['WEIGHT'] * 100
    positions['RETURN'] = positions['RETURN'] * 100
    # positions['FACTORVALUE'] = positions['FACTORVALUE'] * 100
    return positions[
        ['TDATE', 'EXCHANGE', 'PCODE', 'UCODE', 'CLOSE', 'CLOSE1', 'POS', 'RETURN', 'FACTORVALUE', 'FACTOR', 'WEIGHT']
    ].reset_index(drop=True)


# n日净增减
# 净变化为正做多
def mrchg(start_date, price_field='CLOSE', lag=1, **kwargs):
    data = kwargs['data']
    data_mr = kwargs['data_mr']
    liq_days = kwargs['liq_days']
    data['UCODE'] = data['EXCHANGE'].apply(lambda x: str(x)) + data['PCODE'].apply(lambda x: str(x))
    data_mr['UCODE'] = data_mr['EXCHANGE'].apply(lambda x: str(x)) + data_mr['PCODE'].apply(lambda x: str(x))

    calendar = data['TDATE'].drop_duplicates().tolist()

    window_days = kwargs['window_days']
    index_name = 'mrchg_d' + str(window_days)

    start_index = calendar.index(np.array(calendar)[np.array(calendar) >= start_date][0])

    positions = pd.DataFrame()
    for i in range(start_index, len(calendar) - 1):
        t_date = calendar[i]
        data_mr_t = data_mr[
            np.array(data_mr['TDATE'] >= calendar[i - lag - window_days])
            & np.array(data_mr['TDATE'] <= calendar[i - lag])
            ].groupby(by=['UCODE']).sum()[['MRCHG']].reset_index()
        data_mr_range = data_mr_t

        data_mr_range['FACTORVALUE'] = data_mr_range['MRCHG']
        # data_mr_range['POS'] = data_mr_range['FACTORVALUE'] / data_mr_range['FACTORVALUE'].abs()
        # data_mr_range['POS'] = data_mr_range['POS'].fillna(0)
        data_mr_range = ts_pos(data=data_mr_range)

        data_t = data[
            np.array(data['TDATE'] == t_date) & np.array(data['VOL'] > kwargs['min_volume'])
            ][['TDATE', 'EXCHANGE', 'PCODE', 'UCODE', price_field]]

        data_liq = data[
            data['TDATE'] == calendar[i - liq_days]
            ][['UCODE']]

        data_t = pd.merge(data_liq, data_t, on='UCODE', how='inner')

        data_tomorrow = data[
            np.array(data['TDATE'] == calendar[i + 1])
        ][['TDATE', 'EXCHANGE', 'PCODE', 'UCODE', price_field]]

        data_t = pd.merge(data_t[['UCODE', price_field]], data_mr_range, on='UCODE', how='inner')

        data_t = pd.merge(
            data_t.rename(columns={price_field: 'CLOSE'}),
            data_tomorrow.rename(columns={price_field: 'CLOSE1'}),
            on='UCODE', how='left'
        )

        data_t['RETURN'] = (data_t['CLOSE1'] / data_t['CLOSE'] - 1) #* data_t['POS']

        # index_all.append(index_all[-1] * (1 + data_t['RETURN'].mean()))
        data_t['TDATE'] = calendar[i + 1]
        data_t['FACTOR'] = index_name
        data_t = ts_weight(data_t)
        positions = pd.concat([positions, data_t])
        print(index_name + ', ' + t_date.strftime('%Y-%m-%d') + ', ' + str(sum(data_t['POS'] != 0)))
    if len(positions) == 0:
        return
    positions['WEIGHT'] = positions['WEIGHT'] * 100
    positions['RETURN'] = positions['RETURN'] * 100
    # positions['FACTORVALUE'] = positions['FACTORVALUE'] * 100
    return positions[
        ['TDATE', 'EXCHANGE', 'PCODE', 'UCODE', 'CLOSE', 'CLOSE1', 'POS', 'RETURN', 'FACTORVALUE', 'FACTOR', 'WEIGHT']
    ].reset_index(drop=True)


def tspoichg(start_date, **kwargs):
    data = kwargs['data']
    liq_days = kwargs['liq_days']
    data['UCODE'] = data['EXCHANGE'].apply(lambda x: str(x)) + data['PCODE'].apply(lambda x: str(x))
    calendar = data['TDATE'].drop_duplicates().tolist()

    window_days = kwargs['window_days']

    index_name = 'tspoichg_d' + str(window_days)

    start_index = calendar.index(np.array(calendar)[np.array(calendar) >= start_date][0])

    positions = pd.DataFrame()
    for i in range(start_index, len(calendar) - 1):
        t_date = calendar[i]
        lookback_date = calendar[i - window_days]
        data_t = data[
            np.array(data['TDATE'] == t_date)
            & np.array(data['VOL'] > kwargs['min_volume'])
            ][['TDATE', 'EXCHANGE', 'PCODE', 'UCODE', 'CLOSE', 'POI']]

        data_liq = data[
            data['TDATE'] == calendar[i - liq_days]
            ][['UCODE']]

        data_t = pd.merge(data_liq, data_t, on='UCODE', how='inner')

        data_lookback = data[
            np.array(data['TDATE'] == lookback_date)
            & np.array(data['POI'] > 0)
        ][['TDATE', 'UCODE', 'CLOSE', 'POI']]

        data_t = pd.merge(
            data_t[['EXCHANGE', 'PCODE', 'UCODE', 'CLOSE', 'POI']],
            data_lookback[['UCODE', 'POI']].rename(columns={'POI': 'POI0'}),
            on='UCODE', how='left'
        )

        data_t['FACTORVALUE'] = data_t['POI'] / data_t['POI0'] - 1
        data_t = ts_pos(data_t)

        data_tomorrow = data[np.array(data['TDATE'] == calendar[i + 1])]

        data_t = pd.merge(
            data_t, data_tomorrow[['UCODE', 'CLOSE']].rename(columns={'CLOSE': 'CLOSE1'}),
            on='UCODE', how='left'
        )

        data_t['RETURN'] = (data_t['CLOSE1'] / data_t['CLOSE'] - 1)

        data_t['TDATE'] = calendar[i + 1]
        data_t['FACTOR'] = index_name

        data_t = ts_weight(data_t)

        positions = pd.concat([positions, data_t])
        print(index_name + ', ' + t_date.strftime('%Y-%m-%d') + ', ' + str(sum(data_t['POS'] != 0)))
    if len(positions) == 0:
        return
    positions['WEIGHT'] = positions['WEIGHT'] * 100
    positions['RETURN'] = positions['RETURN'] * 100
    positions['FACTORVALUE'] = positions['FACTORVALUE'] * 100
    return positions.drop(columns=['POI', 'POI0']).reset_index(drop=True)


def tspvolchg(start_date, **kwargs):
    data = kwargs['data']
    liq_days = kwargs['liq_days']
    data['UCODE'] = data['EXCHANGE'].apply(lambda x: str(x)) + data['PCODE'].apply(lambda x: str(x))
    calendar = data['TDATE'].drop_duplicates().tolist()

    window_days = kwargs['window_days']

    index_name = 'tspvolchg_d' + str(window_days)

    start_index = calendar.index(np.array(calendar)[np.array(calendar) >= start_date][0])

    positions = pd.DataFrame()
    for i in range(start_index, len(calendar) - 1):
        t_date = calendar[i]
        lookback_date = calendar[i - window_days]
        data_t = data[
            np.array(data['TDATE'] == t_date)
            & np.array(data['VOL'] > kwargs['min_volume'])
            ][['TDATE', 'EXCHANGE', 'PCODE', 'UCODE', 'CLOSE', 'PVOL']]

        data_liq = data[
            data['TDATE'] == calendar[i - liq_days]
            ][['UCODE']]

        data_t = pd.merge(data_liq, data_t, on='UCODE', how='inner')

        data_lookback = data[
            np.array(data['TDATE'] == lookback_date)
            & np.array(data['PVOL'] > 0)
            ][['TDATE', 'UCODE', 'CLOSE', 'PVOL']]

        data_t = pd.merge(
            data_t[['EXCHANGE', 'PCODE', 'UCODE', 'CLOSE', 'PVOL']],
            data_lookback[['UCODE', 'PVOL']].rename(columns={'PVOL': 'PVOL0'}),
            on='UCODE', how='left'
        )

        data_t['FACTORVALUE'] = data_t['PVOL'] / data_t['PVOL0'] - 1
        data_t = ts_pos(data_t)

        data_tomorrow = data[np.array(data['TDATE'] == calendar[i + 1])]

        data_t = pd.merge(
            data_t, data_tomorrow[['UCODE', 'CLOSE']].rename(columns={'CLOSE': 'CLOSE1'}),
            on='UCODE', how='left'
        )

        data_t['RETURN'] = (data_t['CLOSE1'] / data_t['CLOSE'] - 1)

        data_t['TDATE'] = calendar[i + 1]
        data_t['FACTOR'] = index_name

        data_t = ts_weight(data_t)

        positions = pd.concat([positions, data_t])
        print(index_name + ', ' + t_date.strftime('%Y-%m-%d') + ', ' + str(sum(data_t['POS'] != 0)))
    if len(positions) == 0:
        return
    positions['WEIGHT'] = positions['WEIGHT'] * 100
    positions['RETURN'] = positions['RETURN'] * 100
    positions['FACTORVALUE'] = positions['FACTORVALUE'] * 100
    return positions.drop(columns=['PVOL', 'PVOL0']).reset_index(drop=True)


def xspoichg(start_date, **kwargs):
    data = kwargs['data']
    liq_days = kwargs['liq_days']
    data['UCODE'] = data['EXCHANGE'].apply(lambda x: str(x)) + data['PCODE'].apply(lambda x: str(x))
    calendar = data['TDATE'].drop_duplicates().tolist()

    window_days = kwargs['window_days']
    quantile = kwargs['quantile']

    index_name = 'xspoichg_d' + str(window_days) + '_q' + str(quantile)

    start_index = calendar.index(np.array(calendar)[np.array(calendar) >= start_date][0])

    positions = pd.DataFrame()

    for i in range(start_index, len(calendar) - 1):
        t_date = calendar[i]
        lookback_date = calendar[i - window_days]
        data_t = data[
            np.array(data['TDATE'] == t_date)
            & np.array(data['VOL'] > kwargs['min_volume'])
        ][['TDATE', 'EXCHANGE', 'PCODE', 'UCODE', 'CLOSE', 'POI']]

        data_liq = data[
            data['TDATE'] == calendar[i - liq_days]
            ][['UCODE']]

        data_t = pd.merge(data_liq, data_t, on='UCODE', how='inner')

        data_lookback = data[
            np.array(data['TDATE'] == lookback_date)
            & np.array(data['POI'] > 0)
            ][['TDATE', 'UCODE', 'CLOSE', 'POI']]

        data_t = pd.merge(
            data_t[['EXCHANGE', 'PCODE', 'UCODE', 'CLOSE', 'POI']],
            data_lookback[['UCODE', 'POI']].rename(columns={'POI': 'POI0'}),
            on='UCODE', how='left'
        )

        data_t['FACTORVALUE'] = data_t['POI'] / data_t['POI0'] - 1

        data_t = xs_pos(data=data_t, quantile=quantile)

        data_tomorrow = data[np.array(data['TDATE'] == calendar[i + 1])]
        data_t = pd.merge(
            data_t, data_tomorrow[['UCODE', 'CLOSE']].rename(columns={'CLOSE': 'CLOSE1'}), on='UCODE', how='left'
        )
        data_t['RETURN'] = (data_t['CLOSE1'] / data_t['CLOSE'] - 1)
        data_t = xs_weight(data_t)
        pos = data_t

        pos['TDATE'] = calendar[i + 1]
        pos['FACTOR'] = index_name
        positions = pd.concat([positions, pos])
        print(index_name + ', ' + t_date.strftime('%Y-%m-%d') + ', ' + str(sum(data_t['POS'] != 0)))
    if len(positions) == 0:
        return
    positions['WEIGHT'] = positions['WEIGHT'] * 100
    positions['RETURN'] = positions['RETURN'] * 100
    positions['FACTORVALUE'] = positions['FACTORVALUE'] * 100
    return positions.drop(columns=['POI', 'POI0']).reset_index(drop=True)


def xssigma(start_date, **kwargs):
    data = kwargs['data']
    liq_days = kwargs['liq_days']
    data['UCODE'] = data['EXCHANGE'].apply(lambda x: str(x)) + data['PCODE'].apply(lambda x: str(x))
    calendar = data['TDATE'].drop_duplicates().tolist()

    window_days = kwargs['window_days']
    quantile = kwargs['quantile']

    index_name = 'xssigma_d' + str(window_days) + '_q' + str(quantile)

    start_index = calendar.index(np.array(calendar)[np.array(calendar) >= start_date][0])

    positions = pd.DataFrame()
    data_close = data.pivot(index='TDATE', columns='UCODE', values='CLOSE')
    data_vol = data.pivot(index='TDATE', columns='UCODE', values='VOL')
    data_sigma = data_close.pct_change().rolling(window_days).std(ddof=1) * np.sqrt(240)

    for i in range(start_index, len(calendar) - 1):
        t_date = calendar[i]

        ucode_vol = data_vol.columns[data_vol.loc[t_date, :] > kwargs['min_volume']].tolist()
        ucode_liq = data_vol.columns[
            data_vol.loc[calendar[i - max(liq_days, window_days)], :] > kwargs['min_volume']
        ].tolist()
        ucode = list(set(ucode_liq).intersection(set(ucode_vol)))
        data_t = data[
            np.array(data['TDATE'] == t_date)
            ][['TDATE', 'EXCHANGE', 'PCODE', 'UCODE', 'CLOSE']]

        data_t = data_t.merge(
            pd.DataFrame(data_sigma.loc[t_date, ucode]).rename(columns={t_date: 'FACTORVALUE'}).reset_index(),
            on='UCODE', how='inner'
        )

        data_t = xs_pos(data=data_t, quantile=quantile)

        data_tomorrow = data[np.array(data['TDATE'] == calendar[i + 1])]
        data_t = pd.merge(
            data_t, data_tomorrow[['UCODE', 'CLOSE']].rename(columns={'CLOSE': 'CLOSE1'}), on='UCODE', how='left'
        )
        data_t['RETURN'] = (data_t['CLOSE1'] / data_t['CLOSE'] - 1)
        data_t = xs_weight(data_t)
        pos = data_t

        pos['TDATE'] = calendar[i + 1]
        pos['FACTOR'] = index_name
        positions = pd.concat([positions, pos])
        print(index_name + ', ' + t_date.strftime('%Y-%m-%d') + ', ' + str(sum(data_t['POS'] != 0)))
    if len(positions) == 0:
        return
    positions['WEIGHT'] = positions['WEIGHT'] * 100
    positions['RETURN'] = positions['RETURN'] * 100
    positions['FACTORVALUE'] = positions['FACTORVALUE'] * 100
    return positions.reset_index(drop=True)
