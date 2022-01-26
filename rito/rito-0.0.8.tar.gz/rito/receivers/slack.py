import requests
import json
import os
import re

if 'RITO_SLACK_TOKEN' not in os.environ:
    print("To use Rito's slack functions, first create a Slack app on your workspace following these instructions: https://api.slack.com/messaging/sending#getting_started")
    print("Your app needs the permissions channels:read, channels:history, chat:write, files:write, and chat:write.public")
    print("After creating the app and installing it to your workspace, copy its auth token into an environment variable called RITO_SLACK_TOKEN")
    exit(1)

auth_token = os.environ['RITO_SLACK_TOKEN']
recent_messages_to_check = os.environ['RITO_SLACK_HISTORY'] if 'RITO_SLACK_HISTORY' in os.environ else 10

check_interval = 30

def get_message(channel, pattern):
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {auth_token}"
    }

    resp = requests.get("https://slack.com/api/conversations.list", headers=headers)
    resp = json.loads(resp.text)
    if not resp["ok"]:
        raise Exception(resp["error"])

    channels = resp["channels"]

    id = ""
    for _channel in channels:
        if _channel["name"] == channel:
            id = _channel["id"]
    
    if len(id) == 0:
        raise Exception(f"Channel {channel} not available to Rito")
    
    payload = {
        "channel": id,
    }

    resp = requests.get("https://slack.com/api/conversations.history", headers=headers, params=payload)
    resp = json.loads(resp.text)
    if not resp["ok"]:
        raise Exception(resp["error"])
    
    messages = resp["messages"]
    
    # Search backwards for the pattern:
    pattern = re.compile(pattern)
    for idx in range(recent_messages_to_check):
        message = messages[idx]['text']
        if pattern.search(message) != None:
            return message

    return ""