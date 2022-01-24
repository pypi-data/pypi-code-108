#
# Copyright 2021 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
import trafaret as t

from datarobot._compat import Int, String

UserBlueprintTaskArgumentDefinition_ = t.Dict(
    {
        t.Key("name"): String(allow_blank=False),
        t.Key("type"): String(allow_blank=False),
        t.Key("default", optional=True): t.Or(
            t.Or(Int(), String(allow_blank=True), t.Bool(), t.Float(), t.Null()),
            t.List(t.Or(Int(), String(allow_blank=True), t.Bool(), t.Float(), t.Null())),
        ),
        t.Key("values"): t.Or(
            t.Or(Int(), String(allow_blank=True), t.Bool(), t.Float(), t.Null()),
            t.List(t.Or(Int(), String(allow_blank=True), t.Bool(), t.Float(), t.Null())),
            t.Dict().allow_extra("*"),
        ),
        t.Key("tunable", optional=True): t.Bool(),
        t.Key("recommended", optional=True): t.Or(
            t.Or(Int(), String(allow_blank=True), t.Bool(), t.Float(), t.Null()),
            t.List(t.Or(Int(), String(allow_blank=True), t.Bool(), t.Float(), t.Null())),
        ),
    }
).allow_extra("*")


UserBlueprintTaskArgument_ = t.Dict(
    {
        t.Key("key"): String(allow_blank=False),
        t.Key("argument"): t.Or(UserBlueprintTaskArgumentDefinition_),
    }
)
