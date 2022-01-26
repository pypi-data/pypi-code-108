from sklearn.impute import SimpleImputer
from autoai_ts_libs.srom.imputers.base import DecompositionImputer
from sklearn.decomposition import KernelPCA, PCA, TruncatedSVD, IncrementalPCA, NMF
import numpy as np


class PCAImputer(DecompositionImputer):
    """
    Imputer using PCA
    Parameters:
        time_column (int): time column.
        missing_values (obj): missing value to be imputed.
        enable_fillna (boolean): fill na after interpolation if any.
        order (int): look back order.
        base_imputer (obj): base imputer to be used.
        scaler(obj): data scaler object necessary for decomposition.
        max_iter(int): max iterations.
        tol(float): tolerance for singular values.
        n_components(int): number of components.
        whiten(boolean): wheather to whiten or not.
        svd_solver(str): solver.
        random_stat(int): random state.
    """
    def __init__(
        self,
        time_column=-1,
        missing_values=np.nan,
        enable_fillna=True,
        order=-1,
        base_imputer=SimpleImputer(),
        scaler=None,
        max_iter=10,
        tol=1e-3,
        n_components=None,
        whiten=False,
        svd_solver="auto",
        random_state=42,
    ):
        self.n_components = n_components
        self.whiten = whiten
        self.svd_solver = svd_solver
        self.random_state = random_state

        super(PCAImputer, self).__init__(
            time_column=time_column,
            missing_values=missing_values,
            enable_fillna=enable_fillna,
            order=order,
            base_imputer=base_imputer,
            scaler=scaler,
            decomposer=PCA(
                n_components=n_components,
                whiten=whiten,
                svd_solver=svd_solver,
                random_state=random_state,
            ),
            max_iter=max_iter,
            tol=tol,
        )


class KernelPCAImputer(DecompositionImputer):
    """
    Imputer using KernelPCA
    Parameters:
        time_column (int): time column.
        missing_values (obj): missing value to be imputed.
        enable_fillna (boolean): fill na after interpolation if any.
        order (int): look back order.
        base_imputer (obj): base imputer to be used.
        scaler(obj): data scaler object necessary for decomposition.
        max_iter(int): max iterations.
        tol(float): tolerance for singular values.
        n_components(int): number of components.
        kernel(str): kernel to be used.
        random_stat(int): random state.
    """

    def __init__(
        self,
        time_column=-1,
        missing_values=np.nan,
        enable_fillna=True,
        order=-1,
        base_imputer=SimpleImputer(),
        scaler=None,
        max_iter=10,
        tol=1e-3,
        n_components=None,
        kernel="linear",
        random_state=42,
    ):
        self.n_components = n_components
        self.kernel = kernel
        self.random_state = random_state

        super(KernelPCAImputer, self).__init__(
            time_column=time_column,
            missing_values=missing_values,
            enable_fillna=enable_fillna,
            order=order,
            base_imputer=base_imputer,
            scaler=scaler,
            decomposer=KernelPCA(
                n_components=n_components,
                kernel=kernel,
                random_state=random_state,
                fit_inverse_transform=True,  # necessary
            ),
            max_iter=max_iter,
            tol=tol,
        )


class TruncatedSVDImputer(DecompositionImputer):
    """
    Imputer using TruncatedSVD
    Parameters:
        time_column (int): time column.
        missing_values (obj): missing value to be imputed.
        enable_fillna (boolean): fill na after interpolation if any.
        order (int): look back order.
        base_imputer (obj): base imputer to be used.
        scaler(obj): data scaler object necessary for decomposition.
        max_iter(int): max iterations.
        tol(float): tolerance for singular values.
        n_components(int): number of components.
        algorithm(str): algorithm to be used.
    """

    def __init__(
        self,
        time_column=-1,
        missing_values=np.nan,
        enable_fillna=True,
        order=-1,
        base_imputer=SimpleImputer(),
        scaler=None,
        max_iter=10,
        tol=1e-3,
        n_components=None,
        algorithm="randomized",
    ):
        self.n_components = n_components
        self.algorithm = algorithm

        super(TruncatedSVDImputer, self).__init__(
            time_column=time_column,
            missing_values=missing_values,
            enable_fillna=enable_fillna,
            order=order,
            base_imputer=base_imputer,
            scaler=scaler,
            decomposer=TruncatedSVD(n_components=n_components, algorithm=algorithm),
            max_iter=max_iter,
            tol=tol,
        )


class NMFImputer(DecompositionImputer):
    """
    Imputer using NMF
    Parameters:
        time_column (int): time column.
        missing_values (obj): missing value to be imputed.
        enable_fillna (boolean): fill na after interpolation if any.
        order (int): look back order.
        base_imputer (obj): base imputer to be used.
        scaler(obj): data scaler object necessary for decomposition.
        max_iter(int): max iterations.
        tol(float): tolerance for singular values.
        n_components(int): number of components.
        l1_ratio(float): the regularization mixing parameter.
    """
    def __init__(
        self,
        time_column=-1,
        missing_values=np.nan,
        enable_fillna=True,
        order=-1,
        base_imputer=SimpleImputer(),
        scaler=None,
        max_iter=10,
        tol=1e-3,
        n_components=None,
        l1_ratio=0.2,
    ):
        self.n_components = n_components
        self.l1_ratio = l1_ratio

        super(NMFImputer, self).__init__(
            time_column=time_column,
            missing_values=missing_values,
            enable_fillna=enable_fillna,
            order=order,
            base_imputer=base_imputer,
            scaler=scaler,
            decomposer=NMF(n_components=n_components, l1_ratio=l1_ratio),
            max_iter=max_iter,
            tol=tol,
        )


class IncrementalPCAImputer(DecompositionImputer):
    """
    Imputer using IncrementalPCA
    Parameters:
        time_column (int): time column.
        missing_values (obj): missing value to be imputed.
        enable_fillna (boolean): fill na after interpolation if any.
        order (int): look back order.
        base_imputer (obj): base imputer to be used.
        scaler(obj): data scaler object necessary for decomposition.
        max_iter(int): max iterations.
        tol(float): tolerance for singular values.
        n_components(int): number of components.
        whiten(boolean): wheather to whiten or not.
        batch_size(int): batch size.
    """
    def __init__(
        self,
        time_column=-1,
        missing_values=np.nan,
        enable_fillna=True,
        order=-1,
        base_imputer=SimpleImputer(),
        scaler=None,
        max_iter=10,
        tol=1e-3,
        n_components=None,
        whiten=False,
        batch_size=None,
    ):
        self.n_components = n_components
        self.whiten = whiten
        self.batch_size = batch_size

        super(IncrementalPCAImputer, self).__init__(
            time_column=time_column,
            missing_values=missing_values,
            enable_fillna=enable_fillna,
            order=order,
            base_imputer=base_imputer,
            scaler=scaler,
            decomposer=IncrementalPCA(
                n_components=n_components, whiten=whiten, batch_size=batch_size
            ),
            max_iter=max_iter,
            tol=tol,
        )
