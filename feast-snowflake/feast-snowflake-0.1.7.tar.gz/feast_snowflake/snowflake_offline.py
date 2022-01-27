import contextlib
from datetime import datetime
from typing import Callable, ContextManager, Dict, Iterator, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import pyarrow as pa
from pydantic.typing import Literal
from pydantic import Field

from feast import OnDemandFeatureView
from feast.data_source import DataSource
from feast.errors import InvalidEntityType
from feast.feature_view import (
    DUMMY_ENTITY_ID,
    DUMMY_ENTITY_NAME,
    DUMMY_ENTITY_VAL,
    FeatureView,
)
from feast.infra.offline_stores import offline_utils
from feast.infra.offline_stores.offline_store import OfflineStore, RetrievalJob
from feast_snowflake.snowflake_utils import (
    create_new_snowflake_table,
    get_snowflake_conn,
    write_pandas
)
from feast.registry import Registry
from feast.repo_config import FeastConfigBaseModel, RepoConfig

from feast_snowflake.snowflake_source import SnowflakeSource

try:
    from snowflake.connector import SnowflakeConnection
    from snowflake.connector.pandas_tools import write_pandas
except ImportError as e:
    from feast.errors import FeastExtrasDependencyImportError

    raise FeastExtrasDependencyImportError("snowflake", str(e))

from pathlib import Path
import os


class SnowflakeOfflineStoreConfig(FeastConfigBaseModel):
    """ Offline store config for Snowflake """

    type: Literal["feast_snowflake.SnowflakeOfflineStore"] = "feast_snowflake.SnowflakeOfflineStore"
    """ Offline store type selector"""

    config_path: Optional[str] = Path(os.environ['HOME']) / '.snowsql/config'
    """ Snowflake config path -- absolute path required (Cant use ~)"""

    account: Optional[str] = None
    """ Snowflake deployment identifier -- drop .snowflakecomputing.com"""

    user: Optional[str] = None
    """ Snowflake user name """

    password: Optional[str] = None
    """ Snowflake password """

    role: Optional[str] = None
    """ Snowflake role name"""

    warehouse: Optional[str] = None
    """ Snowflake warehouse name """

    database: Optional[str] = None
    """ Snowflake database name """

    schema_: Optional[str] = Field("PUBLIC", alias="schema")
    """ Snowflake schema name """

class SnowflakeOfflineStore(OfflineStore):
    @staticmethod
    def pull_latest_from_table_or_query(
        config: RepoConfig,
        data_source: DataSource,
        join_key_columns: List[str],
        feature_name_columns: List[str],
        event_timestamp_column: str,
        created_timestamp_column: Optional[str],
        start_date: datetime,
        end_date: datetime,
    ) -> RetrievalJob:
        assert isinstance(data_source, SnowflakeSource)
        assert isinstance(config.offline_store, SnowflakeOfflineStoreConfig)

        from_expression = (
            data_source.get_table_query_string()
        )  # returns schema.table as a string

        if join_key_columns:
            partition_by_join_key_string = '"' + '", "'.join(join_key_columns) + '"'
            partition_by_join_key_string = (
                "PARTITION BY " + partition_by_join_key_string
            )
        else:
            partition_by_join_key_string = ""

        timestamp_columns = [event_timestamp_column]
        if created_timestamp_column:
            timestamp_columns.append(created_timestamp_column)

        timestamp_desc_string = '"' + '" DESC, "'.join(timestamp_columns) + '" DESC'
        field_string = (
            '"'
            + '", "'.join(join_key_columns + feature_name_columns + timestamp_columns)
            + '"'
        )

        snowflake_conn = get_snowflake_conn(config.offline_store)

        query = f"""
            SELECT
                {field_string}
                {f''', TRIM({repr(DUMMY_ENTITY_VAL)}::VARIANT,'"') AS "{DUMMY_ENTITY_ID}"''' if not join_key_columns else ""}
            FROM (
                SELECT {field_string},
                ROW_NUMBER() OVER({partition_by_join_key_string} ORDER BY {timestamp_desc_string}) AS "_feast_row"
                FROM {from_expression}
                WHERE "{event_timestamp_column}" BETWEEN TO_TIMESTAMP('{start_date}') AND TO_TIMESTAMP('{end_date}')
            )
            WHERE "_feast_row" = 1
            """

        return SnowflakeRetrievalJob(
            query=query,
            snowflake_conn=snowflake_conn,
            config=config,
            full_feature_names=False,
            on_demand_feature_views=None,
        )

    @staticmethod
    def get_historical_features(
        config: RepoConfig,
        feature_views: List[FeatureView],
        feature_refs: List[str],
        entity_df: Union[pd.DataFrame, str],
        registry: Registry,
        project: str,
        full_feature_names: bool = False,
    ) -> RetrievalJob:
        assert isinstance(config.offline_store, SnowflakeOfflineStoreConfig)

        snowflake_conn = get_snowflake_conn(config.offline_store)

        @contextlib.contextmanager
        def query_generator() -> Iterator[str]:
            table_name = offline_utils.get_temp_entity_table_name()

            entity_schema = _upload_entity_df_and_get_entity_schema(
                entity_df, snowflake_conn, config, table_name
            )

            entity_df_event_timestamp_col = offline_utils.infer_event_timestamp_from_entity_df(
                entity_schema
            )

            expected_join_keys = offline_utils.get_expected_join_keys(
                project, feature_views, registry
            )

            offline_utils.assert_expected_columns_in_entity_df(
                entity_schema, expected_join_keys, entity_df_event_timestamp_col
            )

            entity_df_timestamp_range = _get_entity_df_event_timestamp_range(
                entity_df, entity_df_event_timestamp_col, snowflake_conn, config, table_name,
            )

            # Build a query context containing all information required to template the Snowflake SQL query
            query_context = offline_utils.get_feature_view_query_context(
                feature_refs, feature_views, registry, project, entity_df_timestamp_range
            )

            query_context = _fix_entity_selections_identifiers(query_context)

            # Generate the Snowflake SQL query from the query context
            query = offline_utils.build_point_in_time_query(
                query_context,
                left_table_query_string=table_name,
                entity_df_event_timestamp_col=entity_df_event_timestamp_col,
                entity_df_columns=entity_schema.keys(),
                query_template=MULTIPLE_FEATURE_VIEW_POINT_IN_TIME_JOIN,
                full_feature_names=full_feature_names,
            )

            yield query

        return SnowflakeRetrievalJob(
            query=query_generator,
            snowflake_conn=snowflake_conn,
            config=config,
            full_feature_names=full_feature_names,
            on_demand_feature_views=OnDemandFeatureView.get_requested_odfvs(
                feature_refs, project, registry
            ),
        )


class SnowflakeRetrievalJob(RetrievalJob):
    def __init__(
        self,
        query: Union[str, Callable[[], ContextManager[str]]],
        snowflake_conn: SnowflakeConnection,
        config: RepoConfig,
        full_feature_names: bool,
        on_demand_feature_views: Optional[List[OnDemandFeatureView]],
    ):

        if not isinstance(query, str):
            self._query_generator = query
        else:

            @contextlib.contextmanager
            def query_generator() -> Iterator[str]:
                assert isinstance(query, str)
                yield query

            self._query_generator = query_generator

        self.snowflake_conn = snowflake_conn
        self.config = config
        self._full_feature_names = full_feature_names
        self._on_demand_feature_views = (on_demand_feature_views if on_demand_feature_views else [])

    @property
    def full_feature_names(self) -> bool:
        return self._full_feature_names

    @property
    def on_demand_feature_views(self) -> Optional[List[OnDemandFeatureView]]:
        return self._on_demand_feature_views

    def _to_df_internal(self) -> pd.DataFrame:
        with self._query_generator() as query:

            with self.snowflake_conn as conn:

                df = conn.cursor().execute(query).fetch_pandas_all()

        return df

    def _to_arrow_internal(self) -> pa.Table:
        with self._query_generator() as query:

            with self.snowflake_conn as conn:

                pa_table = conn.cursor().execute(query).fetch_arrow_all()

                if pa_table:

                    return pa_table
                else:
                    empty_result = conn.cursor().execute(query)

                    return pa.Table.from_pandas(
                        pd.DataFrame(columns=[md.name for md in empty_result.description])
                    )

    # Used when we use snowflake as a provider
    # currently no support for odfv
    def _to_internal_table(
        self, feature_view: FeatureView, feature_name_columns: List[str]
    ) -> None:
        with self._query_generator() as query:

            feature_name_str = "', '".join(feature_name_columns)

            if feature_view.entities[0] == DUMMY_ENTITY_NAME:
                entity_key = DUMMY_ENTITY_ID
            else:
                entity_key = feature_view.entities[0]

            query = f"""
                INSERT OVERWRITE INTO "{self.config.online_store.database}"."{self.config.online_store.schema_}"."{self.config.project}_{feature_view.name}"
                    SELECT
                        "entity_key"::VARIANT,
                        "feature_name",
                        "value",
                        "event_ts",
                        "created_ts"
                    FROM
                    (
                      SELECT
                        *,
                        ROW_NUMBER() OVER(PARTITION BY "entity_key","feature_name" ORDER BY "event_ts" DESC, "created_ts" DESC) AS "_feast_row"
                      FROM
                      (
                        SELECT
                            "entity_key",
                            PATH AS "feature_name",
                            VALUE AS "value",
                            "event_ts",
                            "created_ts"
                        FROM
                        (
                          SELECT
                            "{entity_key}" AS "entity_key",
                            OBJECT_PICK(OBJECT_CONSTRUCT(*), '{feature_name_str}') AS "feature_name",
                            "event_timestamp" AS "event_ts",
                            "created" AS "created_ts"
                          FROM
                          (
                            {query}
                          )
                        ), LATERAL FLATTEN(INPUT => "feature_name")
                        UNION ALL
                        SELECT
                            *
                        FROM
                            "{self.config.online_store.database}"."{self.config.online_store.schema_}"."{self.config.project}_{feature_view.name}"
                      )
                    )
                    WHERE
                      "_feast_row" = 1;
                """

            with self.snowflake_conn as conn:

                conn.cursor().execute(query)

        return None

    def to_snowflake(self, table_name: str) -> None:
        """ Save dataset as a new Snowflake table """
        with self.snowflake_conn as conn:

            if self.on_demand_feature_views is not None:
                transformed_df = self.to_df()

                create_new_snowflake_table(conn, transformed_df, table_name)
                write_pandas(conn, transformed_df, table_name)

                return None

            with self._query_generator() as query:
                query = f'CREATE TABLE IF NOT EXISTS "{table_name}" AS ({query});\n'

                cur = conn.cursor().execute(query)

    def to_sql(self) -> str:
        """
        Returns the SQL query that will be executed in Snowflake to build the historical feature table.
        """
        with self._query_generator() as query:
            return query

    def to_arrow_chunks(self, arrow_options: Optional[Dict] = None) -> list:
        with self._query_generator() as query:

            with self.snowflake_conn as conn:

                arrow_batches = conn.cursor().execute(query).get_result_batches()

        return arrow_batches


def _upload_entity_df_and_get_entity_schema(
    entity_df: Union[pd.DataFrame, str],
    conn: SnowflakeConnection,
    config: RepoConfig,
    table_name: str,
) -> Dict[str, np.dtype]:

    if isinstance(entity_df, pd.DataFrame):
        # If the entity_df is a pandas dataframe, upload it to Snowflake
        # and construct the schema from the original entity_df dataframe

        # Write the data from the DataFrame to the table
        create_new_snowflake_table(
            conn, entity_df, table_name, alt_table_type="temporary"
        )
        write_pandas(conn, entity_df, table_name)

        return dict(zip(entity_df.columns, entity_df.dtypes))
    elif isinstance(entity_df, str):
        # If the entity_df is a string (SQL query), create a Snowflake table out of it,
        # get pandas dataframe consisting of 1 row (LIMIT 1) and generate the schema out of it
        conn.cursor().execute(
            f'CREATE TEMPORARY TABLE "{table_name}" AS ({entity_df})',
        )

        limited_entity_df = SnowflakeRetrievalJob(
            f'SELECT * FROM "{table_name}" LIMIT 1',
            conn,
            config,
            full_feature_names=False,
            on_demand_feature_views=None,
        ).to_df()

        return dict(zip(limited_entity_df.columns, limited_entity_df.dtypes))
    else:
        raise InvalidEntityType(type(entity_df))


def _fix_entity_selections_identifiers(query_context) -> list:

    for i, qc in enumerate(query_context):
        for j, es in enumerate(qc.entity_selections):
            query_context[i].entity_selections[j] = f'"{es}"'.replace(" AS ", '" AS "')

    return query_context

def _get_entity_df_event_timestamp_range(
    entity_df: Union[pd.DataFrame, str],
    entity_df_event_timestamp_col: str,
    snowflake_client,
    config: RepoConfig,
    table_name: str,
) -> Tuple[datetime, datetime]:
    if isinstance(entity_df, pd.DataFrame):
        entity_df_event_timestamp = entity_df.loc[
            :, entity_df_event_timestamp_col
        ].infer_objects()
        if pd.api.types.is_string_dtype(entity_df_event_timestamp):
            entity_df_event_timestamp = pd.to_datetime(
                entity_df_event_timestamp, utc=True
            )
        entity_df_event_timestamp_range = (
            entity_df_event_timestamp.min(),
            entity_df_event_timestamp.max(),
        )
    elif isinstance(entity_df, str):
        # If the entity_df is a string (SQL query), determine range
        # from table
        job = snowflake_client.query(f"SELECT MIN({entity_df_event_timestamp_col}) AS min, MAX({entity_df_event_timestamp_col}) AS max FROM {table_name}"
        )
        res = next(job.result())
        entity_df_event_timestamp_range = (
            res.get("min"),
            res.get("max"),
        )
    else:
        raise InvalidEntityType(type(entity_df))

    return entity_df_event_timestamp_range

MULTIPLE_FEATURE_VIEW_POINT_IN_TIME_JOIN = """
/*
 Compute a deterministic hash for the `left_table_query_string` that will be used throughout
 all the logic as the field to GROUP BY the data
*/
WITH "entity_dataframe" AS (
    SELECT *,
        "{{entity_df_event_timestamp_col}}" AS "entity_timestamp"
        {% for featureview in featureviews %}
            {% if featureview.entities %}
            ,(
                {% for entity in featureview.entities %}
                    CAST("{{entity}}" AS VARCHAR) ||
                {% endfor %}
                CAST("{{entity_df_event_timestamp_col}}" AS VARCHAR)
            ) AS "{{featureview.name}}__entity_row_unique_id"
            {% else %}
            ,CAST("{{entity_df_event_timestamp_col}}" AS VARCHAR) AS "{{featureview.name}}__entity_row_unique_id"
            {% endif %}
        {% endfor %}
    FROM "{{ left_table_query_string }}"
),

{% for featureview in featureviews %}

"{{ featureview.name }}__entity_dataframe" AS (
    SELECT
        {{ featureview.entities | map('tojson') | join(', ')}}{% if featureview.entities %},{% else %}{% endif %}
        "entity_timestamp",
        "{{featureview.name}}__entity_row_unique_id"
    FROM "entity_dataframe"
    GROUP BY
        {{ featureview.entities | map('tojson') | join(', ')}}{% if featureview.entities %},{% else %}{% endif %}
        "entity_timestamp",
        "{{featureview.name}}__entity_row_unique_id"
),

/*
 This query template performs the point-in-time correctness join for a single feature set table
 to the provided entity table.

 1. We first join the current feature_view to the entity dataframe that has been passed.
 This JOIN has the following logic:
    - For each row of the entity dataframe, only keep the rows where the `event_timestamp_column`
    is less than the one provided in the entity dataframe
    - If there a TTL for the current feature_view, also keep the rows where the `event_timestamp_column`
    is higher the the one provided minus the TTL
    - For each row, Join on the entity key and retrieve the `entity_row_unique_id` that has been
    computed previously

 The output of this CTE will contain all the necessary information and already filtered out most
 of the data that is not relevant.
*/

"{{ featureview.name }}__subquery" AS (
    SELECT
        "{{ featureview.event_timestamp_column }}" as "event_timestamp",
        {{'"' ~ featureview.created_timestamp_column ~ '" as "created_timestamp",' if featureview.created_timestamp_column else '' }}
        {{featureview.entity_selections | join(', ')}}{% if featureview.entity_selections %},{% else %}{% endif %}
        {% for feature in featureview.features %}
            "{{ feature }}" as {% if full_feature_names %}"{{ featureview.name }}"__"{{feature}}"{% else %}"{{ feature }}"{% endif %}{% if loop.last %}{% else %}, {% endif %}
        {% endfor %}
    FROM {{ featureview.table_subquery }}
    WHERE "{{ featureview.event_timestamp_column }}" <= '{{ featureview.max_event_timestamp }}'
    {% if featureview.ttl == 0 %}{% else %}
    AND "{{ featureview.event_timestamp_column }}" >= '{{ featureview.min_event_timestamp }}'
    {% endif %}
),

"{{ featureview.name }}__base" AS (
    SELECT
        "subquery".*,
        "entity_dataframe"."entity_timestamp",
        "entity_dataframe"."{{featureview.name}}__entity_row_unique_id"
    FROM "{{ featureview.name }}__subquery" AS "subquery"
    INNER JOIN "{{ featureview.name }}__entity_dataframe" AS "entity_dataframe"
    ON TRUE
        AND "subquery"."event_timestamp" <= "entity_dataframe"."entity_timestamp"

        {% if featureview.ttl == 0 %}{% else %}
        AND "subquery"."event_timestamp" >= TIMESTAMPADD(second,-{{ featureview.ttl }},"entity_dataframe"."entity_timestamp")
        {% endif %}

        {% for entity in featureview.entities %}
        AND "subquery"."{{ entity }}" = "entity_dataframe"."{{ entity }}"
        {% endfor %}
),

/*
 2. If the `created_timestamp_column` has been set, we need to
 deduplicate the data first. This is done by calculating the
 `MAX(created_at_timestamp)` for each event_timestamp.
 We then join the data on the next CTE
*/
{% if featureview.created_timestamp_column %}
"{{ featureview.name }}__dedup" AS (
    SELECT
        "{{featureview.name}}__entity_row_unique_id",
        "event_timestamp",
        MAX("created_timestamp") AS "created_timestamp"
    FROM "{{ featureview.name }}__base"
    GROUP BY "{{featureview.name}}__entity_row_unique_id", "event_timestamp"
),
{% endif %}

/*
 3. The data has been filtered during the first CTE "*__base"
 Thus we only need to compute the latest timestamp of each feature.
*/
"{{ featureview.name }}__latest" AS (
    SELECT
        "{{featureview.name}}__entity_row_unique_id",
        MAX("event_timestamp") AS "event_timestamp"
        {% if featureview.created_timestamp_column %}
            ,MAX("created_timestamp") AS "created_timestamp"
        {% endif %}

    FROM "{{ featureview.name }}__base"
    {% if featureview.created_timestamp_column %}
        INNER JOIN "{{ featureview.name }}__dedup"
        USING ("{{featureview.name}}__entity_row_unique_id", "event_timestamp", "created_timestamp")
    {% endif %}

    GROUP BY "{{featureview.name}}__entity_row_unique_id"
),

/*
 4. Once we know the latest value of each feature for a given timestamp,
 we can join again the data back to the original "base" dataset
*/
"{{ featureview.name }}__cleaned" AS (
    SELECT "base".*
    FROM "{{ featureview.name }}__base" AS "base"
    INNER JOIN "{{ featureview.name }}__latest"
    USING(
        "{{featureview.name}}__entity_row_unique_id",
        "event_timestamp"
        {% if featureview.created_timestamp_column %}
            ,"created_timestamp"
        {% endif %}
    )
){% if loop.last %}{% else %}, {% endif %}


{% endfor %}
/*
 Joins the outputs of multiple time travel joins to a single table.
 The entity_dataframe dataset being our source of truth here.
 */

SELECT "{{ final_output_feature_names | join('", "')}}"
FROM "entity_dataframe"
{% for featureview in featureviews %}
LEFT JOIN (
    SELECT
        "{{featureview.name}}__entity_row_unique_id"
        {% for feature in featureview.features %}
            ,{% if full_feature_names %}"{{ featureview.name }}"__"{{feature}}"{% else %}"{{ feature }}"{% endif %}
        {% endfor %}
    FROM "{{ featureview.name }}__cleaned"
) "{{ featureview.name }}__cleaned" USING ("{{featureview.name}}__entity_row_unique_id")
{% endfor %}
"""
