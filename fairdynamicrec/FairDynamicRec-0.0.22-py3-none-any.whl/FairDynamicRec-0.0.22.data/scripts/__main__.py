import argparse
import numpy as np
from fair_dynamic_rec.core.config_cmd import ConfigCmd
from fair_dynamic_rec.core.data_cmd import DataCmd
from pathlib import Path
from fair_dynamic_rec.core import read_config_file
from fair_dynamic_rec.core.util.files import Files
from fair_dynamic_rec.core.util.utils import create_log_name
from fair_dynamic_rec.core.simulators.simulation import OnlineSimulator
from fair_dynamic_rec.core.visualization_cmd import VisualizationCmd
from fair_dynamic_rec.core.metric_cmd import MetricCmd
from datetime import datetime
from fair_dynamic_rec.core.util.ranker_utils import set_rankers

def read_args():
    '''
    Parse command line arguments.
    :return:
    '''
    parser = argparse.ArgumentParser(description= 'The FairDynamicRec tool for running recommender systems experiments in dynamic setting.', epilog='For documentation, refer to: ')

    # todo remove py-eval AS
    # parser.add_argument('action', choices=['run', 'split', 'eval', 'rerank', 'post', 'purge', 'status', 'describe', 'check', 'py-eval'], nargs='?')
    parser.add_argument('action', choices=['run', 'split', 'eval', 'rerank', 'post', 'purge', 'status', 'describe', 'check', 'py-eval'])

    parser.add_argument("-t", "--target", help="Path to experiment directory")#, default='demo01')

    # Optional with arguments
    parser.add_argument("-c", "--conf", help="Use the specified configuration file")

    input_args = parser.parse_args()
    # error_check(vars(input_args))
    return vars(input_args)

def load_config(args: dict) -> ConfigCmd:
    config_file = Files.DEFAULT_CONFIG_FILENAME

    if args['conf']:  # User requested a different configuration file from the default
        config_file = args['conf']

    target = ""
    if (args['target'] != None):
        target = args['target']

    log_file = args['log_name']

    # create a path:

    return read_config_file(config_file, target, log_file)

if __name__ == '__main__':
    print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ": Running experiment.")

    args = read_args()
    # args['action'] = 'run'
    # args['target'] = '/Users/m.mansouryuva.nl/Research/FairDynamicRec/study'

    # purge_old_logs(args['target'] + "/*")
    log_name = create_log_name('FairDynamicRec_log{}.log')
    args['log_name'] = log_name

    config = load_config(args)

    dataObj = DataCmd(config)
    print("#users: " + str(dataObj.n_users) + ", #items: " + str(dataObj.n_items) + ", #train_ratings:" + str(np.count_nonzero(dataObj.train_data)) + ", #test_ratings:" + str(np.count_nonzero(dataObj.test_data)))

    rankers = set_rankers(config, dataObj)

    if args['action'] == 'run':
        sim = OnlineSimulator(config, dataObj)
        sim.run(config, dataObj, rankers)

    if args['action'] == 'run' or args['action'] == 'eval':
        viz = VisualizationCmd(config, dataObj, rankers)
        metric = MetricCmd(config, dataObj, rankers)
        metric.compute(config, dataObj, viz)