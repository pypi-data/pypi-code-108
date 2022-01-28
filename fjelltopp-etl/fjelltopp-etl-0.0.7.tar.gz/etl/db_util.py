import sqlalchemy


def get_db_engine(database=None, username=None, password=None, host=None, engine="postgres", ssm_config=None):

    if ssm_config is None and username is None:
        raise ValueError("Need to provide either ssm_config or username")

    if ssm_config is not None and username is not None:
        raise ValueError("Provide either ssm_config or username")
    if ssm_config is not None:
        username = ssm_config["username"]
        password = ssm_config["password"]
        host = ssm_config["host"] + ":" + str(ssm_config["port"])
        engine = ssm_config["engine"]
        if "dbInstanceIdentifier" in ssm_config:
            database = ssm_config["dbInstanceIdentifier"]
        else:
            database = ssm_config["dbname"]
        
    connection_string = f"{engine}://{username}:{password}@{host}/{database}"

    return sqlalchemy.create_engine(connection_string)
