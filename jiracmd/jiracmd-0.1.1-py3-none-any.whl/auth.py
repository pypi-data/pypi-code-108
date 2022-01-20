import os
from jiracmd.jira import JiraAPIClient

jira = JiraAPIClient(
    os.getenv('JIRA_SERVER'),
    os.getenv('JIRA_USERNAME'),
    os.getenv('JIRA_API_TOKEN')
)
