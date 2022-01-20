from dataclasses import dataclass
from typing import Any, Dict, Optional
import matplotlib.pyplot as plt
import pandas as pd

from arthurai.common.exceptions import InternalValueError, UserValueError, arthur_excepted, MethodNotApplicableError

DemographicParity= "demographic_parity"
EqualOpportunity = "equal_opportunity"
EqualizedOdds = "equalized_odds"

CONSTRAINT_PLOT_DICT = {
    DemographicParity: ["selection_rate", "accuracy"],
    EqualOpportunity: ["true_positive_rate", "accuracy"],
    EqualizedOdds: ["false_positive_rate", "true_positive_rate"]
}


@dataclass
class Curves(object):
    """
    A class which defines information about a given set of curves for a specific sensitive
    attribute and a specific constraint, as well as a dictionary mapping attribute values 
    to the curves themselves
    """
    attribute_name: str
    constraint: str
    max_acc_idx: int
    attr_val_to_threshold: Dict[str, pd.DataFrame]


class ThresholdMitigation(object):
    def __init__(self, arthur_model): # type not enforced to prevent circular imports, not optimal
        """
        arthur_model should be of type ArthurModel. 
        """
        self.model = arthur_model

    def enable(self):
        """
        Triggers workflow to train curves for all constraints and for all sensitive attributes.
        Equivalent to calling `arthurmodel.enable_bias_mitigation()`; here for convenience.
        """
        return self.model.enable_bias_mitigation()

    @arthur_excepted("Failed to fetch curve for given attribute and constraint")
    def get_curves(self, attribute: str, constraint: str = EqualOpportunity):
        """
        Fetch curves for the given sensitive attribute and constraint.

        :param attribute: Name of the sensitive attribute to fetch curves for. 
        :param constraint: 
        :return: a Curves object which contains information about the attribute, constraint, accuracy-maximizing index,
        and the actual curves.
        """

        if constraint not in CONSTRAINT_PLOT_DICT:
            raise UserValueError("`constraint` argument must be one of `demographic_parity`, `equal_opportunity`, or "
                                 "`equalized_odds`.")
        
        attr_id = self.model.get_attribute(attribute).id
        endpoint = (f"/models/{self.model.id}/enrichments/bias_mitigation/curves?attribute_id={attr_id}"
                    f"&constraint={constraint}")
        resp = self.model._client.get(endpoint)['data']  # returns one dictionary of info per sensitive feature value

        if resp is None:
            raise MethodNotApplicableError("No curves were found at this endpoint; check your attribute and constraint. \
            If you were expecting a curve to be here, something has gone wrong; please reach out to an Arthur engineer.")
        
        res = resp[0]
        best_idx = res['optimization_index']

        curve_result = {}
        for res in resp: 
            if 'categorical_value' in res:
                attr_val = res['categorical_value'] 
            else: 
                attr_val = self._continuous_to_str(res)
            curve_result[attr_val] = pd.DataFrame(res['data_points'])

        return Curves(attribute, constraint, best_idx, curve_result)

    def _continuous_to_str(self, res: Dict[str, Any]):
        """
        For continuous sensitive features only: convert continuous buckets into string categories to use as dict keys.
        """
        start = '(-inf,'
        end = 'inf)'

        if "continuous_start" in res:
            start = '(' + str(res["continuous_start"]) + ','
        if "continuous_end" in res: 
            end = str(res["continuous_end"]) + ']'

        if start == '(-inf,' and end == 'inf)':
            raise InternalValueError("This continuous sensitive attribute only has a single bucket?")

        return start + end

    @arthur_excepted("Failed to plot curves")
    def plot_curves(self, curves: Optional[Curves] = None, attribute: Optional[str] = None, constraint: Optional[str] = None):
        """
        Simple plot of the tradeoff curve for a single sensitive attribute and constraint.

        :param curves: one Curves object containing a set of curves corresponding to a single sensitive attribute and constraint.
        """

        if curves is None:
            if attribute is None or constraint is None:
                raise UserValueError("Either `curves`, or both `attribute` and `constraint`, must be provided.")
            curves = self.get_curves(attribute, constraint)

        ax = plt.axes()

        graph_title = curves.constraint + " " + curves.attribute_name
        x, y = CONSTRAINT_PLOT_DICT[curves.constraint]

        ax.set(title=graph_title, xlabel=x, ylabel=y)

        for sens_val in curves.attr_val_to_threshold:
            points = curves.attr_val_to_threshold[sens_val]
            ax.plot(points['x'], points['y'], ls='-', lw=2.0, label='sensitive feature value = ' + sens_val)
        
        if curves.constraint != EqualizedOdds:
            xbest = list(curves.attr_val_to_threshold.values())[0].iloc[curves.max_acc_idx]['x']
            ax.axvline(x=xbest, label="solution")

        ax.legend()
        plt.show()

    @arthur_excepted("Failed to get thresholds for index")
    def get_thresholds_for_idx(self, curves: Curves, idx: int = None):
        """
        Retrieve the thresholds for each group, given a set of curves and aparticular optimization index. 

        :param curves: one Curves object containing a set of curves corresponding to a single sensitive attribute and constraint.
        :param idx: one integer (between 0 and 1000, inclusive) that represents a specific solution option. Defaults to the curve's accuracy-maximizing index.
        :return: a dictionary mapping sensitive feature values to the prediction threshold used for that group. 
        """

        idx = curves.max_acc_idx if idx is None else idx
        if idx < 0 or idx > 1000:
            raise UserValueError("optimization index should be between 0 and 1000, inclusive.")
        thresholds = {}
        for attr in curves.attr_val_to_threshold:
            thresholds[attr] = curves.attr_val_to_threshold[attr].iloc[idx]['threshold']

        return thresholds
