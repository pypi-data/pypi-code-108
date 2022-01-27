import numpy as np
import pandas as pd
from collections import namedtuple

Result = namedtuple("Result", "order score x y")
Column = namedtuple("column", "name values")


class KineticExperiment:
    def __init__(self, analysis_legend = None, all_experiments = None, comparable_experiments = None, substrate_index = None, product_index = None):
        self.flex_index = 0 # for VTNA data it should be 0 for time but in rpka is must be 3 for rates
        if comparable_experiments is None:
            self.sub_ind = analysis_legend["substrate_col"]
            self.prod_ind = analysis_legend["product_col"]
            self.comparable_experiments = [all_experiments[index] for index in analysis_legend["comparable_exps"]]
        else:
            self.sub_ind = substrate_index
            self.prod_ind = product_index
            self.comparable_experiments = comparable_experiments
        self.analyzer = None
        self.initialize_VTNAs()

    def initialize_VTNAs(self):
        t,s,p =  self.parse([exp.data for exp in self.comparable_experiments])
        self.analyzer = VariableTimeNormalization(t, s, p)

    def get_frames(self, n_range):
        ordinates, abscissas, scores = [], [], []
        for n in n_range:
            score, abscissa, ordinate = self.analyzer.get_new_score(n)
            ordinates.append(ordinate)
            abscissas.append(abscissa)
            scores.append(score)
        scores = np.asarray(scores)
        frames = {
            "Ordinates": ordinates,

            "Abscissas": abscissas,

            "Scores"   : scores,

            "Orders"   : n_range
        }
        return frames

    def parse(self, exps):
        times, subs, prods = [], [], []
        for exp in exps:
            times.append(exp[self.flex_index]) #accomodates rpka and vtna data types
            subs.append( exp[self.sub_ind]) #const
            prods.append(exp[self.prod_ind]) #varied
        return times, subs, prods


class Reaction:
    def __init__(self, name = None, data = None):
        self.name            = name
        self.emulator_model  = None
        self.data            = data

        #todo
        self.abscissas   = None
        self.ordinates   = None

    def get_simulations(self, feature_range):
        return self.emulator_model.get_predictions_without_scaling(feature_range)

    def set_dependences(self, params):
        self.abscissas = self.data[params["abscissa_range"]]


# requires list of comperables
class VariableTimeNormalization:
    def __init__(self, times, subs, prods):
        t,s,p = self.non_zero_inputs(times, subs, prods)
        self.prods = (prods[0].name, p)
        self.subs = (subs[0].name,  s)
        self.time = (times[0].name, t)

    def non_zero_inputs(self, times, subs, prods):
        # if a kinetically relevent species has gone to zero conc then the reaction is over (*possible unmes cat)
        prod_points = np.asarray([prod.values for prod in prods])
        sub_points  = np.asarray([sub.values for sub in subs])
        time_points = np.asarray([timepoint.values for timepoint in times])

        final_t, final_s, final_p = [], [], []
        # problem: if entire column is zero, empty list is added
        for t,s,p in zip(time_points, sub_points, prod_points):
            new_t, new_s, new_p = [t[0]],[s[0]],[p[0]]
            #as is we skip over the first item due it likely being zero
            for tt, ss, pp in zip(t[1:],s[1:],p[1:]):
            # for tt, ss, pp in zip(t, s, p):
                if tt == 0 or ss ==0 or pp ==0:
                    pass
                else:
                    new_t.append(tt)
                    new_s.append(ss)
                    new_p.append(pp)
            # need to add first item back in  then append and you should be good -- it was pulling the first zero
            final_t.append(np.asarray(new_t))
            final_s.append(np.asarray(new_s))
            final_p.append(np.asarray(new_p))
        return np.asarray(final_t), np.asarray(final_s), np.asarray(final_p)
        # return time_points, sub_points, prod_points

    def get_new_score(self, n):
        # aucs = self.apply_variable_time_with_similar_domain(n)
        absc, ords = self.apply_variable_time_normalization(n)
        score = self.score(absc, ords)
        return score, absc, ords

    def score(self, abscissas, ordinates):
        data = pd.DataFrame()
        for abscissa, ordinate in zip(abscissas, ordinates):
            dataframe = pd.DataFrame(data={'x': abscissa, 'y': ordinate})
            data = data.append(dataframe)

        sorted_diff = data.sort_values('x').diff()
        error = sorted_diff.abs()['y'].sum()

        return float(error)

    def apply_variable_time_normalization(self, n):
        vtna_curves = []
        for time, sub_conc, prod_conc in zip(self.time[1], self.subs[1], self.prods[1]):
            # calculate new time basis by integrating f(x)=sub_conc[x]^order wrt t
            f = lambda x: x ** n
            y = f(sub_conc)
            if sub_conc[0] == 0:
                y[0] = 0
            variable_time_normalized_abscissa = Integral(time, y).mid_integrals
            variable_time_normalized_abscissa = [0] + variable_time_normalized_abscissa
            time_basis = variable_time_normalized_abscissa

            full_curve = np.stack([time_basis, prod_conc], axis=1)
            vtna_curves.append(full_curve)

        abscissas, ordinates = [], []

        for curve in vtna_curves:
            abscissas.append(curve[:, 0])
            ordinates.append(curve[:, 1])
        return abscissas, ordinates


class Integral:
    def __init__(self, x, y):
        self.x, self.y = x,y

        # for the visualization these can be handy
        self.name      = None
        self.save_path = None

        # get x & y
        x_left, x_right  = self.x[:-1], self.x[1:]
        x_mid = [r-l for l, r in zip(x_left, x_right)]
        y_left, y_right  =  self.y[:-1], self.y[1:]
        y_mid   = (self.y[:-1] + self.y[1:]) / 2

        # get rectangles
        self.left_areas  = [x * y for x, y in zip(x_left,  y_left)]
        self.right_areas = [x * y for x, y in zip(x_right, y_right)]
        self.mid_areas   = [x * y for x, y in zip(x_mid,   y_mid)]

        # sum rectangles (aka integrate)
        self.left_auc    = np.sum(self.left_areas)
        self.right_auc   = np.sum(self.right_areas)
        self.mid_auc     = np.sum(self.mid_areas)

        # Get all available integrals
        left_integrals, right_integrals, mid_integrals = [0], [0], [0]
        for area in self.left_areas:
            left_integrals.append(area+left_integrals[-1])
        for area in self.right_areas:
            right_integrals.append(area+right_integrals[-1])
        for area in self.mid_areas:
            mid_integrals.append(area+mid_integrals[-1])

        self.left_integrals, self.right_integrals, self.mid_integrals = left_integrals[1:], right_integrals[1:], mid_integrals[1:]
