import os

import git
import requests

url = 'https://api.codacy.com'

repo = git.Repo(os.getcwd())
master = repo.head.reference
commit = master.commit.hexsha


def send_report(reports, language):
    headers = {
        'Content-Type': 'application/json',
        'project-token': os.getenv('CODACY_PROJECT_TOKEN'),
    }
    if len(reports) == 1:
        effective_url = f'{url}/2.0/coverage/{commit}/{language.capitalized()}?partial=false'
        print(f"- Sending Codacy report to {effective_url}")
        r = requests.post(url=effective_url, headers=headers, data=reports[0])
        return r.content.decode("utf-8")
    else:
        effective_url = f'{url}/2.0/coverage/{commit}/{language}?partial=true'
        print(f"- Sending Codacy report to {effective_url}")
        for report in reports:
            r = requests.post(url=effective_url, headers=headers, data=report)
            print("- Codacy Report sent!")
            print(f"- {r.content.decode('utf-8')}")
        effective_final_url = f'{url}/2.0/commit/{commit}/coverageFinal'
        print(f"- Sending Final Codacy report to {effective_final_url}")
        final_response = requests.post(url=effective_final_url, headers=headers, json="")
        final_response.content.decode("utf-8")
    return None
