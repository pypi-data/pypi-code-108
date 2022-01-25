# common.py - models that are shared across versions.

from specd.sdk import BaseModel


class AnnotationList(BaseModel):

    # Set of keys that are NOT annotations. New top-level keys must be added.
    META_KEYS = {"errors", "is_created", "additionalProperties", "normalized"}

    def get_annotation(self, key):
        obj_dict = getattr(self, key, None)
        if obj_dict:
            return self.instantiate(self.definitions.Annotation, obj_dict)

    def iter_annotations(self):
        for key in self:
            if key not in AnnotationList.META_KEYS:
                yield self.get_annotation(key)


class AnnotationMatchList(BaseModel):
    # Set of keys that are NOT annotations. New top-level keys must be added.
    META_KEYS = {"errors", "is_created", "additionalProperties", "normalized"}

    def get_annotation(self, key):
        obj_dict = getattr(self, key, None)
        if obj_dict:
            return self.instantiate(self.definitions.AnnotationMatch, obj_dict)

    def iter_annotations(self):
        for key in self:
            if key not in AnnotationMatchList.META_KEYS:
                yield self.get_annotation(key)


class VariantInterpretationResponse(BaseModel):

    # set of keys that are NOT part of the variant interpretations response
    META_KEYS = {"errors", "additionalProperties"}

    def get_var_int_data(self, key):
        obj_dict = getattr(self, key, None)
        if obj_dict:
            return self.instantiate(
                self.definitions.VariantInterpretationSingleResponse, obj_dict
            )

    def iter_var_int_data(self):
        for key in self:
            if key not in VariantInterpretationResponse.META_KEYS:
                yield self.get_var_int_data(key)


# MEGA-MATCH MODELS


def convert_object_to_dict(o):
    if o is None:
        return o
    return {key: getattr(o, key) for key in o}


class MegaMatchSingleTherapyObject(BaseModel):
    def convert_to_dict(self):
        d = {}
        for key in self:
            if key in [
                "detected_alterations",
                "match_results",
                "matched_diseases",
            ]:
                d[key] = [
                    convert_object_to_dict(o) for o in getattr(self, key, [])
                ]
            else:
                d[key] = getattr(self, key)
        return d


class MegaMatchTherapyDocument(BaseModel):
    def convert_single_therapy_to_dict(self, t: MegaMatchSingleTherapyObject):
        if t:
            t = t.convert_to_dict()
        return t

    def convert_to_dict(self):
        d = {}
        for key in self:
            if key == "consolidated":
                d[key] = self.convert_single_therapy_to_dict(
                    getattr(self, key)
                )
            elif key in [
                "approvals",
                "guidelines",
                "special_statuses",
                "evidence",
                "associations",
            ]:
                therapies = getattr(self, key, [])
                d[key] = [
                    self.convert_single_therapy_to_dict(t) for t in therapies
                ]
            else:
                d[key] = getattr(self, key, None)
        return d


class MegaMatchTrialDocument(BaseModel):
    def convert_to_dict(self):
        d = {}
        for key in self:
            if key == "clinical_trial_arms":
                arms = getattr(self, key, [])
                d[key] = [convert_object_to_dict(arm) for arm in arms]
            else:
                d[key] = getattr(self, key, None)
        return d


class MegaMatchResult(BaseModel):
    def convert_therapy_to_dict(self, t: MegaMatchTherapyDocument):
        if t:
            t = t.convert_to_dict()
        return t

    def convert_trial_to_dict(self, t: MegaMatchTrialDocument):
        if t:
            t = t.convert_to_dict()
        return t

    def convert_to_dict(self):
        # convert the therapies/clinical_trials fields from lists of model
        # instances to lists of dicts
        d = {}
        for key in self:
            if key == "therapies":
                therapies = getattr(self, key, [])
                d[key] = [self.convert_therapy_to_dict(t) for t in therapies]
            elif key == "clinical_trials":
                trials = getattr(self, key, [])
                d["clinical_trials"] = [
                    self.convert_trial_to_dict(t) for t in trials
                ]
            else:
                d[key] = getattr(self, key, None)
        return d
