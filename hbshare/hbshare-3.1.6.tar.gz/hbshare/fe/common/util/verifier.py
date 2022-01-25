# -*- coding: utf-8 -*-

import pandas as pd
from hbshare.fe.common.util.exception import InputParameterError
from hbshare.fe.common.util.logger import logger


def verify_trading_day(trading_day_list):
    try:
        pd.DatetimeIndex(trading_day_list)
    except Exception as e:
        msg = "trading day is of bad format: %s" % e.message
        logger.error(msg)
        raise InputParameterError(msg)


def verify_type(var, var_name, var_type, trading_day=None):
    if not isinstance(var, var_type):
        msg = '%s, %s is not a %s, check your input' % (
            trading_day, var_name, str(var_type)) if trading_day is not None else \
            '%s is not a %s, check your input' % (var_name, str(var_type))
        logger.error(msg)
        raise InputParameterError(msg)


def verify_df_not_null(var, var_name, trading_day=None):
    if not var.notnull().all().all():
        msg = 'Date: %s, %s has NaN value, check your input' % (trading_day, var_name) if trading_day is not None else\
            '%s has NaN value, check your input' % var_name
        logger.error(msg)
        raise InputParameterError(msg)


def __verify_risk_model_one_day(trading_day,
                                risk_model_one_day,
                                sub_factors=None):
    if not isinstance(risk_model_one_day, dict):
        msg = '%s risk_model is not a dict, check your input' % trading_day
        logger.error(msg)
        raise InputParameterError(msg)
    verify_type(risk_model_one_day, 'risk_model_one_day', dict)
    exposure_df = risk_model_one_day.get('exposure')
    factor_covariance_df = risk_model_one_day.get('factor_covariance')
    specific_risk_series = risk_model_one_day.get('specific_risk')
    if sub_factors is None:
        verify_type(exposure_df, 'exposure_df', pd.DataFrame, trading_day)
        verify_type(factor_covariance_df, 'factor_covariance_df', pd.DataFrame, trading_day)
        verify_type(specific_risk_series, 'specific_risk_series', pd.Series, trading_day)
        verify_df_not_null(exposure_df, 'exposure_df', trading_day)
        verify_df_not_null(factor_covariance_df, 'factor_covariance_df', trading_day)
        verify_df_not_null(specific_risk_series, 'specific_risk_series', trading_day)
    else:
        verify_type(specific_risk_series, 'specific_risk_series', pd.Series, trading_day)


def verify_risk_model_hist(risk_model_dict, trading_day_list, sub_factors=None):
    verify_type(risk_model_dict, 'risk_model_dict', dict)

    if 'data' not in risk_model_dict.keys() or 'schema' not in risk_model_dict.keys():
        msg = 'missing key data or schema in risk_model'
        logger.error(msg)
        raise InputParameterError(msg)

    if 'industry_field' not in risk_model_dict['schema']:
        msg = 'missing key industry_field in the schema of risk_model'
        logger.error(msg)
        raise InputParameterError(msg)

    if 'style_field' not in risk_model_dict['schema']:
        msg = 'missing key style_field in the schema of risk_model'
        logger.error(msg)
        raise InputParameterError(msg)

    for trading_day in trading_day_list:
        risk_model_one_day = risk_model_dict['data'].get(trading_day)
        if risk_model_one_day is not None:
            __verify_risk_model_one_day(
                trading_day, risk_model_one_day, sub_factors=sub_factors)
        else:
            msg = 'missing risk_model data on %s' % trading_day
            logger.error(msg)
            raise InputParameterError(msg)


def verify_multiple_type(var, var_name, multiple_type, trading_day=None):
    if not isinstance(var, multiple_type):
        msg = '%s, %s is not a %s, check your input' % (
            trading_day, var_name, str(multiple_type)) if trading_day is not None else\
            '%s is not a %s, check your input' % var_name
        logger.error(msg)
        raise InputParameterError(msg)


def verify_simulation_day(simulation_date_list, trading_day_list):
    if simulation_date_list is None or len(simulation_date_list) == 0:
        msg = 'the simulation_date_list is empty'
        logger.error(msg)
        raise InputParameterError(msg)
    elif len(trading_day_list) != 0:
        if simulation_date_list[-1] < trading_day_list[-1] or simulation_date_list[0] > trading_day_list[0]:
            msg = 'the simulation_date_list does not cover the trading_day_list'
            logger.error(msg)
            raise InputParameterError(msg)
    else:
        msg = 'warning trading day is empty'
        logger.warning(msg)
        raise Warning(msg)


def verify_simple_data_duplicate(var, var_name, trading_day=None):
    if len(var) != len(set(var)):
        msg = "Date: %s, %s has duplicated data, check your input" % (trading_day, var_name) if \
            trading_day is not None else "%s has duplicated data, check your input" % var_name
        logger.error(msg)
        raise InputParameterError(message=msg)


def verify_container_fully_inclusion(container, target, container_name, target_name, trading_day=None, is_error=True):
    missing_inclusion_list = list(set(target) - set(container))
    missing_inclusion_list = [str(x) for x in missing_inclusion_list]
    if len(missing_inclusion_list) > 0:
        msg = "Date: %s, %s in %s are not included in %s" % (
            trading_day, ','.join(missing_inclusion_list), target_name, container_name)
        if is_error:
            logger.error(msg)
            raise InputParameterError(message=msg)
        else:
            logger.warning(msg)
            return msg
