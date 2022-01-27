import unittest
from collections import OrderedDict

from syngenta_digital_dta.postgres import json_formatting


class TestJsonFormatting(unittest.TestCase):

    def test_build_json_cte(self):
        actual = json_formatting._build_json_cte(
            json={}
        )

        expected = "WITH _json_cte AS (SELECT '{}'::json AS _json)"

        self.assertEqual(expected, actual)

    def test_get_column_order(self):
        columns = OrderedDict(
            [
                ('guuid', 'generate_uuid_v4()'),
                ('created_at', 'now()'),
                ('updated_at', 'now()'),
            ]
        )

        json_columns = OrderedDict(
            [
                ('time', 'feature.properties.Time'),
                ('machine', 'feature.properties.Machine'),
                ('secID', 'feature.properties.SecID')
            ]
        )

        actual = json_formatting._get_column_order(
            columns, json_columns
        )

        expected = [
            "guuid",
            "created_at",
            "updated_at",
            "time",
            "machine",
            "secID"
        ]

        self.assertEqual(expected, actual)

    def test_build_json_array_subquery(self):
        actual = json_formatting._build_json_array_subquery("feature")
        expected = "SELECT json_array_elements(_json->'feature') AS _jsondict FROM _json_cte"
        self.assertEqual(expected, actual)

    def test_build_select_statement(self):
        columns = OrderedDict(
            [
                ('guuid', 'generate_uuid_v4()'),
                ('created_at', 'now()'),
                ('updated_at', 'now()'),
            ]
        )

        json_columns = OrderedDict(
            [
                ('time', 'feature.properties.Time'),
                ('machine', 'feature.properties.Machine'),
                ('secID', 'feature.properties.SecID')
            ]
        )

        actual = json_formatting._build_select_statement(columns, json_columns, {})
        expected = "SELECT generate_uuid_v4() AS guuid, now() AS created_at, now() AS updated_at, _jsondict -> 'properties' ->> 'Time' AS time, _jsondict -> 'properties' ->> 'Machine' AS machine, _jsondict -> 'properties' ->> 'SecID' AS secID"

        self.assertEqual(expected, actual)

    def test_build_insert_statement(self):

        columns = OrderedDict(
            [
                ('guuid', 'generate_uuid_v4()'),
                ('created_at', 'now()'),
                ('updated_at', 'now()'),
            ]
        )

        json_columns = OrderedDict(
            [
                ('time', 'feature.properties.Time'),
                ('machine', 'feature.properties.Machine'),
                ('secID', 'feature.properties.SecID')
            ]
        )

        actual = json_formatting._build_insert_statement(
            table="my_table",
            column_map=columns,
            json_column_map=json_columns
        )

        expected = "INSERT INTO my_table (guuid, created_at, updated_at, time, machine, secID)"

        self.assertEqual(expected, actual)

    def test_insert_json_into_table(self):
        columns = OrderedDict(
            [
                ('guuid', 'generate_uuid_v4()'),
                ('created_at', 'now()'),
                ('updated_at', 'now()'),
            ]
        )

        json_columns = OrderedDict(
            [
                ('time', 'feature.properties.Time'),
                ('machine', 'feature.properties.Machine'),
                ('secID', 'feature.properties.SecID')
            ]
        )

        actual = json_formatting.insert_json_into_table(
            json="{}",
            table_name="my_table",
            column_map=columns,
            json_column_map=json_columns
        )

        expected = """WITH _json_cte AS (SELECT '{}'::json AS _json)
        INSERT INTO my_table (guuid, created_at, updated_at, time, machine, secID)
        SELECT generate_uuid_v4() AS guuid, now() AS created_at, now() AS updated_at, _jsondict -> 'properties' ->> 'Time' AS time, _jsondict -> 'properties' ->> 'Machine' AS machine, _jsondict -> 'properties' ->> 'SecID' AS secID
        FROM (SELECT json_array_elements(_json->'feature') AS _jsondict FROM _json_cte)x 
"""

        self.assertEqual(expected, actual)

    def test_insert_json_into_table_function_map(self):
        columns = OrderedDict(
            [
                ('guuid', 'generate_uuid_v4()'),
                ('created_at', 'now()'),
                ('updated_at', 'now()'),
            ]
        )

        json_columns = OrderedDict(
            [
                ('time', 'feature.properties.Time'),
                ('machine', 'feature.properties.Machine'),
                ('secID', 'feature.properties.SecID')
            ]
        )

        actual = json_formatting.insert_json_into_table(
            json="{}",
            table_name="my_table",
            column_map=columns,
            json_column_map=json_columns,
            function_map={
                'secID': 'cast({} as varchar)'
            }
        )

        expected = """WITH _json_cte AS (SELECT '{}'::json AS _json)
        INSERT INTO my_table (guuid, created_at, updated_at, time, machine, secID)
        SELECT generate_uuid_v4() AS guuid, now() AS created_at, now() AS updated_at, _jsondict -> 'properties' ->> 'Time' AS time, _jsondict -> 'properties' ->> 'Machine' AS machine, cast(_jsondict -> 'properties' ->> 'SecID' as varchar) as secID
        FROM (SELECT json_array_elements(_json->'feature') AS _jsondict FROM _json_cte)x 
"""

        self.assertEqual(expected, actual)

    def test_on_conflict_clause_do_update(self):
        actual = json_formatting._build_on_conflict(
            conflict_cols=('a', 'b', 'c'),
            update_cols=('b', 'c')
        )

        expected = 'ON CONFLICT (a, b, c) DO UPDATE SET (b,c) = (excluded.b,excluded.c)'

        self.assertEqual(expected, actual)

    def test_on_conflict_clause_do_nothing(self):
        actual = json_formatting._build_on_conflict(
            conflict_cols=('a', 'b', 'c'),
            update_cols=None
        )

        expected = 'ON CONFLICT DO NOTHING'

        self.assertEqual(expected, actual)

    def test_on_conflict_clause_none(self):
        actual = json_formatting._build_on_conflict(
            conflict_cols=None,
            update_cols=None
        )

        expected = ''

        self.assertEqual(expected, actual)