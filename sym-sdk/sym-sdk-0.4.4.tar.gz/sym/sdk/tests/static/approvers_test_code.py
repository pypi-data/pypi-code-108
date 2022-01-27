###
### Begin pure Slack samples
###

SIMPLE_SLACK_CHANNEL_CODE = """
from sym.sdk.annotations import reducer
from sym.sdk.integrations import slack

@reducer
def get_approvers(event):
    return slack.channel('#managers')
"""

SIMPLE_SLACK_USER_CODE = """
from sym.sdk.annotations import reducer
from sym.sdk.integrations import slack

@reducer
def get_approvers(event):
    return slack.user('@David Ruiz')
"""

SIMPLE_SLACK_USER_ID_CODE = """
from sym.sdk.annotations import reducer
from sym.sdk.integrations import slack

@reducer
def get_approvers(event):
    return slack.user(event.payload.user)
"""

SIMPLE_SLACK_GROUP_CODE = """
from sym.sdk.annotations import reducer
from sym.sdk.integrations import slack

@reducer
def get_approvers(event):
    return slack.group(['@David Ruiz', '@Jon Demo'])
"""

SLACK_GROUP_WITH_USERS_CODE = """
from sym.sdk.annotations import reducer
from sym.sdk.integrations import slack, pagerduty

@reducer
def get_approvers(event):
    return slack.group([event.user, event.user])
"""

SIMPLE_ALLOW_SELF_FALSE_CODE = """
import datetime
from sym.sdk.annotations import reducer
from sym.sdk.integrations import slack
@reducer
def get_approvers(event):
    return slack.channel("#break-glass", allow_self=False)
"""

SIMPLE_ALLOW_SELF_TRUE_CODE = """
import datetime
from sym.sdk.annotations import reducer
from sym.sdk.integrations import slack
@reducer
def get_approvers(event):
    return slack.channel("#break-glass", allow_self=True)
"""

GET_APPROVERS_USING_EVENT_CODE = """
import datetime
from sym.sdk.annotations import reducer
from sym.sdk.integrations import slack
@reducer
def get_approvers(event):
    if event.fields["Urgency"] == "High":
        return slack.channel("#break-glass")

    if datetime.datetime.now().hour >= 17:
        return slack.user('@Ari Tang')
    else:
        return [slack.user(u) for u in ['@David Ruiz', '@Jon Demo']]
"""

###
### Begin PagerDuty samples
###

SIMPLE_PAGERDUTY_IS_ON_CALL_CODE = """
from sym.sdk.annotations import reducer
from sym.sdk.integrations import pagerduty, slack

@reducer
def get_approvers(event):
    if pagerduty.is_on_call(event.user):
        return slack.channel("#on-call")
    return slack.channel("#not-on-call")
"""

SIMPLE_PAGERDUTY_IS_ON_CALL_SCHEDULE_CODE = """
from sym.sdk.annotations import reducer
from sym.sdk.integrations import pagerduty, slack

@reducer
def get_approvers(event):
    if pagerduty.is_on_call(event.user, schedule_name="test-schedule"):
        return slack.channel("#on-call")
    return slack.channel("#not-on-call")
"""

SIMPLE_PAGERDUTY_USERS_ON_CALL_CODE = """
from sym.sdk.annotations import reducer
from sym.sdk.integrations import pagerduty, slack

@reducer
def get_approvers(event):
    return [slack.user(u) for u in pagerduty.users_on_call()]
"""

SIMPLE_PAGERDUTY_USERS_ON_CALL_SCHEDULE_CODE = """
from sym.sdk.annotations import reducer
from sym.sdk.integrations import pagerduty, slack

@reducer
def get_approvers(event):
    return [slack.user(u) for u in pagerduty.users_on_call(schedule_name="test-schedule")]
"""
