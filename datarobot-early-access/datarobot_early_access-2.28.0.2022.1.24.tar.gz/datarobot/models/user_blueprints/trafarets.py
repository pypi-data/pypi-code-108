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
from datarobot.models.trafarets import UserBlueprintTaskArgument_

UserBlueprintsHexColumnNameLookupEntry_ = t.Dict(
    {
        t.Key("colname"): String(allow_blank=False),
        t.Key("hex"): String(allow_blank=False),
        t.Key("project_id", optional=True): String(allow_blank=False),
    }
)

ParamValuePair_ = t.Dict(
    {
        t.Key("param"): String(allow_blank=False),
        t.Key("value", optional=True): t.Or(
            t.Or(Int(), String(allow_blank=True), t.Bool(), t.Float(), t.Null()),
            t.List(t.Or(Int(), String(allow_blank=True), t.Bool(), t.Float(), t.Null())),
        ),
    }
)

UserBlueprintsBlueprintTaskData_ = t.Dict(
    {
        t.Key("inputs"): t.List(String(allow_blank=False)),
        t.Key("output_method"): String(allow_blank=False),
        t.Key("output_method_parameters"): t.List(ParamValuePair_),
        t.Key("task_code"): String(allow_blank=False),
        t.Key("task_parameters"): t.List(ParamValuePair_),
        t.Key("x_transformations"): t.List(ParamValuePair_),
        t.Key("y_transformations"): t.List(ParamValuePair_),
    }
)

UserBlueprintsBlueprintTask_ = t.Dict(
    {
        t.Key("task_id"): String(allow_blank=False),
        t.Key("task_data"): UserBlueprintsBlueprintTaskData_,
    }
)

VertexContextItemInfo_ = t.Dict(
    {
        t.Key("inputs"): t.List(String(allow_blank=False)),
        t.Key("outputs"): t.List(String(allow_blank=False)),
    }
)

VertexContextItemMessages_ = t.Dict(
    {
        t.Key("errors", optional=True): t.List(String(allow_blank=False)),
        t.Key("warnings", optional=True): t.List(String(allow_blank=False)),
    }
)

VertexContextItem_ = t.Dict(
    {
        t.Key("task_id"): String(allow_blank=False),
        t.Key("information"): t.Or(VertexContextItemInfo_),
        t.Key("messages"): t.Or(VertexContextItemMessages_),
    }
)

UserBlueprint_ = t.Dict(
    {
        t.Key("blender"): t.Bool(),
        t.Key("blueprint_id"): String(allow_blank=False),
        t.Key("custom_task_version_metadata", optional=True): t.List(
            t.List(String(allow_blank=False))
        ),
        t.Key("diagram"): String(allow_blank=False),
        t.Key("features"): t.List(String(allow_blank=False)),
        t.Key("features_text"): String(allow_blank=True),
        t.Key("hex_column_name_lookup", optional=True): t.List(
            UserBlueprintsHexColumnNameLookupEntry_
        ),
        t.Key("icons"): t.List(Int()),
        t.Key("insights"): String(allow_blank=False),
        t.Key("is_time_series", default=False): t.Bool(),
        t.Key("model_type"): String(allow_blank=False),
        t.Key("project_id", optional=True): String(allow_blank=False),
        t.Key("reference_model", default=False): t.Bool(),
        t.Key("shap_support", default=False): t.Bool(),
        t.Key("supported_target_types"): t.List(String(allow_blank=False)),
        t.Key("supports_gpu", default=False): t.Bool(),
        t.Key("user_blueprint_id"): String(allow_blank=False),
        t.Key("user_id"): String(allow_blank=False),
        t.Key("blueprint", optional=True): t.List(UserBlueprintsBlueprintTask_),
        t.Key("vertex_context", optional=True): t.List(VertexContextItem_),
        t.Key("blueprint_context", optional=True): VertexContextItemMessages_,
    }
).allow_extra("*")


UserBlueprintsInputType_ = t.Dict(
    {t.Key("type"): String(allow_blank=False), t.Key("name"): String(allow_blank=False)}
)

UserBlueprintsInputTypesResponse_ = t.Dict({t.Key("input_types"): t.List(UserBlueprintsInputType_)})


UserBlueprintAddedToMenuItem_ = t.Dict(
    {
        t.Key("blueprint_id"): String(allow_blank=False),
        t.Key("user_blueprint_id"): String(allow_blank=False),
    }
)

UserBlueprintNotAddedToMenuItem_ = t.Dict(
    {
        t.Key("error"): String(allow_blank=False),
        t.Key("user_blueprint_id"): String(allow_blank=False),
    }
)

UserBlueprintAddToMenuResponse_ = t.Dict(
    {
        t.Key("added_to_menu"): t.List(UserBlueprintAddedToMenuItem_),
        t.Key("not_added_to_menu", optional=True): t.List(UserBlueprintNotAddedToMenuItem_),
        t.Key("message", optional=True): String(allow_blank=False),
    }
).allow_extra("*")


UserBlueprintsValidateTaskParameter_ = t.Dict(
    {
        t.Key("message"): String(allow_blank=False),
        t.Key("param_name"): String(allow_blank=False),
        t.Key("value", optional=True): t.Or(
            t.Or(Int(), String(allow_blank=True), t.Bool(), t.Float(), t.Null()),
            t.List(t.Or(Int(), String(allow_blank=True), t.Bool(), t.Float(), t.Null())),
        ),
    }
)

UserBlueprintsValidateTaskParametersResponse_ = t.Dict(
    {t.Key("errors"): t.List(UserBlueprintsValidateTaskParameter_)}
)


UserBlueprintTaskCategoryItem_ = t.Dict(
    {
        t.Key("name"): String(allow_blank=False),
        t.Key("task_codes"): t.List(String(allow_blank=False)),
        t.Key("subcategories", optional=True): t.List(t.Dict().allow_extra("*")),
    }
).allow_extra("*")


ColnameAndType_ = t.Dict(
    {
        t.Key("hex"): String(allow_blank=False),
        t.Key("colname"): String(allow_blank=False),
        t.Key("type"): String(allow_blank=False),
    }
)

TaskDocumentationUrl_ = t.Dict(
    {t.Key("documentation", optional=True): String(allow_blank=True)}
).allow_extra("*")

UserBlueprintTaskCustomTaskMetadata_ = t.Dict(
    {
        t.Key("id"): String(allow_blank=False),
        t.Key("version_major"): Int(),
        t.Key("version_minor"): Int(),
        t.Key("label"): String(allow_blank=False),
    }
).allow_extra("*")

UserBlueprintTask_ = t.Dict(
    {
        t.Key("task_code"): String(allow_blank=False),
        t.Key("label"): String(allow_blank=True),
        t.Key("description"): String(allow_blank=True),
        t.Key("arguments"): t.List(UserBlueprintTaskArgument_),
        t.Key("categories"): t.List(String(allow_blank=False)),
        t.Key("colnames_and_types", optional=True): t.Or(t.List(ColnameAndType_), t.Null),
        t.Key("icon"): Int(),
        t.Key("output_methods"): t.List(String(allow_blank=False)),
        t.Key("time_series_only"): t.Bool(),
        t.Key("url"): t.Or(
            t.Dict().allow_extra("*"), String(allow_blank=True), TaskDocumentationUrl_,
        ),
        t.Key("valid_inputs"): t.List(String(allow_blank=False)),
        t.Key("is_custom_task", optional=True): t.Bool(),
        t.Key("custom_task_id", optional=True): t.Or(String, t.Null),
        t.Key("custom_task_versions", optional=True): t.List(UserBlueprintTaskCustomTaskMetadata_),
        t.Key("supports_scoring_code", optional=True): t.Bool(),
    }
).allow_extra("*")

UserBlueprintTaskLookupEntry_ = t.Dict(
    {
        t.Key("task_code"): String(allow_blank=False),
        t.Key("task_definition"): t.Or(UserBlueprintTask_),
    }
)

UserBlueprintTasksResponse_ = t.Dict(
    {
        t.Key("categories"): t.List(UserBlueprintTaskCategoryItem_),
        t.Key("tasks"): t.List(UserBlueprintTaskLookupEntry_),
    }
)

UserBlueprintSharedRolesResponseValidator_ = t.Dict(
    {
        t.Key("share_recipient_type"): t.Enum("user", "group", "organization"),
        t.Key("role"): t.Enum("CONSUMER", "EDITOR", "OWNER"),
        t.Key("id"): String(allow_blank=False, min_length=24, max_length=24),
        t.Key("name"): String(allow_blank=False),
    }
)

UserBlueprintSharedRolesListResponseValidator_ = t.Dict(
    {
        t.Key("count", optional=True): Int(),
        t.Key("next", optional=True): t.URL,
        t.Key("previous", optional=True): t.URL,
        t.Key("data"): t.List(UserBlueprintSharedRolesResponseValidator_),
        t.Key("total_count", optional=True): Int(),
    }
)


UserBlueprintCatalogSearchItem_ = t.Dict(
    {
        t.Key("id"): String(),
        t.Key("catalog_name"): String(),
        t.Key("description", optional=True): String(),
        t.Key("info_creator_full_name"): String(),
        t.Key("last_modifier_full_name", optional=True): String(),
        t.Key("user_blueprint_id"): String(),
    }
).allow_extra("*")


UserBlueprintValidationRequest_ = t.Dict(
    {
        t.Key("project_id", optional=True): t.String(allow_blank=False),
        t.Key("blueprint"): t.List(UserBlueprintsBlueprintTask_),
    }
)


UserBlueprintValidationResponse_ = t.Dict(
    {
        t.Key("vertex_context"): t.List(VertexContextItem_),
        t.Key("blueprint_context"): VertexContextItemMessages_,
    }
)
