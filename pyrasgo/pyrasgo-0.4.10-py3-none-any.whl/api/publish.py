import pandas as pd
from pathlib import Path

from typing import List, Optional, Dict, Callable
import webbrowser
import yaml

from .error import APIError, ParameterValueError
from pyrasgo import schemas as api
from pyrasgo.primitives import Collection, FeatureList, DataSource, Dataset
from pyrasgo.primitives.dataset import DS_PUBLISHED_STATUS
from pyrasgo.storage.dataframe import utils as df_utils
from pyrasgo.utils import ingestion, naming, udf


class Publish():

    def __init__(self):
        from . import Create, Get, Match, Save, Update
        from .connection import Connection
        from pyrasgo.config import get_session_api_key
        from pyrasgo.storage import DataWarehouse, SnowflakeDataWarehouse

        api_key = get_session_api_key()
        self.api = Connection(api_key=api_key)
        self.data_warehouse: SnowflakeDataWarehouse = DataWarehouse.connect()
        self.get = Get()
        self.match = Match()
        self.create = Create()
        self.update = Update()
        self.save = Save()


    def experiment(self, df: pd.DataFrame,
                         dimensions: List[str],
                         granularity: List[str],
                         features: List[str] = None,
                         return_cli_only: bool = True,
                         verbose: bool = True) -> Collection:
        """
        Accepts a dataframe and publishes:
        - DataFrame as Rasgo DataSource
        - Dataframe columns as Rasgo Features
        - Rasgo Collection comprised of all Features

        params
        ------
        df: DataFrame: Pandas DataFrame to use as source data
        features: List[str]: List of columns to add as features.
                  If none is passed, all columns not in `dimensions` list will be registered as features
        dimensions: List[str]: List of columns to add as dimensions
        granularity: List[str]: List of granularities to apply to dimensions
        verbose: boolean: Print status statements to stdout while function executes

        Returns Rasgo Collection
        """
        features = features if features else []

        if verbose:
            print('Publishing DataFrame as a Rasgo DataSource')
        try:
            source = self.source_data(source_type='dataframe', df=df, verbose=verbose)
            if verbose:
                print('Successfully created:', source)
        except Exception as e:
            print(f'Failed to create DataSource: {e}')
            return
        if verbose:
            print('Creating Features from DataSource')
        try:
            dimensions, features = df_utils.confirm_df_columns(df, dimensions, features)
            source = self.features_from_source(source.id,
                                            features=features,
                                            dimensions=dimensions,
                                            granularity=granularity)
            features = FeatureList(**source.features)
            if verbose:
                print('Successfully created:', features)
        except Exception as e:
            print(f'Failed to create Features: {e}')
            return
        if verbose:
            print('Creating a Collection of your Features')
        try:
            collection = self.create.collection('name', 'Timeseries', granularity[0])
            collection.add_features(features)
            collection.generate_training_data()
            if verbose:
                print('Successfully created:', collection)
        except Exception as e:
            print(f'Failed to create Collection: {e}')
            return
        if not return_cli_only:
            webbrowser.open(f"app.rasgoml.com/collections/{collection.id}")
        return collection

    def features(self, features_dict: Dict,
                 trigger_stats: bool = True) -> DataSource:
        f"""
        Creates or updates Features based on metadata provided in the dict

        params:
            features_dict: Valid Rasgo dict (see below)

        return:
            Rasgo DataSource

        Valid Rasgo dict format:
        -----------------------
        {ingestion.RASGO_DICT}
        """
        # TODO need to publish docs on granularity and data types
        return self.save.features_dict(features_dict, trigger_stats)

    def features_from_df(self,
                         df: pd.DataFrame,
                         dimensions: List[str],
                         features: List[str],
                         granularity: List[str] = None,
                         tags: List[str] = None,
                         sandbox: bool = True):
        granularity = granularity if granularity else []
        tags = tags if tags else []
        raise NotImplementedError("`publish.features_from_df()` is a deprecated method. "
                                  "Please use `publish.features()` or `publish.features_from_source()` instead")

    def features_from_source(self,
                             data_source_id: int,
                             dimensions: List[str],
                             features: List[str] = None,
                             granularity: List[str] = None,
                             tags: List[str] = None,
                             sandbox: bool = True,
                             trigger_stats: bool = True,
                             if_exists: str = 'fail',
                             verbose: bool = False) -> DataSource:
        """
        Publishes Features from an existing DataSource table

        params:
            data_source_id: ID to a Rasgo DataSource
            features: List of column names that will be features
                      If none is passed, all columns not in `dimensions` list will be registered as features
            dimensions: List of column names that will be dimensions
            granularity: List of grains that describe the form of the data. Common values are: 'day', 'week', 'month', 'second'
            tags: List of tags to be added to all features
            sandbox: boolean: False = Production, True = Sandbox
            if_exists:  fail - returns an error message if features already exists against this table
                        return - returns the features without operating on them
                        edit - edits the existing features
                        new - creates new features
            verbose: boolean: Print status statements to stdout while function executes

        return:
            Rasgo DataSource
        """
        features = features if features else []
        granularity = granularity if granularity else []
        tags = tags if tags else []

        # Check for valid DataSource
        data_source = self.get.data_source(data_source_id)
        if not data_source.table:
            raise ValueError(f"DataSource {data_source_id} is not usable. Please make sure it exists and has a valid table registered.")
        if not isinstance(dimensions, list) and all([isinstance(dimension, str) for dimension in dimensions]):
            raise TypeError('Dimensions must be provided as a list of strings.')
        if not isinstance(features, list) and all([isinstance(feature, str) for feature in features]):
            raise TypeError('Features must be provided as a list of strings.')
        if not isinstance(granularity, list):
            if isinstance(granularity, str):
                granularity = [granularity]
            else:
                raise TypeError("granularity must be provided as a list of strings")
        if not isinstance(tags, list):
            if isinstance(tags, str):
                tags = [tags]
            else:
                raise TypeError("tags must be provided as a list of strings")
        if len(granularity) > len(dimensions):
            raise APIError("Number of granularities cannot exceed number of dimensions."
                           "Dimensions are the index fields your data should join on and group by."
                           "Granularity is an attribute that describes precision of your dimensions."
                           "Consider passing more dimensions or fewer granularities.")

        # Confirm requested features and dimensions are columns in the DataSource
        columns = data_source.columns
        if len(columns) == 0:
            raise APIError("This DataSource does not have any columns.")
        dimensions, features = df_utils.confirm_list_columns([c.name for c in columns], dimensions, features)

        # Assemble put request
        put_dimensions = []
        put_features = []
        for c in columns:
            if c.name in dimensions:
                if verbose:
                    print(f'Publishing dimension {c.name}')
                # Dimension / Granularity order matching:
                try:
                    # Try to match the position of the dim with the position of the granularity
                    dim_pos = dimensions.index(c.name)
                    dim_granularity = granularity[dim_pos] if len(granularity) > 1 else granularity[0]
                except:
                    # Otherwise default to the next granularity in the list
                    dim_granularity = granularity.pop(0) if len(granularity) > 1 else granularity[0]
                put_dimensions.append(
                    api.DimensionColumnPut(
                        dataSourceColumnId = c.id,
                        columnName=c.name,
                        displayName=c.name,
                        granularityName=dim_granularity
                    )
                )

            if c.name in features:
                if verbose:
                    print(f'Publishing feature {c.name}')
                put_features.append(
                    api.FeatureColumnPut(
                        dataSourceColumnId=c.id,
                        columnName=c.name,
                        displayName=c.name,
                        description=f"Feature {c.name} created from table {data_source.table}",
                        tags=tags,
                        status="Sandboxed" if sandbox else "Productionized"
                    )
                )

        source_out = self.save.source_features(
            id = data_source.id,
            table = data_source.table,
            name = data_source.name,
            database = data_source.tableDatabase,
            schema = data_source.tableSchema,
            source_code = data_source.sourceCode,
            domain = data_source.domain,
            source_type = data_source.sourceType,
            parent_source_id= data_source.parentId,
            columns = data_source.columns,
            features = put_features,
            dimensions = put_dimensions)

        if trigger_stats:
            if verbose:
                print("Triggering stats for all features. These may take a few minutes to run.")
            self.create.data_source_feature_stats(source_out.id)
        return source_out

    def features_from_source_code(self,
                                  data_source_id: int,
                                  source_code_type: str,
                                  dimensions: List[str],
                                  features: List[str] = None,
                                  granularity: List[str] = None,
                                  tags: List[str] = None,
                                  sql_definition: str = None,
                                  python_function: Callable[[pd.DataFrame], pd.DataFrame] = None,
                                  derivative_source_name: str = None,
                                  sql_view_name: str = None,
                                  sandbox: bool = True,
                                  sql_risk_override: bool = False,
                                  trigger_stats: bool = True,
                                  if_exists: str = 'fail',
                                  verbose: bool = False) -> DataSource:
        """
        Publishes a new derivative DataSource from an existing DataSource table using sql or python code
        and registers Features against columns in the new DataSource

        params:
            data_source_id: ID of an existing Rasgo DataSource that will act as the parent of the derivative source
            source_code_type: Valid string values are ['sql', 'python']
            sql_definition: Valid sql select statement that can create a view
            sql_view_name: ANSI-compliant string to name the new view
            python_function: Valid python function that accepts a dataframe as input and returns a dataframe of features
            features: List of column names that will be features
                      If none is passed, all columns not in `dimensions` list will be registered as features
            dimensions: List of column names that will be dimensions
            granularity: List of grains that describe the form of the data. Common values are: 'day', 'week', 'month', 'second'
            tags: List of tags to be added to all features
            derivative_source_name: Metadata name for the new DataSource being created
            sandbox: boolean: False = Production, True = Sandbox
            sql_risk_override: boolean: pass True if you receive a warning message about a dangerous sql keyword
            if_exists:  fail - returns an error message if features already exists against this table
                        return - returns the features without operating on them
                        edit - edits the existing features
                        new - creates new features
            verbose: boolean: Print status statements to stdout while function executes

        return:
            Rasgo DataSource
        """
        features = features if features else []
        granularity = granularity if granularity else []
        tags = tags if tags else []

        source_code_type = source_code_type.lower()
        if source_code_type not in ["sql", "python"]:
            raise ParameterValueError("source_code_type", ["sql", "python"])
        if source_code_type == "sql" and not sql_definition:
                raise ParameterValueError("sql_definition", ["Valid sql select statement that can create a veiw"])
        elif source_code_type == "python" and not python_function:
                raise ParameterValueError("python_function", ["Valid python function that accepts a dataframe as input and returns a dataframe of features"])

        # Publish the new data as a source
        # First make sure this is a valid source
        parent_source = self.get.data_source(data_source_id)
        if verbose:
            print(f"Publishing derivative source from parent source {parent_source.table}")
        child_source = self.source_data(source_type=source_code_type,
                                        sql_definition=sql_definition if source_code_type == "sql" else None,
                                        python_function=python_function if source_code_type == "python" else None,
                                        data_source_name=derivative_source_name,
                                        data_source_table_name=sql_view_name,
                                        parent_data_source_id=data_source_id,
                                        sql_risk_override=sql_risk_override,
                                        trigger_stats=trigger_stats,
                                        if_exists=if_exists)

        if not child_source:
            raise APIError(f"Unable to create a derivative source from the {source_code_type} code provided."
                            "Please check that it creates a valid view or dataframe and try again.")

        # Then publish features
        if verbose:
            print(f"Publishing features from derivative source {child_source.id}")
        return self.features_from_source(data_source_id=child_source.id,
                                         features=features,
                                         dimensions=dimensions,
                                         granularity=granularity,
                                         tags=tags,
                                         sandbox=sandbox,
                                         trigger_stats=trigger_stats,
                                         if_exists=if_exists)

    def features_from_yml(self,
                          yml_file: str,
                          sandbox: Optional[bool] = True,
                          git_repo: Optional[str] = None,
                          trigger_stats: bool = True,
                          verbose: bool = False) -> DataSource:
        """
        Publishes metadata about Features to Pyrasgo

        params:
            yml_file: Rasgo compliant yml file that describes the feature(s) being created
            sandbox: Status of the features (True = 'Sandboxed' | False = 'Productionized')
            git_repo: Filepath string to these feature recipes in git
            verbose: boolean: Print status statements to stdout while function executes

        return:
            Rasgo DataSource
        """
        with open(yml_file) as fobj:
            if verbose:
                print("Unpacking yml")
            contents = yaml.load(fobj, Loader=yaml.SafeLoader)
        if isinstance(contents, list):
            raise APIError("More than one feature set found, please pass in only one feature set per yml")
        else:
            if verbose:
                print("Publishing features")
            features = self.save.features_dict(contents, trigger_stats)
        return features

    def source_data(self,
                    source_type: str,
                    file_path: Path = None,
                    df: pd.DataFrame = None,
                    table: str = None,
                    table_database: Optional[str] = None,
                    table_schema: Optional[str] = None,
                    sql_definition: str = None,
                    python_function: Optional[Callable[[pd.DataFrame], pd.DataFrame]] = None,
                    data_source_name: str = None,
                    data_source_domain: str = None,
                    data_source_table_name: str = None,
                    parent_data_source_id: Optional[int] = None,
                    sql_risk_override: bool = False,
                    trigger_stats: bool = True,
                    if_exists: str = 'fail',
                    verbose: bool = True
                    ) -> DataSource:
        """
        Push a csv, Dataframe, or table to a Snowflake table and register it as a Rasgo DataSource (TM)

        NOTES: csv files will import all columns as strings

        params:
            source_type: Values: ['csv', 'dataframe', 'table', 'sql', 'python']
            df: pandas DataFrame (only use when passing source_type = 'dataframe')
            file_path: full path to a file on your local machine (only use when passing source_type = 'csv')
            table: name of a valid Snowflake table in your Rasgo account (only use when passing source_type = 'table')
            table_database: Optional: name of the database of the table passed in 'table' param (only use when passing source_type = 'table')
            table_schema: Optional: name of the schema of the table passed in 'table' param (only use when passing source_type = 'table')
            sql_definition: Optional: valid SQL string that will create a new view in your DataWarehous
            python_function: Optional: valid python function that accepts a dataframe as input and returns a dataframe of features
            data_source_name: Optional name for the DataSource (if not provided a random string will be used)
            data_source_table_name: Optional name for the DataSource table in Snowflake (if not provided a random string will be used)
            data_source_domain: Optional domain for the DataSource (default is NULL)
            parent_data_source_id: Optional ID of a valid Rasgo DataSource that is a parent to this DataSource (default is NULL)
            sql_risk_override: boolean: pass True if you receive a warning message about a dangerous sql keyword
            if_exists: Values: ['fail', 'append', 'replace'] directs the function what to do if a DataSource already exists with this table name  (defaults to fail)
            verbose: boolean: Print status statements to stdout while function executes

        return:
            Rasgo DataSource
        """
        # V1 Trade-offs / Possible Future Enhancements
        # --------------
        # csv's upload with all columns as string data type
        # uploading csv locally vs. calling the post/data-source/csv endpoint

        # Validate inputs
        vals = ["csv", "dataframe", "table", "sql", "python"]
        source_type = source_type.lower()
        _org_defaults = self.api._get_default_namespace()

        if source_type not in vals:
            raise ParameterValueError("source_type", vals)
        if source_type == "csv" and not Path(file_path).exists():
                raise FileNotFoundError("Please pass in a valid file path using the `file_path` parameter")
        if source_type == "dataframe":
            if not isinstance(df, pd.DataFrame) or df.empty:
                raise ValueError("Please pass in a valid DataFrame using the `df` parameter")
        if source_type == 'sql':
            if not sql_definition:
                raise ValueError('Please pass in a valid SQL string using the `sql_definition` parameter')
            #check for dangerous sql
            if naming._is_scary_sql(sql_definition) and not sql_risk_override:
                # NOTE: In the future we will want to send an email to the account owner
                #       or require special permissions to run with a sql_risk_override param
                raise ValueError("It looks like the sql string you passed may have some potentially dangerous keywords in it like DELETE or DROP or TRUNCATE. "
                                 "This SQL will be used to create a view in your DataWarehouse. Please ensure this is the code you want to run. "
                                 "If you're confident in your code, please pass in the parameter `sql_risk_override=True` to run this code.")
            if not naming._is_valid_view_sql(sql_definition) and not sql_risk_override:
                raise ValueError("It looks like the sql string you passed is missing basic elements like a SELECT or FROM clause. "
                                 "This SQL will be used to create a view in your DataWarehouse. Please ensure this is the code you want to run. "
                                 "If you're confident in your code, please pass in the parameter `sql_risk_override=True` to run this code.")
        if source_type == "table":
            if not table:
                raise ValueError("Please pass in a valid table using the `table` parameter")
            if if_exists in ["append", "replace"]:
                # Raise this as an error after we've confirmed there will be no backwards compat issues
                print("Data Sources built from SQL tables do not physically append or replace data, proceeding with a no-op registration.")
            parsed_database, parsed_schema, parsed_table = naming.parse_fqtn(table, _org_defaults)
            table = parsed_table
            table_database = table_database or parsed_database
            table_schema = table_schema or parsed_schema
            try:
                src_table = self.data_warehouse.get_source_table(table_name=table, database=table_database, schema=table_schema, record_limit=10)
                if src_table.empty:
                    raise APIError(f"Source table {table} is empty or this role does not have access to it.")
            except:
                raise APIError(f"Source table {table} does not exist or this role does not have access to it.")
        if data_source_table_name == "":
            raise ValueError("The `data_source_table_name` parameter was passed as a blank string, please pass in a valid SQL table name")

        if source_type == "python":
            if not python_function:
                raise ValueError("Please pass in a valid python function using the `python_function` parameter")
            if not parent_data_source_id:
                raise ValueError("Please pass in a valid data source for processing via python function ")
            udf.is_valid_udf(python_function)

        # Determine the ouput table based on user inputs
        if source_type in ["csv", "dataframe", "sql", "python"]:
            table_name = data_source_table_name or naming.random_table_name()
        else: #source_type == "table":
            table_name = table
        table_name = table_name.upper()
        table_database = table_database if source_type == "table" else _org_defaults.get('database')
        table_schema = table_schema if source_type == "table" else _org_defaults.get('schema')
        table_fqtn = naming.make_fqtn(table=table_name, database=table_database, schema=table_schema)

        # Check if a DataSource already exists
        data_source = self.match.data_source(fqtn=table_fqtn)
        if data_source:
            # If it does, override to the existing table
            table_name = data_source.table
            table_database = data_source.tableDatabase
            table_schema = data_source.tableSchema
            table_fqtn = naming.make_fqtn(table=table_name, database=table_database, schema=table_schema)

            # Then handle input directives
            vals = ["append", "fail", "replace"]
            msg = f"DataSource {data_source.id} already exists. "
            if data_source.organizationId != self.api._profile.get('organizationId'):
                raise APIError(msg+"This API key does not have permission to replace it.")
            if data_source.sourceType.lower() != source_type:
                raise APIError(msg+f"Your input parameters would edit the source_type from {data_source.sourceType.lower()} to {source_type}. "
                                    "To change DataSource attributes, use the `update.data_source` method. "
                                    "To update this source table, ensure your input parameters match the DataSource definition.")
            if if_exists not in vals:
                raise ParameterValueError("if_exists", vals)
            if if_exists == 'fail':
                raise APIError(msg+"Pass if_exists='replace' or 'append' to proceed.")

        # Determine operation to perform: [create, append, replace, register, no op]
        _operation = self._source_table_operation(source_type, if_exists, table_fqtn, org_defaults=_org_defaults)
        if verbose:
            print(f"Proceeding with operation {_operation}")

        # Upload to Snowflake
        # Path: csv & dataframe
        if source_type in ["csv", "dataframe"]:
            if source_type == "csv":
                df = pd.read_csv(file_path)
            if verbose:
                print("Uploading to table:", table_name)
            df_utils._cleanse_sql_dataframe(df)
            self.data_warehouse.write_dataframe_to_table(df, table_name=table_name, append=True if if_exists=="append" else False)
            self.data_warehouse.grant_table_ownership(table=table_name, role=self.data_warehouse.publisher_role)
            self.data_warehouse.grant_table_access(table=table_name, role=self.data_warehouse.reader_role)

        # Path: python
        if source_type == "python":
            # Get df from parent source, run function, upload result df as new table
            parent_table_name = self.get.data_source(parent_data_source_id).table
            source_df = self.data_warehouse.get_source_table(table_name=parent_table_name)
            result_df = python_function(source_df)
            if verbose:
                print("Creating table with python transformed dataframe:", table_name)
            df_utils._cleanse_sql_dataframe(result_df)
            self.data_warehouse.write_dataframe_to_table(result_df, table_name=table_name, append=True if if_exists=="append" else False)
            self.data_warehouse.grant_table_ownership(table=table_name, role=self.data_warehouse.publisher_role)
            self.data_warehouse.grant_table_access(table=table_name, role=self.data_warehouse.reader_role)

        # Path: sql
        if source_type == "sql":
            view_query = f"CREATE OR REPLACE VIEW {table_name} AS {sql_definition};"
            if verbose:
                print("Creating sql view as:", view_query)
            self.data_warehouse.execute_query(view_query)
            self.data_warehouse.grant_table_ownership(table=table_name, role=self.data_warehouse.publisher_role)
            self.data_warehouse.grant_table_access(table=table_name, role=self.data_warehouse.reader_role)

        # Path: table
        if source_type == "table":
            if verbose:
                print(f"Granting read access on table {table_name} to {self.data_warehouse.reader_role.upper()}")
            # NOTE: grant_table_acess is intentional here
            # In other methods, we create a table with the rasgo user role and want to hand if off to the reader role
            # In this case, the table is likely part of a pre-existing rbac model and we just want to grant rasgo access
            self.data_warehouse.grant_table_access(table=table_name, role=self.data_warehouse.reader_role, database=table_database, schema=table_schema)

        source_code = None
        if source_type == 'sql':
            source_code = sql_definition
        elif source_type == 'python':
            source_code = udf.stringify_udf(python_function)

        # Publish DataSource
        data_source = self.save.data_source(name=data_source_name or table_name,
                                            table=table_name,
                                            database=table_database if source_type == 'table' else _org_defaults.get('database'),
                                            schema=table_schema if source_type == 'table' else _org_defaults.get('schema'),
                                            source_code=source_code,
                                            domain=data_source_domain,
                                            source_type=source_type,
                                            parent_source_id=parent_data_source_id,
                                            if_exists='edit')
        if data_source:
            if trigger_stats:
                self.create.data_source_stats(data_source.id)
            return data_source
        else:
            raise APIError("DataSource failed to upload")

    def _source_table_operation(self,
                                source_type: str,
                                if_exists: str,
                                to_fqtn: str,
                                from_fqtn: Optional[str] = None,
                                org_defaults: Optional[Dict] = None):
        """
        Called by publish_source_data:
            Given a source_type and tables, return the operation that should be performed to publish this table
        """
        to_database, to_schema, to_table = naming.parse_fqtn(to_fqtn, org_defaults)
        data_source_exists = True if self.match.data_source(fqtn=to_fqtn) is not None else False

        try:
            dest_table = self.data_warehouse.get_source_table(table_name=to_table, database=to_database, schema=to_schema, record_limit=10)
            is_dest_table_empty = dest_table.empty
        except:
            is_dest_table_empty = True

        if source_type in ["csv", "dataframe", "sql", "python"]:
            if not data_source_exists:
                if is_dest_table_empty:
                    return "create"
                else: #not is_dest_table_empty
                    raise APIError(f"A table named {to_fqtn} already exists, but is not registered as a Rasgo DataSource. "
                                   f"Try running this function with params: source_type='table', table='{to_table}'. "
                                    "If this wasn't an intentional match, run this function again to generate a new table name.")
            elif data_source_exists:
                if is_dest_table_empty:
                    return "create"
                else: #not is_dest_table_empty
                    return if_exists
            else:
                raise APIError("Could not determine what operation to perform.")
        elif source_type == "table":
            if not data_source_exists:
                return "register"
            elif not is_dest_table_empty and if_exists in ["append", "replace"]:
                print(f"pyRasgo does not support {if_exists} operations on tables yet.")
            return "no op"
        else:
            raise APIError("Could not determine what operation to perform.")

    def table(
            self,
            fqtn: str,
            name: Optional[str] = None,
            description: Optional[str] = None,
            # parent_dataset_id: Optional[List[int]] = None, TODO
            verbose: bool = False
    ) -> Dataset:
        """
        Register an existing table as a Rasgo Dataset

        params:
            fqtn: The fully qualified table name of the table to register
            name: Optional name to apply to this Rasgo Dataset
            description: Optional description for this Rasgo Dataset
            verbose: Print status statements to stdout while function executes if true
        return:
            Rasgo Dataset
        """
        if verbose:
            print("Publishing table as Rasgo dataset")

        if fqtn.count(".") != 2:
            raise ValueError(f"'{fqtn}' is not a valid fully qualified table name. "
                             f"FQTNs should follow the format DATABASE.SCHEMA.TABLE_NAME.  "
                             f"Please pass a valid FQTN and try again")

        table_database, table_schema, table_name = fqtn.split('.')

        try:
            src_table = self.data_warehouse.get_source_table(
                table_name=table_name,
                database=table_database,
                schema=table_schema,
                record_limit=10
            )
            if src_table.empty:
                raise APIError(f"Source table {table_name} is empty or this role "
                               f"does not have access to it.")
        except:
            raise APIError(f"Source table {table_name} does not exist or this role "
                           f"does not have access to it.")

        # TODO: Re-implement when search by fqtn is available. For now, we'll trust the API to enforce uniqeness on fqtns
        # Check if a Dataset already exists
        # dataset = self.match.dataset(fqtn=fqtn)
        # if dataset:
        #     raise APIError(f"Dataset {dataset.id} already exists in Rasgo")

        # NOTE: grant_table_access is intentional here
        # In other methods, we create a table with the rasgo user role and want to hand if off to the reader role
        # In this case, the table is likely part of a pre-existing rbac model and we just want to grant rasgo access
        self.data_warehouse.grant_table_access(
            table=table_name,
            role=self.data_warehouse.reader_role,
            database=table_database,
            schema=table_schema
        )

        # Publish Dataset
        dataset = self.create._dataset(name=name or table_name,
                                       description=description,
                                       fqtn=fqtn,
                                       status=DS_PUBLISHED_STATUS)
        # Raise API error if backend error creating dataset
        if not dataset:
            raise APIError("DataSource failed to upload")

        # Return dataset if no error
        if verbose:
            print("Done publishing table as Rasgo dataset")
        return Dataset(api_dataset=dataset)

    def df(
            self,
            df: pd.DataFrame = None,
            name: Optional[str] = None,
            description: Optional[str] = None,
            dataset_table_name: str = None,
            # parent_dataset_id: Optional[List[int]] = None, TODO
            verbose: bool = False
    ) -> Dataset:
        """
        Push a Pandas Dataframe a Data Warehouse table and register it as a Rasgo Dataset

        params:
            df: pandas DataFrame
            dataset_name: Optional name for the Dataset (if not provided a random string will be used)
            description: Optional description for this Rasgo Dataset
            dataset_table_name: Optional name for the Dataset table in Snowflake (if not provided a random string will be used)
            verbose: Print status statements to stdout while function executes if true
        return:
            Rasgo Dataset
        """
        if verbose:
            print("Publishing df as Rasgo dataset")
        _org_defaults = self.api._get_default_namespace()
        table_name = (dataset_table_name or naming.random_table_name()).upper()
        name = name or table_name
        table_database = _org_defaults.get('database')
        table_schema = _org_defaults.get('schema')
        fqtn = naming.make_fqtn(table=table_name, database=table_database, schema=table_schema)

        df_utils._cleanse_sql_dataframe(df)
        self.data_warehouse.write_dataframe_to_table(df, table_name=table_name, append=False)
        self.data_warehouse.grant_table_ownership(table=table_name, role=self.data_warehouse.publisher_role)
        self.data_warehouse.grant_table_access(table=table_name, role=self.data_warehouse.reader_role)

        # Create dataset based on new table FQTN created from df
        dataset = self.table(fqtn=fqtn, name=name, description=description, verbose=verbose)
        if verbose:
            print("Done publishing df as Rasgo dataset")
        return dataset

    def dataset(
            self,
            dataset: Dataset,
            name: str,
            description: Optional[str] = None,
            verbose: bool = False
    ) -> Dataset:
        """
        Saves a transformed Dataset in Rasgo to published
        Args:
            dataset: Dataset to save
            name: Name of dataset
            description: Description of dataset
            verbose: If true will print save progress status
        """
        # Saving of previously-existing Datasets is not allowed
        if dataset._api_dataset:
            raise APIError(f"This Dataset already exists in Rasgo. "
                           f"{dataset}. Transform the dataset to save it.")
        if verbose:
            print(f"Saving Dataset with name={name!r} description={description!r}...")
        operation_set = dataset._get_or_create_op_set()
        dataset = self.create._dataset(
            name=name,
            description=description,
            status=DS_PUBLISHED_STATUS,
            dw_table_id=operation_set.operations[-1].dw_table_id,
            dw_operation_set_id=operation_set.id
        )
        dataset = Dataset(api_dataset=dataset, api_operation_set=operation_set)
        if verbose:
            print(f"Finished Saving {dataset}")
        return dataset