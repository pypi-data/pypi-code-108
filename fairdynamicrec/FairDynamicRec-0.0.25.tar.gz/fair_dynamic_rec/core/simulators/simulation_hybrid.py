from rankers import CascadeLSB
from rankers import LSBGreedy
from rankers import AbstractRanker
from utils.click_simulators import CascadeSimulator, PBMSimulator, DBMSimulator, DCMSimulator
from utils.my_parser import SimulationArgumentParser
from utils.simulation import OnlineSimulator
from utils.recommendation_history import *

import numpy as np
import pickle as pk
import datetime
import json
import os


CLICKMODEL_MAP = {'CM': CascadeSimulator,
                  'cascademodel': CascadeSimulator,
                  'cm': CascadeSimulator,
                  'PBM': PBMSimulator,
                  'pbm': PBMSimulator,
                  'positionbasemodel': PBMSimulator,
                  'DCM': DCMSimulator,
                  'dcm': DCMSimulator,
                  'DBM': DBMSimulator,
                  'dbm': DBMSimulator,
                  'documentbasemodel': DBMSimulator
                  }


class HybridSimulator(OnlineSimulator):

    name ='HybridSimulator'

    # def __init__(self, dataset, sim_args, popularity, q_id, user_avg_popularity):
    def __init__(self, dataset, sim_args, q_id):
        """

        :param dataset: dict contains train_x, test_x, theta_star
        :param ClickModel: class: click mode
        :param sim_args: the simulation arguments from utils/my_parser.py
                        we use k: n_position, iteration, seed: random seed, output: output dict
        """
        super(HybridSimulator, self).__init__(dataset, sim_args, q_id)

        # this one is the input for the online algorithms
        self.train_x = dataset['train_x']
        # the following two define the click model
        # for the topic
        self.test_x = dataset['test_x']
        self.theta = dataset['theta_star']
        # for the relevance
        self.z = dataset['z']
        self.mu = dataset['mu']
        self.theta_star = np.concatenate(((1-sim_args.lbda) * self.theta, sim_args.lbda * self.mu))
        self.d_feature = self.z.shape[1]
        self.n_topics = self.train_x.shape[1]
        self.n_items = self.train_x.shape[0]

        self.full_feature = np.zeros((self.n_items, self.d_feature+self.n_topics))
        self.full_feature[:, :self.n_topics] = self.train_x
        self.full_feature[:, self.n_topics:] = self.z

        ClickModel = CLICKMODEL_MAP[self.sim_args.ClickModel]
        self.click_simulator = ClickModel(theta_star=self.theta_star, seed=sim_args.seed)
        # find the best ranking based on the testing feature space.
        self.best_ranking, self.best_delta = self.new_greedy_search()

        # self.popularity = popularity
        self.q_id = q_id
        # self.user_avg_popularity = user_avg_popularity

    def new_greedy_search(self):
        x = self.test_x
        z = self.z
        theta_star = self.theta
        mu = self.mu
        k = self.k
        score_rel = self.sim_args.lbda * np.dot(z, mu)

        delta_t = []
        coverage = np.zeros(self.n_topics)
        ranking = []
        ranking_set = set()
        for i in range(k):
            tie_breaker = self.prng.rand(len(x))
            # Line 8 - 11 of Nips 11
            delta = AbstractRanker.conditional_coverage(x=x, coverage=coverage)
            score = score_rel + (1-self.sim_args.lbda) * np.dot(delta, theta_star)
            tmp_rank = np.lexsort((tie_breaker, -score))
            for tr in tmp_rank:
                if tr not in ranking_set:
                    ranking.append(tr)
                    ranking_set.add(tr)
                    delta_t.append(delta[tr])
                    score_rel[tr] = -10000
                    break
            coverage = AbstractRanker.ranking_coverage(x[ranking])
        delta_t = np.asarray(delta_t)
        delta = np.zeros((k, self.n_topics+self.d_feature))
        delta[:, :self.n_topics] = delta_t
        delta[:, self.n_topics:] = z[ranking]
        return ranking, delta

    def __convert_to_topic_coverage(self, x):
        k, d = x.shape
        delta_t = []
        coverage = np.zeros(d)
        for idx, topic in enumerate(x):
            delta = AbstractRanker.conditional_coverage(x=topic, coverage=coverage)
            delta_t.append((delta))
            coverage = AbstractRanker.ranking_coverage(x[:idx + 1])
        return np.asarray(delta_t)

    def run(self, rankers, save_results=False):
        if type(rankers) is not list:
            rankers = [rankers]

        regret = {}
        reward = {}
        for ranker in rankers:
            regret[ranker.name] = np.zeros(self.iteration)
            reward[ranker.name] = np.zeros(self.iteration)

        for t in range(self.iteration):
            if self.sim_args.same_coins:
                self.click_simulator.set_coins(self.k)

            best_clicks, best_reward = self.click_simulator.get_feedback(self.best_delta)
            for ranker in rankers:
                if ranker.name.split('-')[0] in ['LSBGreedy', 'CascadeLSB', 'DCMLSB']:
                    ranking, tmp = ranker.get_ranking(self.train_x, self.k)
                elif ranker.name.split('-')[0] in ['CascadeLinUCB', 'DCMLinUCB']:
                    ranking, tmp = ranker.get_ranking(self.z, self.k)
                else:
                    # ranking, tmp = ranker.get_ranking(self.full_feature, self.k, self.user_avg_popularity)
                    ranking, tmp = ranker.get_ranking(self.full_feature, self.k, t)
                ranker.n_recommended[np.array(ranking)] = ranker.n_recommended[np.array(ranking)] + 1
                delta_t = self.__convert_to_topic_coverage(self.test_x[ranking])
                delta = np.zeros((self.k, self.n_topics + self.d_feature))
                delta[:, :self.n_topics] = delta_t
                delta[:, self.n_topics:] = self.z[ranking]
                """
                The click is from the click simulator. So it is defined by the testing part. w_test and theta_test.
                Bug from the click log, the bias from train_x to test_x is large. Here, I still use train.
                """
                clicks, t_reward = self.click_simulator.get_feedback(delta)
                if(sum(clicks)>0):
                    save_history(t, self.q_id, ranking, np.array(ranking)[clicks])
                else:
                    save_history(t, self.q_id, ranking, [])

                ranker.update(y=clicks)
                reward[ranker.name][t] = t_reward
                regret[ranker.name][t] = best_reward - t_reward

            if self.sim_args.same_coins:
                self.click_simulator.del_coins()
        # if save_results:
        #     self.__save_results(rankers=rankers, reward=reward, regret=regret)

        return reward, regret

    def save_results(self, q_id, rankers, reward, regret):
        """
        save results to the self.sim_args.output director
        the name is ranker.name+ranker parameters + random seed + save date
        :param rankers: same as self.run()
        :param reward: output of self.run()
        :param regret: output of self.run()
        :return: save results to json file.
        """
        # Saving directory
        if self.sim_args.output[-1] == '/':
            prefix = self.sim_args.output + \
                     '/'.join([self.sim_args.data_name, 'lambda'+str(self.sim_args.lbda), self.sim_args.ClickModel, 'norm-'+str(self.sim_args.normalized),
                               'rep'+str(self.sim_args.iteration), 'd'+str(self.d_feature),
                               'pos'+str(self.sim_args.K), 'topic'+str(self.sim_args.n_topic)]) + '/' + str(q_id) + '/'
        else:
            prefix = self.sim_args.output + '/' + \
                     '/'.join([self.sim_args.data_name, 'lambda'+str(self.sim_args.lbda), self.sim_args.ClickModel, 'norm-'+str(self.sim_args.normalized),
                               'rep'+str(self.sim_args.iteration), 'd'+str(self.d_feature),
                               'pos'+str(self.sim_args.K), 'topic'+str(self.sim_args.n_topic)]) + '/' + str(q_id) + '/'

        if not os.path.exists(prefix):
            os.makedirs(prefix)

        suffix = 'seed-' + str(self.sim_args.seed) + \
                 '-' + str(datetime.datetime.now().date()) + \
                 '-' + str(datetime.datetime.now().time())[:8].replace(':', '-') \
                 + '.js'

        for ranker in rankers:
            save_name = prefix + ranker.name + '-alpha%.2f-sigma%.2f-' % (ranker.alpha, ranker.sigma) + suffix
            objs = {'reward': reward[ranker.name].tolist(),
                    'regret': regret[ranker.name].tolist()
                    }
            with open(save_name, 'w') as f:
                json.dump(objs, f)


if __name__ == '__main__':
    args = SimulationArgumentParser()
    sim_args = args.parse_args('-K 2 --output results/ --data synthetic --seed 2'.split())

    SimulationArgumentParser.print(sim_args)

    with open('../data/synthetic.pkl', 'rb') as f:
        dataset = pk.load(f)

    d = dataset['train_x'].shape[1]
    rankers = [CascadeLSB(d=d, sigma=.1, alpha=.8, seed=sim_args.seed),
               LSBGreedy(d=d, sigma=.1, alpha=.8, seed=sim_args.seed)
              ]

    sim = OnlineSimulator(dataset=dataset, sim_args=sim_args)
    reward, regret = sim.run(rankers=rankers, save_results=True)

    for key in reward:
        print(key, (np.cumsum(reward[key])/np.arange(1, 1+sim_args.iteration))[-10:])

    for key in regret:
        print(key, np.cumsum(regret[key])[-10:])

