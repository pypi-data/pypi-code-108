import logging

import streamlit as st

from mlfoundry_ui.webapp.dashboard_constants import *

logger = logging.getLogger(__name__)


class SideBar:
    def __init__(self, mlfoundry_data):
        self.mlfoundry_data = mlfoundry_data

    @staticmethod
    def project_name_callback(name, page):
        if page == Pages.SINGLE_RUN_VIEW.value:
            st.session_state[PROJECT_SESSION_STATE_MODEL_VIEW] = name
        elif page == Pages.RUN_COMPARISON.value:
            st.session_state[PROJECT_SESSION_STATE_MODEL_COMPARISON] = name

    @staticmethod
    def run_id_callback(run_id, run_name):
        st.session_state[RUN_NAME_SESSION_STATE_MODEL_VIEW] = run_name
        st.session_state[ID_SESSION_STATE_MODEL_VIEW] = run_id

    def sidebar(self, page, project_name_to_id_dict):
        """

        :param page:
        :param project_name_to_id_dict:
        :return:
        """
        if not project_name_to_id_dict:
            st.sidebar.error(f"No project names provided to show data for.")
            return
        project_names = [i for i in project_name_to_id_dict.keys()]
        with st.sidebar.form(f"Project Name {page}"):
            project_name = st.selectbox("Project Name", options=project_names)
            submit_button = st.form_submit_button(
                "Submit",
                on_click=self.project_name_callback,
                args=[project_name, page],
            )
        if page == Pages.SINGLE_RUN_VIEW.value:  # Is this is a single run view
            if PROJECT_SESSION_STATE_MODEL_VIEW not in st.session_state:
                return
            with st.sidebar.form("run_id_form"):
                with st.spinner("Loading Run IDs"):
                    project_id = project_name_to_id_dict[project_name]
                    try:
                        run_name_to_id_dict = self.mlfoundry_data.get_runs_in_project(
                            project_id
                        )
                    except Exception as e:
                        err_msg = f"Was not able to fetch any runs for project {project_name}. Error {e}"
                        st.sidebar.warning(err_msg)
                        logger.exception(err_msg)
                        return
                if not run_name_to_id_dict:
                    err_msg = (
                        f"Was not able to fetch any runs for project {project_name}."
                    )
                    st.sidebar.warning(err_msg)
                    logger.error(err_msg)
                    return
                run_name = st.selectbox(
                    "Run Name",
                    list([run_name for run_name in run_name_to_id_dict.keys()]),
                )
                run_id = run_name_to_id_dict[run_name]

                id_submit_button = st.form_submit_button(
                    "Submit", on_click=self.run_id_callback, args=[run_id, run_name]
                )

            return run_name_to_id_dict

        elif page == Pages.RUN_COMPARISON.value:  # Is this is a run comparison view

            if PROJECT_SESSION_STATE_MODEL_COMPARISON not in st.session_state:
                return
            project_id = project_name_to_id_dict[project_name]
            try:
                run_name_to_id_dict = self.mlfoundry_data.get_runs_in_project(
                    project_id
                )
            except Exception as e:
                err_msg = f"Was not able to fetch any runs for project {project_name}. Error {e}"
                st.sidebar.warning(err_msg)
                logger.error(err_msg)
                return
            if not run_name_to_id_dict:
                err_msg = f"Was not able to fetch any runs for project {project_name}."
                st.sidebar.warning(err_msg)
                logger.error(err_msg)
                return
            return run_name_to_id_dict
        else:
            logger.error(
                f"Received page value {page} but expecting one of {[e.value for e in Pages]}"
            )
