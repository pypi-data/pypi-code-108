import os
from typing import Type


def get_env_var(key: str, default=None, throw_if_missing=False, dtype: Type = str):
    if key not in os.environ:
        if throw_if_missing:
            raise ValueError('Missing environment variable: ', key)
        else:
            return default

    return dtype(os.getenv(key))


# General
CHARSET: str = get_env_var('CHARSET', default='utf-8', dtype=str)

# RabbitMQ
RABBITMQ_HOST: str = get_env_var('RABBITMQ_HOST', dtype=str, default='localhost')
RABBITMQ_PORT: int = get_env_var('RABBITMQ_PORT', dtype=int, default=5672)
RABBITMQ_USER: str = get_env_var('RABBITMQ_USER', dtype=str, default='guest')
RABBITMQ_PASS: str = get_env_var('RABBITMQ_PASS', dtype=str, default='guest')
# parsed as a list of RoutingRule applied over a TranscriptionRequest's JSON representation
RABBITMQ_ROUTING_RULES_JSON: str = get_env_var('RABBITMQ_ROUTING_RULES_JSON', dtype=str, default='[]')
RABBITMQ_TRANSCRIPTION_RESPONSE_QUEUE: str = get_env_var('RABBITMQ_TRANSCRIPTION_RESPONSE_QUEUE', dtype=str, default='transcription_responses')
RABBITMQ_TTL_MILLIS: int = get_env_var('RABBITMQ_TTL_MILLIS', dtype=int, default=900000)  # 15min
