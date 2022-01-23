import json
import os
import pickle

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import streamlit as st

from mlfoundry_ui.webapp.dashboard_constants import *


class FeatureView:
    def __init__(self, dataclass):
        self.mlfoundry_data = dataclass

    def get_schema_shap(self, run_id):
        """
        Return the shap and schema corresponding to each dataslice in a dictionary
        """
        dir_path = self.mlfoundry_data.get_artifact(run_id, STATS_FILE_NAME)
        model_type = self.mlfoundry_data.get_model_type(run_id)
        if dir_path is None:
            st.warning(f"Feature Importance doesn't exists for run {run_id}")
            return None

        dataslice_schemas = {}
        dataslice_shap = {}
        for file_name in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file_name)
            for data_slice_name in DATA_SLICES:
                if data_slice_name in file_name and SCHEMA_FILE_NAME in file_name:
                    with open(file_path, "rb") as f:
                        schema = json.load(f)
                    dataslice_schemas[data_slice_name] = schema

                elif SHAP_VALUE_FILE_NAME in file_name and data_slice_name in file_name:
                    with open(file_path, "rb") as f:
                        shap_values = pickle.load(f)

                    # shap_values is a list of array, the number of arrays is equal to number of classes, in case of regression,
                    # there is only one array.
                    if model_type == REGRESSION_MODEL_TYPE:
                        shap_values = np.array(shap_values)
                        # The column in the array correspond to each feature and rows are samples. So we take mean across the rows
                        shaps = np.abs(shap_values).mean(0)
                        df = pd.DataFrame(np.reshape(shaps, (-1, 1)), columns=[0])
                        # This df will have 0 as column as it is regression and each row corresponds to a feature
                        dataslice_shap[data_slice_name] = df
                    else:
                        # shap_values is a list of array, the number of arrays is equal to number of classes
                        shaps = []
                        num_class = len(shap_values)
                        # The column in the array correspond to each feature and rows are samples. So we take mean across the rows
                        for ind in range(num_class):
                            global_shap_values = np.abs(shap_values[ind]).mean(0)
                            shaps.append(global_shap_values)
                        shaps = np.array(shaps)
                        df = pd.DataFrame(
                            np.reshape(shaps, (-1, shaps.shape[0])),
                            columns=list(range(num_class)),
                        )
                        # This df will have 0,1,2.. as column according to the number of classes and each row corresponds to a feature
                        dataslice_shap[data_slice_name] = df

        return dir_path, dataslice_schemas, dataslice_shap

    # @st.experimental_memo
    def shap_computation(self, dataslice_schemas, dataslice_shap):
        """
        Shap computation given the dataslice_schemas and dataslice_shap
        """
        cols = list(st.columns(2))
        if len(dataslice_shap) > 2:
            cols += list(st.columns(2))

        for i, (data_slice_name, shap_df) in enumerate(dataslice_shap.items()):
            if data_slice_name not in dataslice_schemas.keys():
                continue
            # for each dataslice getting thre shap corresponding to the dataslice
            shap_df["Features"] = dataslice_schemas[data_slice_name][
                "feature_column_names"
            ]
            shap_df = shap_df.sort_values(shap_df.columns[0])
            with cols[i]:
                st.subheader(f"Feature Importance - {data_slice_name} data")
                num_class = len(dataslice_schemas[data_slice_name])
                feature_cols = list(shap_df.columns)
                feature_cols.remove("Features")
                fig = px.bar(shap_df, y="Features", x=feature_cols, orientation="h")
                fig.update_layout(
                    xaxis_title="mean(|SHAP value|)(average impact on model output magnitude)"
                )
                st.write(fig)

    def actual_vs_preds_classification(self, dir_path, dataslice_schemas):
        """
        unique counts file example:
        {'preds': (array([0, 1]), array([1574,   93])),
        'actuals': (array([0, 1]), array([1443,  224])),
        'state_AZ': (array([0, 1]), array([1642,   25]))
        }
        Each feature contains two array, first array conrresponds to unique values in the feature,
        second array correspond to counts corresponding to the unique values
        """
        data = []
        for data_slice_name in dataslice_schemas.keys():
            for file_name in os.listdir(dir_path):
                if (
                    data_slice_name not in file_name
                    or UNIQUE_COUNTS_FILE_NAME not in file_name
                ):
                    continue
                with open(os.path.join(dir_path, file_name), "rb") as f:
                    unique_counts = pickle.load(f)
                # getting the prediction and actual column name
                preds_col = dataslice_schemas[data_slice_name][
                    "prediction_column_name"
                ]  # getting the prediction and actual column name
                actual_col = dataslice_schemas[data_slice_name]["actual_column_name"]
                # getting the classes available in actual column
                classes = unique_counts[actual_col][0]
                ## For each dataslice finding the counts corresponding to classes
                for i in range(len(unique_counts[actual_col][1])):
                    data.append(
                        [
                            f"Class {unique_counts[actual_col][0][i]}",  # class number,
                            unique_counts[actual_col][1][
                                i
                            ],  # count corresponding to the class
                            "Truth Label",
                            data_slice_name,
                        ]
                    )
                for i in range(len(unique_counts[preds_col][1])):
                    data.append(
                        [
                            f"Class {unique_counts[preds_col][0][i]}",  # class number,
                            unique_counts[preds_col][1][
                                i
                            ],  # count corresponding to the class
                            "Predictions",
                            data_slice_name,
                        ]
                    )
        if len(data) != 0:
            pred_actual_df = pd.DataFrame(
                data, columns=["class", "count", "actual_preds", "data_slice"]
            )
            fig = px.bar(
                pred_actual_df,
                x="actual_preds",
                y="count",
                color="class",
                barmode="group",
                facet_row="data_slice",
            )
            fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
            fig.update_annotations(font=dict(size=20))
            fig.update_layout(showlegend=True, xaxis_title="")
            st.subheader("Predictions and Truth Label distribution")
            st.write(fig)

    def whylogs_histogram(self, histogram):
        """
        Preprocesses the histogram data obtained from whylogs
        """
        values = []
        for i in range(len(histogram["bin_edges"]) - 1):
            value = (histogram["bin_edges"][i + 1] + histogram["bin_edges"][i]) / 2
            values += [value] * histogram["counts"][i]
        return values

    def actual_vs_preds_regression(self, dir_path, dataslice_schemas):

        for data_slice_name in dataslice_schemas.keys():
            for file_name in os.listdir(dir_path):
                if (
                    data_slice_name not in file_name
                    or UNIQUE_COUNTS_FILE_NAME not in file_name
                ):
                    continue
                with open(os.path.join(dir_path, file_name), "rb") as f:
                    unique_counts = pickle.load(f)
                preds_col = dataslice_schemas[data_slice_name][
                    "prediction_column_name"
                ]  # getting the prediction and actual column name
                actual_col = dataslice_schemas[data_slice_name]["actual_column_name"]

                actual_histogram = unique_counts[ACTUAL_PREDICTION_REGRESSION][
                    actual_col
                ]
                prediction_histogram = unique_counts[ACTUAL_PREDICTION_REGRESSION][
                    preds_col
                ]
                actual_values = self.whylogs_histogram(actual_histogram)
                prediction_values = self.whylogs_histogram(prediction_histogram)

                st.subheader(f"Actuals vs Prediction - {data_slice_name} data")
                fig = go.Figure()
                fig.add_trace(go.Histogram(x=actual_values, name=actual_col))
                fig.add_trace(go.Histogram(x=prediction_values, name=preds_col))
                fig.update_layout(barmode="overlay")
                fig.update_traces(opacity=0.6)
                st.write(fig)

    def categorical_feature_distribution(self, dir_path, features, dataslice_schemas):
        """
        unique counts file example:
        {'preds': (array([0, 1]), array([1574,   93])),
        'actuals': (array([0, 1]), array([1443,  224])),
        'state_AZ': (array([0, 1]), array([1642,   25]))
        }
        Each feature contains two array, first array conrresponds to unique values in the feature,
        second array correspond to counts corresponding to the unique values

        Returns:
        numerical_feature_names
        """
        numerical_features = features
        for key in dataslice_schemas.keys():
            data_slice_name = key
            categorical_features = dataslice_schemas[key][
                "categorical_feature_column_names"
            ]
            if categorical_features is not None:
                numerical_features = list(set(features) - set(categorical_features))
                break
        if categorical_features is None:
            return numerical_features

        st.subheader("Categorcal feature distribution")
        cat_feature_option = st.selectbox(
            "Categorical Feature", categorical_features, 0
        )

        for file in os.listdir(dir_path):
            if data_slice_name in file and UNIQUE_COUNTS_FILE_NAME in file:
                with open(os.path.join(dir_path, file), "rb") as f:
                    unique_counts = pickle.load(f)
                # Getting the unique count
                unique_count_feature = unique_counts[cat_feature_option]
                # unique_count_feature[0] corresponds to the unique values
                # unique_count_feature[1] correpons to the counts of the value
                fig = go.Figure(
                    [
                        go.Bar(
                            x=unique_count_feature[0],
                            y=unique_count_feature[1],
                            name=cat_feature_option,
                        )
                    ]
                )
                fig.update_layout(showlegend=True)
                st.write(fig)

        return numerical_features

    def numerical_feature_distribution(self, numerical_features, summary_hist):
        """
        Numercial feature distribution is obtained from whyogs
        """
        st.subheader("Numerical feature distribution")
        with st.form("features availabe"):
            feature_options = st.multiselect(
                "Features", numerical_features, [numerical_features[0]]
            )
            submit_button = st.form_submit_button(label="Submit")

        if len(feature_options) == 0:
            st.warning("Please select a feature")
            return

        if not submit_button:
            return
        values_full = []
        bin_sizes = []
        for feature in feature_options:
            values = []
            for i in range(len(summary_hist[feature][WHYLOGS_BINEDGES]) - 1):
                value = (
                    summary_hist[feature][WHYLOGS_BINEDGES][i]
                    + summary_hist[feature][WHYLOGS_BINEDGES][i + 1]
                ) / 2
                values = values + [value] * summary_hist[feature][WHYLOGS_COUNTS][i]
                if i == 0:
                    bin_size = (
                        summary_hist[feature][WHYLOGS_BINEDGES][i + 1]
                        - summary_hist[feature][WHYLOGS_BINEDGES][i]
                    )
                    bin_sizes.append(bin_size)
            values_full = values_full + [values]
        fig = ff.create_distplot(
            values_full, group_labels=feature_options, bin_size=bin_sizes
        )
        fig.update_layout(width=1000, height=650)
        st.write(fig)

    def actual_vs_prediction_time_series(self, dir_path, dataslice_schemas):
        """
        Actual vs Prediction is plotted for the timeseries dataset
        """
        for data_slice_name in dataslice_schemas.keys():
            for file_name in os.listdir(dir_path):
                if (
                    data_slice_name not in file_name
                    or TIME_SERIES_ACTUAL_PREDS_FILE_NAME not in file_name
                ):
                    continue
                preds_vs_actual = pd.read_parquet(os.path.join(dir_path, file_name))

                preds_col = dataslice_schemas[data_slice_name][
                    "prediction_column_name"
                ]  # getting the prediction and actual column name
                actual_col = dataslice_schemas[data_slice_name]["actual_column_name"]
                predictions = preds_vs_actual[preds_col]
                actuals = preds_vs_actual[actual_col]

                st.subheader(f"Actuals vs Prediction - {data_slice_name} data")
                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(
                        x=list(range(len(predictions))), y=predictions, name=preds_col
                    )
                )
                fig.add_trace(
                    go.Scatter(x=list(range(len(actuals))), y=actuals, name=actual_col)
                )
                fig.update_layout(
                    showlegend=True, xaxis_title="time", yaxis_title="value"
                )
                st.write(fig)

    def feature_histogram(self, dir_path, dataslice_schemas):
        """
        Distributin generation, includes:
        1. categorical variable distribution if any
        2. Prediction vs actuals distribution for all the dataslice available
        3. Numerical features distribution
        """
        ## Getting the whylogs histogram
        profile_summary = self.mlfoundry_data.get_whylogs_summary(
            st.session_state[ID_SESSION_STATE_MODEL_VIEW]
        )
        if profile_summary is None:
            st.warning(
                f"Stats doesn't exist for {st.session_state[ID_SESSION_STATE_MODEL_VIEW]}"
            )
            return
        summary = profile_summary["summary"]
        summary = summary.fillna("null")
        features = list(summary["column"])
        summary_hist = profile_summary["hist"]
        st.header("Feature Histogram")
        ### Actuals vs predictions
        model_type = self.mlfoundry_data.get_model_type(
            st.session_state[ID_SESSION_STATE_MODEL_VIEW]
        )
        if model_type in [
            MULTICLASS_CLASSIFICATION_MODEL_TYPE,
            BINARY_CLASSIFICATION_MODEL_TYPE,
        ]:
            self.actual_vs_preds_classification(dir_path, dataslice_schemas)
        elif model_type == REGRESSION_MODEL_TYPE:
            self.actual_vs_preds_regression(dir_path, dataslice_schemas)
        elif model_type == TIMESERIES_MODEL_TYPE:
            self.actual_vs_prediction_time_series(dir_path, dataslice_schemas)

        ### Catergorical feature distribution
        numerical_features = self.categorical_feature_distribution(
            dir_path, features, dataslice_schemas
        )

        ### Numerical feature distribution - from whylogs
        self.numerical_feature_distribution(numerical_features, summary_hist)

    def start_tab(self, project_name, run_id, run_ids):

        result = self.get_schema_shap(run_id)
        if result is None:
            return

        dir_path, dataslice_schemas, dataslice_shap = result

        self.shap_computation(dataslice_schemas, dataslice_shap)

        self.feature_histogram(dir_path, dataslice_schemas)
