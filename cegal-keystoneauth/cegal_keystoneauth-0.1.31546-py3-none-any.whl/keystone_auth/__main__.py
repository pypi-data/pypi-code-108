import argparse
from ctypes import ArgumentError
import jwt
import logging

from cegal.keystone_auth.db import _TokenDb
from cegal.keystone_auth.utils import local_storage_location, pp_dict
from cegal.keystone_auth import logger

parser = argparse.ArgumentParser(
    description="Command-line interface to the cegal-keystoneauth python package"
)

subparsers = parser.add_subparsers(dest="command")

add_parser = subparsers.add_parser(
    "add", help="Adds a set of tokens to the auth database"
)
add_parser.add_argument("--client-id", help="client id")
add_parser.add_argument("--auth-token", help="auth token")
add_parser.add_argument("--id-token", help="id token")
add_parser.add_argument("--refresh-token", help="refresh_token")
add_parser.add_argument("--verbose", action="store_true", help="verbose logging")

list_parser = subparsers.add_parser(
    "list", help="Lists the client ids of the tokens present"
)
list_parser.add_argument("--verbose", action="store_true", help="verbose logging")

dump_parser = subparsers.add_parser("dump", help="Report details of a specified token")
dump_parser.add_argument("client_id", type=str, help="Client id of tokens to report")
dump_parser.add_argument("--verbose", action="store_true", help="verbose logging")

args = parser.parse_args()

logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

db_location = local_storage_location()
logger.debug(f"Using db: {db_location}")

if args.command == "add":
    if not args.client_id:
        raise ArgumentError("Must supply client id")
    if not args.auth_token:
        raise ArgumentError("Must supply auth token")
    # should this be mandatory for 'add'?
    if not args.refresh_token:
        raise ArgumentError("Must supply refresh token")

    db = _TokenDb(db_location, args.client_id)
    db.store_token_in_db(args.id_token, args.auth_token, args.refresh_token)

    logger.info("Token added")

elif args.command == "list":

    db = _TokenDb(db_location, None)
    ids = db.get_client_ids()
    for id in ids:
        print(f"client_id: {id}")
elif args.command == "dump":
    db = _TokenDb(db_location, args.client_id)
    token = db.get_token_from_db()
    print(f"client_id: {token[0]}")

    id = token[1]
    access = token[2]
    refresh = token[3]

    access_token = jwt.decode(
        access,
        options={
            "verify_signature": False,
            "verify_aud": False,
            "verify_exp": False,
        },
        algorithms=["RS256"],
    )

    print(f"access_token: {access}")
    pp_dict(access_token)
    print(f"refresh_token: {refresh}")
    print(f"id_token: {id}")
