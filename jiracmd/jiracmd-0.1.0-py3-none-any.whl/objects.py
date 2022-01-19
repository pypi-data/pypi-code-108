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
        self.updated = self._to_datetime(
                self.fields['updated'],
                return_string=True)

    def _table_dict(self):
        table_dict = {
            "key": self.key,
            "type": self.issue_type,
            "updated": self.updated,
            "summary": self.summary
        }
        return table_dict

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
    issueKey: str = None

    def __post_init__(self):
        self.issueKey = jira.get_issue(self.issueId)['key']

    def __repr__(self):
        date_started = self._to_datetime(self.started, return_string=True)
        return f"Worklog(id={self.id}, timeSpent={self.timeSpent}, started={started})"

    def _table_dict(self):
        table_dict = {
            "id": self.id,
            "issueKey": self.issueKey,
            "started": self._to_datetime(
                self.started,
                return_string=True
            ),
            "timeSpent": self.timeSpent
        }
        return table_dict

