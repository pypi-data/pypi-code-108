import json
import click
from jiracmd.auth import jira
from datetime import datetime
from jiracmd.objects import Issue
from jiracmd.utils import output_table


@click.group(name="issue")
def issue_cli():
    pass

@click.command(name="get")
@click.option('-i', '--issue', required=True)
def issue_get(issue):
    response = jira._get(f'issue/{issue}?expand=changelog')
    print(json.dumps(response.json(), indent=2))

@click.command(name="list")
@click.option('--me', is_flag=True, default=True)
@click.option('-t', '--issue-type', default=None)
@click.option('-s', '--sort-by', default="updated")
def issue_list(me, issue_type, sort_by):
    type_query = ""
    if issue_type:
        type_query = f"and issueType={issue_type}"
    jql = f"assignee=currentuser() {type_query}"
    response = jira._get(f'search?maxResults=100&jql={jql}')
    issues = [Issue(**i) for i in response.json()['issues']]
    issues_table = [issue._table_dict() for issue in issues]
    output_table(issues_table, sort_by=sort_by)

issue_cli.add_command(issue_get)
issue_cli.add_command(issue_list)



# jira/rest/api/2/search?jql=assignee=currentuser()
