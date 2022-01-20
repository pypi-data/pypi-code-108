import pytest
from arthurai.core.models import ArthurModel, ExplainabilityParameters
from arthurai.core.attributes import ArthurAttribute
from tests.test_request_models.fixtures import explainability_response_objects, explainability_json_strings, \
    model_attribute_objects, model_attribute_json_strings, model_response_json_strings, model_response_objects, \
    explainability_dicts, model_attribute_dicts, model_response_dicts


class TestExplainabilityParameterObject:
    @pytest.mark.parametrize('explainability_response, explainability_json_string',
                             tuple(zip(explainability_response_objects.values(), explainability_json_strings.values())))
    def test_explainability_response_serialization(self, explainability_response, explainability_json_string):
        # we will skip the 3rd string as we only want to test deserialization of unknown fields
        if explainability_json_string != explainability_json_strings[3]:
            assert explainability_json_string == explainability_response.to_json()

    @pytest.mark.parametrize('explainability_response, explainability_json_string',
                             tuple(zip(explainability_response_objects.values(), explainability_json_strings.values())))
    def test_explainability_response_deserialization(self, explainability_response, explainability_json_string):
        deserialzed_explainability_response = ExplainabilityParameters.from_json(explainability_json_string)
        assert deserialzed_explainability_response == explainability_response

    @pytest.mark.parametrize('explainability_response, explainability_dict',
                             tuple(zip(explainability_response_objects.values(), explainability_dicts.values())))
    def test_explainability_response_to_dict(self, explainability_response, explainability_dict):
        actual_explainability_response_dict = explainability_response.to_dict()
        assert actual_explainability_response_dict == explainability_dict


class TestArthurAttributeObject:
    @pytest.mark.parametrize('model_attribute_response, model_attribute_json_string',
                             tuple(zip(model_attribute_objects.values(), model_attribute_json_strings.values())))
    def test_model_attribute_response_serialization(self, model_attribute_response, model_attribute_json_string):
        # we will skip the 4th string as we only want to test deserialization of unknown fields
        if model_attribute_json_string != model_attribute_json_strings[4]:
            assert model_attribute_json_string == model_attribute_response.to_json()

    @pytest.mark.parametrize('model_attribute_response, model_attribute_json_string',
                             tuple(zip(model_attribute_objects.values(), model_attribute_json_strings.values())))
    def test_model_attribute_response_deserialization_json(self, model_attribute_response, model_attribute_json_string):
        deserialized_model_attribute_response = ArthurAttribute.from_json(model_attribute_json_string)
        assert deserialized_model_attribute_response == model_attribute_response

    @pytest.mark.parametrize('model_attribute_response, model_attribute_dict',
                             tuple(zip(model_attribute_objects.values(), model_attribute_dicts.values())))
    def test_model_attribute_response_deserialization_dict(self, model_attribute_response, model_attribute_dict):
        actual_model_attribute_response_dict = model_attribute_response.to_dict()
        print(actual_model_attribute_response_dict)
        assert actual_model_attribute_response_dict == model_attribute_dict


class TestArthurModelObject:
    @pytest.mark.parametrize('model_response, model_response_json_string',
                             tuple(zip(model_response_objects.values(), model_response_json_strings.values())))
    def test_model_response_serialization(self, model_response, model_response_json_string):
        # we will skip the 3rd string as we only want to test deserialization of unknown fields
        if model_response_json_string != model_response_json_strings[3]:
            assert model_response_json_string == model_response.to_json()
    @pytest.mark.parametrize('model_response, model_response_json_string',
                             tuple(zip(model_response_objects.values(), model_response_json_strings.values())))
    def test_model_response_deserialization(self, model_response, model_response_json_string):
        deserialzed_model_response = ArthurModel.from_json(model_response_json_string)
        assert deserialzed_model_response == model_response
    @pytest.mark.parametrize('model_response, model_response_dict',
                             tuple(zip(model_response_objects.values(), model_response_dicts.values())))
    def test_model_attribute_response_deserialization(self, model_response, model_response_dict):
        actual_model_response_dict = model_response.to_dict()
        assert actual_model_response_dict == model_response_dict
