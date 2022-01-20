# VERSION
VERSION = "v2/version/"

# ORGANIZATION
ORGANIZATION_BASE = "v2/{0}/"
ORGANIZATION_SETTINGS = "v2/{0}/settings"
ORGANIZATION_USERS = "v2/{0}/users"
ORGANIZATION_CREATE = "v2/organizations"

# USER
USER_BASE = "v2/users/"
USER_LOGIN = "v2/users/sign_in"
USER_CURRENT = "v2/users/me"
USER_MEMBERSHIPS = "v2/users/me/memberships/"

# PROJECT
PROJECTS_BASE = "v2/{0}/projects/"
PROJECT_BASE = "v2/{0}/projects/{1}"
PROJECT_CLONE_SUFFIX = "clone"
PROJECT_BULK_DELETE_SUFFIX = "delete_projects"

# DATASET
DATASETS_BASE = "v2/{0}/datasets/"
DATASET_BASE = "v2/{0}/datasets/{1}"

# COMMIT
COMMITS_BASE = "v2/{0}/datasets/{1}/commits/"
COMMIT_BASE = "v2/{0}/datasets/{1}/commits/{2}"
COMMIT_REMOVE_FILES = "commits/{0}/remove_files?page[size]=1000&sort=id"

# QUERIES
QUERY_BASE = "v2/{0}/datasets/{1}/queries/{2}"
QUERIES_BASE = "v2/{0}/datasets/{1}/queries"

# IMAGE
IMAGES_BASE = "v2/{0}/images/"
IMAGE_BASE = "v2/{0}/images/{1}"

# VOLUME
VOLUMES_BASE = "v2/{0}/projects/{1}/volumes"
VOLUME_BASE = "v2/{0}/projects/{1}/volumes/{2}"

# FLOW
FLOWS_BASE = "v2/{0}/projects/{1}/flows/"
FLOW_BASE = "v2/{0}/projects/{1}/flows/{2}/"
FLOW_SET_SCHEDULE = "start-cron"
FLOW_STOP_SCHEDULE = "stop-cron"
CREATE_WITH_YAML = "create-with-yaml"
RUN_FLOW = "run"
FLOW_TOGGLE_WEBHOOK = "toggle-webhook"
FLOW_TOGGLE_DATASET_UPDATE = "toggle-dataset-update"
FLOW_LATEST_END_COMMITS = "latest-end-commits"
FLOW_REVIEWERS = "reviewers"

# FLOW_VERSION
FLOW_VERSIONS_BASE = "v2/{0}/projects/{1}/flows/{2}/flow-versions"
FLOW_VERSION_BASE = "v2/{0}/projects/{1}/flows/{2}/flow-versions/{3}"
FLOW_VERSION_INFO = "info"
FLOW_VERSION_STOP = "stop"

# WORKFLOW
WORKFLOW_STANDALONE_BASE = "v2/{0}/workflows/"
WORKFLOWS_BASE = "v2/{0}/projects/{1}/workflows/"
WORKFLOWS_BASE_NEW = "v2/{0}/projects/{1}/{2}/"
WORKFLOW_BASE = "v2/{0}/projects/{1}/workflows/{2}/"
WORKFLOW_STOP_SUFFIX = "stop"
WORKFLOW_RESTART_SUFFIX = "restart"
WORKFLOW_SYNC_SUFFIX = "sync"
WORKFLOW_LIST_TYPE_SUFFIX = "?filter={{" \
                            "\"operator\":\"AND\"," \
                            "\"conditions\":[{{\"key\":\"job_type\",\"operator\":\"is\",\"value\":\"{0}\"}}]" \
                            "}}"
WORKflOW_START_SUFFIX = "start"
WORKflOW_START_TENSORBOARD_SUFFIX = "start_tensorboard"
WORKflOW_STOP_TENSORBOARD_SUFFIX = "stop_tensorboard"
WORKFLOW_WRITE_LOGS_SUFFIX = "write_logs"
WORKFLOW_GET_LOGS_SUFFIX = "logs"
WORKFLOW_TAG_SUFFIX = "tags"
WORKFLOW_UPDATE_SUFFIX = "update"

# WORKSPACE
WORKSPACES_BASE = "v2/{0}/projects/{1}/workspaces/"
WORKSPACE_BASE = "v2/{0}/projects/{1}/workspaces/{2}/"
WORKSPACE_BUILD_IMAGE_SUFFIX = "build_image"
WORKSPACE_ACTIVATE_BUILD_IMAGE_ON_STOP_SUFFIX = "activate_build_image_on_stop"
WORKSPACE_DISABLE_BUILD_IMAGE_ON_STOP_SUFFIX = "disable_build_image_on_stop"

# EXPERIMENT
EXPERIMENTS_BASE = "v2/{0}/projects/{1}/experiments/"
EXPERIMENT_BASE = "v2/{0}/projects/{1}/experiments/{2}/"
EXPERIMENT_RERUN_SUFFIX = "rerun"
EXPERIMENT_FINISH_SUFFIX = "finish"
EXPERIMENT_CHARTS_SUFFIX = "charts"
EXPERIMENT_GET_UTILIZATION_SUFFIX = "get_utilization"
EXPERIMENT_CHART_SUFFIX = "charts/{0}"
EXPERIMENT_WRITE_LOGS = "write_logs"
EXPERIMENT_LOGS_SUFFIX = "logs?offset=-1&search=&filter=[\"all\"]"

# WEBAPP
WEBAPPS_BASE = "v2/{0}/projects/{1}/webapps/"
WEBAPP_BASE = "v2/{0}/projects/{1}/webapps/{2}/"

# ENDPOINT
ENDPOINTS_BASE = "v2/{0}/projects/{1}/endpoints"
ENDPOINT_BASE = "v2/{0}/projects/{1}/endpoints/{2}/"
UPDATE_MODEL_VERSION = "update_model"
ENDPOINT_FEEDBACK_LOOP = "feedback_loop"
ROLLBACK_MODEL_VERSION = "rollback_session/{0}"
ENDPOINT_SAMPLE_CODE = "sample_code"
ENDPOINT_REPLICAS = "replicas"
ENDPOINT_POLL_CHARTS = "poll_charts"
ENDPOINT_STATUS = "status"
ENDPOINT_BATCH_SCALE_UP = "batch_scale_up"
ENDPOINT_BATCH_SCALE_DOWN = "batch_scale_down"
ENDPOINT_RULES = "rules"

# COMMON
GET_BY_NAME_SUFFIX = "get_by_name"

# RESOURCES
MACHINES_BASE = "v2/{0}/resources/machines/computes"
SPARK_DRIVERS_BASE = "v2/{0}/resources/spark_driver"
CLUSTERS_BASE = "v2/{0}/resources/clusters"
MACHINE_BASE = "v2/{0}/resources/machines/computes/{1}"
SPARK_DRIVER_BASE = "v2/{0}/resources/spark_driver/{1}"
CLUSTER_BASE = "v2/{0}/resources/clusters/{1}"

# TEMPLATE
TEMPLATES_BASE = "v2/{0}/resources/{1}/{2}/computes"
TEMPLATE_BASE = "v2/{0}/resources/{1}/{2}/computes/{3}"

# SSH
SSH_BASE = "v2/{0}/job_ssh/{1}"
SSH_START_SUFFIX = "start"
SSH_STATUS_SUFFIX = "status"
