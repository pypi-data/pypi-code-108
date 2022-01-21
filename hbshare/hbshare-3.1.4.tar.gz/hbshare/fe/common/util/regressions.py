# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from hbshare.fe.common.util.exception import PreprocessError
from hbshare.fe.common.util.logger import logger
from scipy.optimize import minimize


def linear_regression(n, x, y):
    A = np.array([x, np.ones(n)])
    w = np.linalg.lstsq(A.T, y)
    a = w[0][0]
    residual = y - x * a
    return w[0], residual


def delete_redundancy(x_data_frame, corr_threshold=0.7):
    corr_df = x_data_frame.corr()
    corr_len = len(corr_df)
    x_list = x_data_frame.columns.tolist()
    remove_list = []
    for i in range(corr_len):
        for j in range(i + 1, corr_len):
            if corr_df.iloc[i, j] > corr_threshold:
                remove_list.append(x_list[j])
                continue
    left_list = list(set(x_list) - set(remove_list))
    return x_data_frame[left_list]


class Regression:
    def __init__(self, x_data, y_data, upper, lower, ridge_lambda=0.001, method='ridge', effort='weak',
                 pca_vec_mat=None, use_pca=False):
        if method == "reduce":
            x_data = delete_redundancy(x_data)

        if 'alpha' not in x_data.columns:
            sort_list = ['alpha'] + x_data.columns.tolist()
            x_data.loc[:, 'alpha'] = 1.0
            x_data = x_data[sort_list]

        self.x_data = x_data
        self.y_data = y_data
        self.upper = upper
        self.lower = lower
        self.method = method
        self.effort = effort
        self.pca_vec_mat = pca_vec_mat
        self.use_pca = use_pca
        self.ridge_lambda = ridge_lambda

    def __ols_func(self, x):
        x_beta = (np.matrix(self.x_data) * np.matrix(x).T).A1
        eps = self.y_data - x_beta
        delta = sum(eps ** 2)
        return delta

    def __ridge_func(self, x):
        x_beta = (np.matrix(self.x_data) * np.matrix(x).T).A1
        eps = self.y_data - x_beta
        delta = sum(eps ** 2) + sum(x * x) * self.ridge_lambda
        return delta

    def __get_bnds(self):
        n_param = self.x_data.shape[1]
        x0 = np.ones(n_param) / float(n_param)

        if self.effort == 'hard':
            bnds = [(None, None)] + [(self.lower, self.upper) for _ in range(len(x0) - 1)]
            bnds = tuple(bnds)
        else:
            bnds = tuple((None, None) for _ in x0)
        return bnds, x0

    def __get_cons(self):
        if self.effort == 'hard':
            cons_list_dict = [{'type': 'eq', 'fun': lambda x: sum(x[1:]) - 1}]
        else:
            cons_list_dict = []

        if self.use_pca and self.pca_vec_mat is not None:
            for i in range(len(self.pca_vec_mat)):
                array_list = self.pca_vec_mat[i, :].A1
                cons_list_dict.append({'type': 'ineq', 'fun': lambda x: sum(x[1:] * array_list)})
        cons = tuple(cons_list_dict)
        return cons

    def solve(self):
        if not isinstance(self.x_data, (type(pd.DataFrame()), type(pd.Series()))):
            msg = "NavRegression x_data Type is not pandas.DataFrame and pandas.Series."
            logger.exception(msg)
            raise PreprocessError(message=msg)

        if not isinstance(self.y_data, type(pd.Series())):
            msg = "NavRegression y_data Type is note pandas.Series."
            logger.exception(msg)
            raise PreprocessError(message=msg)

        if len(self.x_data) != len(self.y_data):
            msg = "NavRegression x_data length not equals to y_data length."
            logger.exception(msg)
            raise PreprocessError(message=msg)

        if self.method == 'ridge':
            target_func = self.__ridge_func
        else:
            target_func = self.__ols_func

        bnds, x0 = self.__get_bnds()
        cons = self.__get_cons()
        options = {'disp': False, 'maxiter': 500, 'ftol': 1e-20}

        res = minimize(target_func, x0, bounds=bnds, constraints=cons, method='SLSQP', options=options)
        solution = pd.Series(index=self.x_data.columns.tolist(), data=res.x)
        solution_with_alpha = solution

        y_estimate = self.x_data.dot(solution)

        solution_without_alpha = solution.drop('alpha')
        solution_without_alpha.sort_values(inplace=True)

        sse = self.y_data.subtract(y_estimate).pow(2.0).sum()
        sst = self.y_data.subtract(self.y_data.mean()).pow(2.0).sum()
        r_square = 1 - sse / sst
        p_value = pd.Series()

        return {
            'solution': solution_without_alpha,
            'solution_with_alpha': solution_with_alpha,
            'sse': sse,
            'alpha': res.x[0],
            'y_estimate_wo_alpha': y_estimate.subtract(res.x[0]),
            'r_square': r_square,
            'p_value': p_value
        }
