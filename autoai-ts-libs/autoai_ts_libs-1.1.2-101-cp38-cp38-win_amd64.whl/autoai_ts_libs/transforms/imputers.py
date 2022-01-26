# ************* Begin Copyright - Do not add comments here **************
#   Licensed Materials - Property of IBM
#
#   (C) Copyright IBM Corp. 2019, 2020, All Rights Reserved
#
# The source code for this program is not published or other-
# wise divested of its trade secrets, irrespective of what has
# been deposited with the U.S. Copyright Office.
# **************************** End Copyright ***************************

# Common Wrapper class for all the interpolators
from autoai_ts_libs.srom.imputers.predictive_imputer import PredictiveImputer
from autoai_ts_libs.srom.imputers.interpolators import PreMLImputer
from autoai_ts_libs.watfore.watfore_interpolator import WatForeInterpolator
from autoai_ts_libs.srom.imputers.decomposition_imputers import (
    PCAImputer,
    KernelPCAImputer,
    TruncatedSVDImputer,
    NMFImputer,
    IncrementalPCAImputer,
)
from autoai_ts_libs.srom.imputers.flatten_imputers import (
    FlattenIterativeImputer,
    FlattenKNNImputer,
)
from autoai_ts_libs.srom.imputers.interpolators import (
    PolynomialImputer,
    SplineImputer,
    CubicImputer,
    QuadraticImputer,
    AkimaImputer,
    LinearImputer,
    BaryCentricImputer,
    PreMLImputer,
)
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import KNNImputer
from autoai_ts_libs.srom.imputers.extended_iterative_imputer import ExtendedIterativeImputer
import numpy as np
from typing import List
import copy

# TODO: AT some  point we should wrap the class such that inidividual interpolator names don't show up
# class Autoai_TS_InterpolatorW:
#
#     def __init__(self, WatForeInterpolator):
#         self.__class__ = type(WatForeInterpolator.__class__.__name__,
#                               (self.__class__, WatForeInterpolator.__class__),
#                               {})
#         self.__class__.__name__ = 'Autoai_TS_InterpolatorW'
#         self.__dict__ = WatForeInterpolator.__dict__

# this must be in sync with prep_timeseries_jointopt IMPUTERS variable
IMPUTER_DISPLAY_NAMES = {
    'previous': 'Previous',
    'fill': 'Fill',
    'next': 'Next',
    'flatten_iterative': 'FlattenIterative',
    'cubic': 'Cubic',
    'linear': 'Linear',
    'kernel_pca': 'KernelPCA',
    'pca': 'PCA',
    'truncated_svd': 'TruncatedSVD',
    'incremental_pca': 'IncrementalPCA',
    'flatten_knn': 'FlattenKNN',
    'akima': 'Akima',
    'barycentric': 'Barycentric',
    'polynomial': 'Polynomial',
    'predictive': 'Predictive',
    'quadratic': 'Quadratic',
    'spline': 'Spline',
}

class AutoAITSImputer:
    @staticmethod
    def get_default_imputer_list(**parameters):
        """
        """

        fill_parameters=copy.deepcopy(parameters)
        if "imputer_fill_type" in parameters.keys():
            parameters.pop('imputer_fill_type')
        if "imputer_fill_value" in parameters.keys():
            parameters.pop('imputer_fill_value')
            
        
        watfore_imputers = [
            # linear(**parameters), ##Todo getting some error.
            previous(**parameters),
            fill(**fill_parameters),
            # cubic(**parameters), ##Todo getting some error.
            # nearest(**parameters), ##Todo getting some error.
            next(**parameters),
        ]

        for key in ["ts_ocol_loc", "default_value"]:
            if key in parameters:
                del parameters[key]

        srom_imputers = [
            pca(**parameters),
            kernel_pca(**parameters),
            truncated_svd(**parameters),
            incremental_pca(**parameters),
            flatten_iterative(**parameters),
            flatten_knn(**parameters),
            predictive(**parameters),
            polynomial(**parameters),
            spline(**parameters),
            cubic(**parameters),
            akima(**parameters),
            linear(**parameters),
            barycentric(**parameters),
            quadratic(**parameters),
        ]
        return watfore_imputers + srom_imputers

    @staticmethod
    def filtered_imputer_list(
        available_imputers: List, valid_imputers: List[str]
    ) -> List:
        """Filter the imputer list to pick only a subset

        Args:
            available_imputers (List): List of initialized imputers, i.e., from a call to 
                get_default_imputer_list
            valid_imputers (List[str]): List of strings which name the imputers to include

        Returns:
            List: List of selected initialized imputers
        """
        return [
            imp
            for imp in available_imputers
            if imp.__class__.__name__ in valid_imputers
        ]

    @staticmethod
    def get_display_name(imputer: object):
        return IMPUTER_DISPLAY_NAMES[imputer.__class__.__name__]

    @staticmethod
    def get_imputer_name(imputer: object):
        return f"{imputer.__class__.__name__}_imputer"

# class linear(WatForeInterpolator):
#     def __init__(
#         self,
#         append_tranform=False,
#         ts_icol_loc=-1,
#         ts_ocol_loc=-1,
#         missing_val_identifier=np.nan,
#         default_value=0.0,
#     ):
#         super().__init__(
#             interpolator_type="linear",
#             append_tranform=append_tranform,
#             ts_icol_loc=ts_icol_loc,
#             ts_ocol_loc=ts_ocol_loc,
#             missing_val_identifier=missing_val_identifier,
#             default_value=default_value,
#         )


class previous(WatForeInterpolator):
    def __init__(
        self,
        append_tranform=False,
        ts_icol_loc=-1,
        ts_ocol_loc=-1,
        missing_val_identifier=np.nan,
        default_value=0.0,
    ):
        super().__init__(
            interpolator_type="prev",
            append_tranform=append_tranform,
            ts_icol_loc=ts_icol_loc,
            ts_ocol_loc=ts_ocol_loc,
            missing_val_identifier=missing_val_identifier,
            default_value=default_value,
        )


class fill(WatForeInterpolator):
    def __init__(
        self,
        append_tranform=False,
        ts_icol_loc=-1,
        ts_ocol_loc=-1,
        missing_val_identifier=np.nan,
        default_value=0.0,
        imputer_fill_type="value",
        imputer_fill_value=0.0
    ):
        super().__init__(
            interpolator_type="fill",
            append_tranform=append_tranform,
            ts_icol_loc=ts_icol_loc,
            ts_ocol_loc=ts_ocol_loc,
            missing_val_identifier=missing_val_identifier,
            default_value=default_value,
            imputer_fill_type=imputer_fill_type,
            imputer_fill_value=imputer_fill_value
        )


# class cubic(WatForeInterpolator):
#     def __init__(
#         self,
#         append_tranform=False,
#         ts_icol_loc=-1,
#         ts_ocol_loc=-1,
#         missing_val_identifier=np.nan,
#         default_value=0.0,
#     ):
#         super().__init__(
#             interpolator_type="cubic",
#             append_tranform=append_tranform,
#             ts_icol_loc=ts_icol_loc,
#             ts_ocol_loc=ts_ocol_loc,
#             missing_val_identifier=missing_val_identifier,
#             default_value=default_value,
#         )


# class nearest(WatForeInterpolator):
#     def __init__(
#         self,
#         append_tranform=False,
#         ts_icol_loc=-1,
#         ts_ocol_loc=-1,
#         missing_val_identifier=np.nan,
#         default_value=0.0,
#     ):
#         super().__init__(
#             interpolator_type="nearest",
#             append_tranform=append_tranform,
#             ts_icol_loc=ts_icol_loc,
#             ts_ocol_loc=ts_ocol_loc,
#             missing_val_identifier=missing_val_identifier,
#             default_value=default_value,
#         )


class next(WatForeInterpolator):
    def __init__(
        self,
        append_tranform=False,
        ts_icol_loc=-1,
        ts_ocol_loc=-1,
        missing_val_identifier=np.nan,
        default_value=0.0,
    ):
        super().__init__(
            interpolator_type="next",
            append_tranform=append_tranform,
            ts_icol_loc=ts_icol_loc,
            ts_ocol_loc=ts_ocol_loc,
            missing_val_identifier=missing_val_identifier,
            default_value=default_value,
        )


class pca(PCAImputer):
    def __init__(
        self,
        ts_icol_loc=-1,
        missing_val_identifier=np.nan,
        enable_fillna=True,
        order=5,
        base_imputer=PreMLImputer(),
        scaler=None,
        max_iter=10,
        tol=1e-3,
        n_components=3,
        whiten=False,
        svd_solver="auto",
        random_state=42,
    ):
        super().__init__(
            time_column=ts_icol_loc,
            missing_values=missing_val_identifier,
            enable_fillna=enable_fillna,
            order=order,
            base_imputer=base_imputer,
            scaler=scaler,
            max_iter=max_iter,
            tol=tol,
            n_components=n_components,
            whiten=whiten,
            svd_solver=svd_solver,
            random_state=random_state,
        )
        self.ts_icol_loc = ts_icol_loc
        self.missing_val_identifier = missing_val_identifier


class kernel_pca(KernelPCAImputer):
    def __init__(
        self,
        ts_icol_loc=-1,
        missing_val_identifier=np.nan,
        enable_fillna=True,
        order=5,
        base_imputer=PreMLImputer(),
        scaler=None,
        max_iter=10,
        tol=1e-3,
        n_components=3,
        kernel="linear",
        random_state=42,
    ):
        super().__init__(
            time_column=ts_icol_loc,
            missing_values=missing_val_identifier,
            enable_fillna=enable_fillna,
            order=order,
            base_imputer=base_imputer,
            scaler=scaler,
            max_iter=max_iter,
            tol=tol,
            n_components=n_components,
            kernel=kernel,
            random_state=random_state,
        )
        self.ts_icol_loc = ts_icol_loc
        self.missing_val_identifier = missing_val_identifier


class truncated_svd(TruncatedSVDImputer):
    def __init__(
        self,
        ts_icol_loc=-1,
        missing_val_identifier=np.nan,
        enable_fillna=True,
        order=5,
        base_imputer=PreMLImputer(),
        scaler=None,
        max_iter=10,
        tol=1e-3,
        n_components=3,
        algorithm="randomized",
    ):
        super().__init__(
            time_column=ts_icol_loc,
            missing_values=missing_val_identifier,
            enable_fillna=enable_fillna,
            order=order,
            base_imputer=base_imputer,
            scaler=scaler,
            max_iter=max_iter,
            tol=tol,
            n_components=n_components,
            algorithm=algorithm,
        )
        self.ts_icol_loc = ts_icol_loc
        self.missing_val_identifier = missing_val_identifier


class incremental_pca(IncrementalPCAImputer):
    def __init__(
        self,
        ts_icol_loc=-1,
        missing_val_identifier=np.nan,
        enable_fillna=True,
        order=5,
        base_imputer=PreMLImputer(),
        scaler=None,
        max_iter=10,
        tol=1e-3,
        n_components=3,
        whiten=False,
        batch_size=None,
    ):
        super().__init__(
            time_column=ts_icol_loc,
            missing_values=missing_val_identifier,
            enable_fillna=enable_fillna,
            order=order,
            base_imputer=base_imputer,
            scaler=scaler,
            max_iter=max_iter,
            tol=tol,
            n_components=n_components,
            whiten=whiten,
            batch_size=batch_size,
        )
        self.ts_icol_loc = ts_icol_loc
        self.missing_val_identifier = missing_val_identifier


class flatten_iterative(FlattenIterativeImputer):
    def __init__(
        self,
        ts_icol_loc=-1,
        missing_val_identifier=np.nan,
        enable_fillna=True,
        order=5,
        base_imputer=PreMLImputer(),
        model_imputer=ExtendedIterativeImputer(),
    ):
        super().__init__(
            time_column=ts_icol_loc,
            missing_values=missing_val_identifier,
            enable_fillna=enable_fillna,
            order=order,
            base_imputer=base_imputer,
            model_imputer=model_imputer,
        )
        self.ts_icol_loc = ts_icol_loc
        self.missing_val_identifier = missing_val_identifier


class flatten_knn(FlattenKNNImputer):
    def __init__(
        self,
        ts_icol_loc=-1,
        missing_val_identifier=np.nan,
        enable_fillna=True,
        order=5,
        base_imputer=PreMLImputer(),
        model_imputer=KNNImputer(),
    ):
        super().__init__(
            time_column=ts_icol_loc,
            missing_values=missing_val_identifier,
            enable_fillna=enable_fillna,
            order=order,
            base_imputer=base_imputer,
            model_imputer=model_imputer,
        )
        self.ts_icol_loc = ts_icol_loc
        self.missing_val_identifier = missing_val_identifier


class predictive(PredictiveImputer):
    def __init__(
        self,
        ts_icol_loc=-1,
        missing_val_identifier=np.nan,
        enable_fillna=True,
        order=5,
        max_iter=10,
        tol=1e-3,
        base_imputer=PreMLImputer(),
        base_model=RandomForestRegressor(n_estimators=10, n_jobs=-1, random_state=33),
    ):
        super().__init__(
            time_column=ts_icol_loc,
            missing_values=missing_val_identifier,
            enable_fillna=enable_fillna,
            order=order,
            max_iter=max_iter,
            tol=tol,
            base_imputer=base_imputer,
            base_model=base_model,
        )
        self.ts_icol_loc = ts_icol_loc
        self.missing_val_identifier = missing_val_identifier


class polynomial(PolynomialImputer):
    def __init__(
        self,
        ts_icol_loc=-1,
        missing_val_identifier=np.nan,
        enable_fillna=True,
        order=5,
    ):
        super().__init__(
            time_column=ts_icol_loc,
            missing_values=missing_val_identifier,
            enable_fillna=enable_fillna,
            order=order,
        )
        self.ts_icol_loc = ts_icol_loc
        self.missing_val_identifier = missing_val_identifier


class spline(SplineImputer):
    def __init__(
        self,
        ts_icol_loc=-1,
        missing_val_identifier=np.nan,
        enable_fillna=True,
        order=3,
    ):
        super().__init__(
            time_column=ts_icol_loc,
            missing_values=missing_val_identifier,
            enable_fillna=enable_fillna,
            order=order,
        )
        self.ts_icol_loc = ts_icol_loc
        self.missing_val_identifier = missing_val_identifier


class cubic(CubicImputer):
    def __init__(
        self, ts_icol_loc=-1, missing_val_identifier=np.nan, enable_fillna=True
    ):
        super().__init__(
            time_column=ts_icol_loc,
            missing_values=missing_val_identifier,
            enable_fillna=enable_fillna,
        )
        self.ts_icol_loc = ts_icol_loc
        self.missing_val_identifier = missing_val_identifier


class quadratic(QuadraticImputer):
    def __init__(
        self, ts_icol_loc=-1, missing_val_identifier=np.nan, enable_fillna=True
    ):
        super().__init__(
            time_column=ts_icol_loc,
            missing_values=missing_val_identifier,
            enable_fillna=enable_fillna,
        )
        self.ts_icol_loc = ts_icol_loc
        self.missing_val_identifier = missing_val_identifier


class akima(AkimaImputer):
    def __init__(
        self, ts_icol_loc=-1, missing_val_identifier=np.nan, enable_fillna=True
    ):
        super().__init__(
            time_column=ts_icol_loc,
            missing_values=missing_val_identifier,
            enable_fillna=enable_fillna,
        )
        self.ts_icol_loc = ts_icol_loc
        self.missing_val_identifier = missing_val_identifier


class linear(LinearImputer):
    def __init__(
        self, ts_icol_loc=-1, missing_val_identifier=np.nan, enable_fillna=True
    ):
        super().__init__(
            time_column=ts_icol_loc,
            missing_values=missing_val_identifier,
            enable_fillna=enable_fillna,
        )
        self.ts_icol_loc = ts_icol_loc
        self.missing_val_identifier = missing_val_identifier


class barycentric(BaryCentricImputer):
    def __init__(
        self, ts_icol_loc=-1, missing_val_identifier=np.nan, enable_fillna=True
    ):
        super().__init__(
            time_column=ts_icol_loc,
            missing_values=missing_val_identifier,
            enable_fillna=enable_fillna,
        )
        self.ts_icol_loc = ts_icol_loc
        self.missing_val_identifier = missing_val_identifier

