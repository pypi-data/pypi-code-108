from os import getenv, path, mkdir
from typing import Dict, List, Union
from dotenv import load_dotenv
from lmdb import open
import json


load_dotenv()
DB_DIR = getenv('DB_DIR', './db')

def open_db():
    if not path.exists(DB_DIR):
        mkdir(DB_DIR)

    dbenv = open(
        DB_DIR,
        create=True,
        max_dbs=0
    )

    return dbenv


def transact_get(
    transaction: any,
    key: str,
    *,
    default: Union[Dict, List] = {}
) -> Union[Dict, List]:
    return json.loads(
        transaction.get(
            key.encode(encoding='utf-8'),
            default=bytes(
                json.dumps(default),
                'utf-8'
            )
        )
    )

def get(
    key: str,
    dbenv: any = None,
    *,
    default: Union[Dict, List] = {}
) -> Union[Dict, List]:
    """
        Retrieves an item from db.
    """

    # Open the DB environment if no
    # previously opened instance was passed.
    env = dbenv if dbenv else open_db()

    result = None
    with env.begin() as trnx:
        result = transact_get(
            trnx,
            key,
            default=default
        )

    # Close a self-opened DB environment.
    if not dbenv:
        env.close()
        
    return result


def transact_update(
    transaction: any,
    key: str,
    item: Union[Dict, List]
):
    transaction.put(
        key.encode(encoding='utf-8'),
        bytes(json.dumps(item), 'utf-8')
    )


def update(
    key: str,
    item: Union[Dict, List],
    *,
    dbenv: any = None
):
    """
        Update an item in the db.
    """
    
    # Open the DB environment if no
    # previously opened instance was passed.
    env = dbenv if dbenv else open_db()

    with env.begin(write=True) as trnx:
        transact_update(
            trnx,
            key,
            item
        )

    # Close a self-opened DB environment.
    if not dbenv:
        env.close()