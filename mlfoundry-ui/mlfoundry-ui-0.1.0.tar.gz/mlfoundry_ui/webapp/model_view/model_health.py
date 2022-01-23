import os
import pickle

import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import streamlit as st
from sklearn.metrics import auc

from mlfoundry_ui.webapp.dashboard_constants import *


class ModelHealth:
    def __init__(self, mlfoundry_data) -> None:
        self.mlfoundry_data = mlfoundry_data

    def __metric_name_helper(self, metric_name):
        """
        Given the metric name as stored in S3 returns str in Capitalised and preprocessed form
        Example:
        "mean_absolute_error_train" will be preprocessed and returned as "mean_absolute_error"
        """
        for metric_key, metric_value in METRIC_DICT.items():
            if metric_key in metric_name:
                return metric_value
        return metric_name

    def __roc_helper(self, model_type, multi_dim_metrics):
        fpr = multi_dim_metrics[MULTIDIM_METRICS_ROC][MULTIDIM_METRICS_FPR]
        tpr = multi_dim_metrics[MULTIDIM_METRICS_ROC][MULTIDIM_METRICS_TPR]

        if model_type == BINARY_CLASSIFICATION_MODEL_TYPE:
            fig = px.area(
                x=fpr,
                y=tpr,
                title=f"(AUC={auc(tpr, fpr):.4f})",
                labels=dict(x="False Positive Rate", y="True Positive Rate"),
            )
            fig.add_shape(type="line", line=dict(dash="dash"), x0=0, x1=1, y0=0, y1=1)

        elif model_type == MULTICLASS_CLASSIFICATION_MODEL_TYPE:
            fig = go.Figure()
            fig.add_shape(type="line", line=dict(dash="dash"), x0=0, x1=1, y0=0, y1=1)
            for i in range(len(fpr)):
                name = f"Class {i} (AUC={auc(tpr[i], fpr[i]):.2f})"
                fig.add_trace(go.Scatter(x=fpr[i], y=tpr[i], name=name, mode="lines"))
        # TODO (nikunjbjj): This fig can be referenced before assignment. Need to handle it cleanly.
        return fig

    def __pr_helper(self, model_type, multi_dim_metrics):
        precision = multi_dim_metrics[MULTIDIM_METRICS_PRECISION_RECALL][
            MULTIDIM_METRICS_PRECISION
        ]
        recall = multi_dim_metrics[MULTIDIM_METRICS_PRECISION_RECALL][
            MULTIDIM_METRICS_RECALL
        ]

        if model_type == BINARY_CLASSIFICATION_MODEL_TYPE:
            fig = px.area(x=recall, y=precision, labels=dict(x="Recall", y="Precision"))
            fig.add_shape(type="line", line=dict(dash="dash"), x0=0, x1=1, y0=1, y1=0)

        elif model_type == MULTICLASS_CLASSIFICATION_MODEL_TYPE:
            fig = go.Figure()
            fig.add_shape(type="line", line=dict(dash="dash"), x0=0, x1=1, y0=1, y1=0)
            for i in range(len(precision)):
                name = f"Class {i}"
                fig.add_trace(
                    go.Scatter(x=recall[i], y=precision[i], name=name, mode="lines")
                )

        return fig

    def __roc_pr_helper(self, model_type, multi_dim_metric_dict):
        """Helper function to generate roc and pr curve

        Args:
            model_type (str)
            multi_dim_metrics (dict): multi_dim_metrics fetched from S3

        """
        for data_slice, multi_dim_metrics in multi_dim_metric_dict.items():
            figs = {}
            if MULTIDIM_METRICS_ROC in multi_dim_metrics.keys():
                figs["ROC"] = self.__roc_helper(model_type, multi_dim_metrics)

            if MULTIDIM_METRICS_PRECISION_RECALL in multi_dim_metrics.keys():
                figs["PR"] = self.__pr_helper(model_type, multi_dim_metrics)

            ## Plot the roc and pr curve for the specific data slice
            cols = list(st.columns(2))
            for i, (key, fig) in enumerate(figs.items()):
                cols[i].subheader(f"{key} Curve - {data_slice} data")
                cols[i].write(fig)

    def __confusion_matrix_helper(self):
        """
        Plots confusion matrix for all the dataslice

        Returns:
            multi_dim_metric_dict: multi_dim_metric corresponding to each dataslice
        """
        dir_path = self.mlfoundry_data.get_artifact(
            st.session_state[ID_SESSION_STATE_MODEL_VIEW], MULTIDIM_METRICS
        )
        multi_dim_metric_dict = {}
        confusion_matrix_figs = {}
        for file_name in os.listdir(dir_path):
            with open(os.path.join(dir_path, file_name), "rb") as f:
                multi_dim_metrics = pickle.load(f)

            for data_slice in DATA_SLICES:
                if data_slice not in file_name:
                    continue
                multi_dim_metric_dict[data_slice] = multi_dim_metrics
                matrix = multi_dim_metrics[MULTIDIM_METRICS_CONFUSION_MATRIX]
                matrix = np.flip(matrix, 0)
                fig = ff.create_annotated_heatmap(
                    matrix,
                    colorscale="Viridis",
                    x=[str(x) for x in list(range(len(matrix)))],
                    y=[str(x) for x in list(range(len(matrix) - 1, -1, -1))],
                )
                fig.update_layout(xaxis_title="Predictions", yaxis_title="Actuals")
                confusion_matrix_figs[data_slice] = fig

        cols = list(st.columns(2))
        if len(confusion_matrix_figs.keys()) > 2:
            cols += list(st.columns(2))
        for i, (data_slice, confusion_matrix) in enumerate(
            confusion_matrix_figs.items()
        ):
            with cols[i]:
                st.subheader(f"Confusion Matrix - {data_slice}")
                st.write(confusion_matrix)

        return multi_dim_metric_dict

    def user_generated_metrics(self, id_df_user):

        if id_df_user.empty:
            return
        ## metrics that are lists, example: r2_score = [0.5,0.8,0.9]
        id_df_user_list = id_df_user[
            id_df_user[METRIC_DF_VALUE_COL].apply(lambda x: isinstance(x, list))
        ]
        # metrics that are sigle numbers
        id_df_user = id_df_user[
            ~id_df_user[METRIC_DF_VALUE_COL].apply(lambda x: isinstance(x, list))
        ]
        id_df_user[METRIC_DF_VALUE_COL] = id_df_user[METRIC_DF_VALUE_COL].map(
            lambda x: round(x, 2)
        )

        if len(id_df_user) > 0 or len(id_df_user_list) > 0:
            st.subheader("User Generated Metrics")
        #### User Generated metrics that are single numbers
        if len(id_df_user) > 0:
            fig = go.Figure(
                data=[
                    go.Bar(
                        x=list(id_df_user[METRIC_DF_KEY_COL]),
                        y=list(id_df_user[METRIC_DF_VALUE_COL]),
                        text=list(id_df_user[METRIC_DF_VALUE_COL]),
                        textposition="auto",
                    )
                ]
            )
            fig.update_layout(showlegend=True)
            st.write(fig)
        # user generated metrics that are lists
        if len(id_df_user_list) > 0:
            fig = go.Figure()
            for index, row in id_df_user_list.iterrows():
                fig.add_trace(
                    go.Scatter(
                        x=list(range(len(row[METRIC_DF_KEY_COL]))),
                        y=row[METRIC_DF_VALUE_COL],
                        name=row[METRIC_DF_KEY_COL],
                    )
                )
            fig.update_layout(showlegend=True, yaxis_title="value")
            st.write(fig)

    def __auto_generated_metrics_helper(self, pre_computed_metrics_df):
        """
        This function returns a dictionary where keys are the dataslice and
        values are metrics dataframe corresponding to the dataslice

        """
        pre_computed_metrics = {}
        if pre_computed_metrics_df.empty:
            return pre_computed_metrics
        for data_slice in DATA_SLICES:
            data_slice_df = pre_computed_metrics_df[
                pre_computed_metrics_df[METRIC_DF_KEY_COL].str.endswith(data_slice)
            ]
            if data_slice_df.empty:
                continue
            pre_computed_metrics[data_slice] = data_slice_df
            pre_computed_metrics[data_slice][METRIC_DF_KEY_COL] = pre_computed_metrics[
                data_slice
            ][METRIC_DF_KEY_COL].map(self.__metric_name_helper)

        return pre_computed_metrics

    def auto_generated_metrics(self, id_df_pre_computed):

        if id_df_pre_computed.empty:
            return
        ## auto generated metrics that are lists, example: r2_score = [0.5,0.8,0.9]
        id_df_pre_computed_list = id_df_pre_computed[
            id_df_pre_computed[METRIC_DF_VALUE_COL].apply(lambda x: isinstance(x, list))
        ]
        # metrics that are sigle numbers
        id_df_pre_computed = id_df_pre_computed[
            ~id_df_pre_computed[METRIC_DF_VALUE_COL].apply(
                lambda x: isinstance(x, list)
            )
        ]
        if len(id_df_pre_computed) > 0:
            id_df_pre_computed[METRIC_DF_VALUE_COL] = id_df_pre_computed[
                METRIC_DF_VALUE_COL
            ].map(lambda x: round(x, 2))

        pre_computed_metrics = self.__auto_generated_metrics_helper(id_df_pre_computed)
        pre_computed_metrics_list = self.__auto_generated_metrics_helper(
            id_df_pre_computed_list
        )

        ### Auto generated metric that are single number
        if len(pre_computed_metrics) > 0 or len(pre_computed_metrics_list) > 0:
            st.subheader("Auto Generated Metrics")
        if len(pre_computed_metrics) > 0:
            fig = go.Figure()
            for data_slice, metrics_df in pre_computed_metrics.items():
                fig.add_trace(
                    go.Bar(
                        x=list(metrics_df[METRIC_DF_KEY_COL]),
                        y=list(metrics_df[METRIC_DF_VALUE_COL]),
                        text=list(metrics_df[METRIC_DF_VALUE_COL]),
                        name=data_slice,
                        textposition="auto",
                    )
                )
            fig.update_layout(barmode="group", showlegend=True, yaxis_title="value")
            st.write(fig)

        ## auto generated metrics that are lists, example: r2_score = [0.5,0.8,0.9]
        if len(pre_computed_metrics_list) > 0:
            fig = go.Figure()
            # Each row in the dataframe will contain list of metrics, so plotting them one by one
            for data_slice, metrics_df_list in pre_computed_metrics_list.items():
                for index, row in metrics_df_list.iterrows():
                    fig.add_trace(
                        go.Scatter(
                            x=list(range(len(row[METRIC_DF_KEY_COL]))),
                            y=row[METRIC_DF_VALUE_COL],
                            name=f"{row[METRIC_DF_KEY_COL]} -  {data_slice}",
                        )
                    )
            fig.update_layout(showlegend=True, yaxis_title="value", xaxis_title="step")
            st.write(fig)

    def pre_computed_user_generated_metrics(self, metrics_df):
        """
        Returns user generated and auto generated metrics
        """

        id_df = metrics_df[
            metrics_df[METRIC_DF_RUNID_COL]
            == st.session_state[ID_SESSION_STATE_MODEL_VIEW]
        ]

        if not len(id_df) > 0:
            return

        id_df_pre_computed = id_df[
            id_df[METRIC_DF_KEY_COL].str.startswith(PRECOMPUTED_METRIC)
        ]  ## Filtering precomputed metrics
        id_df_user = id_df[
            ~id_df[METRIC_DF_KEY_COL].str.startswith(PRECOMPUTED_METRIC)
        ]  # filtering user generated metrics

        self.user_generated_metrics(id_df_user)
        self.auto_generated_metrics(id_df_pre_computed)

    def start_tab(self, project_name, run_ids):
        """
        List of things shown;
        1. model type
        2. confusion matrix for each dataslice
        3. roc and pr curve for each data slice
        4. auto computed and user generated metrics
        """

        metrics_df = self.mlfoundry_data.get_metrics(run_ids)
        if metrics_df is None:
            st.warning("No Run exists for the Project")
            return

        if ID_SESSION_STATE_MODEL_VIEW not in st.session_state:
            st.warning("Please specify a Run ID on the side bar")
            return

        model_type = self.mlfoundry_data.get_model_type(
            st.session_state[ID_SESSION_STATE_MODEL_VIEW]
        )
        st.header("Model metrics")

        if model_type in [
            MULTICLASS_CLASSIFICATION_MODEL_TYPE,
            BINARY_CLASSIFICATION_MODEL_TYPE,
        ]:
            #### CONFUSION MATRIX COMPUTATION
            multi_dim_metric_dict = self.__confusion_matrix_helper()
            #### ROC and PR Curve
            self.__roc_pr_helper(model_type, multi_dim_metric_dict)

        ## User and precomputed metrics
        self.pre_computed_user_generated_metrics(metrics_df)
