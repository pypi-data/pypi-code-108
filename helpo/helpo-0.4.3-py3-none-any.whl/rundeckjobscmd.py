import os

import typer

from helpo.rundeckjobs import RundeckJobs

app = typer.Typer()


@app.command()
def search_uptimerobot(
        deployment_action: str = os.environ.get('RD_OPTION_DEPLOYMENT_ACTION'),
        uptimerobot_api_key: str = os.environ.get(
            "RD_OPTION_UPTIMEROBOT_API_KEY"),
        fqdn: str = os.environ.get("RD_OPTION_FQDN"),
        force_apply: bool = bool(os.environ.get('RD_OPTION_FORCE_APPLY'))
):
    rundeck_jobs = RundeckJobs()
    rundeck_jobs.search_uptimerobot(
        deployment_action, uptimerobot_api_key, fqdn, force_apply
    )


@app.command()
def terraform_cloud_workspace(
        pg_user: str = os.environ.get('RD_OPTION_TERRAFORM_PG_BACKEND_USER'),
        pg_password: str = os.environ.get(
            'RD_OPTION_TERRAFORM_PG_BACKEND_PASSWORD'),
        pg_ip: str = os.environ.get('RD_OPTION_TERRAFORM_PG_BACKEND_IP'),
        pg_port: str = os.environ.get('RD_OPTION_TERRAFORM_PG_BACKEND_PORT'),
        pg_db: str = os.environ.get('RD_OPTION_TERRAFORM_PG_BACKEND_DB'),
        deployment_action: str = os.environ.get("RD_OPTION_DEPLOYMENT_ACTION"),
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
        terraform_code_dir: str = "/home/rundeck/codebase/terraform/rootmodule/terraform_cloud_workspace",
):
    rundeck_jobs = RundeckJobs()
    rundeck_jobs.terraform_cloud_workspace(
        pg_user, pg_password, pg_ip, pg_port, pg_db, deployment_action, fqdn, datacenter, organization,
        terraform_cloud_token, with_vcs_repo, auto_apply, execution_mode, deployment_environment,
        vcs_repo_oauth_token_id, tag_names, terraform_code_dir
    )


@app.command()
def hcloud_web_solutions(
        fqdn: str = os.environ.get("RD_OPTION_FQDN"),
        datacenter: str = os.environ.get('RD_OPTION_DATACENTER'),
        organization: str = os.environ.get('RD_OPTION_ORGANIZATION'),
        auto_apply: str = os.environ.get('RD_OPTION_AUTO_APPLY'),
        execution_mode: str = os.environ.get('RD_OPTION_EXECUTION_MODE'),
        deployment_environment: str = os.environ.get(
            'RD_OPTION_DEPLOYMENT_ENVIRONMENT'),
        deployment_action: str = os.environ.get("RD_OPTION_DEPLOYMENT_ACTION"),
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
        web_server_image: str = os.environ.get("RD_OPTION_WEB_SERVER_IMAGE"),
        mariadb_server_image: str = os.environ.get(
            "RD_OPTION_MARIADB_SERVER_IMAGE"),
        web_server_type: str = os.environ.get("RD_OPTION_WEB_SERVER_TYPE"),
        mariadb_server_type: str = os.environ.get(
            "RD_OPTION_MARIADB_SERVER_TYPE"),
        jira_issue_key: str = os.environ.get("RD_OPTION_JIRA_ISSUE_KEY"),
        terraform_cloud_token: str = os.environ.get(
            "RD_OPTION_TERRAFORM_CLOUD_TOKEN"),
        terraform_code_dir: str = f"/home/rundeck/codebase/terraform/rootmodule/hcloud_web_solutions"

):
    rundeck_jobs = RundeckJobs()
    rundeck_jobs.hcloud_web_solutions(fqdn, datacenter, organization, auto_apply, execution_mode,
                                      deployment_environment, deployment_action, setup_wordpress, wordpress_site_title,
                                      with_wordpress_lifter_lms, wordpress_lms_config_repo,
                                      wordpress_lms_config_repo_script_dir, wordpress_lms_config_repo_script_name,
                                      with_lifter_lms_loadtest_course, with_internal_mariadb, vault_login_username,
                                      vault_login_password, atlas_mongo_public_key, atlas_mongo_private_key,
                                      web_server_image, mariadb_server_image, web_server_type, mariadb_server_type,
                                      jira_issue_key, terraform_cloud_token, terraform_code_dir)


@app.command()
def wordpress_deploy(
        fqdn: str = os.environ.get("RD_OPTION_FQDN"),
        datacenter: str = os.environ.get('RD_OPTION_DATACENTER'),
        organization: str = os.environ.get('RD_OPTION_ORGANIZATION'),
        auto_apply: str = os.environ.get('RD_OPTION_AUTO_APPLY'),
        execution_mode: str = os.environ.get('RD_OPTION_EXECUTION_MODE'),
        deployment_environment: str = os.environ.get(
            'RD_OPTION_DEPLOYMENT_ENVIRONMENT'),
        deployment_action: str = os.environ.get("RD_OPTION_DEPLOYMENT_ACTION"),
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
        web_server_image: str = os.environ.get("RD_OPTION_WEB_SERVER_IMAGE"),
        mariadb_server_image: str = os.environ.get(
            "RD_OPTION_MARIADB_SERVER_IMAGE"),
        web_server_type: str = os.environ.get("RD_OPTION_WEB_SERVER_TYPE"),
        mariadb_server_type: str = os.environ.get(
            "RD_OPTION_MARIADB_SERVER_TYPE"),
        jira_issue_key: str = os.environ.get("RD_OPTION_JIRA_ISSUE_KEY"),
        terraform_cloud_token: str = os.environ.get(
            "RD_OPTION_TERRAFORM_CLOUD_TOKEN"),
        terraform_code_dir: str = f"/home/rundeck/codebase/terraform/rootmodule/wordpress_deploy"

):
    rundeck_jobs = RundeckJobs()
    rundeck_jobs.wordpress_deploy(fqdn, datacenter, organization, auto_apply, execution_mode,
                                  deployment_environment, deployment_action, provision_only,
                                  vault_wordpress_server_ssh_path, wordpress_site_title,
                                  with_wordpress_lifter_lms, wordpress_lms_config_repo,
                                  wordpress_lms_config_repo_script_dir, wordpress_lms_config_repo_script_name,
                                  with_lifter_lms_loadtest_course, with_internal_mariadb, vault_login_username,
                                  vault_login_password, atlas_mongo_public_key, atlas_mongo_private_key,
                                  web_server_image, mariadb_server_image, web_server_type, mariadb_server_type,
                                  jira_issue_key, terraform_cloud_token, terraform_code_dir)


@app.command()
def nextjs_build(
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
    rundeck_jobs = RundeckJobs()
    rundeck_jobs.nextjs_build(pg_user, pg_password, pg_ip, pg_port, pg_db, fqdn, organization, deployment_action,
                              deployment_environment, git_domain, git_reponame, git_branch, workspace_name,
                              app_code_dir, vault_login_username,
                              vault_login_password)


@app.command()
def nextjs_deploy(
        fqdn: str = os.environ.get("RD_OPTION_FQDN"),
        git_branch: str = os.environ.get("RD_OPTION_GIT_BRANCH"),
        datacenter: str = os.environ.get('RD_OPTION_DATACENTER'),
        organization: str = os.environ.get('RD_OPTION_ORGANIZATION'),
        auto_apply: str = os.environ.get('RD_OPTION_AUTO_APPLY'),
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
    rundeck_jobs = RundeckJobs()
    rundeck_jobs.nextjs_deploy(fqdn, git_branch, datacenter, organization, execution_mode, deployment_environment,
                               deployment_action, vault_login_username, vault_login_password, jira_issue_key,
                               terraform_cloud_token)


if __name__ == "__main__":
    app()
