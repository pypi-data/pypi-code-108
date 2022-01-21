from kfpubsub import PubSub
from django.conf import settings
from django.db import close_old_connections


class DjangoPubSub(PubSub):

    def __init__(self):
        host = getattr(settings, 'REDIS_HOST', 'localhost')
        port = getattr(settings, 'REDIS_PORT', 6379)
        database = getattr(settings, 'REDIS_DB', 0)

        enable_kafka = getattr(settings, 'KAFKA_ENABLE', False)
        if enable_kafka:
            kafka_brokers = getattr(settings, 'KAFKA_BROKERS', ("localhost:9092", ))
            kafka_group_id = getattr(settings, 'KAFKA_GROUP_ID', None)
            kafka_enable_auto_commit = getattr(settings, 'KAFKA_ENABLE_AUTO_COMMIT', False)
            kafka_topics = getattr(settings, 'KAFKA_TOPICS', None)
            kafka_replication_factor = getattr(settings, 'KAFKA_REPLICATION_FACTOR', 1)
            kafka_partitions = getattr(settings, 'KAFKA_PARTITIONS', 1)
            kafka_poll_timeout = getattr(settings, 'KAFKA_POLL_TIMEOUT', 500)
            kafka_emit_prefix = getattr(settings, 'KAFKA_EMIT_PREFIX', '')
            kafka_receive_prefix = getattr(settings, 'KAFKA_RECEIVE_PREFIX', '')

            super(DjangoPubSub, self).__init__(
                host=host,
                port=port,
                database=database,
                enable_kafka=enable_kafka,
                kafka_brokers=kafka_brokers,
                kafka_group_id=kafka_group_id,
                kafka_enable_auto_commit=kafka_enable_auto_commit,
                kafka_partitions=kafka_partitions,
                kafka_replication_factor=kafka_replication_factor,
                kafka_topics=kafka_topics,
                kafka_poll_timeout=kafka_poll_timeout,
                kafka_emit_prefix=kafka_emit_prefix,
                kafka_receive_prefix=kafka_receive_prefix,
            )
        else:
            super(DjangoPubSub, self).__init__(host=host, port=port, database=database)

    def emit(self, event, message):
        super(DjangoPubSub, self).emit(event, message, emit=getattr(settings, 'PUB_SUB_EMIT', True))

    def receive(self, listeners):
        super(DjangoPubSub, self).receive(listeners, close_old_connections)
