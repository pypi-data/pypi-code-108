#!/usr/bin/env python3

import argparse
import collections
import http.client
import io
import json
import sys
import threading
import urllib
from datetime import datetime

import pkg_resources
import requests
import singer
from jsonschema.validators import Draft4Validator

logger = singer.get_logger()


def emit_state(state):
    if state is not None:
        line = json.dumps(state)
        logger.debug('Emitting state {}'.format(line))
        sys.stdout.write("{}\n".format(line))
        sys.stdout.flush()


def flatten(d, parent_key='', sep='__'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, str(v) if type(v) is list else v))
    return dict(items)


def process_records(config, table, records):

    batch = []

    for rec in records:
        batch.append(rec)

        # submit batch if size limit reached
        if len(batch) >= config.get('max_batch_size'):
            submit_request(config, batch, table)
            batch = []

    # submit remaining entries not exceeding the limit
    if len(batch) > 0:
        submit_request(config, batch, table)

    logger.info(f"Processed {len(records)} total records for table {table}")


def submit_request(config, data, table):
    url = f"{config.get('endpoint', 'https://api.airtable.com/v0')}/{config.get('base')}/{table}"
    headers = {"Authorization": f"Bearer {config.get('api_token')}"}

    payload = {
        "records": data,
        "typecast": config.get("typecast", True)
    }

    req = requests.post(url, json=payload, headers=headers)

    if req.ok:
        logger.info(f"Uploaded {len(data)} records into table {table}")
    else:
        logger.error(req.text)


def persist_lines(config, lines):
    state = None
    schemas = {}
    key_properties = {}
    headers = {}
    validators = {}

    now = datetime.now().strftime('%Y%m%dT%H%M%S')

    # collect records for batch upload
    records_bulk = dict()

    # Loop over lines from stdin
    for line in lines:
        try:
            o = json.loads(line)
        except json.decoder.JSONDecodeError:
            logger.error("Unable to parse:\n{}".format(line))
            raise

        if 'type' not in o:
            raise Exception("Line is missing required key 'type': {}".format(line))
        t = o['type']

        if t == 'RECORD':
            if 'stream' not in o:
                raise Exception("Line is missing required key 'stream': {}".format(line))
            if o['stream'] not in schemas:
                raise Exception(
                    "A record for stream {} was encountered before a corresponding schema".format(o['stream']))
            if o['stream'] not in records_bulk:
                records_bulk[o['stream']] = []

            # Get schema for this record's stream
            schema = schemas[o['stream']]

            # Validate record
            validators[o['stream']].validate(o['record'])

            # If the record needs to be flattened, uncomment this line
            flattened_record = flatten(o['record'])

            records_bulk[o['stream']].append({
                "fields": flattened_record
            })

            state = None
        elif t == 'STATE':
            logger.debug('Setting state to {}'.format(o['value']))
            state = o['value']
        elif t == 'SCHEMA':
            if 'stream' not in o:
                raise Exception("Line is missing required key 'stream': {}".format(line))
            stream = o['stream']
            schemas[stream] = o['schema']
            validators[stream] = Draft4Validator(o['schema'])
            if 'key_properties' not in o:
                raise Exception("key_properties field is required")
            key_properties[stream] = o['key_properties']
        else:
            raise Exception("Unknown message type {} in message {}"
                            .format(o['type'], o))

    # process all collected entries
    for table, records in records_bulk.items():
        process_records(config, table, records)

    return state


def send_usage_stats():
    try:
        version = pkg_resources.get_distribution('target-csv').version
        conn = http.client.HTTPConnection('collector.singer.io', timeout=10)
        conn.connect()
        params = {
            'e': 'se',
            'aid': 'singer',
            'se_ca': 'target-airtable',
            'se_ac': 'open',
            'se_la': version,
        }
        conn.request('GET', '/i?' + urllib.parse.urlencode(params))
        response = conn.getresponse()
        conn.close()
    except:
        logger.debug('Collection request failed')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='Config file')
    args = parser.parse_args()

    if args.config:
        with open(args.config) as input:
            config = json.load(input)
    else:
        config = {}

    if not config.get('disable_collection', False):
        logger.info('Sending version information to singer.io. ' +
                    'To disable sending anonymous usage data, set ' +
                    'the config parameter "disable_collection" to true')
        threading.Thread(target=send_usage_stats).start()

    input = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    state = persist_lines(config, input)

    emit_state(state)
    logger.debug("Exiting normally")


if __name__ == '__main__':
    main()
