# set GOOGLE_APPLICATION_CREDENTIALS=
# c:\Users\rene_\PycharmProjects\package_eisenradio_py\google-cloud\bigqueriy.access\eisenradio-bfb3346e65cd.json
# $env:GOOGLE_APPLICATION_CREDENTIALS=C:\Users\rene_\PycharmProjects\package_eisenradio_py\google-cloud\eisenradio-9a95136e40c9.json
from os import environ

environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:\\Users\\rene_\\PycharmProjects\\package_eisenradio_py\\google-cloud' \
                                            '\\eisenradio-9a95136e40c9.json '

from google.cloud import bigquery

# Note: depending on where this code is being run, you may require
# additional authentication. See:
# https://cloud.google.com/bigquery/docs/authentication/
client = bigquery.Client()

query_job = client.query("""
SELECT COUNT(*) AS num_downloads
FROM `bigquery-public-data.pypi.file_downloads`
WHERE file.project = 'pytest'
  -- Only query the last 30 days of history
  AND DATE(timestamp)
    BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
    AND CURRENT_DATE()""")

results = query_job.result()  # Waits for job to complete.
for row in results:
    print("{} downloads".format(row.num_downloads))
