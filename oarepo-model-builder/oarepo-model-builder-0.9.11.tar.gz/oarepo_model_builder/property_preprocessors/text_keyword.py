from oarepo_model_builder.builders.jsonschema import JSONSchemaBuilder
from oarepo_model_builder.builders.mapping import MappingBuilder
from oarepo_model_builder.invenio.invenio_record_schema import InvenioRecordSchemaBuilder
from oarepo_model_builder.property_preprocessors import PropertyPreprocessor, process
from oarepo_model_builder.utils.deepmerge import deepmerge
from oarepo_model_builder.stack import ModelBuilderStack


class TextKeywordPreprocessor(PropertyPreprocessor):
    TYPE = 'text_keyword'
    #
    # type='fulltext' in model
    #

    @process(model_builder=JSONSchemaBuilder,
             path='**/properties/*',
             condition=lambda current, stack: current.type == 'fulltext')
    def modify_fulltext_schema(self, data, stack: ModelBuilderStack, **kwargs):
        data['type'] = 'string'
        return data

    @process(model_builder=MappingBuilder,
             path='**/properties/*',
             condition=lambda current, stack: current.type == 'fulltext')
    def modify_fulltext_mapping(self, data, stack: ModelBuilderStack, **kwargs):
        data['type'] = 'text'
        return data

    @process(model_builder=InvenioRecordSchemaBuilder,
             path='**/properties/*',
             condition=lambda current, stack: current.type == 'fulltext')
    def modify_fulltext_marshmallow(self, data, stack: ModelBuilderStack, **kwargs):
        data['type'] = 'string'
        return data

    #
    # type='keyword' in model
    #

    @process(model_builder=JSONSchemaBuilder,
             path='**/properties/*',
             condition=lambda current, stack: current.type == 'keyword')
    def modify_keyword_schema(self, data, stack: ModelBuilderStack, **kwargs):
        data['type'] = 'string'
        return data

    @process(model_builder=MappingBuilder,
             path='**/properties/*',
             condition=lambda current, stack: current.type == 'keyword')
    def modify_keyword_mapping(self, data, stack: ModelBuilderStack, **kwargs):
        data['type'] = 'keyword'
        deepmerge(
            data.setdefault('oarepo:mapping', {}),
            {
                'ignore_above': self.settings['elasticsearch']['keyword-ignore-above']
            })
        return data

    @process(model_builder=InvenioRecordSchemaBuilder,
             path='**/properties/*',
             condition=lambda current, stack: current.type == 'keyword')
    def modify_keyword_marshmallow(self, data, stack: ModelBuilderStack, **kwargs):
        data['type'] = 'string'
        return data

    #
    # type='fulltext+keyword' in model
    #

    @process(model_builder=JSONSchemaBuilder,
             path='**/properties/*',
             condition=lambda current, stack: current.type == 'fulltext+keyword')
    def modify_fulltext_keyword_schema(self, data, stack: ModelBuilderStack, **kwargs):
        data['type'] = 'string'
        return data

    @process(model_builder=MappingBuilder,
             path='**/properties/*',
             condition=lambda current, stack: current.type == 'fulltext+keyword')
    def modify_fulltext_keyword_mapping(self, data, stack: ModelBuilderStack, **kwargs):
        data['type'] = 'text'
        deepmerge(
            data.setdefault('oarepo:mapping', {}),
            {
                'fields': {
                    'keyword': {
                        'type': 'keyword',
                        'ignore_above': self.settings['elasticsearch']['keyword-ignore-above']
                    }
                }
            }, [])
        return data

    @process(model_builder=InvenioRecordSchemaBuilder,
             path='**/properties/*',
             condition=lambda current, stack: current.type == 'fulltext+keyword')
    def modify_fulltext_keyword_marshmallow(self, data, stack: ModelBuilderStack, **kwargs):
        data['type'] = 'string'
        return data
