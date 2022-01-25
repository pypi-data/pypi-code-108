from pydantic import BaseSettings, BaseModel


class RabbitConfig(BaseModel):
    user: str = "core"
    password: str = None
    host: str = "localhost"

    @property
    def con_string(self):
        return f"amqp://{self.user}:{self.password}@{self.host}/"


class S3Settings(BaseModel):
    aws_access_key_id: str = "minioadmin"
    aws_secret_access_key: str = "minioadmin"
    endpoint_url: str = "http://localhost:9000"


class Config(BaseSettings):
    rabbit: RabbitConfig = None
    s3: S3Settings = None
    exchange_name: str = "tasks"
    n_workers: int = 1
    coordinator_path: str = "/run/coordinator"
    logger_path: str = "/run/logger"
    consumer_user: str = "appuser"
    interpreter: str = "/home/appuser/env/bin/python3"
    cwd: str = "/home/appuser/app"
    project_meta: str = "mmf.yml"
    consumer_script: str = "-m ipc consume"
    secret_key: str = ""
    public_key: str = "key.pub"
    project_id: int = 0

    class Config:
        env_file_encoding = "utf-8"
        extra = "allow"
        env_nested_delimiter = "__"


config = Config(_env_file=".secrets.env")
