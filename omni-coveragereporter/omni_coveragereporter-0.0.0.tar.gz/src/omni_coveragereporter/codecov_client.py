import os

import git
import requests

repo = git.Repo(os.getcwd())
master = repo.head.reference
commit = master.commit.hexsha

url = 'https://codecov.io/upload/v4'

separator = "\n<<<<<< EOF\n"


def send_report(codecov_reports):
    params = {
        'commit': commit,
        'token': os.getenv('CODECOV_TOKEN'),
        'branch': master
    }
    headers = {
        'Content-Type': 'text/plain'
    }
    r = requests.post(url, params=params, headers=headers, data="")
    decode = r.content.decode("utf-8").split(sep='\n')
    view = decode[0]
    print(f"- Report contents will be visible here {view}")
    upload_to_s3_url = decode[1]
    print(f"- Sending contents to {upload_to_s3_url}")

    print(decode)
    codecov_report = separator.join(codecov_reports) + separator

    print(codecov_report)
    r = requests.put(upload_to_s3_url, headers=headers, data=codecov_report)
    return r.content.decode("utf-8")
