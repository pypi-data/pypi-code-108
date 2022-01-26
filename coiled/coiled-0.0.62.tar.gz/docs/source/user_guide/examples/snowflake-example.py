# Set environment variables related to Snowflake

import os

os.environ["SNOWFLAKE_USER"] = "SNOWFLAKE_USER"
os.environ["SNOWFLAKE_PASSWORD"] = "SNOWFLAKE_PASSWORD"
os.environ["SNOWFLAKE_ACCOUNT"] = "SNOWFLAKE_ACCOUNT"
os.environ["SNOWFLAKE_WAREHOUSE"] = "dask_snowflake_wh"

# Verify Snowflake connectivity

import os

import snowflake.connector

ctx = snowflake.connector.connect(
    user=os.environ["SNOWFLAKE_USER"],
    password=os.environ["SNOWFLAKE_PASSWORD"],
    account=os.environ["SNOWFLAKE_ACCOUNT"],
)

cs = ctx.cursor()

schema = "TPCDS_SF100TCL"
table = "CALL_CENTER"

cs.execute("USE SNOWFLAKE_SAMPLE_DATA")
cs.execute("SELECT * FROM " + schema + "." + table)

one_row = str(cs.fetchone())

print(one_row)

# Create a Coiled environment

import coiled

coiled.create_software_environment(
    name="coiled-snowflake",
    pip=[
        "dask[distributed, dataframe, diagnostics]",
        "snowflake-connector-python",
        "dask-snowflake",
    ],
)

# Create a Dask cluster with Coiled

import coiled

cluster = coiled.Cluster(
    name="coiled-snowflake",
    software="coiled-snowflake",
    n_workers=10,
)

from dask.distributed import Client

client = Client(cluster)
print("Dashboard:", client.dashboard_link)

# Generate synthetic data

import dask

ddf = dask.datasets.timeseries(
    start="2021-01-01",
    end="2021-03-31",
)

# Create a warehouse and database in Snowflake

import os

import snowflake.connector

ctx = snowflake.connector.connect(
    user=os.environ["SNOWFLAKE_USER"],
    password=os.environ["SNOWFLAKE_PASSWORD"],
    account=os.environ["SNOWFLAKE_ACCOUNT"],
    warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
)

cs = ctx.cursor()

cs.execute("CREATE WAREHOUSE IF NOT EXISTS dask_snowflake_wh")
cs.execute("CREATE DATABASE IF NOT EXISTS dask_snowflake_db")
cs.execute("USE DATABASE dask_snowflake_db")

# Write data to Snowflake in parallel

from dask_snowflake import to_snowflake

connection_kwargs = {
    "user": os.environ["SNOWFLAKE_USER"],
    "password": os.environ["SNOWFLAKE_PASSWORD"],
    "account": os.environ["SNOWFLAKE_ACCOUNT"],
    "warehouse": os.environ["SNOWFLAKE_WAREHOUSE"],
    "database": "dask_snowflake_db",
    "schema": "PUBLIC",
}

to_snowflake(
    ddf,
    name="dask_snowflake_table",
    connection_kwargs=connection_kwargs,
)

# Read data from Snowflake in parallel

from dask_snowflake import read_snowflake

ddf = read_snowflake(
    query="""
        SELECT *
        FROM dask_snowflake_table;
    """,
    connection_kwargs=connection_kwargs,
)

print(ddf.head())

# Work with Dask as usual

result = ddf.X.mean()
print(result.compute())
