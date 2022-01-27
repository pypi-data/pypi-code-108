from typing import List, Optional

from pyrasgo import schemas
from pyrasgo.primitives import Dataset, DataSource, Feature
from pyrasgo.primitives.dataset import DS_PUBLISHED_STATUS
from pyrasgo.utils import ingestion, naming
from tqdm import tqdm

from .error import APIError, APIWarning


class Save():

    def __init__(self):
        from pyrasgo.config import get_session_api_key
        from pyrasgo.storage import DataWarehouse, SnowflakeDataWarehouse

        from . import Create, Get, Match, Update
        from .connection import Connection

        api_key = get_session_api_key()
        self.api = Connection(api_key=api_key)
        self.data_warehouse: SnowflakeDataWarehouse = DataWarehouse.connect()
        self.get = Get()
        self.match = Match()
        self.create = Create()
        self.update = Update()

    def data_source(self, table: str,
                    name: str = None,
                    database: Optional[str] = None,
                    schema: Optional[str] = None,
                    source_code: Optional[str] = None,
                    domain: Optional[str] = None,
                    source_type: Optional[str] = None,
                    parent_source_id: Optional[int] = None,
                    if_exists: str = 'return'
                    ) -> DataSource:
        """
        Creates or updates a DataSource depending on the defined parameters

        if_exists:  return - returns the source without operating on it
                    edit - edits the existing source
                    new - creates a new source
        """
        fqtn = naming.make_fqtn(table=table, database=database, schema=schema)
        ds = self.match.data_source(fqtn=fqtn)
        if ds:
            if if_exists == 'return':
                return ds
            elif if_exists in ['edit', 'replace', 'append']:
                return self.update.data_source(id=ds.id, name=name, table=table, database=database, schema=schema, source_code=source_code, domain=domain, source_type=source_type, parent_source_id=parent_source_id)
            else:
                raise APIError(f"Table {fqtn} is already registered as Data Source {ds.id}")
        return self.create.data_source(name=name, table=table, database=database, schema=schema, source_code=source_code, domain=domain, source_type=source_type, parent_source_id=parent_source_id)

    def dataframe(self, unique_id: str,
                  name: str = None,
                  shared_status: str = None,
                  column_hash: Optional[str] = None,
                  update_date: str = None,
                  if_exists: str = 'return') -> schemas.Dataframe:
        """
        Creates or returns a Dataframe depending on of the defined parameters

        if_exists:  return - returns the source without operating on it
                    edit - edits the existing source
                    new - creates a new source
        """
        df = self.match.dataframe(unique_id=unique_id)
        if df:
            if if_exists == 'return':
                return df
            elif if_exists in ['edit', 'replace', 'append']:
                return self.update.dataframe(df.uniqueId, name, shared_status, column_hash, update_date)
            else:
                raise APIError(f"ID {unique_id} is already registered as DataFrame {df.id}")
        return self.create.dataframe(unique_id, name, shared_status, column_hash, update_date)

    def feature(self,
                data_source_id: int,
                column_name: str,
                display_name: str,
                data_type: str,
                description: Optional[str] = None,
                granularity: Optional[str] = None,
                status: Optional[str] = None,
                tags: Optional[List[str]] = None,
                git_repo: Optional[str] = None,
                if_exists: str = 'return') -> Feature:
        """
        Creates or updates a feature depending on existence of the defined parameters

        if_exists:  return - returns the source without operating on it
                    edit - edits the existing source
                    new - creates a new source
        """
        column_name = column_name or display_name
        description = description or f"Feature that contains {display_name} data"
        status = status or "Sandboxed"

        ft = self.match.feature(column_name=column_name, data_source_id=data_source_id)
        if ft:
            if if_exists == 'return':
                return ft
            elif if_exists in ['edit', 'replace', 'append']:
                return self.update.feature(id=ft.id, display_name=display_name, column_name=column_name, description=description, status=status, tags=tags or [], git_repo=git_repo)
            else:
                raise APIError(
                    f"Column {column_name} is already registered in DataSource {data_source_id} as Feature {ft.id}")
        return self.create.feature(data_source_id=data_source_id, display_name=display_name, column_name=column_name, description=description, status=status, git_repo=git_repo, tags=tags or [])

    def features_dict(self, features_dict: dict,
                      trigger_stats: bool = True) -> DataSource:
        """
        Creates or updates features based on values in a dict
        """
        if not ingestion._confirm_valid_dict(dict_in=features_dict):
            raise APIError("Not a valid dict")
        source_table = features_dict.get("sourceTable")
        ds_name = features_dict.get("name", source_table)
        # Using a set here to de-dup tags
        tags = set()
        if isinstance(features_dict.get("tags"), list):
            tags.update(features_dict.get("tags"))
        attributes = []
        # Handle two attribute formats:
        # 1) List of dicts
        if isinstance(features_dict.get("attributes"), list):
            for a in features_dict.get("attributes"):
                if isinstance(a, dict):
                    for k, v in a.items():
                        attributes.append({k: v})
        # 2) dict
        if isinstance(features_dict.get("attributes"), dict):
            for k, v in features_dict.get("attributes").items():
                attributes.append({k: v})
        source_code = features_dict.get("sourceCode")
        source_type = features_dict.get("sourceType")

        # Send a save request here, because it ignores missing fields
        # We don't want to overwrite attributes that aren't present in the dict
        data_source = self.data_source(
            table=source_table,
            name=ds_name,
            source_type=source_type,
            source_code=source_code,
            if_exists="edit")

        columns = data_source.columns

        # Assemble dimensions
        # for col in columns:
        put_dimensions = []
        for dim in features_dict["dimensions"]:
            column_name = dim.get("columnName")
            display_name = dim.get("displayName")
            data_type = dim.get("dataType")
            ds_column = [col.id for col in columns if col.name.upper() == column_name.upper()]
            if len(ds_column) > 0:
                ds_col_id = ds_column[0]
            else:
                APIWarning(f'Potential data issue encountered while publishing dimension: '
                           f'Column {column_name} not found in table {source_table}')
                ds_col_id = None
            # if we get an enum, convert it to str so pydantic doesn't get mad
            if isinstance(data_type, schemas.DataType):
                data_type = data_type.value
            dim_granularity = dim.get("granularity")
            put_dimensions.append(
                schemas.DimensionColumnPut(
                    dataSourceColumnId=ds_col_id,
                    columnName=column_name,
                    displayName=display_name,
                    granularityName=dim_granularity
                )
            )

        # Assemble features
        put_features = []
        for feature in features_dict["features"]:
            display_name = feature.get("displayName")
            column_name = feature.get("columnName")
            data_type = feature.get("dataType")
            ds_column = [col.id for col in columns if col.name.upper() == column_name.upper()]
            if len(ds_column) > 0:
                ds_col_id = ds_column[0]
            else:
                APIWarning(f'Potential data issue encountered while publishing feature: '
                           f'Column {column_name} not found in table {source_table}')
                ds_col_id = None
            # if we get an enum, convert it to str so pydantic doesn't get mad
            if isinstance(data_type, schemas.DataType):
                data_type = data_type.value
            description = feature.get("description", f"Feature that contains {display_name} data")
            # apply source tags to all features...
            feature_tags = tags
            # ...and add feature-specific tags
            if isinstance(feature.get("tags"), list):
                feature_tags.update(feature.get("tags"))
            feature_attributes = attributes
            if isinstance(feature.get("attributes"), list):
                for a in feature.get("attributes"):
                    if isinstance(a, dict):
                        for k, v in a.items():
                            feature_attributes.append({k: v})
            if isinstance(feature.get("attributes"), dict):
                for k, v in feature.get("attributes").items():
                    feature_attributes.append({k: v})
            attributes_put = []
            for kv in feature_attributes:
                for i in kv:
                    attributes_put.append(schemas.Attribute(key=i, value=kv[i]))
            status = "Sandboxed" if features_dict.get("status") == "Sandboxed" else "Productionized"
            put_features.append(
                schemas.FeatureColumnPut(
                    dataSourceColumnId=ds_col_id,
                    columnName=column_name,
                    displayName=display_name,
                    description=description,
                    status=status,
                    tags=list(feature_tags),
                    attributes=attributes_put
                )
            )

        source_out = self.source_features(
            id=data_source.id,
            table=data_source.table,
            name=data_source.name,
            database=data_source.tableDatabase,
            schema=data_source.tableSchema,
            source_code=data_source.sourceCode,
            domain=data_source.domain,
            source_type=data_source.sourceType,
            parent_source_id=data_source.parentId,
            columns=data_source.columns,
            features=put_features,
            dimensions=put_dimensions)

        # Post stats for features
        if trigger_stats:
            self.create.data_source_feature_stats(source_out.id)
        return source_out

    def column_importance_stats(self, id: str, payload: schemas.feature.FeatureImportanceStats):
        """
        Sends a json payload of importance from a dataFrame to the API so it can render in the WebApp
        """
        # First update timestamp on the DF object
        self.dataframe(unique_id=id, update_date=payload.timestamp, if_exists='edit')
        return self.create.column_importance_stats(id, payload)

    def feature_importance_stats(self, id: int, payload: schemas.feature.FeatureImportanceStats):
        """
        sends a JSON payload of importance from a collection to the API so it can store and render stats later
        """
        return self.create.feature_importance_stats(id=id, payload=payload)

    def dataframe_profile(self, id: str, payload: schemas.feature.ColumnProfiles):
        """
        Send a json payload of a dataframe profile so it can render in the WebApp
        """
        # First update timestamp on the DF object
        self.dataframe(unique_id=id, update_date=payload.timestamp, if_exists='edit')
        return self.create.dataframe_profile(id, payload)

    def source_features(self, id: int,
                        table: str,
                        name: str,
                        database: Optional[str],
                        schema: Optional[str],
                        source_code: Optional[str],
                        domain: Optional[str],
                        source_type: Optional[str],
                        parent_source_id: Optional[int],
                        columns: List[schemas.DataSourceColumnPut],
                        features: Optional[List[schemas.FeatureColumnPut]],
                        dimensions: Optional[List[schemas.DimensionColumnPut]],
                        if_exists: str = 'placebo'
                        ) -> DataSource:
        """
        Creates or updates a DataSource + its Features and Dimensions using the defined parameters
        """
        organization_id = self.api._profile.get('organizationId')
        data_source = schemas.DataSourcePut(name=name,
                                            table=table,
                                            tableDatabase=database,
                                            tableSchema=schema,
                                            sourceCode=source_code,
                                            domain=domain,
                                            sourceType=source_type,
                                            parentId=parent_source_id,
                                            columns=columns,
                                            features=features,
                                            dimensions=dimensions,
                                            organizationId=organization_id)
        response = self.api._put(f"/data-source/{id}/features", data_source.dict(), api_version=1).json()
        return DataSource(api_object=response)

