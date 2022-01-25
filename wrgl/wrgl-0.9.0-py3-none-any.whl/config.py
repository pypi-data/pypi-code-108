# SPDX-License-Identifier: Apache-2.0
# Copyright © 2021 Wrangle Ltd

import typing
import attr

from wrgl.serialize import field_transformer


@attr.s(auto_attribs=True, field_transformer=field_transformer(globals()))
class User(object):
    """User configuration, this corresponds to the `user` section in config.yaml.
    Learn more about `configuration options`_.

    In the context of a hosted repository, this holds information about the default user that perform
    automated actions such as updating reflog whenever the repository receive a push.

    :ivar str name: default user's name
    :ivar str email: default user's email
    """
    name: str
    email: str


@attr.s(auto_attribs=True, field_transformer=field_transformer(globals()))
class Receive(object):
    """Receive configuration, this corresponds to the `receive` section in config.yaml.
    Learn more about `configuration options`_.

    :ivar bool deny_non_fast_forwards: don't allow non-fast-forward pushes, learn more `here <https://www.wrgl.co/doc/wrgl-reference/push#refspec>`_
    :ivar bool deny_deletes: don't allow ref deletion
    """
    deny_non_fast_forwards: bool
    deny_deletes: bool


@attr.s(auto_attribs=True, field_transformer=field_transformer(globals()))
class Branch(object):
    """Branch's upstream configuration, this corresponds to the `branch` section in config.yaml.
    Learn more about `configuration options`_.

    This configuration is rarely useful for a hosted repository because most hosted repositories do not have upstreams.

    :ivar str remote: upstream remote of the branch
    :ivar str merge: upstream ref of the branch
    """
    remote: str
    merge: str


@attr.s(auto_attribs=True, field_transformer=field_transformer(globals()))
class Auth(object):
    """Authentication configuration, this corresponds to the `auth` section in config.yaml.
    Learn more about `configuration options`_.

    :ivar str token_duration: how long before a JWT token given by the `/authenticate/` endpoint of Wrgld expire.
        This is a string in the format "72h3m0.5s". Tokens last for 90 days by default.
    """
    token_duration: str


@attr.s(auto_attribs=True, field_transformer=field_transformer(globals()))
class Pack(object):
    """Packfile configuration, this corresponds to the `pack` section in config.yaml.
    Learn more about `configuration options`_.

    :ivar int max_file_size: maximum packfile size in bytes
    """
    max_file_size: int


@attr.s(auto_attribs=True, field_transformer=field_transformer(globals()))
class Remote(object):
    """Remote configuration, this corresponds to the `remote` section in config.yaml.
    Learn more about `configuration options`_.

    This configuration is rarely useful in the context of hosted repositories, unless you want your upstreams to have upstreams themselves.

    :ivar str url: url of the remote
    :ivar list[str] fetch: list of refspec to automatically fetch from this upstream
    :ivar list[str] push: list of refspec to automatically push to this upstream
    :ivar bool mirror: whether this upstream should mirror the repository
    """
    url: str
    fetch: typing.List[str]
    push: typing.List[str]
    mirror: bool


@attr.s(auto_attribs=True, field_transformer=field_transformer(globals()))
class Config(object):
    """Configurations as recorded in config.yaml, which can also be read/update via the `/config/ endpoint <https://www.wrgl.co/doc/http-api#config>`_.
    Learn more about `configuration options`_.

    :ivar User user: user configuration
    :ivar dict[str, Remote] remote: mapping of remote configurations
    :ivar Receive receive: receive configurations
    :ivar dict[str, Branch] branch: branch upstreams configurations
    :ivar Auth auth: authentication configurations
    :ivar Pack pack: packfile configurations
    """
    user: User
    remote: typing.Dict[str, Remote]
    receive: Receive
    branch: typing.Dict[str, Branch]
    auth: Auth
    pack: Pack
