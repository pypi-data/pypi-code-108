import coiled
import dask.dataframe as dd
import prefect
from dask.distributed import Client


# Prefect task that uses Coiled for a large computation
@prefect.task
def transform():
    # Create and connect to Coiled cluster
    cluster = coiled.Cluster(n_workers=10, name="prefect-task")
    client = Client(cluster)
    print("Dashboard:", client.dashboard_link)

    # Read CSV data from S3
    df = dd.read_csv(
        "s3://nyc-tlc/trip data/yellow_tripdata_2019-*.csv",
        dtype={
            "payment_type": "UInt8",
            "VendorID": "UInt8",
            "passenger_count": "UInt8",
            "RatecodeID": "UInt8",
        },
        storage_options={"anon": True},
        blocksize="16 MiB",
    ).persist()

    # Compute result
    result = df.groupby("passenger_count").tip_amount.mean().compute()
    return result


# Prefect task without Coiled
@prefect.task()
def clean(series):
    # Filter for 2 or more passengers
    series = series[series.index > 0]
    # Round tip amount to 2 decimal places
    series = round(series, 2)
    return series


with prefect.Flow(
    name="NYC Taxi Riders Tip Amounts",
) as flow:
    series = transform()
    cleaned = clean(series)

flow.run()
