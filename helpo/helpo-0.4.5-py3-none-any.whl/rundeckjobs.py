import json
import os
import shutil
import subprocess
import tempfile

import hvac
import requests
import tldextract
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_random
from distutils.util import strtobool


def rmdir(dir_location):
    if os.path.isdir(dir_location):
        logger.info(f"Removing existing config dir {dir_location}")
        shutil.rmtree(dir_location)
        logger.info(f"Removed existing config dir {dir_location}")


def extract_domain_parts(fqdn):
    fqdn_parts = tldextract.extract(fqdn)
    return fqdn_parts


def write_into_file(file_content, file_location):
    with open(file_location, "w") as f:
        f.write(file_content)


def prepare_terraform_environment(data_dir):
    os.environ["PATH"] += os.pathsep + f"{os.path.expanduser('~')}/bin"
    os.environ["TF_REGISTRY_DISCOVERY_RETRY"] = "10"
    os.environ["TF_REGISTRY_CLIENT_TIMEOUT"] = "60"
    os.environ["TF_IN_AUTOMATION"] = "true"
    os.environ["TF_PLUGIN_CACHE_DIR"] = f"{os.path.expanduser('~')}/.terraform.d/plugin-cache"
    # os.environ["TF_DATA_DIR"] = data_dir
    if not os.path.exists(f"{os.path.expanduser('~')}/.terraform.d/plugin-cache"):
        os.makedirs(f"{os.path.expanduser('~')}/.terraform.d/plugin-cache")


class RundeckJobs(object):
    def __init__(
            self,
            uptimerobot_api_url: str = "https://api.uptimerobot.com/v2/getMonitors",
    ):
        self.uptimerobot_api_url = uptimerobot_api_url

    min_retry_delay = int(os.environ.get("RD_OPTION_MIN_RETRY_DELAY", 60))
    max_retry_delay = int(os.environ.get("RD_OPTION_MIN_RETRY_DELAY", 180))
    number_of_retries = int(os.environ.get("RD_OPTION_NUMBER_OF_RETRIES", 3))

    wait_random_range: tuple = (min_retry_delay, max_retry_delay)

    @retry(wait=wait_random(*wait_random_range), stop=stop_after_attempt(number_of_retries))
    def run_command(self, command, cwd, check=True):
        subprocess.run(command, cwd=cwd, check=check)

    def clone_rundeck_codebase(self, gitlab_deploy_token: str):
        repository_directory = tempfile.mkdtemp()
        with tempfile.TemporaryDirectory() as tmpdir:
            self.run_command(["git", "clone", "--depth", "1",
                              f"https://oauth2:{gitlab_deploy_token}@gitlab.zadapps.info/infrastructure/rundeck/rundeck.git",
                              repository_directory], cwd="/tmp")
        return repository_directory

    def search_uptimerobot(
            self,
            deployment_action: str = os.environ.get(
                'RD_OPTION_DEPLOYMENT_ACTION'),
            uptimerobot_api_key: str = os.environ.get(
                "RD_OPTION_UPTIMEROBOT_API_KEY"),
            fqdn: str = os.environ.get("RD_OPTION_FQDN"),
            force_apply: bool = strtobool(os.environ.get('RD_OPTION_FORCE_APPLY'))):
        if deployment_action != 'apply':
            print("Skipping website hosting check as deployment action is not apply")
            exit(0)

        url = self.uptimerobot_api_url

        payload = f"api_key={uptimerobot_api_key}&search={fqdn}"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        matched_monitors = [response.json()['monitors'][i]['friendly_name'] for i in range(len(
            response.json()['monitors'])) if response.json()['monitors'][i]['friendly_name'] == fqdn]

        if not matched_monitors:
            print(f"{fqdn} seems to be a new site, skipping!")
            exit(0)
        elif force_apply:
            print("Force apply is requested, ignoring check results")
            exit(0)
        else:
            print(
                f"{fqdn} is alive, want to force redeployment? then change option `force_apply` value to `true`")
            exit(1)

    @retry(wait=wait_random(*wait_random_range), stop=stop_after_attempt(number_of_retries))
    def terraform_cloud_workspace(
            self,
            pg_user: str = os.environ.get(
                'RD_OPTION_TERRAFORM_PG_BACKEND_USER'),
            pg_password: str = os.environ.get(
                'RD_OPTION_TERRAFORM_PG_BACKEND_PASSWORD'),
            pg_ip: str = os.environ.get('RD_OPTION_TERRAFORM_PG_BACKEND_IP'),
            pg_port: str = os.environ.get(
                'RD_OPTION_TERRAFORM_PG_BACKEND_PORT'),
            pg_db: str = os.environ.get('RD_OPTION_TERRAFORM_PG_BACKEND_DB'),
            deployment_action: str = os.environ.get(
                "RD_OPTION_DEPLOYMENT_ACTION"),
            fqdn: str = os.environ.get("RD_OPTION_FQDN"),
            datacenter: str = os.environ.get('RD_OPTION_DATACENTER'),
            organization: str = os.environ.get('RD_OPTION_ORGANIZATION'),
            terraform_cloud_token: str = os.environ.get(
                'RD_OPTION_TERRAFORM_CLOUD_TOKEN'),
            with_vcs_repo: str = os.environ.get('RD_OPTION_WITH_VCS_REPO'),
            auto_apply: str = os.environ.get('RD_OPTION_AUTO_APPLY'),
            execution_mode: str = os.environ.get('RD_OPTION_EXECUTION_MODE'),
            deployment_environment: str = os.environ.get(
                'RD_OPTION_DEPLOYMENT_ENVIRONMENT'),
            vcs_repo_oauth_token_id: str = os.environ.get(
                'RD_OPTION_VCS_REPO_OAUTH_TOKEN_ID'),
            tag_names: str = os.environ.get('RD_OPTION_TAG_NAMES'),
            terraform_code_dir: str = f"{os.path.expanduser('~')}/codebase/terraform/rootmodule/terraform_cloud_workspace",
    ):

        pg_backend_conn_str = f"postgres://{pg_user}:{pg_password}@{pg_ip}:{pg_port}/{pg_db}"

        config_dir_location = f'/tmp/{fqdn}'
        rmdir(config_dir_location)

        backend_config_file_location = f"/tmp/{fqdn}.backend.tfvars"
        backend_config_file_content = f'''conn_str = "{pg_backend_conn_str}"'''
        write_into_file(backend_config_file_content,
                        backend_config_file_location)

        vars_file_location = f"/tmp/{fqdn}.tfvars"
        vars_file_content = f"""
        fqdn = "{fqdn}"
        datacenter = "{datacenter}"
        organization = "{organization}"
        terraform_cloud_token = "{terraform_cloud_token}"
        with_vcs_repo = {with_vcs_repo}
        auto_apply = {auto_apply}
        execution_mode = "{execution_mode}"
        deployment_environment = "{deployment_environment}"
        vcs_repo_oauth_token_id = "{vcs_repo_oauth_token_id}"
        tag_names = {json.dumps(tag_names.split(','))}
        """
        write_into_file(vars_file_content, vars_file_location)

        os.environ["PATH"] += os.pathsep + f"{os.path.expanduser('~')}/bin"
        os.environ["TF_REGISTRY_DISCOVERY_RETRY"] = "10"
        os.environ["TF_REGISTRY_CLIENT_TIMEOUT"] = "60"
        os.environ["TF_IN_AUTOMATION"] = "true"

        shutil.copytree(f"{terraform_code_dir}/", f"{config_dir_location}/")
        self.run_command(["terraform", "init", "-input=false", "-reconfigure", "-force-copy",
                          f"-backend-config", backend_config_file_location],
                         cwd=config_dir_location, check=True)
        try:
            subprocess.run(["terraform", "workspace", "select", f"{fqdn}.{deployment_environment}.{datacenter}"],
                           cwd=config_dir_location, check=True)
        except subprocess.CalledProcessError:
            subprocess.run(["terraform", "workspace", "new", f"{fqdn}.{deployment_environment}.{datacenter}"],
                           cwd=config_dir_location, check=True)

        plan_file_location = f"{config_dir_location}/config.plan"

        if deployment_action == "apply":
            self.run_command(
                ["terraform", "plan", "-out", plan_file_location,
                 "-input=false", "-var-file", vars_file_location],
                cwd=config_dir_location, check=True)
            self.run_command(["terraform", "apply", "-input=false", "-auto-approve", plan_file_location],
                             cwd=config_dir_location, check=True)
        elif deployment_action == "destroy":
            self.run_command(["terraform", "plan", "-destroy", "-out", plan_file_location, "-input=false", "-var-file",
                              vars_file_location], cwd=config_dir_location, check=True)
            self.run_command(["terraform", "apply", "-input=false", "-auto-approve", plan_file_location],
                             cwd=config_dir_location, check=True)
            self.run_command(["terraform", "workspace", "select",
                              "default"], cwd=config_dir_location, check=True)
            self.run_command(["terraform", "workspace", "delete", f"{fqdn}.{deployment_environment}.{datacenter}"],
                             cwd=config_dir_location, check=True)

    @retry(wait=wait_random(*wait_random_range), stop=stop_after_attempt(number_of_retries))
    def hcloud_web_solutions(
            self,
            fqdn: str = os.environ.get("RD_OPTION_FQDN"),
            datacenter: str = os.environ.get('RD_OPTION_DATACENTER'),
            organization: str = os.environ.get('RD_OPTION_ORGANIZATION'),
            auto_apply: str = os.environ.get('RD_OPTION_AUTO_APPLY'),
            execution_mode: str = os.environ.get('RD_OPTION_EXECUTION_MODE'),
            deployment_environment: str = os.environ.get(
                'RD_OPTION_DEPLOYMENT_ENVIRONMENT'),
            deployment_action: str = os.environ.get(
                "RD_OPTION_DEPLOYMENT_ACTION"),
            setup_wordpress: str = os.environ.get("RD_OPTION_SETUP_WORDPRESS"),
            wordpress_site_title: str = os.environ.get(
                "RD_OPTION_WORDPRESS_SITE_TITLE"),
            with_wordpress_lifter_lms: str = os.environ.get(
                "RD_OPTION_WITH_WORDPRESS_LIFTER_LMS"),
            wordpress_lms_config_repo: str = os.environ.get(
                "RD_OPTION_WORDPRESS_LMS_CONFIG_REPO"),
            wordpress_lms_config_repo_script_dir: str = os.environ.get(
                "RD_OPTION_WORDPRESS_LMS_CONFIG_REPO_SCRIPT_DIR"),
            wordpress_lms_config_repo_script_name: str = os.environ.get(
                "RD_OPTION_WORDPRESS_LMS_CONFIG_REPO_SCRIPT_NAME"),
            with_lifter_lms_loadtest_course: str = os.environ.get(
                "RD_OPTION_WITH_LIFTER_LMS_LOADTEST_COURSE"),
            with_internal_mariadb: str = os.environ.get(
                "RD_OPTION_WITH_INTERNAL_MARIADB"),
            vault_login_username: str = os.environ.get(
                "RD_OPTION_VAULT_LOGIN_USERNAME"),
            vault_login_password: str = os.environ.get(
                "RD_OPTION_VAULT_LOGIN_PASSWORD"),
            atlas_mongo_public_key: str = os.environ.get(
                "RD_OPTION_ATLAS_MONGO_PUBLIC_KEY"),
            atlas_mongo_private_key: str = os.environ.get(
                "RD_OPTION_ATLAS_MONGO_PRIVATE_KEY"),
            web_server_image: str = os.environ.get(
                "RD_OPTION_WEB_SERVER_IMAGE"),
            mariadb_server_image: str = os.environ.get(
                "RD_OPTION_MARIADB_SERVER_IMAGE"),
            web_server_type: str = os.environ.get("RD_OPTION_WEB_SERVER_TYPE"),
            mariadb_server_type: str = os.environ.get(
                "RD_OPTION_MARIADB_SERVER_TYPE"),
            jira_issue_key: str = os.environ.get("RD_OPTION_JIRA_ISSUE_KEY"),
            terraform_cloud_token: str = os.environ.get(
                "RD_OPTION_TERRAFORM_CLOUD_TOKEN"),
            terraform_code_dir: str = f"{os.path.expanduser('~')}/codebase/terraform/rootmodule/hcloud_web_solutions"

    ):

        fqdn_parts = extract_domain_parts(fqdn)
        sld = f"{fqdn_parts.domain}.{fqdn_parts.suffix}"
        webserver_netdata_fqdn = f"netdata-webserver.{sld}" if fqdn_parts.subdomain == "" else f"netdata-webserver-{fqdn}"
        mariadb_server_netdata_fqdn = f"netdata-dbserver.{sld}" if fqdn_parts.subdomain == "" else f"netdata-dbserver-{fqdn}"
        webserver_fqdn = f"webserver.{sld}" if fqdn_parts.subdomain == "" else f"webserver-{fqdn}"
        mariadb_server_fqdn = f"dbserver.{sld}" if fqdn_parts.subdomain == "" else f"dbserver-{fqdn}"
        project_name = organization
        vault_client = hvac.Client(
            url='https://vault.zadapps.info',

        )
        vault_client.login(
            "/v1/auth/{0}/login/{1}".format("userpass", vault_login_username),
            json={"password": vault_login_password},
        )
        hcloud_token = vault_client.secrets.kv.read_secret_version(
            path=f'tenant/devops/{project_name}/hetzner')['data']['data']['api_token']

        config_dir_location = f'/tmp/{fqdn}'
        rmdir(config_dir_location)

        backend_config_file_location = f"/tmp/{fqdn}.backend.tfvars"
        backend_config_file_content = '''
            organization = "%s"
            workspaces {
              name = "%s-%s-%s"
            }
            ''' % (organization, fqdn.replace('.', '_'), deployment_environment, datacenter)
        write_into_file(backend_config_file_content,
                        backend_config_file_location)

        os.environ["PATH"] += os.pathsep + f"{os.path.expanduser('~')}/bin"

        terraformrc_file_content = '''credentials "app.terraform.io" {
              token = "%s"
            }''' % terraform_cloud_token
        write_into_file(terraformrc_file_content,
                        f"{os.path.expanduser('~')}/.terraformrc")

        os.environ["TF_REGISTRY_DISCOVERY_RETRY"] = "10"
        os.environ["TF_REGISTRY_CLIENT_TIMEOUT"] = "60"
        os.environ["TF_IN_AUTOMATION"] = "true"

        shutil.copytree(f"{terraform_code_dir}/", f"{config_dir_location}/")
        self.run_command(
            ["terraform", "init", "-input=false", "-reconfigure", "-force-copy", "-backend-config",
             backend_config_file_location], cwd=config_dir_location,
            check=True)

        vars_file_location = f"{config_dir_location}/{fqdn}.auto.tfvars"
        vars_file_content = f"""fqdn = "{fqdn}"
            project_name = "{project_name}"
            sld = "{sld}"
            webserver_netdata_fqdn = "{webserver_netdata_fqdn}"
            mariadb_server_netdata_fqdn = "{mariadb_server_netdata_fqdn}"
            webserver_fqdn = "{webserver_fqdn}"
            mariadb_server_fqdn = "{mariadb_server_fqdn}"
            deployment_environment = "{deployment_environment}"
            setup_wordpress = "{setup_wordpress}"
            wordpress_site_title = "{wordpress_site_title}"
            with_wordpress_lifter_lms = "{with_wordpress_lifter_lms}"
            wordpress_lms_config_repo = "{wordpress_lms_config_repo}"
            wordpress_lms_config_repo_script_dir = "{wordpress_lms_config_repo_script_dir}"
            wordpress_lms_config_repo_script_name = "{wordpress_lms_config_repo_script_name}"
            with_lifter_lms_loadtest_course = "{with_lifter_lms_loadtest_course}"
            with_internal_mariadb = "{with_internal_mariadb}"
            hcloud_token = "{hcloud_token}"
            vault_login_username = "{vault_login_username}"
            vault_login_password = "{vault_login_password}"
            atlas_mongo_public_key = "{atlas_mongo_public_key}"
            atlas_mongo_private_key = "{atlas_mongo_private_key}"
            web_server_image = "{web_server_image}"
            mariadb_server_image = "{mariadb_server_image}"
            web_server_type = "{web_server_type}"
            mariadb_server_type = "{mariadb_server_type}"
            jira_issue_key = "{jira_issue_key}"
            """
        write_into_file(vars_file_content, vars_file_location)

        if deployment_action == "apply":
            self.run_command(["terraform", "apply", "-input=false", "-auto-approve"], cwd=config_dir_location,
                             check=True)
            if deployment_environment == "testing":
                deployment_action = "destroy"
                destroy_delay = "3d"
                self.run_command(
                    ["rd", "run", "--project", "main", "--job", "Datacenter/Hetzner/Cloud/Deploy", "--delay",
                     destroy_delay, "--",
                     "-deployment_action", f"{deployment_action}",
                     "-fqdn", f"{fqdn}",
                     "-project_name", f"{project_name}",
                     "-sld", f"{sld}",
                     "-webserver_netdata_fqdn", f"{webserver_netdata_fqdn}",
                     "-mariadb_server_netdata_fqdn", f"{mariadb_server_netdata_fqdn}",
                     "-webserver_fqdn", f"{webserver_fqdn}",
                     "-mariadb_server_fqdn", f"{mariadb_server_fqdn}",
                     "-deployment_environment", f"{deployment_environment}",
                     "-setup_wordpress", f"{setup_wordpress}",
                     "-wordpress_site_title", f"{wordpress_site_title}",
                     "-with_wordpress_lifter_lms", f"{with_wordpress_lifter_lms}",
                     "-wordpress_lms_config_repo", f"{wordpress_lms_config_repo}",
                     "-wordpress_lms_config_repo_script_dir", f"{wordpress_lms_config_repo_script_dir}",
                     "-wordpress_lms_config_repo_script_name", f"{wordpress_lms_config_repo_script_name}",
                     "-with_lifter_lms_loadtest_course", f"{with_lifter_lms_loadtest_course}",
                     "-with_internal_mariadb", f"{with_internal_mariadb}",
                     "-hcloud_token", f"{hcloud_token}",
                     "-vault_login_username", f"{vault_login_username}",
                     "-vault_login_password", f"{vault_login_password}",
                     "-atlas_mongo_public_key", f"{atlas_mongo_public_key}",
                     "-atlas_mongo_private_key", f"{atlas_mongo_private_key}",
                     "-web_server_image", f"{web_server_image}",
                     "-mariadb_server_image", f"{mariadb_server_image}",
                     "-web_server_type", f"{web_server_type}",
                     "-mariadb_server_type", f"{mariadb_server_type}",
                     "-jira_issue_key", f"{jira_issue_key}",
                     "-tag_names", f"{os.environ.get('RD_OPTION_TAG_NAMES')}",
                     "-auto_apply", f"{auto_apply}",
                     "-execution_mode", f"{execution_mode}"],
                    cwd=config_dir_location, check=True)

        elif deployment_action == "destroy":
            self.run_command(["terraform", "destroy", "-input=false", "-auto-approve"], cwd=config_dir_location,
                             check=True)
            pg_creds = vault_client.secrets.kv.read_secret_version(
                path=f'tenant/devops/{project_name}/terraform-pgsql')['data']['data']
            self.terraform_cloud_workspace(pg_user=pg_creds['user'],
                                           pg_password=pg_creds['password'],
                                           pg_ip=pg_creds['ip'],
                                           pg_port=pg_creds['port'],
                                           pg_db=pg_creds['db_name'],
                                           fqdn=fqdn, organization=organization,
                                           datacenter=datacenter,
                                           tag_names=os.environ.get(
                                               'RD_OPTION_TAG_NAMES'),
                                           with_vcs_repo=os.environ.get(
                                               'RD_OPTION_WITH_VCS_REPO'),
                                           execution_mode=execution_mode, deployment_environment=deployment_environment,
                                           deployment_action=deployment_action)

    @retry(wait=wait_random(*wait_random_range), stop=stop_after_attempt(number_of_retries))
    def wordpress_deploy(
            self,
            fqdn: str = os.environ.get("RD_OPTION_FQDN"),
            datacenter: str = os.environ.get('RD_OPTION_DATACENTER'),
            organization: str = os.environ.get('RD_OPTION_ORGANIZATION'),
            auto_apply: str = os.environ.get('RD_OPTION_AUTO_APPLY'),
            execution_mode: str = os.environ.get('RD_OPTION_EXECUTION_MODE'),
            deployment_environment: str = os.environ.get(
                'RD_OPTION_DEPLOYMENT_ENVIRONMENT'),
            deployment_action: str = os.environ.get(
                "RD_OPTION_DEPLOYMENT_ACTION"),
            provision_only: str = os.environ.get("RD_OPTION_PROVISION_ONLY"),
            vault_wordpress_server_ssh_path: str = os.environ.get(
                "RD_OPTION_VAULT_WORDPRESS_SERVER_SSH_PATH"),
            wordpress_site_title: str = os.environ.get(
                "RD_OPTION_WORDPRESS_SITE_TITLE"),
            with_wordpress_lifter_lms: str = os.environ.get(
                "RD_OPTION_WITH_WORDPRESS_LIFTER_LMS"),
            wordpress_lms_config_repo: str = os.environ.get(
                "RD_OPTION_WORDPRESS_LMS_CONFIG_REPO"),
            wordpress_lms_config_repo_script_dir: str = os.environ.get(
                "RD_OPTION_WORDPRESS_LMS_CONFIG_REPO_SCRIPT_DIR"),
            wordpress_lms_config_repo_script_name: str = os.environ.get(
                "RD_OPTION_WORDPRESS_LMS_CONFIG_REPO_SCRIPT_NAME"),
            with_lifter_lms_loadtest_course: str = os.environ.get(
                "RD_OPTION_WITH_LIFTER_LMS_LOADTEST_COURSE"),
            with_internal_mariadb: str = os.environ.get(
                "RD_OPTION_WITH_INTERNAL_MARIADB"),
            vault_login_username: str = os.environ.get(
                "RD_OPTION_VAULT_LOGIN_USERNAME"),
            vault_login_password: str = os.environ.get(
                "RD_OPTION_VAULT_LOGIN_PASSWORD"),
            atlas_mongo_public_key: str = os.environ.get(
                "RD_OPTION_ATLAS_MONGO_PUBLIC_KEY"),
            atlas_mongo_private_key: str = os.environ.get(
                "RD_OPTION_ATLAS_MONGO_PRIVATE_KEY"),
            web_server_image: str = os.environ.get(
                "RD_OPTION_WEB_SERVER_IMAGE"),
            mariadb_server_image: str = os.environ.get(
                "RD_OPTION_MARIADB_SERVER_IMAGE"),
            web_server_type: str = os.environ.get("RD_OPTION_WEB_SERVER_TYPE"),
            mariadb_server_type: str = os.environ.get(
                "RD_OPTION_MARIADB_SERVER_TYPE"),
            jira_issue_key: str = os.environ.get("RD_OPTION_JIRA_ISSUE_KEY"),
            terraform_cloud_token: str = os.environ.get(
                "RD_OPTION_TERRAFORM_CLOUD_TOKEN"),
            terraform_code_dir: str = f"{os.path.expanduser('~')}/codebase/terraform/rootmodule/wordpress_deploy"

    ):

        fqdn_parts = extract_domain_parts(fqdn)
        sld = f"{fqdn_parts.domain}.{fqdn_parts.suffix}"
        webserver_netdata_fqdn = f"netdata-webserver.{sld}" if fqdn_parts.subdomain == "" else f"netdata-webserver-{fqdn}"
        mariadb_server_netdata_fqdn = f"netdata-dbserver.{sld}" if fqdn_parts.subdomain == "" else f"netdata-dbserver-{fqdn}"
        webserver_fqdn = f"webserver.{sld}" if fqdn_parts.subdomain == "" else f"webserver-{fqdn}"
        mariadb_server_fqdn = f"dbserver.{sld}" if fqdn_parts.subdomain == "" else f"dbserver-{fqdn}"
        project_name = organization
        vault_client = hvac.Client(
            url='https://vault.zadapps.info',

        )
        vault_client.login(
            "/v1/auth/{0}/login/{1}".format("userpass", vault_login_username),
            json={"password": vault_login_password},
        )
        hcloud_token = vault_client.secrets.kv.read_secret_version(
            path=f'tenant/devops/{project_name}/hetzner')['data']['data']['api_token']

        config_dir_location = f'/tmp/{fqdn}'
        rmdir(config_dir_location)

        backend_config_file_location = f"/tmp/{fqdn}.backend.tfvars"
        backend_config_file_content = '''
            organization = "%s"
            workspaces {
              name = "%s-%s-%s"
            }
            ''' % (organization, fqdn.replace('.', '_'), deployment_environment, datacenter)
        write_into_file(backend_config_file_content,
                        backend_config_file_location)

        os.environ["PATH"] += os.pathsep + f"{os.path.expanduser('~')}/bin"

        terraformrc_file_content = '''credentials "app.terraform.io" {
              token = "%s"
            }''' % terraform_cloud_token
        write_into_file(terraformrc_file_content,
                        f"{os.path.expanduser('~')}/.terraformrc")

        os.environ["TF_REGISTRY_DISCOVERY_RETRY"] = "10"
        os.environ["TF_REGISTRY_CLIENT_TIMEOUT"] = "60"
        os.environ["TF_IN_AUTOMATION"] = "true"

        shutil.copytree(f"{terraform_code_dir}/", f"{config_dir_location}/")
        self.run_command(
            ["terraform", "init", "-input=false", "-reconfigure", "-force-copy", "-backend-config",
             backend_config_file_location], cwd=config_dir_location,
            check=True)

        vars_file_location = f"{config_dir_location}/{fqdn}.auto.tfvars"
        vars_file_content = f"""fqdn = "{fqdn}"
            project_name = "{project_name}"
            sld = "{sld}"
            webserver_netdata_fqdn = "{webserver_netdata_fqdn}"
            mariadb_server_netdata_fqdn = "{mariadb_server_netdata_fqdn}"
            webserver_fqdn = "{webserver_fqdn}"
            mariadb_server_fqdn = "{mariadb_server_fqdn}"
            deployment_environment = "{deployment_environment}"
            provision_only = "{provision_only}"
            vault_wordpress_server_ssh_path = "{vault_wordpress_server_ssh_path}"
            wordpress_site_title = "{wordpress_site_title}"
            with_wordpress_lifter_lms = "{with_wordpress_lifter_lms}"
            wordpress_lms_config_repo = "{wordpress_lms_config_repo}"
            wordpress_lms_config_repo_script_dir = "{wordpress_lms_config_repo_script_dir}"
            wordpress_lms_config_repo_script_name = "{wordpress_lms_config_repo_script_name}"
            with_lifter_lms_loadtest_course = "{with_lifter_lms_loadtest_course}"
            with_internal_mariadb = "{with_internal_mariadb}"
            hcloud_token = "{hcloud_token}"
            vault_login_username = "{vault_login_username}"
            vault_login_password = "{vault_login_password}"
            atlas_mongo_public_key = "{atlas_mongo_public_key}"
            atlas_mongo_private_key = "{atlas_mongo_private_key}"
            web_server_image = "{web_server_image}"
            mariadb_server_image = "{mariadb_server_image}"
            web_server_type = "{web_server_type}"
            mariadb_server_type = "{mariadb_server_type}"
            jira_issue_key = "{jira_issue_key}"
            """
        write_into_file(vars_file_content, vars_file_location)

        if deployment_action == "apply":
            self.run_command(["terraform", "apply", "-input=false", "-auto-approve"], cwd=config_dir_location,
                             check=True)
            if deployment_environment == "testing":
                deployment_action = "destroy"
                destroy_delay = "3d"
                self.run_command(
                    ["rd", "run", "--project", "main", "--job", "Datacenter/Hetzner/Cloud/Deploy", "--delay",
                     destroy_delay, "--",
                     "-deployment_action", f"{deployment_action}",
                     "-fqdn", f"{fqdn}",
                     "-project_name", f"{project_name}",
                     "-sld", f"{sld}",
                     "-webserver_netdata_fqdn", f"{webserver_netdata_fqdn}",
                     "-mariadb_server_netdata_fqdn", f"{mariadb_server_netdata_fqdn}",
                     "-webserver_fqdn", f"{webserver_fqdn}",
                     "-mariadb_server_fqdn", f"{mariadb_server_fqdn}",
                     "-deployment_environment", f"{deployment_environment}",
                     "-provision_only", f"{provision_only}",
                     "-vault_wordpress_server_ssh_path", f"{vault_wordpress_server_ssh_path}",
                     "-wordpress_site_title", f"{wordpress_site_title}",
                     "-with_wordpress_lifter_lms", f"{with_wordpress_lifter_lms}",
                     "-wordpress_lms_config_repo", f"{wordpress_lms_config_repo}",
                     "-wordpress_lms_config_repo_script_dir", f"{wordpress_lms_config_repo_script_dir}",
                     "-wordpress_lms_config_repo_script_name", f"{wordpress_lms_config_repo_script_name}",
                     "-with_lifter_lms_loadtest_course", f"{with_lifter_lms_loadtest_course}",
                     "-with_internal_mariadb", f"{with_internal_mariadb}",
                     "-hcloud_token", f"{hcloud_token}",
                     "-vault_login_username", f"{vault_login_username}",
                     "-vault_login_password", f"{vault_login_password}",
                     "-atlas_mongo_public_key", f"{atlas_mongo_public_key}",
                     "-atlas_mongo_private_key", f"{atlas_mongo_private_key}",
                     "-web_server_image", f"{web_server_image}",
                     "-mariadb_server_image", f"{mariadb_server_image}",
                     "-web_server_type", f"{web_server_type}",
                     "-mariadb_server_type", f"{mariadb_server_type}",
                     "-jira_issue_key", f"{jira_issue_key}",
                     "-tag_names", f"{os.environ.get('RD_OPTION_TAG_NAMES')}",
                     "-auto_apply", f"{auto_apply}",
                     "-execution_mode", f"{execution_mode}"],
                    cwd=config_dir_location, check=True)

        elif deployment_action == "destroy":
            self.run_command(["terraform", "destroy", "-input=false", "-auto-approve"], cwd=config_dir_location,
                             check=True)
            pg_creds = vault_client.secrets.kv.read_secret_version(
                path=f'tenant/devops/{project_name}/terraform-pgsql')['data']['data']
            self.terraform_cloud_workspace(pg_user=pg_creds['user'],
                                           pg_password=pg_creds['password'],
                                           pg_ip=pg_creds['ip'],
                                           pg_port=pg_creds['port'],
                                           pg_db=pg_creds['db_name'],
                                           fqdn=fqdn, organization=organization,
                                           datacenter=datacenter,
                                           tag_names=os.environ.get(
                                               'RD_OPTION_TAG_NAMES'),
                                           with_vcs_repo=os.environ.get(
                                               'RD_OPTION_WITH_VCS_REPO'),
                                           execution_mode=execution_mode, deployment_environment=deployment_environment,
                                           deployment_action=deployment_action)

    def nextjs_build(
            self,
            pg_user: str = os.environ.get(
                'RD_OPTION_TERRAFORM_PG_BACKEND_USER'),
            pg_password: str = os.environ.get(
                'RD_OPTION_TERRAFORM_PG_BACKEND_PASSWORD'),
            pg_ip: str = os.environ.get('RD_OPTION_TERRAFORM_PG_BACKEND_IP'),
            pg_port: str = os.environ.get(
                'RD_OPTION_TERRAFORM_PG_BACKEND_PORT'),
            pg_db: str = os.environ.get('RD_OPTION_TERRAFORM_PG_BACKEND_DB'),
            fqdn: str = os.environ.get("RD_OPTION_FQDN"),
            organization: str = os.environ.get('RD_OPTION_ORGANIZATION'),
            deployment_action: str = os.environ.get(
                'RD_OPTION_DEPLOYMENT_ACTION'),
            deployment_environment: str = os.environ.get(
                'RD_OPTION_DEPLOYMENT_ENVIRONMENT'),
            git_domain: str = os.environ.get('RD_OPTION_GIT_DOMAIN'),
            git_reponame: str = os.environ.get('RD_OPTION_GIT_REPONAME'),
            git_branch: str = os.environ.get('RD_OPTION_GIT_BRANCH'),
            workspace_name: str = os.environ.get('RD_OPTION_WORKSPACE_NAME'),
            app_code_dir: str = os.environ.get('RD_OPTION_APP_CODE_DIR'),
            vault_login_username: str = os.environ.get(
                'RD_OPTION_VAULT_LOGIN_USERNAME'),
            vault_login_password: str = os.environ.get(
                'RD_OPTION_VAULT_LOGIN_PASSWORD'),
    ):
        pg_backend_conn_str = f"postgres://{pg_user}:{pg_password}@{pg_ip}:{pg_port}/{pg_db}"

        config_dir_location = f'/tmp/{fqdn}.{deployment_environment}.build'
        rmdir(config_dir_location)
        vault_client = hvac.Client(
            url='https://vault.zadapps.info',
        )
        vault_client.login(
            "/v1/auth/{0}/login/{1}".format("userpass", vault_login_username),
            json={"password": vault_login_password},
        )
        gitlab_deploy_token = vault_client.secrets.kv.read_secret_version(
            path=f'tenant/devops/zadgroup/gitlab-deploy-token')['data']['data']['token']
        rundeck_codebase_dir = self.clone_rundeck_codebase(gitlab_deploy_token)
        terraform_code_dir = f"{rundeck_codebase_dir}/terraform/rootmodule/nextjs_build"

        backend_config_file_location = f"/tmp/{fqdn}.{deployment_environment}.build.backend.tfvars"
        backend_config_file_content = f'''conn_str = "{pg_backend_conn_str}"'''
        write_into_file(backend_config_file_content,
                        backend_config_file_location)

        fqdn_parts = extract_domain_parts(fqdn)
        sld = f"{fqdn_parts.domain}.{fqdn_parts.suffix}"
        vars_file_location = f"/tmp/{fqdn}.{deployment_environment}.build.tfvars"
        vars_file_content = f"""
        fqdn = "{fqdn}"
        sld = "{sld}"
        project_name = "{organization}"
        git_domain = "{git_domain}"
        git_reponame = "{git_reponame}"
        git_branch = "{git_branch}"
        workspace_name = "{workspace_name}"
        app_code_dir = "{app_code_dir}"
        vault_login_username = "{vault_login_username}"
        vault_login_password = "{vault_login_password}"
        """
        write_into_file(vars_file_content, vars_file_location)

        prepare_terraform_environment(config_dir_location)
        os.environ["TF_DATA_DIR"] = config_dir_location
        self.run_command(["terraform", "init", "-input=false", "-reconfigure", "-force-copy",
                          f"-backend-config", backend_config_file_location],
                         cwd=terraform_code_dir, check=True)
        try:
            subprocess.run(["terraform", "workspace", "select", f"{fqdn}.build"],
                           cwd=terraform_code_dir, check=True)
        except subprocess.CalledProcessError:
            subprocess.run(["terraform", "workspace", "new", "-lock=false", f"{fqdn}.build"],
                           cwd=terraform_code_dir, check=True)

        plan_file_location = f"./config.plan"

        if deployment_action == "apply":
            self.run_command(
                ["terraform", "plan", "-out", plan_file_location,
                 "-input=false", "-var-file", vars_file_location],
                cwd=terraform_code_dir, check=True)
            self.run_command(["terraform", "apply", "-input=false", "-auto-approve", plan_file_location],
                             cwd=terraform_code_dir, check=True)
        elif deployment_action == "destroy":
            self.run_command(["terraform", "plan", "-destroy", "-out", plan_file_location, "-input=false", "-var-file",
                              vars_file_location], cwd=terraform_code_dir, check=True)
            self.run_command(["terraform", "apply", "-input=false", "-auto-approve", plan_file_location],
                             cwd=terraform_code_dir, check=True)
            self.run_command(["terraform", "workspace", "select",
                              "default"], cwd=terraform_code_dir, check=True)
            self.run_command(["terraform", "workspace", "delete", f"{fqdn}.build"],
                             cwd=terraform_code_dir, check=True)
        rmdir(rundeck_codebase_dir)

    @retry(wait=wait_random(*wait_random_range), stop=stop_after_attempt(number_of_retries))
    def nextjs_deploy(
            self,
            fqdn: str = os.environ.get("RD_OPTION_FQDN"),
            git_branch: str = os.environ.get("RD_OPTION_GIT_BRANCH"),
            datacenter: str = os.environ.get('RD_OPTION_DATACENTER'),
            organization: str = os.environ.get('RD_OPTION_ORGANIZATION'),
            execution_mode: str = os.environ.get('RD_OPTION_EXECUTION_MODE'),
            deployment_environment: str = os.environ.get(
                'RD_OPTION_DEPLOYMENT_ENVIRONMENT'),
            deployment_action: str = os.environ.get(
                "RD_OPTION_DEPLOYMENT_ACTION"),
            vault_login_username: str = os.environ.get(
                "RD_OPTION_VAULT_LOGIN_USERNAME"),
            vault_login_password: str = os.environ.get(
                "RD_OPTION_VAULT_LOGIN_PASSWORD"),
            jira_issue_key: str = os.environ.get("RD_OPTION_JIRA_ISSUE_KEY"),
            terraform_cloud_token: str = os.environ.get(
                "RD_OPTION_TERRAFORM_CLOUD_TOKEN"),
    ):

        fqdn_parts = extract_domain_parts(fqdn)
        sld = f"{fqdn_parts.domain}.{fqdn_parts.suffix}"
        project_name = organization
        vault_client = hvac.Client(
            url='https://vault.zadapps.info',
        )
        vault_client.login(
            "/v1/auth/{0}/login/{1}".format("userpass", vault_login_username),
            json={"password": vault_login_password},
        )

        config_dir_location = f'/tmp/{fqdn}'
        rmdir(config_dir_location)
        gitlab_deploy_token = vault_client.secrets.kv.read_secret_version(
            path=f'tenant/devops/zadgroup/gitlab-deploy-token')['data']['data']['token']
        rundeck_codebase_dir = self.clone_rundeck_codebase(gitlab_deploy_token)
        terraform_code_dir = f"{rundeck_codebase_dir}/terraform/rootmodule/nextjs_deploy"

        backend_config_file_location = f"/tmp/{fqdn}.backend.tfvars"
        backend_config_file_content = '''
            organization = "%s"
            workspaces {
              name = "%s-%s-%s"
            }
            ''' % (organization, fqdn.replace('.', '_'), deployment_environment, datacenter)
        write_into_file(backend_config_file_content,
                        backend_config_file_location)

        os.environ["PATH"] += os.pathsep + f"{os.path.expanduser('~')}/bin"

        terraformrc_file_content = '''credentials "app.terraform.io" {
              token = "%s"
            }''' % terraform_cloud_token
        write_into_file(terraformrc_file_content,
                        f"{os.path.expanduser('~')}/.terraformrc")

        prepare_terraform_environment(config_dir_location)
        self.run_command(
            ["terraform", "init", "-input=false", "-reconfigure", "-force-copy", "-backend-config",
             backend_config_file_location], cwd=terraform_code_dir,
            check=True)

        vars_file_location = f"/tmp/{fqdn}.auto.tfvars"
        vars_file_content = f"""fqdn = "{fqdn}"
            git_branch = "{git_branch}"
            project_name = "{project_name}"
            sld = "{sld}"
            deployment_environment = "{deployment_environment}"
            vault_login_username = "{vault_login_username}"
            vault_login_password = "{vault_login_password}"
            jira_issue_key = "{jira_issue_key}"
            """
        write_into_file(vars_file_content, vars_file_location)

        if deployment_action == "apply":
            self.run_command(["terraform", "apply", "-input=false", "-auto-approve", "-var-file", vars_file_location],
                             cwd=terraform_code_dir,
                             check=True)
        elif deployment_action == "destroy":
            self.run_command(["terraform", "destroy", "-input=false", "-auto-approve", "-var-file", vars_file_location],
                             cwd=terraform_code_dir,
                             check=True)
            pg_creds = vault_client.secrets.kv.read_secret_version(
                path=f'tenant/devops/{project_name}/terraform-pgsql')['data']['data']
            self.terraform_cloud_workspace(pg_user=pg_creds['user'],
                                           pg_password=pg_creds['password'],
                                           pg_ip=pg_creds['ip'],
                                           pg_port=pg_creds['port'],
                                           pg_db=pg_creds['db_name'],
                                           fqdn=fqdn, organization=organization,
                                           datacenter=datacenter,
                                           tag_names=os.environ.get(
                                               'RD_OPTION_TAG_NAMES'),
                                           with_vcs_repo=os.environ.get(
                                               'RD_OPTION_WITH_VCS_REPO'),
                                           execution_mode=execution_mode, deployment_environment=deployment_environment,
                                           deployment_action=deployment_action)

        rmdir(rundeck_codebase_dir)
