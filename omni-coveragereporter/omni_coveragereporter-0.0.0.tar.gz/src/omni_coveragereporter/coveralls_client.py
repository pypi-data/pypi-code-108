import os
import tempfile

import requests

temporaryFolder = tempfile.gettempdir()

url = 'https://coveralls.io/api/v1/jobs'
coveralls_file = 'coveralls.json'

coveralls_tmp_file = os.path.join(temporaryFolder, coveralls_file)


def send_report(report):
    file_save = open(coveralls_tmp_file, "w")
    file_save.write(report)
    print(f"- Saved file in {file_save.name}")
    file_save.close()
    files = {'json_file': open(coveralls_tmp_file, 'rb')}
    r = requests.post(
        url=url,
        files=files,
    )
    return r.content.decode('utf-8')
