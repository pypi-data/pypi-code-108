import logging
import random

import plotly.graph_objects as go
import streamlit as st

from mlfoundry_ui.webapp.dashboard_constants import *

# from scipy.sparse.construct import random


logger = logging.getLogger(__name__)


class ModelComparison:
    def __init__(self, mlfoundry_data) -> None:
        self.mlfoundry_data = mlfoundry_data

    def start_tab(self, run_ids):
        metrics_df = self.mlfoundry_data.get_metrics(run_ids)
        metrics_df_list = metrics_df[
            metrics_df[METRIC_DF_VALUE_COL].apply(lambda x: isinstance(x, list))
        ]
        metrics_df = metrics_df[
            ~metrics_df[METRIC_DF_VALUE_COL].apply(lambda x: isinstance(x, list))
        ]

        comparison_columns = st.selectbox(
            "Comparison By", [METRIC_DF_RUNID_COL, METRIC_DF_RUN_NAME_COL], 0
        )

        unique_runs = list(
            set(
                list(metrics_df[comparison_columns])
                + list(metrics_df_list[comparison_columns])
            )
        )
        if comparison_columns == METRIC_DF_RUNID_COL:
            runs = st.multiselect("Run IDs", unique_runs, unique_runs)
        elif comparison_columns == METRIC_DF_RUN_NAME_COL:
            runs = st.multiselect("Run Names", unique_runs, unique_runs)
        else:
            logger.error(
                f"Expecting one of the following "
                f"{METRIC_DF_RUNID_COL, METRIC_DF_RUN_NAME_COL} to be selected. Got {comparison_columns}"
            )
            return

        if len(metrics_df) == 0:
            logger.info(f"No metrics are logged.")
            return

        metrics = list(metrics_df[METRIC_DF_KEY_COL].unique())
        metrics_df = metrics_df[metrics_df[comparison_columns].isin(runs)]
        dat = []
        for metric in metrics:
            try:
                x = list(
                    metrics_df[metrics_df[METRIC_DF_KEY_COL] == metric][
                        comparison_columns
                    ]
                )
                y = list(
                    metrics_df[metrics_df[METRIC_DF_KEY_COL] == metric][
                        METRIC_DF_VALUE_COL
                    ]
                )
                dat.append(go.Bar(x=x, y=y, name=metric))
                fig = go.Figure(data=[go.Bar(x=x, y=y)])
                fig.update_traces(
                    marker_color=random.choice(COLORS),
                    marker_line_width=1.5,
                    opacity=0.6,
                )
                fig.update_layout(title_text=metric)
                st.write(fig)
            except Exception as err:
                logger.error(
                    f"Error happened in plotting metric {metric}. Error: {err}"
                )

        fig = go.Figure(data=dat)
        fig.update_layout(barmode="group", width=1000, height=600)
        st.write(fig)
