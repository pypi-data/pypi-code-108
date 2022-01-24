from django.test import TestCase

from django_pg_trunk.models import QueryStatistic
from django_pg_trunk.utils import get_current_database_id


class PgTrunkTests(TestCase):
    def test_query_statistic_model(self):
        # Test fetching QueryStatistic objects from pg_stat_statements database.
        self.assertIsNotNone(QueryStatistic.objects.first())

        # Count will be increased since statistics of the query that
        # calculates the count will be added to the pg_stat_statements.
        query_statistic_count = QueryStatistic.objects.count()
        self.assertEqual(QueryStatistic.objects.count(), query_statistic_count + 1)

    def test_get_current_database_id(self):
        database_id = get_current_database_id()
        self.assertTrue(
            QueryStatistic.objects.filter(query="SELECT current_database()", dbid=database_id).exists()
        )
