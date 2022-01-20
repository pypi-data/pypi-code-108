from fair_dynamic_rec.core.rankers.random import *
from fair_dynamic_rec.core.rankers.naive_greedy import *
from fair_dynamic_rec.core.rankers.naive_epsilon_greedy import *
from fair_dynamic_rec.core.rankers.thompson_sampling import *
from fair_dynamic_rec.core.rankers.kl_upper_confidence_bound import *
from fair_dynamic_rec.core.rankers.linear_submodular_bandit import *
from fair_dynamic_rec.core.rankers.linear_upper_confidence_bound import *
from fair_dynamic_rec.core.rankers.hybrid_lsb_linucb import *
from fair_dynamic_rec.core.rankers.lsb_random import *
from fair_dynamic_rec.core.rankers.ea_linear_submodular_bandit import *
from fair_dynamic_rec.core.rankers.ea_linear_upper_confidence_bound import *

RankerModel = {'random': Random, 'naive_greedy': NaiveGreedy, 'naive_epsilon_greedy': NaiveEpsilonGreedy,
               'thompson_sampling': ThompsonSampling, 'kl_upper_confidence_bound': KLUCB, 'linear_submodular_bandit': LSB,
               'linear_upper_confidence_bound': LinUCB, 'hybrid-lsb-linucb': HybridLSBLinUCB, 'lsb-random': LSBRandom,
               'ea_linear_submodular_bandit': EALSB, 'ea_linear_upper_confidence_bound': EALinUCB}


def set_rankers(config, dataObj):
    rankers = []
    for params in config.rankers:
        if len(params["multiple_val_params"]) > 0:
            for param in params["multiple_val_params"]:
                _conf = dict(list(params["single_val_params"].items()) + list(param.items()))
                rankers.append(
                    {'ranker': RankerModel[params["single_val_params"]["name"]["value"]](config, dataObj, _conf),
                     'config': _conf}
                )
        elif len(params["single_val_params"]) > 0:
            rankers.append(
                {'ranker': RankerModel[params["single_val_params"]["name"]["value"]](config, dataObj, params["single_val_params"]),
                 'config': params["single_val_params"]}
            )
        # _ranker = RankerModel[params["single_val_params"]["name"]](config, dataObj)
        # # _ranker.load_data(config, dataObj)
        # _config = dict(list(config.items()) + list(params["single_val_params"].items()))
        # for param in params["multiple_val_params"]:
        #     _ranker.config = dict(list(_ranker.config.items()) + list(param.items()))
        #
        # rankers.append({'ranker': _ranker, 'config': _config})
    return rankers