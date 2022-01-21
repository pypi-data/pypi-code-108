import sys
import pathlib
import inspect
import os
import json
import datetime

sys.path.append(str(pathlib.Path(__file__).resolve().parent / 'src'))
from main import main
from MXException import *
import uuid


def get_event():
    event_json = {}
    event = {}
    event_path = pathlib.Path(__file__).resolve().parent / 'event.json'
    if os.path.exists(str(event_path)):
        with open(event_path) as event_file:
            event_json = json.loads(event_file.read())
    event['body'] = event_json['body'] if 'body' in event_json else {}
    event['query_string_parameters'] = event_json[
        'query_string_parameters'] if 'query_string_parameters' in event_json else {}
    event['source'] = event_json['source'] if 'source' in event_json else {}
    event['job_name'] = os.path.basename(pathlib.Path(__file__).resolve().parent)
    event['job_instance_id'] = uuid.uuid4().__str__()
    event['retry_attempt'] = event_json['retry_attempt'] if 'retry_attempt' in event_json else 0
    return event


if __name__ == '__main__':
    start_time = datetime.datetime.now()
    try:
        print('Batch Job Started', 'Started at', start_time.strftime('%Y-%m-%dT%H:%M:%S%z'))
        sig = inspect.signature(main)
        parameters_count = len(sig.parameters)
        if parameters_count == 0:
            main()
        elif parameters_count == 1:
            event = get_event()
            main(event)
        else:
            raise MXTooManyParametersError()
    finally:
        end_time = datetime.datetime.now()
        print('Batch Job Ended,', 'Ended at', end_time.strftime('%Y-%m-%dT%H:%M:%S%z'))
        time_diff = (end_time - start_time).seconds
        sec = time_diff % 60
        minutes = (time_diff // 60) % 60
        hour = time_diff // 3600
        runtime = ''
        runtime += (str(hour) + ' hr ') if hour > 0 else ''
        runtime += (str(minutes) + ' min ') if minutes > 0 else ''
        runtime += (str(sec) + ' sec ') if runtime == '' or sec > 0 else ''
        print('Batch Job Runtime :', runtime)
