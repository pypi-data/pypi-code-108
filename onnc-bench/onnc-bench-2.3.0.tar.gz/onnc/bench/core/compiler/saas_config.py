timeout = 300  # in seconds
poll_interval = 0.5  # in seconds

URI_MAP = {
    "saas_login": {
        "uri": "/users/login",
        "method": "POST"
    },
    "saas_create_project": {
        "uri": "/projects",
        "method": "POST"
    },
    "saas_get_project_id_by_name": {
        "uri": "/projects?filter[where][name]={}",
        "method": "GET"
    },
    "saas_upload_file": {
        "uri": "/files",
        "method": "POST"
    },
    "saas_create_compilation": {
        "uri": "/compilations",
        "method": "POST"
    },
    "saas_create_build": {
        "uri": "/builds",
        "method": "POST"
    },
    "saas_get_build_state": {
        "uri": "/builds/{}",
        "method": "GET"
    },
    "saas_download_deployment_package": {
        "uri": "/files/{}",
        "method": "GET"
    },
    "saas_upload_report": {
        "uri": "/compilation-reports",
        "method": "POST"
    },
    "saas_list_devices": {
        "uri": "/boards",
        "method": "GET"
    }

}
