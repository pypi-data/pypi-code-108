#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import json
from confluent_kafka import Producer, KafkaException, KafkaError

def obtenirConfigurationsProducteurDepuisVariablesEnvironnement():
    bootstrap_servers = os.environ['BOOTSTRAP_SERVERS'] if 'BOOTSTRAP_SERVERS' in os.environ else 'localhost:9092'
    
    config_kafka = {
        'bootstrap.servers': bootstrap_servers
    }
    if 'KAFKA_SECURITY_PROTOCOL' in os.environ:
        config_kafka['security.protocol'] = os.environ['KAFKA_SECURITY_PROTOCOL']
    if 'KAFKA_SSL_CA_LOCATION' in os.environ:
        config_kafka['ssl.ca.location'] = os.environ['KAFKA_SSL_CA_LOCATION']
    if 'KAFKA_SSL_CERTIFICATE_LOCATION' in os.environ:
        config_kafka['ssl.certificate.location'] = os.environ['KAFKA_SSL_CERTIFICATE_LOCATION']
    if 'KAFKA_SSL_KEY_LOCATION' in os.environ:
        config_kafka['ssl.key.location'] = os.environ['KAFKA_SSL_KEY_LOCATION']
    if 'KAFKA_SSL_KEY_PASSWORD' in os.environ:
        config_kafka['ssl.key.password'] = os.environ['KAFKA_SSL_KEY_PASSWORD']    

    return config_kafka    

def creerProducteur(config):
    producteur = Producer(**config)
    return producteur
"""
Fonction: publierMessage
Description: Cette fonction permet produire un message sur un topic Kafka
Paramètres:
    producteur: Producteur Kafka à utiliser
    message: Dictionnaire du message à publier:
        key: Clé pour publier le message
        value: Message à publier
    topic:Topic Kafka sur lequel publier le message
Retour:
    True si le message a bien été publié
"""    
def publierMessage(producteur, message, topic, logger=None):
    def callback_livraison(err, msg):
        if err:
            log_message = "Livraison du message impossible: {}".format(err)
            if logger is not None:
                logentry = {}
                logentry['topic'] = msg.topic()
                logentry['partition'] = msg.partition()
                logentry['offset'] = msg.offset()
                logentry['message_code'] = "ERREUR_PRODUCTEUR"
                logger.error(log_message, extra=logentry)
            
            else:
                print(log_message)
        else:
            log_message = "Le message a été livré. Topic {}, Partition {}, Offset {}".format(
                msg.topic(),
                msg.partition(),
                msg.offset())
            if logger is not None:
                logentry = {}
                logentry['topic'] = msg.topic()
                logentry['partition'] = msg.partition()
                logentry['offset'] = msg.offset()
                logentry['message_code'] = "CALLBACK_MESSAGE_PUBLIE"
                logger.info(log_message, extra=logentry)
            else:
                print(log_message)
                
    if logger is None:
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger()
    try:
        
        key = encode_to_bytes(message['key']) if 'key' in message else None
        value = encode_to_bytes(message['value']) if 'value' in message else None
        producteur.produce(topic, value=value, key=key, callback=callback_livraison)
        logentry = {}
        logentry['topic'] = topic
        logentry['key'] = key.decode() if key is not None else ""
        logentry['value'] = value.decode() if value is not None else ""
        logentry['message_code'] = "MESSAGE_PUBLIE"
        log_message = "Message {} publié sur le topic {}".format(logentry['key'], topic)
        logger.info(log_message, extra=logentry)
    except BufferError as e:
        logentry = {}
        logentry['topic'] = topic
        logentry['key'] = key.decode() if key is not None else ""
        logentry['value'] = value.decode() if value is not None else ""
        logentry['message_code'] = "PRODUCTEUR_QUEUE_MESSAGE_PLEINE"
        log_message = "La queue de message est pleine. Erreur {}".format(str(e))
        logger.error(log_message, extra=logentry)
        return False
    except KafkaError as e:
        logentry = {}
        logentry['topic'] = topic
        logentry['key'] = key.decode() if key is not None else ""
        logentry['value'] = value.decode() if value is not None else ""
        logentry['message_code'] = "ERREUR_PRODUCTEUR"
        logentry['error_code'] = e.error_code
        logentry['reason'] = e.reason
        log_message = "Erreur Kafka: {}: {}".format(e.error_code, e.reason)
        logger.error(log_message, extra=logentry)
        return False
    except KafkaException as e:
        logentry = {}
        logentry['topic'] = topic
        logentry['key'] = key.decode() if key is not None else ""
        logentry['value'] = value.decode() if value is not None else ""
        logentry['message_code'] = "ERREUR_PRODUCTEUR"
        logentry['error_code'] = e.error_code
        logentry['reason'] = e.reason
        log_message = "Erreur Kafka: {}: {}".format(e.args[0].error_code, e.args[0].reason)
        logger.error(log_message, extra=logentry)
        return False
        
    producteur.flush()
    return True

def encode_to_bytes(value=None):
    if type(value) is str:
        return value.encode()
    elif type(value) is dict:
        return json.dumps(value).encode()
    else:
        return value