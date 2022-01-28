import pymysql
import numpy as np
import pandas as pd
from scipy import optimize as sco


def generate_table(database, table, generate_sql, sql_ip, sql_user, sql_pass, table_comment=''):
    db = pymysql.connect(sql_ip, sql_user, sql_pass, database)

    cursor = db.cursor()

    sql = 'create table `' + table + '` ' + generate_sql + ' comment=\'' + table_comment + '\''
    cursor.execute(sql)
    db.close()


def portfolio_var(weights, cov_matrix):
    return np.dot(weights.T, np.dot(cov_matrix, weights))


def risk_contribute(weights, cov_matrix):
    std = np.sqrt(portfolio_var(weights, cov_matrix))
    mrc = np.matrix(cov_matrix) * np.matrix(weights).T
    return np.multiply(mrc, np.matrix(weights).T) / std


def portfolio_annualised_performance(weights, mean_returns, cov_matrix, freq=252):
    returns = np.sum(mean_returns * weights) * freq
    std = np.sqrt(portfolio_var(weights, cov_matrix)) * np.sqrt(freq)
    return std, returns


def negative_sharpe_ratio(weights, mean_returns, cov_matrix, risk_free_rate, freq=252):
    p_var, p_ret = portfolio_annualised_performance(weights, mean_returns, cov_matrix, freq=freq)
    return -(p_ret - risk_free_rate) / p_var


def max_sharpe_ratio(mean_returns, cov_matrix, risk_free_rate=0.015, freq=252, single_max=0.3):
    num_assets = len(mean_returns)
    args = (mean_returns, cov_matrix, risk_free_rate, freq)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    # bound = (0.0, 1.0)
    # bounds = tuple(bound for asset in range(num_assets))
    bounds = sco.Bounds([0] * num_assets, [single_max] * num_assets)
    result = sco.minimize(
        negative_sharpe_ratio,
        np.array(num_assets * [1 / num_assets]),
        args=args,
        method='SLSQP',
        bounds=bounds,
        constraints=constraints
    )
    return pd.DataFrame(
        result.x,
        index=mean_returns.index,
        columns=['allocation']
    )
