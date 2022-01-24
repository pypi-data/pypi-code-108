from typing import Literal


def user_content() -> str:
    return "\n\n" + """
@authorized
@api
@pymongo
@jsonclass
class User:
    id: str = types.readonly.str.primary.mongoid.required
    email: str = types.str.email.unique.authidentity.required
    password: str = types.writeonly.str.securepw.length(8, 16).salt.authbycheckpw.required
    name: str | None
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required
    """.strip() + "\n"


def admin_content() -> str:
    return "\n\n" + """
@authorized
@api
@pymongo
@jsonclass
class Admin:
    id: str = types.readonly.str.primary.mongoid.required
    email: str = types.str.email.unique.authidentity.required
    password: str = types.writeonly.str.securepw.length(8, 16).salt.authbycheckpw.required
    name: str | None
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required
    """.strip() + "\n"


def app_content(include_user: bool, include_admin: bool) -> str:

    return f"""
from __future__ import annotations
from datetime import datetime
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo
from jsonclasses_server import api, {'authorized, ' if include_user or include_admin else ''}server




# You can create a model by using class and type hint syntax, with decorators
# decorated.
#
# Models with relationships are supported.
#
# To understand the types modifier pipeline syntax, check our documentation:
#
# https://docs.jsonclasses.com/docs/api-documentation/types-modifiers
#
# @api
# @pymongo
# @jsonclass
# class MyModel:
#     id: str = types.readonly.str.primary.mongoid.required
#     one: str
#     two: int = 1
#     created_at: datetime = types.readonly.datetime.tscreated.required
#     updated_at: datetime = types.readonly.datetime.tsupdated.required
{user_content() if include_user else ''}{admin_content() if include_admin else ''}

app = server()


# You can still write custom routes if synthesized routes don't satisfy your
# need. To understand the ORM methods, check our documentation:
#
# https://docs.jsonclasses.com/docs/api-documentation/orm-addons
    """.strip() + '\n'
