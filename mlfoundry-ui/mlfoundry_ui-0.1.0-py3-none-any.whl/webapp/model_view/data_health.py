import datetime

import plotly.figure_factory as ff
import plotly.graph_objects as go
import streamlit as st


class DataHealth:
    def __init__(self, mlfoundry_data):
        self.mlfoundry_data = mlfoundry_data

    def start_tab(self, project_name, id, run_ids):

        ## Whylogs profile summary computation
        profile_summary = self.mlfoundry_data.get_whylogs_summary(
            st.session_state["id_model"]
        )

        if profile_summary is None:
            st.warning(
                f"Profile summary doesn't exists for run {st.session_state['id_model']}"
            )
            return
        summary = profile_summary["summary"]
        summary = summary.fillna("null")

        st.subheader("Profile Summary")

        st.dataframe(summary)
