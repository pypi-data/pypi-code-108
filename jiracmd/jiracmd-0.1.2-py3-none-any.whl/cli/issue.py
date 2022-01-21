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
@click.option('-o', '--output', default="yaml")
@click.option('-c', '--changelog', is_flag=True, default=False)
@click.option('--short', is_flag=True, default=False)
def issue_get(issue, output, changelog, short):
    get_params = []
    if changelog:
        get_params.append("expand=changelog") 
    response = jira.get_issue(issue, params=get_params)
    print(Issue(**response).get_outputs(short=short).get(output))

@click.command(name="list")
@click.option('-a', '--assignee', default=None)
@click.option('-t', '--issue-type', default=None)
@click.option('-s', '--sort-by', default="updated")
def issue_list(assignee, issue_type, sort_by):
    type_query = ""
    query_assignee = assignee or "currentuser()"
    if issue_type:
        type_query = f"and issueType={issue_type}"
    jql = f"assignee={query_assignee} {type_query}"
    response = jira._get(f'search?maxResults=100&jql={jql}')
    issues = [Issue(**i) for i in response.json()['issues']]
    issues_table = [issue.to_short_dict(remove_items="description") for issue in issues]
    output_table(issues_table, sort_by=sort_by)

issue_cli.add_command(issue_get)
issue_cli.add_command(issue_list)

