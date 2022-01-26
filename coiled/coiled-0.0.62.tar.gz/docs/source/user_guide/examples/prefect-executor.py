import datetime
import random

import pandas as pd
import prefect
import s3fs
from prefect.engine.executors import DaskExecutor
from prefect.utilities.notifications import slack_notifier

# Input parameter for CSV filename on Amazon S3
filename = prefect.Parameter(
    name="filename",
    default="s3://nyc-tlc/trip data/yellow_tripdata_2020-01.csv",
)

# Setup for Slack notifications
handler = slack_notifier(
    backend_info=False,
    only_states=[prefect.engine.state.Success, prefect.engine.state.Failed],
)

prefect.context.secrets = {
    "SLACK_WEBHOOK_URL": "https://hooks.slack.com/services/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"
}


# Our normal Prefect flow
@prefect.task
def download(filename):
    # Read taxi data from S3 and emit chunks for each hour of data
    s3 = s3fs.S3FileSystem(anon=True)
    with s3.open(filename) as f:
        df = pd.read_csv(f, nrows=10_000)
    times = pd.DatetimeIndex(df.tpep_pickup_datetime)
    return [chunk for _, chunk in df.groupby([times.hour, times.date])]


@prefect.task(max_retries=5, retry_delay=datetime.timedelta(seconds=2))
def clean(df):
    if random.random() < 0.2:
        raise Exception("Random failure")

    df = df[df.tip_amount > 0]
    return df


@prefect.task
def best(df):
    if not df.empty:
        best_tip_idx = (df.tip_amount / df.total_amount).argmax()
        row = df.iloc[best_tip_idx]
        prefect.context.logger.info("Best row: %s", row)
        return row


with prefect.Flow(
    name="Most Generous NYC Taxi Riders",
    state_handlers=[handler],
) as flow:
    dataframes = download(filename)
    cleaned = clean.map(dataframes)
    best.map(cleaned)


# This section connects Prefect to Coiled
# Comment this out in order to run locally
import coiled

executor = DaskExecutor(
    cluster_class=coiled.Cluster,
    cluster_kwargs={
        "software": "jrbourbeau/prefect",
        "shutdown_on_close": False,
        "name": "prefect-executor",
    },
)

flow.run(
    executor=executor,
)
