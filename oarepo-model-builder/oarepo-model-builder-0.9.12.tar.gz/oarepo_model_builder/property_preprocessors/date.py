from oarepo_model_builder.builders.jsonschema import JSONSchemaBuilder
from oarepo_model_builder.invenio.invenio_record_schema import InvenioRecordSchemaBuilder
from oarepo_model_builder.property_preprocessors import PropertyPreprocessor, process
from oarepo_model_builder.stack import ModelBuilderStack
from oarepo_model_builder.utils.deepmerge import deepmerge


class DatePreprocessor(PropertyPreprocessor):
    TYPE = 'date'

    @process(model_builder=JSONSchemaBuilder,
             path='**/properties/*',
             condition=lambda current, stack: current.type == 'date')
    def modify_date_jsonschema(self, data, stack: ModelBuilderStack, **kwargs):
        data['type'] = 'string'
        data.setdefault('format', 'date')
        return data

    @process(model_builder=InvenioRecordSchemaBuilder,
             path='**/properties/*',
             condition=lambda current, stack: current.type == 'date')
    def modify_date_marshmallow(self, data, stack: ModelBuilderStack, **kwargs):
        deepmerge(
            data.setdefault('oarepo:marshmallow', {}),
            {
                'class': 'ma_fields.Date'
                # TODO: validators, such as minDate, maxDate, minDateExclusive, maxDateExclusive
            }
        )
        return data
