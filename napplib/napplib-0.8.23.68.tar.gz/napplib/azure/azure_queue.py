# coding: utf-8
import os
import json
import base64
from azure.storage.queue import QueueClient


class AzureQueue:
    def __init__(self, account_name, queue_name, account_key):
        """Create object AzureQueue to connect and access a  specific Azure Queue
        
        Arguments:
            account_name {str} -- [Account name]
            queue_name {str} -- [Queue Name]
            account_key {str} -- [Account key]
        """
        print('Initializing Azure Queue...')

        self.account_name = account_name
        self.queue_name = queue_name
        self.account_key = account_key

        # create a connection string for connect to QueueClient
        connect_str = f'DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net'

        # set connect_str and queue_name for create object to access 
        # specific queue
        self.queue_client = QueueClient.from_connection_string(connect_str, queue_name)

    def add_message(self, message):
        """Receive message in string and send to azure queue
        
        Arguments:
            message {str} -- [content string]
        """

        self.queue_client.send_message(message)
        print('Message sent!')

    def remove_message(self, message):
        """Receive obj message and collect message.id for execute azure function delete_message
        
        Arguments:
            message {obj} -- [azure message object]
        """
        self.queue_client.delete_message(message.id, message.pop_receipt)
        print(f'Message {message.id} removed!')

    def edit_message(self, message, message_edited, visibility_timeout=0):
        """Receive the object message and message_edited in string, collect object message id,
        and set new content(message_edited)
        
        Arguments:
            message {obj} -- [azure message objects]
            message_edited {str} -- [content string]
        
        Keyword Arguments:
            visibility_timeout {int} -- [visilility timeout] (default: {0})
        """
        self.queue_client.update_message(
            message.id,
            message.pop_receipt,
            visibility_timeout=visibility_timeout,
            content=message_edited)

    def count_messages(self):
        """count messages
        
        Returns:
            [int] -- [total messages in queue]
        """
        properties = self.queue_client.get_queue_properties()
        count = properties.approximate_message_count
        return int(count)

    def get_messages(self):
        """collect all messages in queue
        
        Returns:
            [list] -- [list of objects messages queue]
        """
        return self.queue_client.receive_messages()
    
    def encode_message(self, content):
        return base64.b64encode(
            bytes(json.dumps(content), 'utf8')).decode('utf8')

    def decode_message(self, content):
        decode = base64.b64decode(content).decode('utf8')
        return json.loads(decode)

