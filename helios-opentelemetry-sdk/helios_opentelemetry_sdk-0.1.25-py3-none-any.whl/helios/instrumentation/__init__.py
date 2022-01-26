from logging import getLogger

from helios.instrumentation.aiosmtplib import HeliosAiosmtplibInstrumentor
from helios.instrumentation.base import HeliosBaseInstrumentor
from helios.instrumentation.botocore import HeliosBotocoreInstrumentor
from helios.instrumentation.django import HeliosDjangoInstrumentor
from helios.instrumentation.elasticsearch import HeliosElasticsearchInstrumentor
from helios.instrumentation.fastapi import HeliosFastAPIInstrumentor
from helios.instrumentation.flask import HeliosFlaskInstrumentor
from helios.instrumentation.httpx import HeliosHttpxInstrumentor
from helios.instrumentation.kafka import HeliosKafkaInstrumentor
from helios.instrumentation.logging import HeliosLoggingInstrumentor
from helios.instrumentation.pika import HeliosPikaInstrumentor
from helios.instrumentation.pymongo import HeliosPymongoInstrumentor
from helios.instrumentation.pyspark import HeliosPySparkInstrumentor
from helios.instrumentation.redis import HeliosRedisInstrumentor
from helios.instrumentation.requests import HeliosRequestsInstrumentor
from helios.instrumentation.sentry import HeliosSentryInstrumentor
from helios.instrumentation.starlette import HeliosStarletteInstrumentor
from helios.instrumentation.tornado import HeliosTornadoInstrumentor
from helios.instrumentation.urllib import HeliosUrllibInstrumentor
from helios.instrumentation.urllib3 import HeliosUrllib3Instrumentor
from helios.instrumentation.aiohttp import HeliosAiohttpInstrumentor

_LOG = getLogger(__name__)

instrumentor_names = [
    ('opentelemetry.instrumentation.aiopg', 'AiopgInstrumentor'),
    ('opentelemetry.instrumentation.asyncpg', 'AsyncPGInstrumentor'),
    ('opentelemetry.instrumentation.boto', 'BotoInstrumentor'),
    ('opentelemetry.instrumentation.celery', 'CeleryInstrumentor'),
    ('opentelemetry.instrumentation.mysql', 'MySQLInstrumentor'),
    ('opentelemetry.instrumentation.psycopg2', 'Psycopg2Instrumentor'),
    ('opentelemetry.instrumentation.pymemcache', 'PymemcacheInstrumentor'),
    ('opentelemetry.instrumentation.pymysql', 'PyMySQLInstrumentor'),
    ('opentelemetry.instrumentation.sqlalchemy', 'SQLAlchemyInstrumentor'),
    ('opentelemetry.instrumentation.sqlite3', 'SQLite3Instrumentor'),
]
default_instrumentation_list = [
    HeliosAiosmtplibInstrumentor(),
    HeliosBotocoreInstrumentor(),
    HeliosDjangoInstrumentor(),
    HeliosElasticsearchInstrumentor(),
    HeliosFastAPIInstrumentor(),
    HeliosFlaskInstrumentor(),
    HeliosHttpxInstrumentor(),
    HeliosKafkaInstrumentor(),
    HeliosLoggingInstrumentor(),
    HeliosPikaInstrumentor(),
    HeliosPySparkInstrumentor(),
    HeliosPymongoInstrumentor(),
    HeliosRedisInstrumentor(),
    HeliosRequestsInstrumentor(),
    HeliosSentryInstrumentor(),
    HeliosStarletteInstrumentor(),
    HeliosTornadoInstrumentor(),
    HeliosUrllib3Instrumentor(),
    HeliosUrllibInstrumentor(),
    HeliosAiohttpInstrumentor(),
]

for module_name, instrumentor_name in instrumentor_names:
    instrumentor = HeliosBaseInstrumentor.init_instrumentor(module_name, instrumentor_name)
    if instrumentor is not None:
        default_instrumentation_list.append(instrumentor)
