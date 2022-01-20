import json
import pika as pika
from change_event_service.database import db
from change_event_service.modules.rest.models import ChangeEventModel


def consume_change_events(app_context):
    mq_host = app_context.config.get('MQ_HOST')
    mq_vhost = app_context.config.get('MQ_VHOST')
    mq_user = app_context.config.get('MQ_USER')
    mq_pass = app_context.config.get('MQ_PASS')
    mq_queue = app_context.config.get('MQ_QUEUE')
    mq_exchange = app_context.config.get('MQ_EXCHANGE')
    mq_routing_key = app_context.config.get('MQ_ROUTING_KEY')

    def on_message(channel, method_frame, header_frame, body):
        app_context.logger.debug(f'Received message: {body}')
        try:
            _body = json.loads(body)
            change_event = ChangeEventModel(**_body)
            db.session.add(change_event)
            db.session.commit()
        except Exception as e:
            app_context.logger.error(f'Error: {e}')
            db.session.rollback()
            channel.basic_publish(exchange=mq_exchange, routing_key=mq_routing_key, body=body)
        finally:
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)

    cred = pika.PlainCredentials(mq_user, mq_pass)
    conn = pika.BlockingConnection(pika.ConnectionParameters(host=mq_host, virtual_host=mq_vhost, credentials=cred))
    channel = conn.channel()
    channel.basic_consume(mq_queue, on_message)
