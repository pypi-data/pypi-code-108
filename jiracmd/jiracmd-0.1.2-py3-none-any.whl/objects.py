import json
from dataclasses import dataclass
from jiracmd.jira import JiraObject
from jiracmd.auth import jira

@dataclass
class Issue(JiraObject):
    id: str
    self: str
    expand: str
    key: str
    fields: dict
    summary: str = None
    issue_type: str = None
    updated: str = None

    def __post_init__(self):
        self.summary = self.fields['summary']
        self.issue_type = self.fields['issuetype']['name']
        self.updated = self.datetime_field(
                self.fields['updated'],
                return_string=True)
        worklog = self.fields.pop('worklog', None)

    def to_short_dict(self, remove_items=[]):
        table_dict = {
            "key": self.key,
            "type": self.issue_type,
            "assignee": self.fields['assignee']['displayName'],
            "updated": self.updated,
            "summary": self.summary,
            "description": self.fields['description']
        }
        filtered_dict = {
            k:v for (k,v) in table_dict.items()
            if k not in remove_items
        }
        return filtered_dict

@dataclass
class Worklog(JiraObject):
    id: str
    self: str
    author: dict
    updateAuthor: dict
    timeSpent: str 
    timeSpentSeconds: int
    issueId: str
    created: str
    updated: str
    started: str
    issue_key: str = None

    def __post_init__(self):
        if not self.issue_key:
            self.issue_key = jira.get_issue(self.issueId)['key']

    def __repr__(self):
        date_started = self.datetime_field(self.started, return_string=True)
        return f"Worklog(id={self.id}, timeSpent={self.timeSpent}, started={date_started})"

    def to_short_dict(self):
        table_dict = {
            "id": self.id,
            "author": self.author['displayName'],
            "issueKey": self.issue_key,
            "started": self.datetime_field(
                self.started,
                return_string=True
            ),
            "timeSpent": self.timeSpent
        }
        return table_dict

