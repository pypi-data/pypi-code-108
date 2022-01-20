from typing import Tuple
import grpc
import pymongo
from pymongo.collection import Collection

import cryptoshred.backends
from cryptoshred import convenience as CS
from pyfactcast.client import sync as FS
from pyfactcast.client.entities import Fact

from fact_lake.config import get_configuration, get_factcast_configuration, get_logger

app_config = get_configuration()  # TODO make configurable
fs_config = get_factcast_configuration(app_config)

log = get_logger("playing")


key_backend = cryptoshred.backends.DynamoDbSsmBackend(
    iv_param=app_config.cryptoshred_init_vector
)

fact_store = FS.FactStore(
    FS.get_synchronous_grpc_client(get_factcast_configuration(app_config))
)


def _connect_to_mongo(namespace: str) -> Tuple[Collection, Collection]:
    mongo_client = pymongo.MongoClient(
        host=app_config.mongo_server,
        port=app_config.mongo_port,
        username=app_config.mongo_username,
        password=app_config.mongo_password,
        tls=app_config.mongo_tls,
        tlsAllowInvalidCertificates=app_config.mongo_tls_invalid_certificates,
        tlsCAFile=app_config.mongo_tls_ca_file_path,
        retryWrites=app_config.mongodb_retry_writes,
    )
    db = mongo_client.get_database("facts")
    state_collection = db["last_seen"]
    collection = db[namespace]
    return (collection, state_collection)


def project_namespace(namespace: str) -> None:

    # * https://pymongo.readthedocs.io/en/stable/faq.html#is-pymongo-fork-safe
    collection, state_collection = _connect_to_mongo(namespace=namespace)

    state = state_collection.find_one(filter={"namespace": namespace})
    last_seen = None
    if state:
        last_seen = state["last_seen"]

    try:
        with fact_store as fs:
            for item in fs.subscribe(
                subscription_specs=[
                    FS.SubscriptionSpec(
                        ns=namespace,
                    )
                ],
                after_fact=last_seen,
                continuous=True,
            ):
                log.info(f"[{namespace}] Next fact")
                fact_id = _insert_fact(item=item, collection=collection)

                state_collection.find_one_and_update(
                    filter={"namespace": namespace},
                    update={"$set": {"last_seen": fact_id}},
                    upsert=True,
                )

    except grpc._channel._MultiThreadedRendezvous:
        log.warning("GRPC error")
        project_namespace(namespace=namespace)


def _insert_fact(item: Fact, collection: Collection) -> str:
    fact_id = item.header.id
    mongo_item = item.dict()
    mongo_item["_id"] = fact_id

    res = CS.find_and_decrypt_in_dict(input=[item.payload], key_backend=key_backend)
    mongo_item["payload"] = res[0]
    collection.insert_one(mongo_item).inserted_id
    return str(fact_id)
