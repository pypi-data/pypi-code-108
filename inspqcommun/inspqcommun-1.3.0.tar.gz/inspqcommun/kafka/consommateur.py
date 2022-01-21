#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from json.decoder import JSONDecodeError
import os
import uuid
from confluent_kafka import Consumer, KafkaException, KafkaError
from distutils.util import strtobool
import json

class ConfigurationConsommateurKafka():
    kafka = {}
    max_poll_records = 0
    
    def __init__(self, kafka={}, max_poll_record=0):
        self.kafka = kafka
        self.max_poll_records = max_poll_record
        
def obtenirConfigurationsConsommateurDepuisVariablesEnvironnement(logger=None):
    bootstrap_servers = os.environ['BOOTSTRAP_SERVERS'] if 'BOOTSTRAP_SERVERS' in os.environ else 'localhost:9092'
    consumer_group_id = os.environ['CONSUMER_GROUP_ID'] if 'CONSUMER_GROUP_ID' in os.environ else 'consumer-{}'.format(uuid.uuid1())
    consumer_session_timeout_ms = 6000
    try:
        consumer_session_timeout_ms = int(os.environ['CONSUMER_SESSION_TIMEOUT_MS']) if 'CONSUMER_SESSION_TIMEOUT_MS' in os.environ else 6000
    except ValueError as e:
        log_message = "CONSUMER_SESSION_TIMEOUT_MS set to 6000 due to invalid value. {}".format(str(e))
        if logger is not None:
            logentry = {}
            logentry['configuration'] = 'CONSUMER_SESSION_TIMEOUT_MS'
            logentry['message_code'] = 'CONFIGURATION_INVALIDE'
            logger.warn(log_message, extra=logentry)
        else:
            print(log_message)
            
    consumer_fetch_wait_max_ms = 10
    try:
        consumer_fetch_wait_max_ms = int(os.environ['CONSUMER_FETCH_WAIT_MAX_MS']) if 'CONSUMER_FETCH_WAIT_MAX_MS' in os.environ else 10
    except ValueError as e:
        log_message = "CONSUMER_FETCH_WAIT_MAX_MS set to 6000 due to invalid value. {}".format(str(e))
        if logger is not None:
            logentry = {}
            logentry['configuration'] = 'CONSUMER_FETCH_WAIT_MAX_MS'
            logentry['message_code'] = 'CONFIGURATION_INVALIDE'
            logger.warn(log_message, extra=logentry)
        else:
            print(log_message)
    consumer_enable_partition_eof = False
    try:
        consumer_enable_partition_eof = strtobool(os.environ['CONSUMER_ENABLE_PARTITON_EOF']) if 'CONSUMER_ENABLE_PARTITON_EOF' in os.environ else False
    except ValueError as e:
        log_message = "CONSUMER_ENABLE_PARTITON_EOF set to False due to invalid value. {}".format(str(e))
        if logger is not None:
            logentry = {}
            logentry['configuration'] = 'CONSUMER_ENABLE_PARTITON_EOF'
            logentry['message_code'] = 'CONFIGURATION_INVALIDE'
            logger.warn(log_message, extra=logentry)
        else:
            print(log_message)
    consumer_auto_offset_reset = os.environ['CONSUMER_AUTO_OFFSET_RESET'] if 'CONSUMER_AUTO_OFFSET_RESET' in os.environ else 'smallest'
    consumer_enable_auto_commit = True
    try:
        consumer_enable_auto_commit = strtobool(os.environ['CONSUMER_ENABLE_AUTO_COMMIT']) if 'CONSUMER_ENABLE_AUTO_COMMIT' in os.environ else True
    except ValueError as e:
        log_message = "CONSUMER_ENABLE_AUTO_COMMIT set to True due to invalid value. {}".format(str(e))
        if logger is not None:
            logentry = {}
            logentry['configuration'] = 'CONSUMER_ENABLE_AUTO_COMMIT'
            logentry['message_code'] = 'CONFIGURATION_INVALIDE'
            logger.warn(log_message, extra=logentry)
        else:
            print(log_message)
    consumer_max_poll_records = 0
    try:
        consumer_max_poll_records = int(os.environ['CONSUMER_MAX_POLL_RECORDS']) if 'CONSUMER_MAX_POLL_RECORDS' in os.environ else 0
    except ValueError as e:
        log_message = "CONSUMER_MAX_POLL_RECORDS set to 0 due to invalid value. {}".format(str(e))
        if logger is not None:
            logentry = {}
            logentry['configuration'] = 'CONSUMER_MAX_POLL_RECORDS'
            logentry['message_code'] = 'CONFIGURATION_INVALIDE'
            logger.warn(log_message, extra=logentry)
        else:
            print(log_message)
    
    config_consommateur_kafka = {
        'bootstrap.servers': bootstrap_servers,
        'group.id': consumer_group_id,
        'session.timeout.ms': consumer_session_timeout_ms,
        'fetch.wait.max.ms': consumer_fetch_wait_max_ms,
        'enable.partition.eof': consumer_enable_partition_eof,
        'enable.auto.commit': consumer_enable_auto_commit,
        'default.topic.config': {'auto.offset.reset': consumer_auto_offset_reset}
    }
    if 'KAFKA_SECURITY_PROTOCOL' in os.environ:
        config_consommateur_kafka['security.protocol'] = os.environ['KAFKA_SECURITY_PROTOCOL']
    if 'KAFKA_SSL_CA_LOCATION' in os.environ:
        config_consommateur_kafka['ssl.ca.location'] = os.environ['KAFKA_SSL_CA_LOCATION']
    if 'KAFKA_SSL_CERTIFICATE_LOCATION' in os.environ:
        config_consommateur_kafka['ssl.certificate.location'] = os.environ['KAFKA_SSL_CERTIFICATE_LOCATION']
    if 'KAFKA_SSL_KEY_LOCATION' in os.environ:
        config_consommateur_kafka['ssl.key.location'] = os.environ['KAFKA_SSL_KEY_LOCATION']
    if 'KAFKA_SSL_KEY_PASSWORD' in os.environ:
        config_consommateur_kafka['ssl.key.password'] = os.environ['KAFKA_SSL_KEY_PASSWORD']

    config = ConfigurationConsommateurKafka(kafka=config_consommateur_kafka, max_poll_record=consumer_max_poll_records)
    
    return config    
    
def creerConsommateur(config, topics):
    consommateur = Consumer(config)
    consommateur.subscribe(topics)
    return consommateur
"""
Fonction: consommerTopics
Description: Cette fonction permet de lire tous les messages d'un consommateur
Paramètres:
    consommateur: Consommateur Kafaka à utiliser pour lire les messages
    topics: Liste de topics pour lesquel vérifier si on a atteint la fin des offsets
    batch_size: grosseur des lots à consommer. La valeur par défaut est 0 pour un seul lot contenant tous les messages
    decode: Décode les messages et les clé si vrai.
Retour:
    Dictionnaire:
        Clé: Non du topic duquel le message vient
        Valeur: Dictionnaire:
            key: Clé du message Kafka 
            value: valeur du message Kafka
        
        exemple:
        messages: {
            'topic1': [
                {'key': 1, 'value': "test"},
                {'key': 2, 'value': "test2"}
            ],
            'topic2': [
                {'key': 3, 'value': "test3"},
                {'key': 4, 'value': "test4"}
            ]
        }
        Voire la documentation https://docs.confluent.io/platform/current/clients/confluent-kafka-python/#confluent_kafka.Consumer
"""    
def consommerTopics(consommateur, topics=[], batch_size=0, decode=False):
    finMessages = False
    finTopics = {}
    for topic in topics:
        finTopics[topic] = False
    tentatives = 0
    messages = {}
    nb_messages_consommes = 0
    while not finMessages:
        msg = consommateur.poll(timeout=0.1)
        if msg is None:
            tentatives = tentatives + 1
        elif not msg.error():
            if msg.topic() not in messages:
                messages[msg.topic()] = []
            message = {}
            message["value"] = decode_from_bytes(msg.value()) if decode else msg.value()
            message["key"] = decode_from_bytes(msg.key()) if decode else msg.key()
            messages[msg.topic()].append(message)
            nb_messages_consommes += 1
        else:
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    finTopics[msg.topic()] = True
                else:
                    print(msg.error().str())
        if (batch_size > 0 and nb_messages_consommes >= batch_size) or tentatives > 100 or all(finTopics.values()):
            finMessages = True
                
    return messages

def decode_from_bytes(value=None):
    try:
        decoded = json.loads(value.decode())
        return decoded
    except JSONDecodeError:
        decoded = value.decode()
        return decoded
    return value
