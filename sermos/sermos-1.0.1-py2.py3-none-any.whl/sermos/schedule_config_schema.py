""" Schemas for Schedule Configuration
"""
import re
from celery.schedules import crontab_parser
from croniter import croniter
from marshmallow.validate import OneOf
from marshmallow.exceptions import ValidationError
from marshmallow import Schema, fields, EXCLUDE, pre_load, validates_schema


class ExcludeUnknownSchema(Schema):
    """ Remove unknown keys from loaded dictionary

    # TODO this seems to be just ignoring and letting through vs excluding...
    """
    class Meta:
        unknown = EXCLUDE


class IntervalScheduleSchema(Schema):
    every = fields.Integer(required=True)
    period = fields.String(
        required=True,
        validate=OneOf(['microseconds', 'seconds', 'minutes', 'hours',
                        'days']))


class CrontabScheduleSchema(Schema):
    minute = fields.String(required=True)
    hour = fields.String(required=True)
    dayOfWeek = fields.String(required=True)
    dayOfMonth = fields.String(required=True)
    monthOfYear = fields.String(required=True)

    @validates_schema
    def validate_values(self, data, **kwargs):
        if data['minute'] is None or data['hour'] is None or \
            data['dayOfWeek'] is None or data['dayOfMonth'] is None or\
                data['monthOfYear'] is None:
            raise ValidationError("Empty crontab value")

        test_cron_expression = \
            f"{data['minute']} {data['hour']} {data['dayOfMonth']} " \
            f"{data['monthOfYear']} {data['dayOfWeek']}"

        if not croniter.is_valid(test_cron_expression):
            return ValidationError("Invalid crontab value")


class Schedule(fields.Dict):
    def _serialize(self, value, attr, obj, **kwargs):
        return value

    def _deserialize(self, value, attr, data, **kwargs):
        if data['scheduleType'] == 'crontab':
            schema = CrontabScheduleSchema()
        else:
            schema = IntervalScheduleSchema()
        return schema.load(value)


class ScheduleConfigSchemaV1(ExcludeUnknownSchema):
    """ Definition of a single schedule entry

    TODO: Add validation based on schedule_type and the relevant optional fields
    TODO: Add validation that each name is unique
    """

    scheduleType = fields.String(
        required=True,
        validate=OneOf(['interval', 'crontab']),
        description="The Celery schedule type of this entry.",
        example="interval",
        data_key='scheduleType')

    queue = fields.String(required=True,
                          description="Name of queue on which to place task.",
                          example="my-default-queue")
    task = fields.String(required=True,
                         description="Path to task to invoke.",
                         example="my_app.module.method")
    exchange = fields.String(
        required=False,
        description="Exchange for the task. Celery default "
        "used if not set, which is recommended.",
        example="tasks")
    routing_key = fields.String(
        required=False,
        description="Routing key for the task. Celery "
        "default used if not set, which is recommended.",
        example="task.default",
        data_key='routingKey')
    expires = fields.Integer(
        required=False,
        description="Number of seconds after which task "
        "expires if not executed. Default: no expiration.",
        example=60)

    schedule = Schedule(required=True)

    @pre_load
    def validate_string_fields(self, item, **kwargs):
        """ Ensure string fields with no OneOf validation conform to patterns
        """
        if item is None:
            raise ValidationError("NoneType provided, check input.")

        validation_map = {
            'name': r'^[\w\d\-\_\.\s]+$',
            'queue': r'^[\w\d\-\_\.]+$',
            'task': r'^[\w\d\-\_\.]+$',
            'exchange': r'^[\w\d\-\_\.]+$',
            'routing_key': r'^[\w\d\-\_\.]+$'
        }
        for field in validation_map:
            if item.get(field, None) is None:
                continue
            if not bool(re.match(validation_map[field], item[field])):
                raise ValidationError(
                    f"Invalid {field}: `{item[field]}``. Must match pattern: "
                    f"{validation_map[field]}")

        if 'scheduleType' not in item:
            raise ValidationError('Missing required field scheduleType')

        if item['scheduleType'] == 'crontab':
            cron_validation_map = {
                'minute': crontab_parser(60),
                'hour': crontab_parser(24),
                'dayOfWeek': crontab_parser(7),
                'dayOfMonth': crontab_parser(31, 1),
                'monthOfYear': crontab_parser(12, 1)
            }

            for field in cron_validation_map:
                try:
                    cron_validation_map[field].parse(item['schedule'][field])
                except:
                    raise ValidationError(
                        f"Invalid {field}: `{item['schedule'][field]}`. Must "
                        "be valid crontab pattern.")

        return item


class BaseScheduleSchema(ExcludeUnknownSchema):
    __schema_version__ = 0

    name = fields.String(required=True,
                         description="Name of schedule entry.",
                         example="My Scheduled Task")
    schemaVersion = fields.Integer(required=True)
    config = fields.Dict(required=True)
    enabled = fields.Boolean(required=True,
                             description="Whether entry is enabled.",
                             example=True)
    # TODO Figure out where that wonky timestamp format is coming from and
    # update this and in celery_beat.py.
    lastRunAt = fields.DateTime(allow_none=True,
                                missing=None,
                                description="Timestamp of last run time.",
                                example="Tue, 18 Aug 2020 01:36:06 GMT",
                                data_key='lastRunAt')
    totalRunCount = fields.Integer(
        allow_none=True,
        missing=0,
        description="Count of number of executions.",
        example=12345,
        data_key='totalRunCount')

    @classmethod
    def get_by_version(cls, version):
        for subclass in cls.__subclasses__():
            if subclass.__schema_version__ == version:
                return subclass

        return None

    @classmethod
    def get_latest(cls):
        max_version = 0
        max_class = None
        for subclass in cls.__subclasses__():
            if subclass.__schema_version__ > max_version:
                max_version = max_version
                max_class = subclass

        return max_class

    @validates_schema
    def validate_scheduled_tasks(self, data, **kwargs):
        schema_version = data['schemaVersion']
        TaskSchema = BaseScheduleSchema.get_by_version(schema_version)
        schema = TaskSchema()
        schema.load(data)


class ScheduleSchemaV1(BaseScheduleSchema):
    __schema_version__ = 1

    config = fields.Nested(
        ScheduleConfigSchemaV1,
        required=True,
        description="Configuration information for this schedule.")

    def validate_scheduled_tasks(self, data, **kwargs):
        # We need to add this function to avoid infinite recursion since
        # the BaseScheduleSchema class above uses the same method for
        # validation
        pass
