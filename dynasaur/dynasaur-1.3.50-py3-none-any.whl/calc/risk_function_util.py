import numpy as np
import itertools


class DCDF(object):

    def __init__(self, dcdf_probs):
        """

        Args:
            dcdf: i.e [[0.0, 0.0], [0.086, 1.654], [0.169, 2.012], [0.254, 2.119], [0.337, 2.227],
            [0.420, 2.382], [0.501, 2.983],  [0.582, 3.212], [0.667, 3.293], [0.751, 3.434],
            [0.836, 3.590], [0.920, 4.089], [1.0, 4.102]]

        Returns:

        """

        self._prob = np.asarray(dcdf_probs)[:, 0]
        self._x = np.asarray(dcdf_probs)[:, 1]
        self._x[0] = -np.Inf

    def calculate_dcdf(self, values):
        """function to calculate

        Args:
          function_name: param values:
        
        :return calculated value:
          values: 

        Returns:

        """
        if type(values) is list:
            return [self._prob[np.where(value > self._x)][-1] for value in values]
        else:
            return self._prob[np.where(values > self._x)][-1]

    def get_x_where_risk_is_value(self, val=1):
        """

        Args:
          function_name: param val:
          val:  (Default value = 1)

        Returns:

        """
        ret_vals = self._x[-1] if len(np.where(self._prob > val)[0]) == 0 else self._x[np.where(self._prob > val)[0][0]]
        return ret_vals


class RibCriteria:
    """ """
    def __init__(self, dcdf):
        self._dcdf = dcdf

    def calculate_age_risk(self, us, age):
        """

        Args:
          us: param age:
          age: 

        Returns:

        """
        if np.isnan(us):
            return 0.0
        sus = 100. * (us / (1.0 - (age - 25.) * 0.0051))
        result = self._dcdf.calculate_dcdf(sus)
        #from .standard_functions import StandardFunction
        #xy = StandardFunction.ccdf_sigmoid(param_dict={"x": sus, "x0": 3, "k": 1})
        return result

    def calc_num_frac(self, rib_ids, risk):
        """

        Args:
          param_dict: param units:
          rib_ids: 
          risk: 

        Returns:

        """

        # remove zero risk entries
        # due to performance issues in the calculation (combinatoric!!)
        for i in reversed(list(range(len(rib_ids)))):
            if risk[rib_ids[i]] == 0.0:
                del risk[rib_ids[i]]
                del rib_ids[i]

        # X = 0 to 7 fractures
        sf = []
        for f in range(8):
            s = 0.0
            c = 0
            # for i in itertools.permutations(a,f):
            for i in itertools.combinations(rib_ids, f):
                c += 1
                p1 = 1.0
                for j in i:
                    p1 = p1 * risk[j]
                p2 = 1.0
                for k in np.setdiff1d(np.array(rib_ids), np.array(i)):
                    p2 = p2 * (1.0 - risk[k])
                s = s + p1 * p2
            sf.append(s)
        sf.append(1 - np.sum(sf))
        return sf
