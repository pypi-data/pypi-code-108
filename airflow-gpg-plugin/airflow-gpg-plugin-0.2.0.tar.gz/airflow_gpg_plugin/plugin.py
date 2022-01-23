from airflow.plugins_manager import AirflowPlugin

from airflow_gpg_plugin.hooks.gpg_hook import GpgHook


class AirflowGPGPlugin(AirflowPlugin):
    name = "airflow_gpg_plugin"
    hooks = [
        GpgHook
    ]
    executors = []
    macros = []
    admin_views = []
    flask_blueprints = []
    menu_links = []
