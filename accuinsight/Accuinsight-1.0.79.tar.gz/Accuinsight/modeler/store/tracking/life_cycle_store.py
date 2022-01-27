import json

from Accuinsight.modeler.entities import Run
from Accuinsight.modeler.protos.life_cycle_pb2 import LcCreateRun, LifecycleService, LcGitInfo, LcPyDepen
from Accuinsight.modeler.store.tracking.lc_abstract_store import AbstractStore as LcAbstractStore
from Accuinsight.modeler.utils.proto_json_utils import message_to_json
from Accuinsight.modeler.utils.rest_utils import call_endpoint, extract_api_info_for_service
from Accuinsight.modeler.utils.os_getenv import get_os_env
from Accuinsight.modeler.core.Run.ParseRun import BaseParser
from Accuinsight.modeler.core.Run.RunInfo.RunInfo import dict_to_list
from Accuinsight.modeler.core.LcConst.LcConst import SOURCE_FILE_GIT_META, PYTHON_DEPENDENCY, SOURCE_FILE_GIT_REPO, \
    SOURCE_FILE_GIT_COMMIT_ID
from Accuinsight.modeler.entities.lc_run_info import LcRunInfo as EntityRunInfo
from Accuinsight.modeler.core.LcConst import LcConst
from Accuinsight.modeler.entities.lc_artifact import LcArtifact as EntityArtifact

_PATH_PREFIX = ""
_METHOD_TO_INFO = extract_api_info_for_service(LifecycleService, _PATH_PREFIX)


def _set_run_info(current_run_meta, user_sso_id):
    model_path = ''
    json_path = ''

    if current_run_meta[LcConst.RUN_OBJ_BEST_MODEL_H5_PATH] is not None:
        model_path = current_run_meta[LcConst.RUN_OBJ_BEST_MODEL_H5_PATH]

    if current_run_meta[LcConst.RUN_OBJ_BEST_MODEL_JOBLIB_PATH] is not None:
        model_path = current_run_meta[LcConst.RUN_OBJ_BEST_MODEL_JOBLIB_PATH]

    if current_run_meta[LcConst.RUN_OBJ_BEST_MODEL_JSON_PATH] is not None:
        json_path = current_run_meta[LcConst.RUN_OBJ_BEST_MODEL_JSON_PATH]

    run_info = EntityRunInfo(
        user_id=user_sso_id,
        start_time=current_run_meta[LcConst.START_TIME],
        end_time=current_run_meta[LcConst.END_TIME],
        duration=current_run_meta[LcConst.DELTA_TIME],
        artifact_location="",
        run_status="FINISHED",
        path=current_run_meta[LcConst.RUN_OBJ_MODEL_FILE_PATH],
        model_path=model_path,
        json_path=json_path,
        run_name=current_run_meta[LcConst.RUN_OBJ_NAME],
        note=""
    )

    return run_info


class RestStore(LcAbstractStore):
    """
    Client for a remote tracking server accessed via REST API calls
    """

    def __init__(self, get_host_creds):
        super(RestStore, self).__init__()
        self.get_host_creds = get_host_creds

    def _call_endpoint(self, api, json_body, current_run_meta):
        endpoint, method = _METHOD_TO_INFO[api]

        # '/project/{project}/workspace/{workspaceId}/experiment/{experimentId}/run'
        if api.__name__ == 'LcCreateRun':
            env_value = get_os_env()
            endpoint = endpoint.replace('{project}', str(env_value[LcConst.ENV_PROJECT_ID]))
            endpoint = endpoint.replace('{workspaceId}', str(env_value[LcConst.ENV_WORKSPACE_ID]))
            endpoint = endpoint.replace('{experimentId}', str(env_value[LcConst.ENV_EXPERIMENT_ID]))

        response_proto = api.Response()
        return call_endpoint(self.get_host_creds(), endpoint, method, json_body, response_proto, current_run_meta)

    def lc_create_run(self, current_run_meta):
        """
        Create a run under the specified experiment ID.

        :return: The ID of the created Run object
        """

        # read workspace environment
        # project_id, workspace_id, experiment_id and user_id
        env_value = get_os_env()
        project_id = str(env_value[LcConst.ENV_PROJECT_ID])
        workspace_id = str(env_value[LcConst.ENV_WORKSPACE_ID])
        experiment_id = str(env_value[LcConst.ENV_EXPERIMENT_ID])
        user_id = str(env_value[LcConst.ENV_USER_SSO_ID])  # owner id
        language_id = str(env_value[LcConst.ENV_LANGUAGE_ID])

        with open(current_run_meta[LcConst.RUN_RESULT_PATH][LcConst.RUN_MODEL_JSON_PATH]) as run_json_file:
            json_data = json.load(run_json_file)

            try:
                user_id = json_data['user_id']
            except KeyError:
                pass

        run_proto = _set_run_info(current_run_meta, user_id).to_proto()

        git_meta = {'filename': '', 'repo': '', 'commit': ''}
        git_meta_data = LcGitInfo(
            url=git_meta[SOURCE_FILE_GIT_REPO],
            commit=git_meta[SOURCE_FILE_GIT_COMMIT_ID]
        )
        if SOURCE_FILE_GIT_META in current_run_meta:
            git_meta = current_run_meta[SOURCE_FILE_GIT_META]
            if SOURCE_FILE_GIT_REPO in git_meta:
                git_meta_data = LcGitInfo(
                    url=git_meta[SOURCE_FILE_GIT_REPO],
                    commit=git_meta[SOURCE_FILE_GIT_COMMIT_ID]
                )

        py_depen = LcPyDepen(data=[])
        if PYTHON_DEPENDENCY in current_run_meta:
            pdep = current_run_meta[PYTHON_DEPENDENCY]
            pdep_list = dict_to_list(pdep)
            py_depen = LcPyDepen(
                data=pdep_list
            )

        # to get parameter and metric
        run_data = BaseParser.run_parser(BaseParser.get_parser_type(current_run_meta), current_run_meta)
        metric_data = run_data['metrics']
        parameter_data = run_data['params']
        visual_data = None
        if 'visual' in run_data:
            visual_data = run_data['visual']

        artifact = EntityArtifact(
            name=run_data['artifact']['name'],
            version=run_data['artifact']['version']
        )
        artifact_proto = artifact.to_proto()

        req_body = message_to_json(
            LcCreateRun(
                project_id=project_id,
                workspace_id=workspace_id,
                experiment_id=experiment_id,
                userId=user_id,
                language_id=language_id,
                #path=git_meta['filename'], # TODO brian_todo set model file path
                #name='dummy.py', # TODO brian_todo set model file name
                run=run_proto,
                artifact=artifact_proto,
                git=git_meta_data,
                parameter=parameter_data,
                metrics=metric_data,
                visuals=visual_data,
                dependency=py_depen
            )
        )

        response_proto = self._call_endpoint(LcCreateRun, req_body, current_run_meta)
        run = Run.from_proto(response_proto.run)
        return run

    def create_tag(self, run_id, tag):
        """
        Set a tag for the specified run

        :param run_id: String ID of the run
        :param tag: RunTag instance to log
        """

        # TODO brian_todo

        pass
