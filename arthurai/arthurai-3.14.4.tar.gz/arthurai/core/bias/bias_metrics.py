from typing import Optional
from datetime import datetime

from arthurai.common.exceptions import arthur_excepted, UserValueError, MethodNotApplicableError

class BiasMetrics(object):
    def __init__(self, arthur_model):

        self.model = arthur_model 

    @arthur_excepted("Failed to get group-conditional confusion matrices")
    def group_confusion_matrices(self, attr_name: str, 
                           pred_property: Optional[str] = None,
                           batch_id: Optional[str] = None,
                           start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None,
                           return_by_metric=True):
        """
        Get group-conditional confusion matrices for all inferences, with the option to filter for a `batch_id` or
        a particular chunk of time. Currently only supports calculating bias with respect to a single sensitive
        attribute at a time. This method handles both binary and multiclass models. 

        :param attr_name: The name of the sensitive attribute to get metrics for.
        :param pred_property: For multiclass models, the predicted label to get the confusion matrix for. 
        :param batch_id: Optional filter to limit calculations to a specific batch ID. 
        :param start_time: Optional filter to limit calculations to inferences after a specific timestamp.
        :param end_time: Optional filter to limit calculations to inferences before a specific timestamp.
        :param return_by_metric: Whether the returned dictionary of results should be keyed by metric or by sensitive attribute value.

        :return: Either a dict of the form `{ metric: { sens_1: val1, sens_2: val2 }, ...}` (default) or its reverse. 
        """

        # check whether model has any attributes marked as `monitor_for_bias`
        if not self.model.check_has_bias_attrs():
            raise MethodNotApplicableError("This model does not have any attributes set to monitor for bias.")

        if not self.model.check_attr_is_bias(attr_name):
            raise MethodNotApplicableError("This attribute is not set to monitor for bias.")

        if batch_id and not self.model.is_batch:
            raise UserValueError("This is not a batch model; remove the `batch_id` argument.")

        pos_attr = self.model.get_positive_predicted_class()

        if pos_attr:
            q = _bias_cm_query(attr_name, batch_id=batch_id, 
                                            classifier_threshold=self.model.classifier_threshold,
                                            start_time=start_time,
                                            end_time=end_time)
        elif not pred_property:
            raise UserValueError("For a multiclass model, the `pred_property` parameter must be specified.")
        else:
            q = _bias_multiclass_cm_query(attr_name, pred_property=pred_property,
                                            batch_id=batch_id,
                                            start_time=start_time,
                                            end_time=end_time)

        resp = self.model.query(q)

        sens_keyed = {x[attr_name]: x['confusion_matrix'] for x in resp}

        if return_by_metric:
            metr_keys = ['accuracy_rate', 'balanced_accuracy_rate', 'f1', 'false_negative_rate', 'false_positive_rate', 'precision', 'true_negative_rate', 'true_positive_rate']
            return {x: {s: sens_keyed[s][x]for s in sens_keyed.keys()} for x in metr_keys} # reverse the dictionary 

        return sens_keyed


    @arthur_excepted("Failed to get group-conditional positivity rates")
    def group_positivity_rates(self, attr_name: str,
                            batch_id: str = None,
                            start_time: datetime = None,
                            end_time:datetime = None):
        """
        Get group-conditional positivity rates for all inferences, with the option to filter for a `batch_id` or
        a particular chunk of time. Currently only supports calculating bias with respect to a single sensitive
        attribute at a time. This method currently only handles binary models. 

        :param attr_name: The name of the sensitive attribute to get metrics for.
        :param batch_id: Optional filter to limit calculations to a specific batch ID. 
        :param start_time: Optional filter to limit calculations to inferences after a specific timestamp.
        :param end_time: Optional filter to limit calculations to inferences before a specific timestamp.

        :return: A dict of the form {sens_1: pos_1, sens_2: pos_2, ...}
        """

        # check whether model has any attributes marked as `monitor_for_bias`
        if not self.model.check_has_bias_attrs():
            raise MethodNotApplicableError("This model does not have any attributes set to monitor for bias.")

        if not self.model.check_attr_is_bias(attr_name):
            raise MethodNotApplicableError("This attribute is not set to monitor for bias.")
        
        if batch_id and not self.model.is_batch:
            raise UserValueError("This is not a batch model; remove the `batch_id` argument.")

        pos_attr = self.model.get_positive_predicted_class()

        if pos_attr:
            q = _bias_pr_query(attr_name, pred_property=pos_attr,
                                            batch_id=batch_id, 
                                            classifier_threshold=self.model.classifier_threshold,
                                            start_time=start_time,
                                            end_time=end_time)
        else:
            raise UserValueError("Positivity rates are currently only supported for binary classifiers.")

        resp = self.model.query(q)
        return {x[attr_name]: x['positive_rate'] for x in resp}

    # ALIAS METHOD NAMES
    demographic_parity = group_positivity_rates


def _bias_cm_query(sens_attr, classifier_threshold=0.5,  batch_id=None, start_time=None, end_time=None):
    """
    Get group-conditional `metric` (either `confusionMatrixRate` or `rate`) for BINARY classifier
    If batch_id or start/end times are None, then do this over all batches / all time
    Query is identical for streaming
    """

    query = {
        "select": [
            {
                "property": sens_attr
            },
            {
                "function": "confusionMatrixRate",
                "parameters": {
                "threshold": classifier_threshold
                }
            }
            ],
        "group_by": [
            {
                "property": sens_attr
            }
        ]
        }

    query = _add_filters(query, batch_id, start_time, end_time)

    return query

def _bias_multiclass_cm_query(sens_attr, pred_property, batch_id=None, start_time=None, end_time=None):
    """
    Get group-conditional confusion matrix for MULTICLASS classifier (`rate` doesn't apply here, since there is no single threshold)
    If batch_id or start/end times are None, then do this over all batches / all time
    Query is identical for streaming
    """

    query =   {
        "select": [
        {
            "property": sens_attr
        },
        {
            "function": "confusionMatrixRateMulticlass",
            "parameters": {
                "predicted_property": pred_property
            }
        }
        ],
        "group_by": [
        {
            "property": sens_attr
        }
        ]
    }

    query = _add_filters(query, batch_id, start_time, end_time)

    return query

def _bias_pr_query(sens_attr, pred_property, classifier_threshold=0.5, batch_id=None, start_time=None, end_time=None):
    """
    Get group-conditional positivity rates for BINARY classifier
    If batch_id or start/end times are None, then do this over all batches/all time
    Query is identical for streaming
    """

    query = {
        "select": [
            {
                "property": sens_attr
            },
            {
                "function": "rate",
                "alias": "positive_rate",
                "parameters": {
                    "property": pred_property,
                    "comparator": "gte",
                    "value": classifier_threshold
                }
            }
        ], 
        "group_by": [{
            "property": sens_attr
        }]
    }

    query = _add_filters(query, batch_id, start_time, end_time)
    
    return query

def _add_filters(query, batch_id = None, start_time=None, end_time=None):
    if batch_id:
        query["filter"] = [
            {
                "property": "batch_id",
                "comparator": "eq",
                "value": batch_id
            }           
        ]
    
    if start_time:
        query["filter"] = [
            {
                "property": "inference_timestamp",
                "comparator": "gte",
                "value": start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        ]

    if end_time:
        query["filter"] = [
            {
                "property": "inference_timestamp",
                "comparator": "lte",
                "value": end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        ]

    return query
