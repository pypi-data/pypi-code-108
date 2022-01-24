from psycopg2 import ProgrammingError

from nehushtan.logger.NehushtanFileLogger import NehushtanFileLogger
from nehushtan.postgres.PgSQLKit import PgSQLKit
from nehushtan.postgres.PgSQLKitConfig import PgSQLKitConfig
from nehushtan.postgres.PgSQLResultSet import PgSQLResultSet


class PgSQLTestEnv:
    def __init__(self):
        self.__logger = NehushtanFileLogger()

    def get_pg_kit_instance(self):
        return PgSQLKit(PgSQLKitConfig(
            {
                'host': '127.0.0.1',
                'port': 15432,
                'dbname': 'postgres',
                'user': 'postgres',
                'password': 'PGsql000',
                'autocommit': True,
            }
        ))

    def log(self, content, context=None):
        self.__logger.notice(content, context)

    def log_for_result_set(self, result_set: PgSQLResultSet):
        self.__logger.notice(
            f'QUERY: \n{result_set.get_query().decode()}\n',
            {
                "row_count": result_set.get_row_count(),
                "last_inserted_row_id": result_set.get_last_inserted_row_id(),
            }
        )
        try:
            if result_set.get_row_count() > 0:
                result_set.get_status_message()
                rows = result_set.fetch_all_remaining_rows()
                for row in rows:
                    self.__logger.info('> ', {"row": row})
        except ProgrammingError:
            pass
