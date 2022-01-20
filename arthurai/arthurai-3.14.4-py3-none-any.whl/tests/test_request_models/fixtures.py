import os
import json

from arthurai.core.attributes import AttributeCategory, AttributeBin, ArthurAttribute
from arthurai.core.models import ArthurModel, ExplainabilityParameters
from arthurai.core.alerts import AlertRule, AlertRuleSeverity,AlertRuleBound
from arthurai.common.constants import ValueType, InputType, Stage, OutputType
from tests.test_request_models import load_json_string, load_json

# *************************************************************
# fixtures for the TestExplainabilityParametersObject class
# *************************************************************
explainability_response_objects = {
    1: ExplainabilityParameters(explanation_algo='lime',
                                enabled=True,
                                model_server_cpu='800m',
                                model_server_memory='1Gi',
                                explanation_nsamples=4000),
    2: ExplainabilityParameters(explanation_algo='lime',
                                enabled=True),
    3: ExplainabilityParameters(explanation_algo='lime',
                                enabled=True,
                                model_server_cpu='800m',
                                explanation_nsamples=4000)
}

explainability_json_strings = {
    1: '{"enabled": true, "explanation_algo": "lime", "model_server_cpu": "800m", "model_server_memory": "1Gi", '
       '"explanation_nsamples": 4000}',
    2: '{"enabled": true, "explanation_algo": "lime"}',
    3: '{"enabled": true, "explanation_algo": "lime", "model_server_cpu": "800m", "explanation_nsamples": 4000, '
       '"foo": "bar"}'
}

explainability_dicts = {
    1: {
        "explanation_algo": "lime",
        "enabled": True,
        "model_server_cpu": "800m",
        "model_server_memory": "1Gi",
        "explanation_nsamples": 4000
    },
    2: {
        "explanation_algo": "lime",
        "enabled": True
    },
    3: {
        "explanation_algo": "lime",
        "enabled": True,
        "model_server_cpu": "800m",
        "explanation_nsamples": 4000
    }
}

# *************************************************************
# fixtures for the TestExplainabilityParametersObject class
# *************************************************************
categories_1 = [
    AttributeCategory(value='value1'),
    AttributeCategory(value='value2'),
    AttributeCategory(value='value3')
]

categories_2 = [
    AttributeCategory(label='positive_label', value='1'),
    AttributeCategory(label='negative_label', value='0')
]

bins_1 = [
    AttributeBin(continuous_start=0, continuous_end=5),
    AttributeBin(continuous_start=5, continuous_end=18),
    AttributeBin(continuous_start=18, continuous_end=30),
    AttributeBin(continuous_start=30, continuous_end=65),
    AttributeBin(continuous_start=65, continuous_end=100)
]

model_attribute_objects = {
    1: ArthurAttribute(id='8514e278-24d1-4e20-b209-3c77eb2b247f',
                       name='attr_1',
                       value_type=ValueType.Integer,
                       stage=Stage.ModelPipelineInput,
                       categorical=True,
                       monitor_for_bias=False,
                       categories=categories_1,
                       is_unique=False,
                       is_positive_predicted_attribute=False),
    2: ArthurAttribute(id='8514e278-24d1-4e20-b209-3c77eb2b247f',
                       name='attr_2',
                       position=1,
                       value_type=ValueType.Boolean,
                       stage=Stage.ModelPipelineInput,
                       categorical=True,
                       monitor_for_bias=True,
                       categories=categories_2,
                       is_unique=False,
                       is_positive_predicted_attribute=True),
    3: ArthurAttribute(id='04418f36-529b-451e-8524-c57d09d9b02f',
                       name='attr_3',
                       value_type=ValueType.Integer,
                       stage=Stage.ModelPipelineInput,
                       categorical=False,
                       monitor_for_bias=False,
                       min_range=0,
                       max_range=100,
                       bins=bins_1,
                       is_unique=False,
                       is_positive_predicted_attribute=False),
    4: ArthurAttribute(id='8514e278-24d1-4e20-b209-3c77eb2b247f',
                       name='attr_3',
                       value_type=ValueType.Integer,
                       stage=Stage.ModelPipelineInput,
                       categorical=False,
                       monitor_for_bias=False,
                       min_range=0,
                       max_range=100,
                       bins=bins_1,
                       is_unique=False,
                       is_positive_predicted_attribute=False)
}

# load_json()

model_attribute_json_strings = {
    1: load_json_string(os.path.join(os.path.dirname(__file__), 'resources', 'attribute_with_categories.json')),
    2: load_json_string(os.path.join(os.path.dirname(__file__), 'resources', 'attribute_with_categories_and_labels.json')),
    3: load_json_string(os.path.join(os.path.dirname(__file__), 'resources', 'attribute_with_bins.json')),
    4: load_json_string(os.path.join(os.path.dirname(__file__), 'resources', 'attribute_with_unknown_properties.json'))
}

model_attribute_dicts = {
    1: {
        "id": "8514e278-24d1-4e20-b209-3c77eb2b247f",
        "name": "attr_1",
        "value_type": ValueType.Integer,
        "stage": Stage.ModelPipelineInput,
        "categorical": True,
        "monitor_for_bias": False,
        "categories": [
            {
                "value": "value1"
            },
            {
                "value": "value2"
            },
            {
                "value": "value3"
            }
        ],
        "is_unique": False,
        "is_positive_predicted_attribute": False
    },
    2: {
        "id": "8514e278-24d1-4e20-b209-3c77eb2b247f",
        "name": "attr_2",
        "value_type": ValueType.Boolean,
        "stage": Stage.ModelPipelineInput,
        "position": 1,
        "categorical": True,
        "monitor_for_bias": True,
        "categories": [
            {
                "value": "1",
                "label": "positive_label"
            },
            {
                "value": "0",
                "label": "negative_label"
            }
        ],
        "is_unique": False,
        "is_positive_predicted_attribute": True
    },
    3: {
        "id": "04418f36-529b-451e-8524-c57d09d9b02f",
        "name": "attr_3",
        "value_type": ValueType.Integer,
        "stage": Stage.ModelPipelineInput,
        "categorical": False,
        "min_range": 0,
        "max_range": 100,
        "monitor_for_bias": False,
        "bins": [
            {
                "continuous_start": 0,
                "continuous_end": 5
            },
            {
                "continuous_start": 5,
                "continuous_end": 18
            },
            {
                "continuous_start": 18,
                "continuous_end": 30
            },
            {
                "continuous_start": 30,
                "continuous_end": 65
            },
            {
                "continuous_start": 65,
                "continuous_end": 100
            }
        ],
        "is_unique": False,
        "is_positive_predicted_attribute": False
    }
}

# *************************************************************
# fixtures for the TestArthurModelObject class
# *************************************************************

model_response_objects = {
    1: ArthurModel(id='ac55c7b4-2db7-4902-8cc3-969ed67a20c8',
                   partner_model_id='3456',
                   input_type=InputType.Tabular,
                   output_type=OutputType.Regression,
                   explainability=explainability_response_objects[1],
                   display_name='test model 1',
                   archived=False,
                   created_at='2020-05-15T15:55:17.631797',
                   updated_at='2020-05-15T16:01:07.961584',
                   attributes=[model_attribute_objects[1], model_attribute_objects[2]],
                   tags=['keyword1', 'keyword2'],
                   classifier_threshold=0.5,
                   client=None),
    2: ArthurModel(id='ac55c7b4-2db7-4902-8cc3-969ed67a20c8',
                   partner_model_id='3456',
                   input_type=InputType.Tabular,
                   output_type=OutputType.Regression,
                   explainability=explainability_response_objects[2],
                   archived=False,
                   created_at='2020-05-15T15:55:17.631797',
                   updated_at='2020-05-15T16:01:07.961584',
                   attributes=[model_attribute_objects[3]],
                   classifier_threshold=0.5,
                   client=None),
    3: ArthurModel(id='ac55c7b4-2db7-4902-8cc3-969ed67a20c8',
                   partner_model_id='3456',
                   input_type=InputType.Tabular,
                   output_type=OutputType.Regression,
                   explainability=explainability_response_objects[2],
                   archived=False,
                   created_at='2020-05-15T15:55:17.631797',
                   updated_at='2020-05-15T16:01:07.961584',
                   attributes=[model_attribute_objects[3]],
                   classifier_threshold=0.5,
                   client=None)
}

model_response_json_strings = {
    1: load_json_string(os.path.join(os.path.dirname(__file__), 'resources', 'model_with_categories.json')),
    2: load_json_string(os.path.join(os.path.dirname(__file__), 'resources', 'model_with_attributes.json')),
    3: load_json_string(os.path.join(os.path.dirname(__file__), 'resources', 'model_with_unknown_properties.json')),
    4: load_json_string(os.path.join(os.path.dirname(__file__), 'resources', 'model_binary_with_bias.json')),
    5: load_json_string(os.path.join(os.path.dirname(__file__), 'resources', 'model_multiclass_with_bias.json'))
}

model_response_dicts = {
    1: {
        "partner_model_id": "3456",
        "input_type": InputType.Tabular,
        "output_type": OutputType.Regression,
        "explainability": {
            "explanation_algo": "lime",
            "enabled": True,
            "model_server_cpu": "800m",
            "model_server_memory": "1Gi",
            "explanation_nsamples": 4000
        },
        "id": "ac55c7b4-2db7-4902-8cc3-969ed67a20c8",
        "display_name": "test model 1",
        "is_batch": False,
        "archived": False,
        "created_at": "2020-05-15T15:55:17.631797",
        "updated_at": "2020-05-15T16:01:07.961584",
        "attributes": [
            {
                "id": "8514e278-24d1-4e20-b209-3c77eb2b247f",
                "name": "attr_1",
                "value_type": ValueType.Integer,
                "stage": Stage.ModelPipelineInput,
                "categorical": True,
                "monitor_for_bias": False,
                "categories": [
                    {
                        "value": "value1"
                    },
                    {
                        "value": "value2"
                    },
                    {
                        "value": "value3"
                    }
                ],
                "is_unique": False,
                "is_positive_predicted_attribute": False
            },
            {
                "id": "8514e278-24d1-4e20-b209-3c77eb2b247f",
                "name": "attr_2",
                "value_type": ValueType.Boolean,
                "stage": Stage.ModelPipelineInput,
                "position": 1,
                "categorical": True,
                "monitor_for_bias": True,
                "categories": [
                    {
                        "value": "1",
                        "label": "positive_label"
                    },
                    {
                        "value": "0",
                        "label": "negative_label"
                    }
                ],
                "is_unique": False,
                "is_positive_predicted_attribute": True
            }
        ],
        "tags": [
            "keyword1",
            "keyword2"
        ],
        "classifier_threshold": 0.5
    },
    2: {
        "partner_model_id": "3456",
        "input_type": InputType.Tabular,
        "output_type": OutputType.Regression,
        "explainability": {
            "explanation_algo": "lime",
            "enabled": True
        },
        "id": "ac55c7b4-2db7-4902-8cc3-969ed67a20c8",
        "is_batch": False,
        "archived": False,
        "created_at": "2020-05-15T15:55:17.631797",
        "updated_at": "2020-05-15T16:01:07.961584",
        "attributes": [
            {
                "id": "04418f36-529b-451e-8524-c57d09d9b02f",
                "name": "attr_3",
                "value_type": ValueType.Integer,
                "stage": Stage.ModelPipelineInput,
                "categorical": False,
                "min_range": 0,
                "max_range": 100,
                "monitor_for_bias": False,
                "bins": [
                    {
                        "continuous_start": 0,
                        "continuous_end": 5
                    },
                    {
                        "continuous_start": 5,
                        "continuous_end": 18
                    },
                    {
                        "continuous_start": 18,
                        "continuous_end": 30
                    },
                    {
                        "continuous_start": 30,
                        "continuous_end": 65
                    },
                    {
                        "continuous_start": 65,
                        "continuous_end": 100
                    }
                ],
                "is_unique": False,
                "is_positive_predicted_attribute": False
            }
        ],
        "classifier_threshold": 0.5
    },
    3: {
        "partner_model_id": "3456",
        "input_type": InputType.Tabular,
        "output_type": OutputType.Regression,
        "explainability": {
            "explanation_algo": "lime",
            "enabled": True
        },
        "id": "ac55c7b4-2db7-4902-8cc3-969ed67a20c8",
        "is_batch": False,
        "archived": False,
        "created_at": "2020-05-15T15:55:17.631797",
        "updated_at": "2020-05-15T16:01:07.961584",
        "attributes": [
            {
                "id": "04418f36-529b-451e-8524-c57d09d9b02f",
                "name": "attr_3",
                "value_type": ValueType.Integer,
                "stage": Stage.ModelPipelineInput,
                "categorical": False,
                "min_range": 0,
                "max_range": 100,
                "monitor_for_bias": False,
                "bins": [
                    {
                        "continuous_start": 0,
                        "continuous_end": 5
                    },
                    {
                        "continuous_start": 5,
                        "continuous_end": 18
                    },
                    {
                        "continuous_start": 18,
                        "continuous_end": 30
                    },
                    {
                        "continuous_start": 30,
                        "continuous_end": 65
                    },
                    {
                        "continuous_start": 65,
                        "continuous_end": 100
                    }
                ],
                "is_unique": False,
                "is_positive_predicted_attribute": False
            }
        ],
        "classifier_threshold": 0.5
    }
}


# *************************************************************
# fixtures for AlertRules
# *************************************************************
AlertRuleObject_1 = AlertRule(
    bound=AlertRuleBound.Upper,
    threshold=0.5,
    metric_id="e14e6aac-0c94-4a78-a104-871f70b8b476",
    severity=AlertRuleSeverity.Warning
)

AlertRuleDict_1 = {
    "bound": "upper",
    "threshold": 0.5,
    "metric_id": "e14e6aac-0c94-4a78-a104-871f70b8b476",
    "severity": "warning",
    "enabled": True
}

AlertRuleJson_1 = json.dumps(load_json(os.path.join(os.path.dirname(__file__), 'resources', 'alert_rule_1.json')))

AlertRuleObject_2 = AlertRule(
    bound=AlertRuleBound.Upper,
    threshold=0.5,
    metric_id="e14e6aac-0c94-4a78-a104-871f70b8b476",
    severity=AlertRuleSeverity.Warning
)

AlertRuleDict_2 = {
    "bound": "upper",
    "threshold": 0.5,
    "metric_id": "e14e6aac-0c94-4a78-a104-871f70b8b476",
    "severity": "warning",
    "enabled": True,
}

AlertRuleJson_2 = json.dumps(load_json(os.path.join(os.path.dirname(__file__), 'resources', 'alert_rule_2.json')))

AlertRuleObject_3 = AlertRule(
    bound=AlertRuleBound.Upper,
    threshold=0.5,
    metric_id="e14e6aac-0c94-4a78-a104-871f70b8b476",
    severity=AlertRuleSeverity.Warning,
    enabled=False,
    id="37c8a2cb-b607-4b77-9a89-9d34ee6e3516"
)

AlertRuleDict_3 = {
    "bound": "upper",
    "threshold": 0.5,
    "metric_id": "e14e6aac-0c94-4a78-a104-871f70b8b476",
    "severity": "warning",
    "enabled": False,
    "id": "37c8a2cb-b607-4b77-9a89-9d34ee6e3516",
}

AlertRuleJson_3 = json.dumps(load_json(os.path.join(os.path.dirname(__file__), 'resources', 'alert_rule_3.json')))

