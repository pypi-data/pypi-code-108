import requests
import json
import os

if 'RITO_SLACK_TOKEN' not in os.environ:
    print("To use Rito's slack functions, first create a Slack app on your workspace following these instructions: https://api.slack.com/messaging/sending#getting_started")
    print("Your app needs the permissions channels:read, channels:history, chat:write, files:write, and chat:write.public")
    print("After creating the app and installing it to your workspace, copy its auth token into an environment variable called RITO_SLACK_TOKEN")
    exit(1)

auth_token = os.environ['RITO_SLACK_TOKEN']

def send_message(channel, text):
    payload = {
        "channel": channel,
        "text": text,
    }

    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {auth_token}"
    }

    resp = requests.post("https://slack.com/api/chat.postMessage", data=json.dumps(payload), headers=headers)
    resp = json.loads(resp.text)
    if not resp["ok"]:
        raise Exception(resp["error"])