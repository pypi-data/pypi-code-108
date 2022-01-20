from continual.python.sdk.exceptions import InvalidArgumentError
from continual.python.utils.utils import parse_feature_set_name
import copy
from google.protobuf.json_format import MessageToDict
from continual.rpc.management.v1 import management_types_pb2

MAX_ENTITY_DEPTH = 5


def cleanup_value(qd):
    for f in qd["fields"]:
        if "value" in f:
            del f["value"]
        if "relation" in f:
            cleanup_value(f["relation"])

    if "related" in qd:
        for q in qd["related"]:
            cleanup_value(q)


class Query:
    def __init__(self, qrepr):
        if isinstance(qrepr, management_types_pb2.Query):
            self._qrepr = qrepr
        elif isinstance(qrepr, bytes):
            self._qrepr = management_types_pb2.Query()
            self._qrepr.ParseFromString(qrepr)
        elif isinstance(qrepr, str):
            qrepr_b = eval(qrepr)
            self._qrepr = management_types_pb2.Query()
            self._qrepr.ParseFromString(qrepr_b)
        else:
            self._qrepr = management_types_pb2.Query(**qrepr)

        self._inputs = None
        self._outputs = None
        self._featuresets = None

    def serialize(self):
        return self._qrepr.SerializeToString()

    def to_proto(self):
        return self._qrepr

    def to_dict(self):
        return MessageToDict(self._qrepr, preserving_proto_field_name=True)

    def __repr__(self):
        return repr(self._qrepr)

    def set_id(self, id):
        for f in self._qrepr.fields:
            if f.index == True:
                if isinstance(id, str):
                    f.value.text = id
                else:
                    f.value.number = id
                return

        id_feature = management_types_pb2.QueryFeature(
            name="id",
            type=management_types_pb2.FieldType.TEXT,
            model=False,
            value=management_types_pb2.FeatureValue(text=id),
        )

        self._qrepr.fields.append(id_feature)

    @property
    def fields(self):
        return self._qrepr.fields

    @property
    def related(self):
        return self._qrepr.related

    def clone(self):
        return Query(copy.deepcopy(self._qrepr))

    def build_field_list(
        self, query, path, inputs, outputs, featuresets, include_id, related=False
    ):
        id = query.name.split("/")[3]

        if path is None:
            featuresets.append(
                {"name": id, "type": management_types_pb2.FieldType.TEXT}
            )

        for f in query.fields:
            if f.exclude:
                continue

            # Skip index for related featuresets.
            if related and f.type == management_types_pb2.FieldType.INDEX:
                continue

            # For models the field names are not qualified.
            if query.name.split("/")[2] == "models":
                qualified_name = f.name
            else:
                qualified_name = id + ":" + f.name
            if path is not None:
                qualified_name = path + "$" + qualified_name
            if f.HasField("relation"):
                featuresets.append({"name": qualified_name, "type": f.type})
                self.build_field_list(
                    f.relation, qualified_name, inputs, outputs, featuresets, include_id
                )
            else:
                if f.model:
                    outputs.append({"name": qualified_name, "type": f.type})
                else:
                    if f.index and not include_id:
                        continue

                    if f.time_index and not include_id:
                        continue

                    if path is not None and f.index:
                        inputs.append(
                            {
                                "name": path,
                                "type": f.type,
                                "index": f.index,
                                "time_index": f.time_index,
                            }
                        )
                    else:
                        inputs.append(
                            {
                                "name": qualified_name,
                                "type": f.type,
                                "index": f.index,
                                "time_index": f.time_index,
                            }
                        )

        for q in query.related:
            self.build_field_list(
                q, path, inputs, outputs, featuresets, include_id, related=True
            )

    def get_model_version_io(self, include_id=True):
        if (
            self._inputs is not None
            and self._outputs is not None
            and self._featuresets is not None
        ):
            return self._inputs, self._outputs
        inputs = []
        outputs = []
        featuresets = []
        query = self._qrepr
        self.build_field_list(query, None, inputs, outputs, featuresets, include_id)
        self._inputs = inputs
        self._outputs = outputs
        self._featuresets = featuresets
        return inputs, outputs

    def can_hydrate(self, overrides: dict):

        has_hydrateable_values = False

        inputs, outputs = self.get_model_version_io(include_id=True)

        has_missing_values = False
        for input in inputs:
            input_name = input["name"]
            if input_name in overrides:
                overrides[input_name]
                if input["index"]:
                    has_hydrateable_values = True
            else:
                if not input["index"]:
                    has_missing_values = True

        return has_hydrateable_values and has_missing_values

    def _override(self, query, key_splits, value):
        splits = key_splits[0].split(":")

        fieldId = key_splits[0]
        featureset_id = None
        if len(splits) > 1:
            featureset_id = splits[0]
            fieldId = splits[1]

        comps = parse_feature_set_name(query["name"])
        resource_id = ""
        if "featureSets" in comps:
            resource_id = comps["featureSets"]
        elif "models" in comps:
            resource_id = comps["models"]
        if featureset_id is not None and resource_id != featureset_id:
            raise InvalidArgumentError(
                "error - path of override [{}] does not match query for name [{}]".format(
                    key_splits[0], resource_id
                )
            )

        for i in range(0, len(splits)):
            for f in query["fields"]:
                if f["name"] != fieldId:
                    continue

                if len(key_splits) == 1:
                    f["value"] = value
                    return

                if f["relation"] != None:
                    self._override(f["relation"], key_splits[1:], value)

        return

    def override(self, overrides: dict):
        qdict = self.to_dict()
        cleanup_value(qdict)
        for key in overrides:
            value = overrides[key]
            splits = key.split("$")
            current_fs = qdict
            self._override(qdict, splits, value)
            for i in range(0, len(splits)):
                for f in current_fs["fields"]:
                    if f["name"] != splits[i]:
                        continue

                    if len(splits) == 1:
                        f["value"] = value
                        continue

                    if f["relation"] is not None:
                        current_fs = f["relation"]
        return qdict

    def get_index_name(self):
        for f in self._qrepr.fields:
            if f.type == management_types_pb2.FieldType.INDEX or f.index:
                return f.name
        return None

    def get_split_name(self):
        for f in self._qrepr.fields:
            if f.type == management_types_pb2.FieldType.SPLIT or f.split:
                return f.name
        return None

    def get_time_index_name(self):
        for f in self._qrepr.fields:
            if f.type == management_types_pb2.FieldType.TIME_INDEX or f.time_index:
                return f.name
        return None

    def get_exclude_list(self):
        exclude_fields = []
        for f in self._qrepr.fields:
            if f.exclude:
                exclude_fields.append(f.qualified_name)

            if f.relation is not None:
                r_excludes = Query(f.relation).get_exclude_list()
                exclude_fields.extend(r_excludes)

        for r in self._qrepr.related:
            r_excludes = Query(r).get_exclude_list()
            exclude_fields.extend(r_excludes)
        return exclude_fields

    def get_dtype(self, field_name: str):
        fs_splits = field_name.split("$")
        """
             "id"  ==> Model field.
             "tweets:text"  ==> Related entity field.
             "author$users:name" ==> Joined relation field.
             "author:$user:location$locations:name" ==> Nested join field.
        """
        object_name = None
        if ":" in fs_splits[0]:
            column_name = fs_splits[0].split(":")[1]
            object_name = fs_splits[0].split(":")[0]
        else:
            column_name = fs_splits[0]

        # Check if the name can be found in fields.
        for f in self._qrepr.fields:
            if column_name == f.name:
                if len(fs_splits) > 1 and f.relation is not None:
                    return Query(f.relation).get_dtype("$".join(fs_splits[1:]))
                else:
                    return f.dtype

        if object_name is None:
            return ""
        for r in self._qrepr.related:
            if r.name.split("/")[3] == object_name:
                if len(fs_splits) > 1:
                    return Query(r).get_dtype("$".join(fs_splits[1:]))
                else:
                    return Query(r).get_dtype(field_name)
        return ""

    def get_field(self, field_name: str):
        fs_splits = field_name.split("$")
        """
             "id"  ==> Model field.
             "tweets:text"  ==> Related entity field.
             "author$users:name" ==> Joined relation field.
             "author:$user:location$locations:name" ==> Nested join field.
        """
        object_name = None
        if ":" in fs_splits[0]:
            column_name = fs_splits[0].split(":")[1]
            object_name = fs_splits[0].split(":")[0]
        else:
            column_name = fs_splits[0]

        # Check if the name can be found in fields.
        for f in self._qrepr.fields:
            if column_name == f.name:
                if len(fs_splits) > 1 and f.relation is not None:
                    return Query(f.relation).get_dtype("$".join(fs_splits[1:]))
                else:
                    return f

        if object_name is None:
            return None

        for r in self._qrepr.related:
            if r.name.split("/")[3] == object_name:
                if len(fs_splits) > 1:
                    return Query(r).get_dtype("$".join(fs_splits[1:]))
                else:
                    return Query(r).get_dtype(field_name)
        return None

    @staticmethod
    def _contains_parent_id(fs_ids: dict, name):
        parent = name
        while ":" in parent:
            parent = parent[0 : parent.rindex(":")]
            if "$" in parent:
                parent = parent[0 : parent.rindex("$")]
            if parent in fs_ids:
                return True

        return False

    @staticmethod
    def deserialize(encoded):
        nqp = management_types_pb2.Query()
        nqp.ParseFromString(encoded)
        return Query(nqp)

    @staticmethod
    def get_related_feature_sets(entity: str, featuresets: dict):
        ret_list = []
        for fs in featuresets:
            featureset = featuresets[fs]
            if featureset.schema.entity != entity:
                continue
            ret_list.append(featureset)
        return ret_list

    @staticmethod
    def form_query(
        query: dict = None,
        model=None,
        normalized: bool = False,
        related: bool = False,
        metadata: bool = False,
        path=None,
        all_featuresets: dict = None,
        level=0,
    ) -> management_types_pb2.Query:

        """Recursively forms a training data set query."""
        j_dict = query
        if j_dict is None:
            j_dict = management_types_pb2.Query()

        # Start with level 1.
        # MAX_ENTITY_DEPTH defines the maximum recursion of joins to do.
        level = level + 1

        is_model = False

        if model.name.split("/")[2] == "models":
            is_model = True

        model_id = model.name.split("/")[3]
        j_dict.name = model.name

        if not is_model:
            j_dict.entity_id = model.schema.entity
        if model.schema.table:
            j_dict.table_name = model.schema.table

        exclude_columns = []
        if model.schema.exclude_columns is not None:
            exclude_columns = set(model.schema.exclude_columns)

        for m in model.schema.columns:
            # TODO remove the metadata features if not requested.
            # if not metadata and not m.index and not m.time_index:
            #    continue
            qualified_name = m.name
            if related:
                qualified_name = model_id + ":" + m.name

            if path is not None:
                qualified_name = model_id + ":" + m.name
                qualified_name = path + "$" + qualified_name

            # TODO: track metadata field.
            qfeature = management_types_pb2.QueryFeature(
                name=m.name,
                type=m.type,
                dtype=m.dtype,
                qualified_name=qualified_name,
            )
            if is_model and m.name == model.schema.target:
                qfeature.model = True

            if (
                qfeature.type == management_types_pb2.INDEX
                or m.name == model.schema.index
            ):
                qfeature.index = True

            if (
                qfeature.type == management_types_pb2.TIME_INDEX
                or m.name == model.schema.time_index
            ):
                qfeature.time_index = True

            if qfeature.type == management_types_pb2.SPLIT or (
                is_model and m.name == model.schema.split
            ):
                qfeature.split = True

            if m.name in exclude_columns:
                qfeature.exclude = True

            if m.entity is not None and m.entity != "" and level < MAX_ENTITY_DEPTH:
                fss = Query.get_related_feature_sets(m.entity, all_featuresets)
                if fss == None or len(fss) == 0:
                    continue

                Query.form_query(
                    qfeature.relation,
                    fss[0],
                    None,
                    metadata=metadata,
                    path=qualified_name,
                    all_featuresets=all_featuresets,
                    level=level,
                )

            j_dict.fields.append(qfeature)
        if not related and not is_model and model.schema.entity is not None:
            all_fs = Query.get_related_feature_sets(
                model.schema.entity, all_featuresets
            )
            for fs in all_fs:
                if fs.name == model.name:
                    continue
                sub_query = management_types_pb2.Query()
                Query.form_query(
                    sub_query,
                    fs,
                    None,
                    related=True,
                    metadata=metadata,
                    path=path,
                    all_featuresets=all_featuresets,
                    level=level,
                )
                j_dict.related.append(sub_query)

        return Query(j_dict)
