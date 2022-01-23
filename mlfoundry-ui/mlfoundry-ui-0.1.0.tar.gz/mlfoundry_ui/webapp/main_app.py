import logging
import sys

import hydralit as hy
import streamlit as st

from mlfoundry_ui.constants import MLFOUNDRY_DOCUMENTATION_LINK
from mlfoundry_ui.webapp.dashboard_constants import *
from mlfoundry_ui.webapp.mlfoundry_data import MLFoundryData
from mlfoundry_ui.webapp.model_comparison.model_comparison import ModelComparison
from mlfoundry_ui.webapp.model_view.data_health import DataHealth
from mlfoundry_ui.webapp.model_view.feature_view import FeatureView
from mlfoundry_ui.webapp.model_view.model_health import ModelHealth
from mlfoundry_ui.webapp.sidebar import SideBar

logger = logging.getLogger(__name__)


def page_navigation():
    with st.sidebar:
        selected_page = st.radio("Page", [e.value for e in Pages])
    return selected_page


def deal_with_single_run_view(run_name_to_id_dict, mlfoundry_data, app):
    if ID_SESSION_STATE_MODEL_VIEW in st.session_state:
        run_ids = [run_id for run_id in run_name_to_id_dict.values()]

        @app.addapp(title="Model Health")
        def model_health():
            modelhealth_page = ModelHealth(mlfoundry_data)
            modelhealth_page.start_tab(
                st.session_state[PROJECT_SESSION_STATE_MODEL_VIEW], run_ids
            )

        @app.addapp(title="Data Health")
        def data_health():
            datahealth_page = DataHealth(mlfoundry_data)
            datahealth_page.start_tab(
                st.session_state[PROJECT_SESSION_STATE_MODEL_VIEW],
                st.session_state[ID_SESSION_STATE_MODEL_VIEW],
                run_ids,
            )

        @app.addapp(title="Feature Health")
        def feature_view():
            featureview_page = FeatureView(mlfoundry_data)
            featureview_page.start_tab(
                st.session_state[PROJECT_SESSION_STATE_MODEL_VIEW],
                st.session_state[ID_SESSION_STATE_MODEL_VIEW],
                run_ids,
            )

        app.run()


def deal_with_model_comparison_view(run_name_to_id_dict, mlfoundry_data, app):
    if PROJECT_SESSION_STATE_MODEL_COMPARISON in st.session_state:
        run_ids = [run_id for run_id in run_name_to_id_dict.values()]

        @app.addapp(title="Model Comparison")
        def comparison():
            modelcomparison_page = ModelComparison(mlfoundry_data)
            modelcomparison_page.start_tab(run_ids)

        app.run()


def main():

    # TODO (nikunjbjj): Need to use argparse here.
    if len(sys.argv) > 1:
        mlruns_path = sys.argv[1]
    else:
        mlruns_path = ""

    app = hy.HydraApp(
        title="MLFoundry dashboard",
        hide_streamlit_markers=False,
        navbar_sticky=True,
    )
    mlfoundry_data = MLFoundryData(mlruns_path)
    sidebar = SideBar(mlfoundry_data)

    project_name_to_id_dict = mlfoundry_data.project_options()
    if not project_name_to_id_dict:
        st.warning(
            f"No projects are logged in the path {mlruns_path} using mlfoundry. "
            f"Please use {MLFOUNDRY_DOCUMENTATION_LINK} to find instructions to log data."
            f"Can't bring up the dashboard."
        )
        return

    selected_page = page_navigation()

    run_name_to_id_dict = sidebar.sidebar(selected_page, project_name_to_id_dict)

    # TODO (nikunjbjj): Handle the case if the above function returns None because of error.
    # if run_ids_names_tuple is None:
    #     st.warning(
    #         f"Problem happened selecting the project or run. Can't bring up the dashboard"
    #     )
    #     return
    if selected_page == Pages.SINGLE_RUN_VIEW.value:
        deal_with_single_run_view(run_name_to_id_dict, mlfoundry_data, app)
    elif selected_page == Pages.RUN_COMPARISON.value:
        deal_with_model_comparison_view(run_name_to_id_dict, mlfoundry_data, app)
    else:
        logger.error(
            f"Received page value {selected_page} but expecting one of {[e.value for e in Pages]}"
        )


if __name__ == "__main__":
    main()
