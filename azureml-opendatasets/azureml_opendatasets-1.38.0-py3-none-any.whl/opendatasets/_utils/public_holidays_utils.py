# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import lzma
import os.path
import pickle
from datetime import date, datetime, timedelta
from io import StringIO

import numpy as np
import pandas as pd
import pkg_resources
from pandas import Series

pkgs = __name__.split('.')
PACKAGE_NAME = '.'.join(pkgs[: pkgs.index('opendatasets') + 1])


def get_window_by_effect_gap(effect: str, gap: int) -> int:
    """
    Generate holiday window number.

    :param effect: holiday window effect level
    :param gap: the delta days between current holiday and the last/next holiday
    """
    effect_num = 0
    if effect == 'Low':
        effect_num = 2
    if effect == 'Meduim':
        effect_num = 5
    if effect == 'High':
        effect_num = 10
    if effect_num > gap:
        return gap
    else:
        return effect_num


def adding_holidayname_by_window(_countryOrRegion: str, _countryOrRegionCode: str, _name: str,
                                 window: int, window_type: str, curDate: date, data: pd.DataFrame) \
        -> pd.DataFrame:
    """
    Generate holiday window name.

    :param _countryOrRegion: country or region of current data.
    :param _countryOrRegionCode: countryOrRegionCode of current data.
    :param _name: holiday name which needs be processed.
    :param window: window of current holiday.
    :param window_type: lower window or upper window.
    :param curDate: date of the holiday.
    :param data: holiday data which needs be processed.
    :return: The dataframe with holidayname base on the window added row by row.
    """
    for i in range(1, window + 1):
        newDate = curDate
        windowInName = ' days '
        if i == 1:
            windowInName = ' day '
        if window_type == 'lower':
            windowInName = windowInName + 'before '
            newDate = curDate + timedelta(days=-i)
        if window_type == 'upper':
            windowInName = windowInName + 'after '
            newDate = curDate + timedelta(days=i)
        if np.datetime64(newDate) not in data['Date'].values:
            name = str(i) + windowInName + _name
            data = data.append({'Name': name, 'Date': newDate, 'CountryOrRegion': _countryOrRegion,
                                'CountryCode': _countryOrRegionCode}, ignore_index=True)
    return data


def adding_holidayname_by_window_row_by_row(data: pd.DataFrame, target_data: pd.DataFrame) -> pd.DataFrame:
    """
    Generate holiday window names row by row.

    :param data: holiday data which needs be iterated.
    :param target_data: holiday data which needs be processed.
    :return: The dataframe with holidayname base on the window added row by row.
    """
    target_data_origin = target_data.copy()
    country_lst = Series(data.CountryCode.values,
                         index=data.CountryOrRegion).to_dict().keys()
    for item in country_lst:
        temp_target = target_data[target_data.CountryOrRegion == item]
        temp_country_df = data[data.CountryOrRegion == item]
        for idx, row in temp_country_df.iterrows():
            lower = row['lowerWindow']
            upper = row['upperWindow']

            _countryOrRegion = row['CountryOrRegion']
            _countryOrRegionCode = row['CountryCode']
            curDate = pd.to_datetime(row['Date'])
            _name = row['Name']
            temp_target = adding_holidayname_by_window(_countryOrRegion, _countryOrRegionCode, _name,
                                                       lower, 'lower', curDate, temp_target)
            temp_target = adding_holidayname_by_window(_countryOrRegion, _countryOrRegionCode, _name,
                                                       upper, 'upper', curDate, temp_target)
        target_data_origin = pd.concat([target_data_origin, temp_target], ignore_index=True) \
            .drop(columns=['index']).drop_duplicates()
        target_data_origin.reset_index(drop=True)
    return target_data_origin


def update_holidays_by_adding_window(target_dir: str) -> None:
    """Generate the holidays csv with window into name."""
    holiday_dataPath = pkg_resources \
        .resource_filename(PACKAGE_NAME,
                           os.path.join('data', 'holidays.7z'))
    holiday_origin_dataPath = pkg_resources \
        .resource_filename(PACKAGE_NAME,
                           os.path.join('data', 'holidays_origin.7z'))
    window_dataPath = pkg_resources \
        .resource_filename(PACKAGE_NAME,
                           os.path.join('data', 'holiday_effect_window.7z'))
    dir_tmp = target_dir if target_dir.endswith("\\") else target_dir + "\\"
    window_dataPath_csv = dir_tmp + 'holiday_effect_window.csv'
    holiday_window = pd.read_csv(window_dataPath_csv, encoding='utf-8-sig')
    holiday_window['effectLevel'] = [x if x and not pd.isnull(
        x) else "" for x in holiday_window['effectLevel']]
    with lzma.open(window_dataPath, "wb") as fw:
        fw.write(pickle.dumps(holiday_window))
    with lzma.open(window_dataPath, "rb") as fr:
        holiday_window = pickle.loads(fr.read())

    with lzma.open(holiday_origin_dataPath, "rb") as f:
        df_origin = pickle.loads(f.read())
    df_origin = df_origin.rename(columns={'normalizeHolidayName': 'Name', 'countryOrRegion': 'CountryOrRegion',
                                          'countryRegionCode': 'CountryCode', 'date': 'Date',
                                          'isPaidTimeOff': 'IsPaidTimeOff'})
    df_com = df_origin.set_index(['holidayName', 'CountryOrRegion']) \
        .join(holiday_window.set_index(['holidayName', 'CountryOrRegion']), how='left')
    df_com = df_com.reset_index()
    df_com['isObserved'] = df_com['holidayName'].apply(
        lambda x: x.find("(Observed)"))
    df_com = df_com[df_com.isObserved < 0]
    _holidays = df_com.reset_index()

    country_lst = Series(_holidays.CountryCode.values,
                         index=_holidays.CountryOrRegion).to_dict().keys()

    current_df = pd.DataFrame(
        columns=['Date', 'CountryOrRegion', 'gapFormer', 'gapNext'])
    for item in country_lst:
        temp_dts = list(dict.fromkeys(
            _holidays[_holidays.CountryOrRegion == item]['Date'].tolist(), None).keys())
        temp_dts.sort()
        i = 0
        while i < len(temp_dts):
            gapN = 0
            gapF = 0
            if i == len(temp_dts) - 1:
                gapN = 0
            elif i >= 0:
                gapN = (temp_dts[i + 1] - temp_dts[i]).days
                if i > 0:
                    gapF = (temp_dts[i] - temp_dts[i - 1]).days
            current_df = current_df.append({'Date': temp_dts[i], 'CountryOrRegion': item,
                                            'gapFormer': gapF, 'gapNext': gapN}, ignore_index=True)
            i = i + 1

    temp = _holidays.copy()
    temp.drop(columns=['holidayName', 'isObserved',
                       'effectLevel'], inplace=True)

    _holidays = _holidays.set_index(['Date', 'CountryOrRegion']) \
        .join(current_df.set_index(['Date', 'CountryOrRegion']), how='left')
    _holidays = _holidays.reset_index()
    temp.reset_index(inplace=True, drop=True)

    _holidays['lowerWindow'] = _holidays.apply(lambda row:
                                               get_window_by_effect_gap(
                                                   row['effectLevel'], row['gapFormer']),
                                               axis=1)
    _holidays['upperWindow'] = _holidays.apply(lambda row:
                                               get_window_by_effect_gap(
                                                   row['effectLevel'], row['gapNext']),
                                               axis=1)

    # Here is the part to generate holiday window names
    temp = adding_holidayname_by_window_row_by_row(_holidays, temp)

    temp['_IsPaidTimeOff'] = [x if isinstance(
        x, bool) else np.nan for x in temp['IsPaidTimeOff']]
    temp.drop(columns=['IsPaidTimeOff'], inplace=True)
    temp = temp.rename(
        columns={'_IsPaidTimeOff': 'IsPaidTimeOff'}).sort_values(by=['Date'])
    temp = temp.rename(columns={'Date': 'date',
                                'Name': 'normalizeHolidayName',
                                'CountryOrRegion': 'countryOrRegion',
                                'CountryCode': 'countryRegionCode',
                                'IsPaidTimeOff': 'isPaidTimeOff'})
    csv_content = temp.to_csv(index=False, date_format='%m/%d/%Y')
    df = pd.read_csv(StringIO(csv_content),
                     parse_dates=['date'],
                     date_parser=lambda x: pd.datetime.strptime(x, '%m/%d/%Y'))
    with lzma.open(holiday_dataPath, "wb") as f:
        f.write(pickle.dumps(df))


def prepare_for_update(target_dir: str) -> None:
    holiday_dataPath = pkg_resources \
        .resource_filename(PACKAGE_NAME,
                           os.path.join('data', 'holidays.7z'))
    holiday_origin_dataPath = pkg_resources \
        .resource_filename(PACKAGE_NAME,
                           os.path.join('data', 'holidays_origin.7z'))
    window_dataPath = pkg_resources \
        .resource_filename(PACKAGE_NAME,
                           os.path.join('data', 'holiday_effect_window.7z'))

    dir_tmp = target_dir if target_dir.endswith("\\") else target_dir + "\\"
    target_dir = dir_tmp + r"backup_" + \
        datetime.utcnow().strftime("%Y%m%d%H%M%S") + "\\"
    holiday_window_updated = dir_tmp + r"holiday_effect_window.csv"
    holiday_window_7z_path = target_dir + r"holiday_effect_window.7z"
    holiday_origin_7z_path = target_dir + r"holidays_origin.7z"
    holiday_7z_path = target_dir + r"holidays.7z"

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    with lzma.open(holiday_dataPath, "rb") as f:
        backupdf = pickle.loads(f.read())
        with lzma.open(holiday_7z_path, "wb") as fw:
            fw.write(pickle.dumps(backupdf))
    with lzma.open(holiday_origin_dataPath, "rb") as f:
        backupdf = pickle.loads(f.read())
        with lzma.open(holiday_origin_7z_path, "wb") as fw:
            fw.write(pickle.dumps(backupdf))

    with lzma.open(window_dataPath, "rb") as f:
        holiday_window = pickle.loads(f.read())
        with lzma.open(holiday_window_7z_path, "wb") as fw:
            fw.write(pickle.dumps(holiday_window))
    holiday_window.to_csv(holiday_window_updated,
                          encoding='utf-8-sig', index=False, date_format='%m/%d/%Y')
