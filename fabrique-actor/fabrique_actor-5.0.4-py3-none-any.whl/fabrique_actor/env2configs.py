import os

import dotenv

dotenv.load_dotenv(dotenv_path="/opt/app/configs/.env")  # if exists
import json

cert_path = "/opt/app/cert"  # if exists
krb_path = "/opt/app/krb"  # if exists


class EnvDict(dict):
    """
    os.environ dict with human readable exception when env var doesn't exists
    ! should be created dynamically for env patching
    """
    def __init__(self):
        super().__init__(os.environ)

    def __getitem__(self, key):
        print('get item')
        res = self.get(key)
        if res is None:
            raise Exception(f'Env var "{key}" not found')
        return res



def provide_ssl(cnf):
    """
    Helper for ssl/sasl kafka configs
    :param cnf: conf dict
    :return: enriched conf dict
    """
    envdict = EnvDict()

    security_prot = envdict.get("FABRIQUE_KAFKA_SECURITY_PROTOCOL", "PLAINTEXT")
    assert security_prot in ["PLAINTEXT", "SASL_PLAINTEXT", "SASL_SSL", "SSL"]
    cnf["security.protocol"] = security_prot.lower()
    if "SSL" in security_prot:
        cnf["enable.ssl.certificate.verification"] = envdict.get("FABRIQUE_KAFKA_SSL_CERT_VERIFICATION", "false")
        ssl_type = envdict.get(f"FABRIQUE_KAFKA_SSL_CERT_TYPE", "")

        key_password = envdict.get("FABRIQUE_KAFKA_SSL_PASSWORD", "")
        keystore_password = envdict.get("FABRIQUE_KAFKA_SSL_KEYSTORE_PASSWORD", "")

        if ssl_type in ['PKCS12', 'KEYSTORE']:
            cnf["ssl.keystore.location"] = f"{cert_path}/keystore.p12"
            if keystore_password:
                cnf["ssl.keystore.password"] = keystore_password

        elif ssl_type == 'SEP_FILES':
            cnf["ssl.ca.location"] = f"{cert_path}/kafka-ca-cert"
            cnf["ssl.certificate.location"] = f"{cert_path}/kafka-client.pem"
            cnf["ssl.key.location"] = f"{cert_path}/kafka-client.key"
            if key_password:
                cnf["ssl.key.password"] = key_password
        else:
            raise Exception("UNKNOWN SSL CONFIG")

    if "SASL" in security_prot:
        cnf["sasl.kerberos.keytab"] = f"{krb_path}/kerberos.keytab"
        cnf["sasl.kerberos.principal"] = os.environ["FABRIQUE_KAFKA_SASL_KERBEROS_PRINCIPAL"]


class KafkaConf:
    def __init__(self):
        envdict = EnvDict()

        configs = {
            'bootstrap.servers': os.environ["FABRIQUE_KAFKA_SERVERS"]
        }
        provide_ssl(configs)
        self.configs = configs
        debug = envdict.get("FABRIQUE_KAFKA_DEBUG", "")
        if debug:
            self.configs['debug'] = debug


class AdminConf(KafkaConf):
    def __init__(self):
        envdict = EnvDict()
        super().__init__()

        self.kafka_def_auto_topics = bool(envdict.get('FABRIQUE_KAFKA_DEFAULT_AUTO_TOPICS', 'true'))
        self.partitions = int(envdict.get('PARTITIONS', '0'))
        self.replication = int(envdict.get('REPLICATION', '1'))
        self.retention_ms = int(envdict.get('RETENTION_MS', '86400000'))
        self.retention_bytes = int(envdict.get('RETENTION_BYTES', 1024 * 1024 * 100))
        self.metrics_topic = envdict.get('FABRIQUE_METRIC_COLLECTOR_TOPIC', 'fabrique.monitor.in')
        self.metrics_retention_ms = int(envdict.get('FABRIQUE_KAFKA_METRICS_RETENTION_MS', '86400000'))
        self.metrics_retention_bytes = int(envdict.get('FABRIQUE_KAFKA_METRICS_RETENTION_BYTES', '150000000'))
        self.min_mes_to_report = int(envdict.get('FABRIQUE_SYNC_MIN_MES_TO_REPORT', '6000'))
        self.min_sec_to_report = float(envdict.get('FABRIQUE_SYNC_MIN_SEC_TO_REPORT', '1.0'))


class ConsConf(KafkaConf):
    def __init__(self):
        print('init ConsConf')
        envdict = EnvDict()

        super().__init__()
        self.topic_in = envdict['TOPIC_IN']
        self.consumer_num_messages = int(envdict.get('CONSUMER_NUM_MESSAGES', '20000'))
        self.consumer_timeout_s = float(envdict.get('CONSUMER_TIMEOUT_S', '0.1'))
        self.configs['session.timeout.ms'] = envdict.get('FABRIQUE_KAFKA_SESSION_TIMEOUT', '6000')
        self.configs['auto.offset.reset'] = envdict.get('FABRIQUE_KAFKA_OFFSET_RESET', 'latest')
        self.configs['enable.auto.commit'] = envdict.get('FABRIQUE_KAFKA_AUTO_COMMIT', 'true')
        self.configs['group.id'] = envdict.get('GROUP_ID')
        print(f'self.topic_in: {self.topic_in}')
        print(f"self.configs['group.id']: {self.configs['group.id']}")


class ProdConf(KafkaConf):
    def __init__(self, sends_to_topic_out=True, is_dispatcher=False):
        print('init ProdConf')
        envdict = EnvDict()

        super().__init__()
        if is_dispatcher:
            print(envdict['TOPIC_OUT_DICT'])
            self.topic_out_dict = json.loads(envdict['TOPIC_OUT_DICT']) if sends_to_topic_out else None
            self.topic_out = None
        else:
            self.topic_out_dict = None
            self.topic_out = envdict['TOPIC_OUT'] if sends_to_topic_out else None
        self.configs['queue.buffering.max.messages'] = envdict.get('FABRIQUE_KAFKA_SEND_BUFFER', '35000')
        print(f'sends_to_topic_out={sends_to_topic_out}, is_dispatcher={is_dispatcher}')
        print(f'self.topic_out: {self.topic_out}')
        print(f'self.topic_out_dict: {self.topic_out_dict}')
