from celery.utils.log import get_task_logger
logging = get_task_logger(__name__)

from auger_ml.core.auger_messenger import AugerMessenger

class WarmStartOptimizer(object):
    def __init__(self, optimizer_params, options, _trialsQueue=None):
        self.optimizer_params = optimizer_params
        self.options = options

        #logging.info("Init optimizer: %s(%s). Algotithm: %s" % (self.options['optimizer_name'], self.options['optimizer_params'], self.options.get('optimizer_algorithm', '')))

    def get_next_trials(self):
        limit = self.optimizer_params.get("num_trials")
        if not limit:
            algorithm_names = list(self.options.get('search_space', {}).keys())
            limit = max(2,
                int((self.options.get('max_n_trials', 250)*0.05)/max(len(algorithm_names), 1)))

        logging.info("WarmStartOptimizer limit: %s"%limit)
        warm_start_trials = AugerMessenger(self.options).get_warm_start_trials(limit)

        trials = []
        if warm_start_trials:

            for item in warm_start_trials:
                if not 'ensembles' in item.get('algorithm_name', ''):
                    if 'KittyBoostClassifier' in item.get('algorithm_name'):
                        item['algorithm_name'] = 'auger_ml.algorithms.cat_boost.CatBoostClassifier'
                    if 'KittyBoostRegressor' in item.get('algorithm_name'):
                        item['algorithm_name'] = 'auger_ml.algorithms.cat_boost.CatBoostRegressor'

                    trials.append({
                        'algorithm_name': item.get('algorithm_name'),
                        'algorithm_params': item.get('algorithm_params')
                    })


        return trials, None
