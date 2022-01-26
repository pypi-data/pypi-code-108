# Create a Coiled environment

import coiled

coiled.create_software_environment(
    name="coiled-mongodb",
    pip=[
        "dask[distributed, diagnostics, dataframe]",
        "pymongo[srv]",
        "git+https://github.com/coiled/dask-mongo.git",
    ],
)

# Create a Dask cluster with Coiled

import coiled

cluster = coiled.Cluster(
    name="coiled-mongodb",
    software="coiled-mongodb",
    n_workers=10,
)

from dask.distributed import Client

client = Client(cluster)
print("Dashboard:", client.dashboard_link)

# Read data from MongoDB in parallel

from dask_mongo import read_mongo

# Replace the username, password, and cluster address with your own connection details
host_uri = "mongodb+srv://<username>:<password>@<mongodb-cluster-address>/myFirstDatabase?retryWrites=true&w=majority"

bag = read_mongo(
    connection_kwargs={"host": host_uri},
    database="sample_airbnb",
    collection="listingsAndReviews",
    chunksize=500,
)

bag.take(1)

# Work with Dask as usual

bag.pluck("property_type").frequencies().compute()


def process(record):
    try:
        yield {
            "accomodates": record["accommodates"],
            "bedrooms": record["bedrooms"],
            "price": float(str(record["price"])),
            "country": record["address"]["country"],
        }
    except KeyError:
        pass


# Filter only apartments
b_flattened = (
    bag.filter(lambda record: record["property_type"] == "Apartment")
    .map(process)
    .flatten()
)
b_flattened.take(3)

ddf = b_flattened.to_dataframe()
ddf
ddf.head()

ddf.groupby(["country"])["price"].mean().compute()


# Write data to MongoDB in parallel

import dask.bag as db
from dask_mongo import to_mongo

new_bag = db.from_delayed(
    ddf.map_partitions(lambda x: x.to_dict(orient="records")).to_delayed()
)

new_bag.take(1)

to_mongo(
    new_bag,
    database="new_database",
    collection="new_collection",
    connection_kwargs={"host": host_uri},
)
