import json
import pika
import sys
from loguru import logger


logger.remove()
logger.add(sys.stderr, format="{level:<10} {time} {message}", level='INFO', colorize=True)

def connect(host, port, user, password):
    global channel
    try:
        credentials = pika.PlainCredentials(user, password)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host, port, credentials=credentials))
        channel = connection.channel()
        return channel
    except:
        logger.error(f"Connection to rabbitMQ'{host, port, user, password}' failed.")

def setStatus(status:str, req:str):

    messageBody = {
        'ProcessDefinitionKey': req['ProcessDefinitionKey'],
        'ProcessInstanceId': req['ProcessInstanceId'],
        'BusinessKey': req['BusinessKey'],
        'TaskId': req['TaskId'],
        'ExternalTaskName': req['ExternalTaskName'],
        'Result': '',
        'OutputVariables': {}
    }

    if status == 'COMPLETED':
        messageBody['Result'] = 'Complete'
        messageBody= json.dumps(messageBody)
        channel.queue_declare(queue='task-completed', durable=True)
        channel.basic_publish(exchange='', routing_key='task-completed', body=messageBody)
        logger.info(messageBody)
    else:
        logger.error(f"Status '{status}' not found. Task set to 'COMPLETED'.")
