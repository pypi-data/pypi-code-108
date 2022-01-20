"""
    Utils for monitoring systems.
    Influx DB will be used for monitoring DB
"""
import os
from lantern_data_manager.influx import InfluxController
from lantern_sl.utils.time import current_ts
## Base variables definition.

IS_LOCAL = os.environ.get('IS_LOCAL', None)
INSIDE_VPC = os.environ.get('INSIDE_VPC', None)
MONITOR_INFLUX_URL = os.environ.get("MONITOR_INFLUX_URL_PUBLIC" if not INSIDE_VPC or IS_LOCAL else "MONITOR_INFLUX_URL", None)
MONITOR_INFLUX_ORGANIZATION = os.environ.get("MONITOR_INFLUX_ORGANIZATION", None)
MONITOR_INFLUX_BUCKET = os.environ.get("MONITOR_INFLUX_BUCKET", None)
MONITOR_INFLUX_TOKEN = os.environ.get("MONITOR_INFLUX_TOKEN", None)

STAGE = os.environ.get("STAGE", None)
LOG_LEVEL = os.environ.get("LOG_LEVEL", None)
AWS_LAMBDA_FUNCTION_NAME = os.environ.get("AWS_LAMBDA_FUNCTION_NAME", None)
AWS_LAMBDA_FUNCTION_MEMORY_SIZE = os.environ.get("AWS_LAMBDA_FUNCTION_MEMORY_SIZE", None)
AWS_EXECUTION_ENV = os.environ.get("AWS_EXECUTION_ENV", None)
LOG_LEVEL = os.environ.get("LOG_LEVEL", None)



_controller = InfluxController(url=MONITOR_INFLUX_URL, org=MONITOR_INFLUX_ORGANIZATION, token=MONITOR_INFLUX_TOKEN)


def monitor(id, data, tags={}, debug=False):
    """ track monitoring request with id saving the data to be monitored and some optional tags. 

    Args:
        id (string): unique id to identify this record in monitoring bucket/org
        data (struct, of {key: value}): List of values to monitor.
        tags (list, of strings): List of strings to tag record. Defaults to {}.
            stage will be added as a known tag.
    Ussage example:

        - monitor(id="step_blank", data={"device_id": "BD1234", "temp": 12})
        - monitor(id="step_entrypoint", data={"device_id": "BD1234"} tags=["ble", "sigfox"])
    """
    try:
        if debug:
            print("-- Monitoring with id: {}, data:{} tags:{}".format(id, data, tags))

        # validations
        if not MONITOR_INFLUX_URL:
            raise Exception("MONITOR_INFLUX_URL and MONITOR_INFLUX_URL_PUBLIC not found in env variables, remember to add following variables to your env: MONITOR_INFLUX_URL, MONITOR_INFLUX_URL_PUBLIC, MONITOR_INFLUX_ORGANIZATION, MONITOR_INFLUX_BUCKET, MONITOR_INFLUX_TOKEN")
        if not MONITOR_INFLUX_ORGANIZATION:
            raise Exception("MONITOR_INFLUX_ORGANIZATION not found in env variables, remember to add following variables to your env: MONITOR_INFLUX_URL, MONITOR_INFLUX_ORGANIZATION, MONITOR_INFLUX_BUCKET, MONITOR_INFLUX_TOKEN")
        if not MONITOR_INFLUX_BUCKET:
            raise Exception("MONITOR_INFLUX_BUCKET not found in env variables, remember to add following variables to your env: MONITOR_INFLUX_URL, MONITOR_INFLUX_ORGANIZATION, MONITOR_INFLUX_BUCKET, MONITOR_INFLUX_TOKEN")
        if not MONITOR_INFLUX_TOKEN:
            raise Exception("MONITOR_INFLUX_TOKEN not found in env variables, remember to add following variables to your env: MONITOR_INFLUX_URL, MONITOR_INFLUX_ORGANIZATION, MONITOR_INFLUX_BUCKET, MONITOR_INFLUX_TOKEN")

        if not id:
            raise Exception("id is required in monitor input")
        if not data or not data.keys():
            raise Exception("Data is required as a {key: value}, example: {\"device_id\": \"BD001\"}")

        telemetry = {}
        telemetry['measurement'] = id
        telemetry["fields"] = {}
        for key in data.keys():
            telemetry["fields"][key] = data[key]
        if STAGE:
            tags["stage"] = STAGE
        if LOG_LEVEL:
            tags["log_level"] = LOG_LEVEL
        if AWS_LAMBDA_FUNCTION_NAME:
            tags["lambda_name"] = AWS_LAMBDA_FUNCTION_NAME
        if AWS_LAMBDA_FUNCTION_MEMORY_SIZE:
            tags["lambda_memory"] = AWS_LAMBDA_FUNCTION_MEMORY_SIZE
        if AWS_EXECUTION_ENV:
            tags["aws_execution_env"] = AWS_EXECUTION_ENV
        if tags:
            telemetry['tags'] = tags
        
        telemetry["time"] = current_ts()
        if debug:
            print("-- Saving Monitoring with, org: {}, bucket: {}, telemetry: {}".format(MONITOR_INFLUX_ORGANIZATION, MONITOR_INFLUX_BUCKET, telemetry))
        _controller.add_telemetries(bucket=MONITOR_INFLUX_BUCKET, telemetries=[telemetry])
    except Exception as e:
        if debug:
            raise e