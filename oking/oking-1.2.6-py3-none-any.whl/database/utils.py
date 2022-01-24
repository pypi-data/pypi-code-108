
class DatabaseConfig:
    def __init__(self, sql: str, db_type: str, db_name: str, db_host: str, db_user: str, db_pwd: str, db_client: str):
        self.db_type = db_type
        self.sql = sql
        self.db_name = db_name
        self.db_host = db_host
        self.db_user = db_user
        self.db_pwd = db_pwd
        self.db_client = db_client


def get_database_config(job_config: dict):
    return DatabaseConfig(
        job_config.get('sql'),
        job_config.get('db_type'),
        job_config.get('db_name'),
        job_config.get('db_host'),
        job_config.get('db_user'),
        job_config.get('db_pwd'),
        job_config.get('db_client'))