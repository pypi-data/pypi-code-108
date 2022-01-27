from sqlalchemy.engine import create_engine


class Warehouse:
    def __init__(self, credentials):
        self.type = credentials["type"]
        self.database = (
            credentials.get("database")
            or credentials.get("project")
            or credentials.get("dbname")
        )
        self.schema = credentials.get("schema") or credentials.get("dataset")
        self.user = credentials.get("user")
        self.password = credentials.get("password") or credentials.get("pass")

        # BigQuery
        self.keyfile = credentials.get("keyfile")
        self.method = credentials.get("method")

        # Snowflake
        self.account = credentials.get("account")
        self.role = credentials.get("role")
        self.private_key_path = credentials.get("private_key_path")
        self.private_key_passphrase = credentials.get("private_key_passphrase")
        self.warehouse = credentials.get("warehouse")

        # Redshift
        self.host = credentials.get("host")
        self.port = credentials.get("port")

        self.engine = self.generate_engine()

    def generate_engine(self):
        engine = None
        if self.type == "bigquery":
            uri = f"bigquery://{self.database}/{self.schema}"
            if self.method == "oauth":
                engine = create_engine(uri)
            elif self.method == "service-account":
                engine = create_engine(uri, credentials_path=self.keyfile)
        elif self.type == "snowflake":
            if self.password:
                uri = f"snowflake://{self.user}:{self.password}@{self.account}/{self.warehouse}"
            engine = create_engine(uri)
        elif self.type in ["redshift", "postgres"]:
            uri = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
            engine = create_engine(uri)
        else:
            raise Exception(f"Database type {self.type} not supported.")
        if not engine:
            raise Exception(
                f"Authentication method for database type {self.type} not supported."
            )
        return engine

    def generate_query(self, schema, database):
        if self.type == "bigquery":
            query = f"select table_name from `{database}.{schema}.INFORMATION_SCHEMA.TABLES`"  # nosec
        elif self.type == "snowflake":
            query = f"select table_name from {database}.information_schema.tables where table_schema = '{schema.upper()}'"  # nosec
        elif self.type in ["redshift", "postgres"]:
            query = f"select table_name from information_schema.tables where table_schema = '{schema}'"  # nosec
        return query

    def run_query(self, schemas, database):
        tables = set()
        for schema in schemas:
            query = self.generate_query(schema, database)
            rows = self.engine.execute(query).fetchall()
            for row in rows:
                tables.add(row[0].lower())
        return tables
