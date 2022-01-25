import sys

import typer
from loguru import logger

from helpo.jira import Jira

app = typer.Typer()


@logger.catch
@app.command()
def create_project(key: str,
                   name: str,
                   description: str,
                   lead_account_id: str,
                   project_template_key: str,
                   assignee_type: str,
                   project_type_key: str,
                   jira_username: str = '',
                   jira_token: str = ''):
    jira_api = Jira(jira_username, jira_token)
    specs = {
        "key": key,
        "name": name,
        "description": description,
        "leadAccountId": lead_account_id,
        "projectTemplateKey": project_template_key,
        "assigneeType": assignee_type,
        "projectTypeKey": project_type_key
    }

    project_details = jira_api.create_project(specs)
    typer.echo(project_details)


@logger.catch
@app.command()
def delete_project(key: str,
                   jira_username: str = '',
                   jira_token: str = ''):
    jira_api = Jira(jira_username, jira_token)
    jira_api.delete_project(key)
    typer.echo('Success')


@logger.catch
@app.command()
def create_project_from_template(project_id: str, key: str,
                                 name: str, lead: str,
                                 jira_username: str = '',
                                 jira_token: str = ''):
    jira_api = Jira(jira_username, jira_token)
    project_info = jira_api.create_project_from_template(
        project_id, key, name, lead)
    if project_info:
        typer.echo(project_info)
    else:
        sys.exit(1)


if __name__ == "__main__":
    app()
