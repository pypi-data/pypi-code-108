from typing import List, Union, Optional
from datalogue.errors import DtlError, _property_not_found
from datalogue.models.transformations.commons import Transformation
from datalogue.models.classifier import (
    ClassificationMethod,
    _classification_method_from_payload,
)
from datalogue.dtl_utils import _parse_list
from uuid import UUID


# Kept because classify_fields is still depending on it
class Classifier(object):
    def __init__(
        self, classification_methods: List[ClassificationMethod], default_class_id: Optional[Union[UUID, str]] = None,
    ):
        """
        Build a local Classifier

        :param classification_methods: ordered list of Classification Methods
        :param default_class_id: allows the user to specify the class to be defaulted to, if all classification methods
            fail. Default value is `Unknown`. (currently part of replace_class, see below)
        """
        self.classification_methods = classification_methods
        self.default_class_id = default_class_id

    def __repr__(self):
        return (
            "Classifier("
            f"default_class= {self.default_class_id} "
            f"classification_methods= \n{self.classification_methods})"
        )

    def __eq__(self, other: "Classifier"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def _as_payload(self) -> dict:
        base = {
            "classificationMethods": list(map(lambda m: m._as_payload(), self.classification_methods)),
            "defaultClass": self.default_class_id,
        }
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, "Classifier"]:
        classification_methods = json.get("classificationMethods")
        if classification_methods is None:
            return _property_not_found("classificationMethods", json)
        else:
            classification_methods = _parse_list(_classification_method_from_payload)(classification_methods)
            if isinstance(classification_methods, DtlError):
                return classification_methods

        default_class = json.get("default_class")

        return Classifier(classification_methods, default_class)


class Classify(Transformation):
    """
    Apply classes to all data streaming through a pipeline. Classification is based on the Classifier supplied.
    """

    type_str = "Classify"

    def __init__(
        self,
        classifier_id: Union[str, UUID],
        fields_to_target: Optional[List[List[str]]] = None,
        add_class_fields=False,
        add_score_fields=False,
    ):
        """
        Unless specified with parameters below, this transformation does not alter the data schema; classes are
        represented in the backend only.

        :param classifier_id: id of the classifier to use for classification
        :param fields_to_target: specifies which fields to target for classification; remainder are not classified by
         this transformation
        :param add_class_fields: if True, adds a field containing class name for every classified field
        :param add_score_fields: if True, adds a field containing class score for every classified field
        :param use_uuid: When enabled, pipeline will be able to compare by classId instead of class names. requirements:
        1. add_class_fields and add_score_fields must be false
        2. Currently works for Obfuscate transformation

        """

        Transformation.__init__(self, Classify.type_str)
        self.classifier_id = classifier_id
        self.fields_to_target = fields_to_target
        self.add_class_fields = add_class_fields
        self.add_score_fields = add_score_fields

    def __eq__(self, other: "Classify"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return (
            "Classify("
            f"classifier_id= {self.classifier_id}, "
            f"fields_to_target= {self.fields_to_target}, "
            f"add_class_fields= {self.add_class_fields}, "
            f"add_score_fields= {self.add_score_fields})"
        )

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["classifier"] = str(self.classifier_id)
        base["fieldsToTarget"] = self.fields_to_target
        base["addClassFields"] = self.add_class_fields
        base["addScoreFields"] = self.add_score_fields
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, "Classify"]:
        classifier_id = json.get("classifier")
        if classifier_id is None:
            return _property_not_found("classifier", json)

        fields_to_target = json.get("fieldsToTarget")

        add_class_fields = json.get("addClassFields")
        if add_class_fields is None:
            add_class_fields = False

        add_score_fields = json.get("addScoreFields")
        if add_score_fields is None:
            add_score_fields = False

        return Classify(classifier_id, fields_to_target, add_class_fields, add_score_fields)
