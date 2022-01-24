"""A data source for the M5 dataset."""

import copy
import os.path as osp
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset

from forecast.data import FUTURE_DEP_KEY, FUTURE_IND_KEY, PAST_DEP_KEY, PAST_IND_KEY
from forecast.data.batch_transforms import (
    BatchNormalizer,
    BatchTransform,
    GenericBatchTransform,
    NormalizationMode,
    Normalizer,
)
from forecast.data.dataset import TimeSeriesDataset
import forecast.data.date_featurizers as dfeat
from forecast.data.sources.data_source import AbstractDataSource, DataSourceConfig, EncodingSpec
import forecast.data.transforms as tfs
from forecast.data.utils import ragged_split_by_count, to_float32


class M5DataSource(AbstractDataSource):
    """M5 Competition Data."""

    DEFAULT_FORECAST_HORIZON = 28
    NUM_PRODUCTS = 3049
    NUM_STORES = 10
    TRAIN_START_IND = 1
    TRAIN_END_IND = 1913
    VAL_START_IND = 1914
    VAL_END_IND = 1941

    def __init__(
        self,
        forecast_horizon: Optional[int] = None,
        val_split: Optional[int] = None,
        date_featurizers: Optional[Sequence[dfeat.DateFeaturizer]] = None,
        eager: bool = False,
    ):
        """Instantiates an M5DataSource.

        Parameters
        ----------
        forecast_horizon: int, optional
            The number of samples to be forecasted, defaults to `DEFAULT_FORECAST_HORIZON`
        val_split: int, optional
            Unused.
        date_featurizers: Sequence[DateFeaturizer], optional
            A list of featurizers to apply to the date column, defaults to None which signifies: HourOfDay, DayOfWeek,
            DayOfMonth, DayOfYear, and Holiday.
        eager: bool, optional
            If True, loads the data upon object creation rather than lazily. Defaults to False.

        """
        super().__init__()

        default_val_len = M5DataSource.VAL_END_IND - M5DataSource.VAL_START_IND + 1
        self._val_len = val_split if val_split is not None else default_val_len

        # set our forecast horizon
        if forecast_horizon:
            if forecast_horizon > self._val_len:
                raise ValueError("Forecast horizon cannot exceed validation set length.")
            self._forecast_horizon = forecast_horizon
        else:
            self._forecast_horizon = M5DataSource.DEFAULT_FORECAST_HORIZON

        # set our featurizers (performed across the entire dataset)
        if date_featurizers is None:
            self._featurizers = [
                dfeat.DayOfWeekFeaturizer(),
                dfeat.DayOfMonthFeaturizer(),
                dfeat.MonthOfYearFeaturizer(),
            ]
        elif not isinstance(date_featurizers, Sequence):
            raise TypeError(f"`date_featurizers` should be of type Sequence, is of type {type(date_featurizers)}")
        else:
            self._featurizers = list(copy.deepcopy(date_featurizers))

        self._data: Optional[pd.DataFrame] = None
        if eager:
            self._load_data()

    def get_config(self) -> DataSourceConfig:
        """Provides the configuration describing the data source.

        Returns
        -------
        DataSourceConfig
            The number of input channels and the desired prediction horizon

        """
        # column order: sales,sell_price,item_id,store_id,holiday,snap,[date_features]
        nondate_feature_count = 5
        encodings = [
            EncodingSpec(feature_index=1, num_vals=M5DataSource.NUM_PRODUCTS),
            EncodingSpec(feature_index=2, num_vals=M5DataSource.NUM_STORES),
        ]
        if self._featurizers:
            encodings += [
                EncodingSpec(feature_index=i + nondate_feature_count, num_vals=f.num_values)
                for i, f in enumerate(self._featurizers)
                if f.num_values > 2
            ]

        return DataSourceConfig(
            feature_channels=nondate_feature_count + len(self._featurizers),
            forecast_channels=1,  # sales
            encodings=encodings,
        )

    def _build_dataset(
        self,
        data: List[np.ndarray],
        window_size: int,
        one_hot: bool = False,
        drop_first: Optional[bool] = None,
        sales_scaling: Optional[np.ndarray] = None,
        price_scaling: Optional[np.ndarray] = None,
        *,
        include_untransformed: bool = True,
    ) -> TimeSeriesDataset:
        """Builds a `TimeSeriesDataset` from a given `np.ndarray` of data.

        Parameters:
        -----------
        data: np.ndarray
            The electricity data
        window_size: int
            The number of samples required to make a forecast
        one_hot: bool, optional
            Whether embeddable variables should be converted to a one-hot encoding, defaults to False
        drop_first: bool or None, optional
            If `one_hot` is True, determines whether index=0 --> the 0 vector or [1, 0, ...]. Only valid if `one_hot`
            is True. Defaults to None.

        """
        if drop_first is not None and not one_hot:
            raise ValueError("`drop_first` supplied but is only applicable if `one_hot` is True")

        targets = [0]

        tf_list: List[tfs.AbstractTransform] = []

        if sales_scaling is not None:
            if sales_scaling.ndim == 2:
                tf_list.append(
                    tfs.FeatureNormalizer(
                        [PAST_DEP_KEY, FUTURE_DEP_KEY],
                        0,
                        {"offset": sales_scaling[:, 0], "scale": sales_scaling[:, 1]},
                        inplace=True,
                    )
                )
            elif sales_scaling.ndim == 3:
                tf_list.append(
                    tfs.SeriesFeatureNormalizer(
                        [PAST_DEP_KEY, FUTURE_DEP_KEY],
                        lambda x: int(_create_series_id(x[1], x[2]).item()),
                        0,
                        {"offset": sales_scaling[:, :, 0], "scale": sales_scaling[:, :, 1]},
                        inplace=True,
                    )
                )
            else:
                raise ValueError(
                    "sales scaling array must be of dimension 2 (uniform) or 3 (per series), "
                    f"is of shape {sales_scaling.shape}"
                )
        if price_scaling is not None:
            if price_scaling.ndim == 2:
                tf_list.append(
                    tfs.FeatureNormalizer(
                        [PAST_IND_KEY, FUTURE_IND_KEY],
                        0,
                        {"offset": price_scaling[:, 0], "scale": price_scaling[:, 1]},
                        inplace=True,
                    )
                )
            elif price_scaling.ndim == 3:
                tf_list.append(
                    tfs.SeriesFeatureNormalizer(
                        [PAST_IND_KEY, FUTURE_IND_KEY],
                        lambda x: int(_create_series_id(x[1], x[2]).item()),
                        0,
                        {"offset": price_scaling[:, :, 0], "scale": price_scaling[:, :, 1]},
                        inplace=True,
                    )
                )
            else:
                raise ValueError(
                    "price scaling array must be of dimension 2 (uniform) or 3 (per series), "
                    f"is of shape {price_scaling.shape}"
                )

        if one_hot:
            drop = True if drop_first else False
            config = self.get_config()

            assert len(config.encodings) >= 2  # there should always at least be product/store encodings
            ohes: List[tfs.AbstractTransform] = [
                tfs.OneHotEncode(
                    [e.feature_index for e in config.encodings],
                    [e.num_vals for e in config.encodings],
                    drop_first=drop,
                ),
                tfs.OneHotEncode(
                    [e.feature_index for e in config.encodings],
                    [e.num_vals for e in config.encodings],
                    drop_first=drop,
                    key=FUTURE_IND_KEY,
                ),
            ]
            tf_list = ohes + tf_list
        transform = tfs.ComposedTransform(tf_list) if tf_list else None
        return TimeSeriesDataset(
            data,
            window_size,
            self._forecast_horizon,
            targets,
            transform=transform,
            include_untransformed=include_untransformed,
        )

    def get_dataset(
        self,
        window_size: int,
        one_hot: bool = False,
        drop_first: Optional[bool] = None,
    ) -> Tuple[Dataset, Dataset]:
        """Creates training and val datasets from the M5 data.

        Parameters:
        -----------
        window_size: int
            The number of samples required to make a forecast
        one_hot: bool, optional
            Whether embeddable variables should be converted to a one-hot encoding, defaults to False
        drop_first: bool or None, optional
            If `one_hot` is True, determines whether index=0 --> the 0 vector or [1, 0, ...]. Only valid if `one_hot`
            is True. Defaults to None.

        """
        if self._data is None:
            self._load_data()

        # TODO: only derive constants from train set not train/val
        # if normalization_group == "series":
        #     # axes are (group, feature, offset/scalar)
        #     if normalization_method == "standard":
        #         sales_factors = self._data["sales"].groupby(level=0).agg(["mean", "std"]).to_numpy()[:, None, :]
        #         price_factors = self._data["sell_price"].groupby(level=0).agg(["mean", "std"]).to_numpy()[:, None, :]
        #
        #         # if price is uniform, set std to 1 to eliminate error (all vals will be 0 anyways)
        #         price_factors[price_factors[:, 0, 1] == 0, 0, 1] = 1
        #     elif normalization_method == "minmax":
        #         sales_factors = self._data["sales"].groupby(level=0).agg(["min", "max"]).to_numpy()
        #         sales_factors[:, 1] = sales_factors[:, 1] - sales_factors[:, 0]
        #         sales_factors = sales_factors[:, None, :]
        #
        #         price_factors = self._data["sell_price"].groupby(level=0).agg(["min", "max"]).to_numpy()
        #         price_factors[:, 1] = price_factors[:, 1] - price_factors[:, 0]
        #         price_factors = price_factors[:, None, :]
        #
        #         # if price is uniform, set range to 1 and mean subtracted value to 0.5
        #         price_factors[price_factors[:, 0, 1] == 0, 0, :] += np.array([-0.5, 1])
        #     elif normalization_method == "none":
        #         sales_factors = price_factors = None
        #     else:
        #         raise ValueError(f"Unknown `normalization_method` value {normalization_method}")
        # elif normalization_group == "all":
        #     # axes are (feature, offset/scalar)
        #     if normalization_method == "standard":
        #         sales_factors = self._data["sales"].apply(["mean", "std"])[None, :]
        #         price_factors = self._data["sell_price"].apply(["mean", "std"])[None, :]
        #     elif normalization_method == "minmax":
        #         sales_factors = self._data["sales"].apply(["min", "max"]).to_numpy()[None, :]
        #         sales_factors[:, 1] = sales_factors[:, 1] - sales_factors[:, 0]
        #
        #         price_factors = self._data["sell_price"].apply(["min", "max"]).to_numpy()[None, :]
        #         price_factors[:, 1] = price_factors[:, 1] - price_factors[:, 0]
        #     elif normalization_method == "none":
        #         sales_factors = price_factors = None
        #     else:
        #         raise ValueError(f"Unknown `normalization_method` value {normalization_method}")
        # else:
        #     raise ValueError(f"Unknown `normalization_group` value {normalization_group}")
        sales_factors = price_factors = None

        # split the dataset by an arbitrary count
        data_train, data_val = ragged_split_by_count(self._data, self._val_len, window_size)

        ds_train = self._build_dataset(
            to_float32(data_train), window_size, one_hot, drop_first, sales_factors, price_factors
        )
        ds_val = self._build_dataset(
            to_float32(data_val), window_size, one_hot, drop_first, sales_factors, price_factors
        )
        return ds_train, ds_val

    def _load_data(self) -> None:
        """Loads M5 data.

        Assumes the data has previously been downloaded from https://www.kaggle.com/c/m5-forecasting-accuracy/data.
        """
        data_dir = osp.dirname(osp.realpath(__file__))
        csv_path = osp.join(data_dir, "processed_m5.csv")
        item_path = osp.join(data_dir, "item_mapping.csv")
        store_path = osp.join(data_dir, "store_mapping.csv")
        if not osp.exists(csv_path):
            calendar_path = osp.join(data_dir, "calendar.csv")
            prices_path = osp.join(data_dir, "sell_prices.csv")
            sales_train_eval_path = osp.join(data_dir, "sales_train_evaluation.csv")
            if not all(osp.exists(p) for p in [calendar_path, prices_path, sales_train_eval_path]):
                raise FileNotFoundError(
                    "All of calendar.csv, prices.csv, and sales_train_validation.csv must be present. "
                    "See https://www.kaggle.com/c/m5-forecasting-accuracy/data for download instructions."
                )
            # process the data
            # load the calendar data
            calendar = pd.read_csv(calendar_path)
            calendar["holiday"] = (~calendar["event_name_1"].isna()).astype("int8")
            calendar = calendar.astype({"snap_CA": "int8", "snap_TX": "int8", "snap_WI": "int8"})
            calendar.drop(
                [
                    "weekday",
                    "wday",
                    "month",
                    "year",
                    "event_name_1",
                    "event_type_1",
                    "event_name_2",
                    "event_type_2",
                ],
                axis=1,
                inplace=True,
            )
            calendar["date"] = pd.to_datetime(calendar["date"])

            # load the sales data
            sales_train_eval = pd.read_csv(sales_train_eval_path)
            melted_sales_data = sales_train_eval.melt(
                id_vars=["item_id", "dept_id", "cat_id", "store_id", "state_id"],
                value_vars=[f"d_{i}" for i in range(M5DataSource.TRAIN_START_IND, M5DataSource.VAL_END_IND + 1)],
                var_name="d",
                value_name="sales",
            )
            del sales_train_eval

            # merge with the calendar data
            melted_sales_data.drop(["dept_id", "cat_id"], axis=1, inplace=True)
            sales_and_dates = melted_sales_data.merge(calendar, on="d", how="left")
            del calendar, melted_sales_data

            # fold the snap columns
            sales_and_dates["snap"] = (
                ((sales_and_dates["state_id"] == "CA") & sales_and_dates["snap_CA"])
                | ((sales_and_dates["state_id"] == "TX") & sales_and_dates["snap_TX"])
                | ((sales_and_dates["state_id"] == "WI") & sales_and_dates["snap_WI"])
            ).astype("int8")
            sales_and_dates.drop(["d", "snap_CA", "snap_TX", "snap_WI", "state_id"], axis=1, inplace=True)

            # load the price data
            prices = pd.read_csv(prices_path)
            data = sales_and_dates.merge(prices, on=["item_id", "store_id", "wm_yr_wk"], how="left")
            del sales_and_dates, prices

            data.drop(["wm_yr_wk"], axis=1, inplace=True)
            data = data.astype({"item_id": "category", "store_id": "category"})

            def create_categorical_mapping(df: pd.DataFrame, col: str) -> pd.DataFrame:
                categories = df[col].cat.categories.to_frame().reset_index().drop("index", axis=1)
                categories.rename({0: col}, axis=1, inplace=True)
                categories["code"] = categories[col].apply(lambda c: df[col].cat.categories.get_loc(c))
                return categories

            store_categories = create_categorical_mapping(data, "store_id")
            item_categories = create_categorical_mapping(data, "item_id")
            store_categories.to_csv(store_path, index=False)
            item_categories.to_csv(item_path, index=False)

            # convert the categorical variables to their integer codes [0, N-1]
            # categories are sorted alphabetically
            data["store_id"] = data["store_id"].cat.codes
            data["item_id"] = data["item_id"].cat.codes

            # rearrange the columns to the desired order (sales first)
            data = data[["sales", "sell_price", "item_id", "store_id", "holiday", "snap", "date"]]
            data.sort_values(["store_id", "item_id", "date"], inplace=True)

            data.to_csv(csv_path, index=False)
            df = data
        else:
            df = pd.read_csv(csv_path)

        # cast to appropriate datatypes
        df = df.astype(
            {
                "snap": "int8",
                "holiday": "int8",
                "item_id": "int16",
                "store_id": "int8",
                "sell_price": "float32",
                "sales": "float32",
            }
        )
        df["date"] = pd.to_datetime(df["date"])
        df["store_item_id"] = _create_series_id(df["item_id"], df["store_id"])

        # all NA sales prices precede the first sale of the item
        df = df[~df["sell_price"].isna()].reset_index(drop=True)

        # validate
        assert df["store_id"].nunique() == M5DataSource.NUM_STORES
        assert df["item_id"].nunique() == M5DataSource.NUM_PRODUCTS
        assert df["date"].nunique() == M5DataSource.VAL_END_IND

        df = df.set_index(["store_item_id", "date"])
        if self._featurizers:
            dts = df.index.get_level_values(-1)
            for featurizer in self._featurizers:
                df[featurizer.name] = featurizer(dts)

        # store the df
        self._data = df

    @property
    def batch_transform(self) -> BatchTransform:
        if self._data is None:
            raise ValueError("Cannot create batch_transform prior to loading data")
        normalization_group = "series"
        normalization_method = "minmax"
        if normalization_group == "series":
            # axes are (offset/scalar, group, feature, 1)
            if normalization_method == "standard":
                # num series, 2
                sales_factors = self._data["sales"].groupby(level=0).agg(["mean", "std"]).to_numpy()
                price_factors = self._data["sell_price"].groupby(level=0).agg(["mean", "std"]).to_numpy()

                # 2, num_series, # features, 1
                sales_factors = sales_factors.T[:, :, None, None]
                price_factors = price_factors.T[:, :, None, None]

                # if price is uniform, set std to 1 to eliminate error (all vals will be 0 anyways)
                price_factors[1, price_factors[1, :, 0, 0] == 0, 0, 0] = 1
            elif normalization_method == "minmax":
                # num series, 2
                sales_factors = self._data["sales"].groupby(level=0).agg(["min", "max"]).to_numpy()
                price_factors = self._data["sell_price"].groupby(level=0).agg(["min", "max"]).to_numpy()

                # compute range
                sales_factors[:, 1] = sales_factors[:, 1] - sales_factors[:, 0]
                price_factors[:, 1] = price_factors[:, 1] - price_factors[:, 0]

                # 2, num_series, # features, 1
                sales_factors = sales_factors.T[:, :, None, None]
                price_factors = price_factors.T[:, :, None, None]

                # if price is uniform, set range to 1 and mean subtracted value to 0.5
                price_factors[:, price_factors[1, :, 0, 0] == 0, 0, 0] += np.array([-0.5, 1])[:, None]
            elif normalization_method == "none":
                sales_factors = price_factors = None
            else:
                raise ValueError(f"Unknown `normalization_method` value {normalization_method}")
        elif normalization_group == "all":
            # axes are (offset/scalar, feature)
            if normalization_method == "standard":
                sales_factors = self._data["sales"].apply(["mean", "std"])[:, None]
                price_factors = self._data["sell_price"].apply(["mean", "std"])[:, None]
            elif normalization_method == "minmax":
                sales_factors = self._data["sales"].apply(["min", "max"]).to_numpy()[:, None]
                sales_factors[1, :] = sales_factors[1, :] - sales_factors[0, :]

                price_factors = self._data["sell_price"].apply(["min", "max"]).to_numpy()[:, None]
                price_factors[1, :] = price_factors[1, :] - price_factors[0, :]
            elif normalization_method == "none":
                sales_factors = price_factors = None
            else:
                raise ValueError(f"Unknown `normalization_method` value {normalization_method}")
        else:
            raise ValueError(f"Unknown `normalization_group` value {normalization_group}")

        st = torch.Tensor(sales_factors)
        pt = torch.Tensor(price_factors)
        # return M5BatchTransform(st, pt)

        mode = NormalizationMode.PER_SERIES
        st = st.squeeze(-1)
        pt = pt.squeeze(-1)
        return GenericBatchTransform(
            normalizer=BatchNormalizer(
                past_regressor=Normalizer(0, pt[0], pt[1], mode) if pt is not None else None,
                past_regressand=Normalizer(0, st[0], st[1], mode) if st is not None else None,
                future_regressor=Normalizer(0, pt[0], pt[1], mode) if pt is not None else None,
                future_regressand=Normalizer(0, st[0], st[1], mode) if st is not None else None,
            ),
            series_indexer=lambda t: _create_series_id(t[:, 1, 0], t[:, 2, 0]),
        )


def _create_series_id(item_id, store_id):
    return item_id + store_id * M5DataSource.NUM_PRODUCTS


class M5BatchTransform(BatchTransform):
    def __init__(self, sales_normalizer: Optional[torch.Tensor], price_normalizer: Optional[torch.Tensor]):
        self._sales_norm = sales_normalizer
        self._price_norm = price_normalizer

    def do(self, batch: Mapping[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
        if self._sales_norm is not None or self._price_norm is not None:
            inds = _create_series_id(batch[PAST_IND_KEY][:, 1, 0], batch[PAST_IND_KEY][:, 2, 0]).long().squeeze()
            if self._sales_norm is not None:
                for k in [PAST_DEP_KEY, FUTURE_DEP_KEY]:
                    if k in batch:
                        batch[k][:, [0], :] -= self._sales_norm[0, inds, :, :]
                        batch[k][:, [0], :] /= self._sales_norm[1, inds, :, :]
            if self._price_norm is not None:
                for k in [PAST_IND_KEY, FUTURE_IND_KEY]:
                    if k in batch:
                        batch[k][:, [0], :] -= self._price_norm[0, inds, :, :]
                        batch[k][:, [0], :] /= self._price_norm[1, inds, :, :]
        return dict(batch)

    def undo_y(self, y: torch.Tensor, batch: Mapping[str, torch.Tensor]) -> torch.Tensor:
        if self._sales_norm is not None:
            inds = _create_series_id(batch[PAST_IND_KEY][:, 1, 0], batch[PAST_IND_KEY][:, 2, 0]).long().squeeze()
            y *= self._sales_norm[1, inds, :, :]
            y += self._sales_norm[0, inds, :, :]
        return y
