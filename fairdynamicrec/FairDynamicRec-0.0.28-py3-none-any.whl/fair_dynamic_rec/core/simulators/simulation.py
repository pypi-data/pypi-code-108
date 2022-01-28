from functools import reduce
from fair_dynamic_rec.core.simulators.click_simulator.cascade_model import *
from fair_dynamic_rec.core.rankers.abstract_ranker import AbstractRanker
from fair_dynamic_rec.core.util.utils import get_param_config_name
from fair_dynamic_rec.core.util.outputs import save_rankings_online_simulator, save_rewards
from tqdm import tqdm
from datetime import datetime
from scipy.special import expit

ClickModel = {'cascade': CascadeModel}

# This class uses user and playlist features datasets to simulate users responses to a list of recommendations

class OnlineSimulator():
    def __init__(self, config, dataObj):
        self.prng = np.random.RandomState(seed=config.seed)
        # self.data = dataObj.load_features(config)
        # config.get_optimal_ranker()
        # config.get_online_simulator_settings()
        self.optimal_rankings, self.optimal_scores = self.get_optimal_ranking(config, dataObj)
        # ClickModel = config.feedback_model
        self.click_simulator = ClickModel[config.feedback_model](config)
        self.optimal_clicks, self.optimal_rewards = self.click_simulator.get_feedback(self.optimal_scores)

    def run(self, config, dataObj, rankers):
        print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ": Simulation started with " + str(config.rounds) + " rounds")
        overall_optimal_reward = np.zeros(config.rounds)
        self.rankers = rankers#self.set_rankers(config, dataObj)
        overall_rewards = np.zeros((len(self.rankers), config.rounds))
        # regret = np.zeros((len(rankers), config.rounds))
        # overall_rankings = np.zeros((len(rankers), config.rounds))
        # overall_clicks = np.zeros((len(rankers), config.rounds))
        for i in tqdm(range(config.rounds)):
            # Select batch of n_users_per_round users
            user_ids = np.random.choice(range(dataObj.n_users), config.n_users_per_round, replace=False)
            overall_optimal_reward[i] = np.take(self.optimal_rewards, user_ids).sum()
            # Iterate over all policies
            for j in range(len(self.rankers)):
                # Compute n_recos recommendations
                rankings = self.rankers[j]["ranker"].get_ranking(user_ids, i)
                # Compute rewards
                clicks, rewards = self.compute_rewards(config, dataObj, user_ids, rankings)
                # Update policy based on rewards
                self.rankers[j]["ranker"].update(user_ids, rankings, clicks, i)
                overall_rewards[j, i] = rewards.sum()
                # regret[j, i] = overall_optimal_reward.sum() - rewards.sum()
                # overall_rankings[j, i] = rankings
                # overall_clicks[j, i] = clicks
                save_rankings_online_simulator(config, dataObj, get_param_config_name(self.rankers[j]["config"]), i, rankings, clicks, user_ids)
        save_rewards(config, self.rankers, overall_optimal_reward, overall_rewards)
            # Print info
            # if i == 0 or (i + 1) % print_every == 0 or i + 1 == n_rounds:
            #     logger.info("Round: %d/%d. Elapsed time: %f sec." % (i + 1, n_rounds, time.time() - start_time))
            #     logger.info("Cumulative regrets: \n%s \n" % "\n".join(
            #         ["	%s : %s" % (policies_name[j], str(np.sum(overall_optimal_reward - overall_rewards[j]))) for j
            #          in range(n_policies)]))


    def get_optimal_ranking(self, config, dataObj):
        self.user_features, self.item_features = AbstractRanker.get_features_for_optimal_ranker(config, dataObj)
        if config.optimal_ranker == 'naive_relevance':
            # batch_user_features = np.take(self.user_features, batch_user_ids, axis=0)
            probs = self.user_features.dot(self.item_features.T)
            optimal_rankings = np.argsort(-probs)[:, :config.list_size]
            batch_item_features = np.take(self.item_features, optimal_rankings, axis=0)
            n_users = self.user_features.shape[0]
            optimal_scores = np.zeros((n_users, config.list_size))
            # th_reward = np.zeros(n_users)
            for i in range(n_users):
                # optimal_scores[i] = 1 - reduce(lambda x, y: x * y, 1 - expit(self.user_features[i].dot(batch_item_features[i].T)))
                optimal_scores[i] = self.user_features[i].dot(batch_item_features[i].T)
            return optimal_rankings, optimal_scores
        elif config.optimal_ranker == 'topical_coverage':
            n_users = self.user_features.shape[0]
            optimal_rankings, optimal_scores = np.zeros((n_users, config.list_size), dtype=int), np.zeros((n_users, config.list_size))
            tie_breaker = self.prng.rand(len(self.item_features))
            for i in range(n_users):
                # gain_in_topic_coverage_t = []
                coverage = np.zeros(self.item_features.shape[1])
                ranking = []
                # ranking_set = set()
                for j in range(config.list_size):
                    # Line 8 - 11 of Nips 11
                    gain_in_topic_coverage = AbstractRanker.conditional_coverage(x=self.item_features, coverage=coverage)
                    probs = np.dot(gain_in_topic_coverage, self.user_features[i])
                    tmp_rank = np.lexsort((tie_breaker, -probs))
                    for tr in tmp_rank:
                        if tr not in ranking:
                            ranking.append(tr)
                            optimal_scores[i, j] = self.user_features[i].dot(gain_in_topic_coverage[tr].T)
                            # optimal_scores[i, j] = gain_in_topic_coverage[tr]
                            break
                    coverage = AbstractRanker.ranking_coverage(self.item_features[ranking])
                optimal_rankings[i] = np.asarray(ranking)
            return optimal_rankings, optimal_scores
        elif config.optimal_ranker == 'hybrid':
            n_users = self.user_features.shape[0]
            optimal_rankings, optimal_scores = np.zeros((n_users, config.list_size), dtype=int), np.zeros((n_users, config.list_size))
            for i in range(n_users):
                # x = dataObj.feature_data['test_item_topical_features']
                # z = dataObj.feature_data['test_item_latent_features']
                # theta_star = dataObj.feature_data['test_user_topical_features']
                # mu = dataObj.feature_data['test_user_latent_features']
                # k = self.k
                # score_rel = config.lmbda * np.dot(dataObj.feature_data['test_user_latent_features'][i], dataObj.feature_data['test_item_latent_features'].T)
                score_rel = config.lmbda * np.dot(dataObj.feature_data['test_user_latent_features'][i], dataObj.feature_data['train_item_latent_features'].T)

                # delta_t = []
                gain_in_topic_coverage_t = []
                coverage = np.zeros(dataObj.feature_data['test_item_topical_features'].shape[1])
                ranking = []
                # ranking_set = set()
                for j in range(config.list_size):
                    tie_breaker = self.prng.rand(len(dataObj.feature_data['test_item_topical_features']))
                    # Line 8 - 11 of Nips 11
                    gain_in_topic_coverage = AbstractRanker.conditional_coverage(x=dataObj.feature_data['test_item_topical_features'], coverage=coverage)
                    score = score_rel + (1 - config.lmbda) * np.dot(gain_in_topic_coverage, dataObj.feature_data['test_user_topical_features'][i])
                    tmp_rank = np.lexsort((tie_breaker, -score))
                    for tr in tmp_rank:
                        if tr not in ranking:
                            ranking.append(tr)
                            # ranking_set.add(tr)
                            gain_in_topic_coverage_t.append(gain_in_topic_coverage[tr])
                            # optimal_scores[i, j] = gain_in_topic_coverage[tr]
                            score_rel[tr] = -10000
                            break
                    coverage = AbstractRanker.ranking_coverage(dataObj.feature_data['test_item_topical_features'][ranking])
                optimal_rankings[i] = np.asarray(ranking)
                gain_in_topic_coverage_t = np.asarray(gain_in_topic_coverage_t)
                delta = np.zeros((config.list_size, dataObj.feature_data['test_item_topical_features'].shape[1] + dataObj.feature_data['train_item_latent_features'].shape[1]))
                delta[:, :dataObj.feature_data['test_item_topical_features'].shape[1]] = gain_in_topic_coverage_t
                # self.optimal_scores[:, dataObj.feature_data['test_item_topical_features'].shape[1]:] = dataObj.feature_data['test_item_latent_features'][ranking]
                delta[:, dataObj.feature_data['test_item_topical_features'].shape[1]:] = dataObj.feature_data['train_item_latent_features'][ranking]
                optimal_scores[i, :] = self.user_features[i].dot(delta.T)
            return optimal_rankings, optimal_scores

    def compute_rewards(self, config, dataObj, batch_users, rankings):
        batch_user_features = np.take(self.user_features, batch_users, axis=0)
        batch_item_features = np.take(self.item_features, rankings, axis=0)
        if config.optimal_ranker == 'naive_relevance':
            n_users = batch_user_features.shape[0]
            scores = np.zeros((n_users, config.list_size))
            # reward = np.zeros(n_users)
            for i in range(n_users):
                scores[i] = batch_user_features[i].dot(batch_item_features[i].T)
                # reward[i] = 1 - reduce(lambda x, y: x * y, 1 - probas)
            return self.click_simulator.get_feedback(scores)
        elif config.optimal_ranker == 'topical_coverage':
            n_users = batch_user_features.shape[0]
            scores = np.zeros((n_users, config.list_size))
            for i in range(n_users):
                topic_coverage = self.__convert_to_topic_coverage(batch_item_features[i])
                scores[i] = batch_user_features[i].dot(topic_coverage.T)
            return self.click_simulator.get_feedback(scores)
        elif config.optimal_ranker == 'hybrid':
            n_users = batch_user_features.shape[0]
            scores = np.zeros((n_users, config.list_size))
            for i in range(n_users):
                topic_coverage = self.__convert_to_topic_coverage(dataObj.feature_data['test_item_topical_features'][rankings[i]])
                item_full_feature = np.zeros((config.list_size, dataObj.feature_data['test_item_topical_features'].shape[1] + dataObj.feature_data['train_item_latent_features'].shape[1]))
                item_full_feature[:, :dataObj.feature_data['test_item_topical_features'].shape[1]] = topic_coverage
                item_full_feature[:, dataObj.feature_data['test_item_topical_features'].shape[1]:] = dataObj.feature_data['train_item_latent_features'][rankings[i]]
                scores[i] = batch_user_features[i].dot(item_full_feature.T)
            return self.click_simulator.get_feedback(scores)

    def __convert_to_topic_coverage(self, x):
        k, d = x.shape
        score = []
        coverage = np.zeros(d)
        for idx, topic in enumerate(x):
            score.append(AbstractRanker.conditional_coverage(x=topic, coverage=coverage))
            coverage = AbstractRanker.ranking_coverage(x[:idx+1])
        return np.asarray(score)






    # Computes expected reward for each user given their recommendations
    def compute_theoretical_rewards(self, batch_user_ids, batch_recos):
        batch_user_features = np.take(self.user_features, batch_user_ids, axis=0)
        batch_playlist_features = np.take(self.playlist_features, batch_recos, axis=0)
        n_users = len(batch_user_ids)
        th_reward = np.zeros(n_users)
        for i in range(n_users):
            probas = expit(batch_user_features[i].dot(batch_playlist_features[i].T))
            th_reward[i] = 1 - reduce(lambda x, y: x * y, 1 - probas)
        return th_reward

    # Computes list of n recommendations with highest expected reward for each user
    def compute_optimal_recos(self, batch_user_ids, n):
        batch_user_features = np.take(self.user_features, batch_user_ids, axis=0)
        probas = batch_user_features.dot(self.playlist_features.T)
        optim = np.argsort(-probas)[:, :n]
        return optim

    # Computes highest expected reward for each user
    def compute_optimal_theoretical_rewards(self):
        n_users = self.user_features.shape[0]
        u = 0
        step = 100000
        while u < n_users:
            users_ids = range(u, min(n_users, u + step))
            opt_recos = self.compute_optimal_recos(users_ids, self.n_recos)
            opt_rewards = self.compute_theoretical_rewards(users_ids, opt_recos)
            self.th_rewards[u:min(n_users, u + step)] = opt_rewards
            u += step
        return

        # Computes list of n recommendations with highest expected reward for each segment

    def compute_segment_optimal_recos(self, n):
        n_segments = len(np.unique(self.user_segment))
        segment_recos = np.zeros((n_segments, n), dtype=np.int64)
        for i in range(n_segments):
            mean_probas = np.mean(expit(
                np.take(self.user_features, np.where(self.user_segment == i)[0], axis=0).dot(self.playlist_features.T)),
                                  axis=0)
            reward = 1 - reduce(lambda x, y: x * y, 1 + np.sort(-mean_probas)[:n])
            segment_recos[i] = np.argsort(-mean_probas)[:n]
        return segment_recos

    # Computes highest expected reward for each segment
    def compute_segment_optimal_theoretical_rewards(self):
        n_users = self.user_features.shape[0]
        u = 0
        step = 100000
        segment_recos = self.compute_segment_optimal_recos(self.n_recos)
        while u < n_users:
            users_ids = range(u, min(n_users, u + step))
            user_segment = np.take(self.user_segment, users_ids)
            opt_recos = np.take(segment_recos, user_segment, axis=0)
            opt_rewards = self.compute_theoretical_rewards(users_ids, opt_recos)
            self.th_segment_rewards[u:min(n_users, u + step)] = opt_rewards
            u += step
        return

        # Given a list of users and their respective list of recos (each of size self.n_recos), computes

    # corresponding simulated reward
    def simulate_batch_users_reward(self, batch_user_ids, batch_recos):

        # First, compute probability of streaming each reco and draw rewards accordingly
        batch_user_features = np.take(self.user_features, batch_user_ids, axis=0)
        batch_playlist_features = np.take(self.playlist_features, batch_recos, axis=0)
        n_users = len(batch_user_ids)
        n = len(batch_recos[0])
        probas = np.zeros((n_users, n))
        for i in range(n_users):
            probas[i] = expit(
                batch_user_features[i].dot(batch_playlist_features[i].T))  # probability to stream each reco
        rewards = np.zeros((n_users, n))
        i = 0
        rewards_uncascaded = np.random.binomial(1, probas)  # drawing rewards from probabilities
        positive_rewards = set()

        # Then, for each user, positive rewards after the first one are set to 0 (and playlists as "unseen" subsequently)
        # to imitate a cascading browsing behavior
        # (nonetheless, users can be drawn several times in the batch of a same round ; therefore, each user
        # can have several positive rewards - i.e. stream several playlists - in a same round, consistently with
        # the multiple-plays framework from the paper)
        nz = rewards_uncascaded.nonzero()
        for i in range(len(nz[0])):
            if nz[0][i] not in positive_rewards:
                rewards[nz[0][i]][nz[1][i]] = 1
                positive_rewards.add(nz[0][i])
        return rewards




# CLICKMODEL_MAP = {'CM': CascadeSimulator,
#                   'cascademodel': CascadeSimulator,
#                   'cm': CascadeSimulator,
#                   'PBM': PBMSimulator,
#                   'pbm': PBMSimulator,
#                   'positionbasemodel': PBMSimulator,
#                   'DCM': DCMSimulator,
#                   'dcm': DCMSimulator,
#                   'DBM': DBMSimulator,
#                   'dbm': DBMSimulator,
#                   'documentbasemodel': DBMSimulator
#                   }
#
#
# class OnlineSimulator1(object):
#
#     name ='OnlineSimulator'
#
#     def __init__(self, dataset, sim_args, q_id):
#         """
#
#         :param dataset: dict contains train_x, test_x, theta_star
#         :param ClickModel: class: click mode
#         :param sim_args: the simulation arguments from utils/my_parser.py
#                         we use k: n_position, iteration, seed: random seed, output: output dict
#         """
#         self.sim_args = sim_args
#         self.iteration = sim_args.iteration
#         self.k = sim_args.K
#         self.prng = np.random.RandomState(seed=sim_args.seed)
#         # this one is the input for the online algorithms
#         self.train_x = dataset['train_x']
#         # the following two define the click model
#         self.test_x = dataset['test_x']
#         self.theta_star = dataset['theta_star']
#
#         self.n_topics = self.train_x.shape[1]
#         self.n_items = self.train_x.shape[0]
#         ClickModel = CLICKMODEL_MAP[self.sim_args.ClickModel]
#         self.click_simulator = ClickModel(theta_star=self.theta_star, seed=sim_args.seed)
#         # find the best ranking based on the testing feature space.
#         self.best_ranking, self.best_delta = self.__greedy_search(self.test_x, self.k)
#
#         self.q_id = q_id
#
#     def __greedy_search(self, x, k):
#         """
#         search for the optimal ranking
#         :param x: input feature
#         :param k: number of postions
#         :return: optimal ranking
#         """
#         delta_t = []
#         coverage = np.zeros(self.n_topics)
#         ranking = []
#         ranking_set = set()
#         for i in range(k):
#             tie_breaker = self.prng.rand(len(x))
#             # Line 8 - 11 of Nips 11
#             delta = AbstractRanker.conditional_coverage(x=x, coverage=coverage)
#             score = np.dot(delta, self.theta_star)
#             tmp_rank = np.lexsort((tie_breaker, -score))
#             for tr in tmp_rank:
#                 if tr not in ranking_set:
#                     ranking.append(tr)
#                     ranking_set.add(tr)
#                     delta_t.append(delta[tr])
#                     break
#             coverage = AbstractRanker.ranking_coverage(x[ranking])
#         return ranking, np.asarray(delta_t)
#
#     def __convert_to_topic_coverage(self, x):
#         k, d = x.shape
#         delta_t = []
#         coverage = np.zeros(d)
#         for idx, topic in enumerate(x):
#             delta = AbstractRanker.conditional_coverage(x=topic, coverage=coverage)
#             delta_t.append((delta))
#             coverage = AbstractRanker.ranking_coverage(x[:idx+1])
#         return np.asarray(delta_t)
#
#     def run(self, rankers, save_results=False):
#         if type(rankers) is not list:
#             rankers = [rankers]
#
#         regret = {}
#         reward = {}
#         for ranker in rankers:
#             regret[ranker.name] = np.zeros(self.iteration)
#             reward[ranker.name] = np.zeros(self.iteration)
#
#         for i in range(self.iteration):
#             if self.sim_args.same_coins:
#                 self.click_simulator.set_coins(self.k)
#
#             best_clicks, best_reward = self.click_simulator.get_feedback(self.best_delta)
#             for ranker in rankers:
#                 ranking, delta = ranker.get_ranking(self.train_x, self.k, i)
#                 ranker.n_recommended[np.array(ranking)] = ranker.n_recommended[np.array(ranking)] + 1
#                 delta = self.__convert_to_topic_coverage(self.test_x[ranking])
#                 """
#                 The click is from the click simulator. So it is defined by the testing part. w_test and theta_test.
#                 Bug from the click log, the bias from train_x to test_x is large. Here, I still use train.
#                 """
#                 clicks, t_reward = self.click_simulator.get_feedback(delta)
#
#                 if (sum(clicks) > 0):
#                     save_history(i, self.q_id, ranking, np.array(ranking)[clicks])
#                 else:
#                     save_history(i, self.q_id, ranking, [])
#
#                 ranker.update(y=clicks)
#                 reward[ranker.name][i] = t_reward
#                 regret[ranker.name][i] = best_reward - t_reward
#
#             if self.sim_args.same_coins:
#                 self.click_simulator.del_coins()
#         # if save_results:
#         #     self.__save_results(rankers=rankers, reward=reward, regret=regret)
#
#         return reward, regret
#
#     def save_results(self, q_id, rankers, reward, regret):
#         """
#         save results to the self.sim_args.output director
#         the name is ranker.name+ranker parameters + random seed + save date
#         :param rankers: same as self.run()
#         :param reward: output of self.run()
#         :param regret: output of self.run()
#         :return: save results to json file.
#         """
#         # Saving directory
#         if self.sim_args.output[-1] == '/':
#             prefix = self.sim_args.output + \
#                      '/'.join([self.sim_args.data_name, self.sim_args.ClickModel, 'norm-'+str(self.sim_args.normalized),
#                                'rep'+str(self.sim_args.iteration),
#                                'pos'+str(self.sim_args.K), 'topic'+str(self.sim_args.n_topic)]) + '/' + str(q_id) + '/'
#         else:
#             prefix = self.sim_args.output + '/' + \
#                      '/'.join([self.sim_args.data_name, self.sim_args.ClickModel, 'norm-'+str(self.sim_args.normalized),
#                                'rep'+str(self.sim_args.iteration),
#                                'pos'+str(self.sim_args.K), 'topic'+str(self.sim_args.n_topic)]) + '/' + str(q_id) + '/'
#
#         if not os.path.exists(prefix):
#             os.makedirs(prefix)
#
#         suffix = 'seed-' + str(self.sim_args.seed) + \
#                  '-' + str(datetime.datetime.now().date()) + \
#                  '-' + str(datetime.datetime.now().time())[:8].replace(':', '-') \
#                  + '.js'
#
#         for ranker in rankers:
#             save_name = prefix + ranker.name + '-alpha%.2f-sigma%.2f-' % (ranker.alpha, ranker.sigma) + suffix
#             objs = {'reward': reward[ranker.name].tolist(),
#                     'regret': regret[ranker.name].tolist()
#                     }
#             with open(save_name, 'w') as f:
#                 json.dump(objs, f)
#
# class OnlineNaiveSimulator(object):
#
#     name ='OnlineNaiveSimulator'
#
#     def __init__(self, dataset, sim_args, q_id):
#         """
#
#         :param dataset: dict contains train_x, test_x, theta_star
#         :param ClickModel: class: click mode
#         :param sim_args: the simulation arguments from utils/my_parser.py
#                         we use k: n_position, iteration, seed: random seed, output: output dict
#         """
#         self.sim_args = sim_args
#         self.iteration = sim_args.iteration
#         self.k = sim_args.K
#         self.prng = np.random.RandomState(seed=sim_args.seed)
#         # this one is the input for the online algorithms
#         self.train_x = dataset['train_x']
#         # the following two define the click model
#         self.test_x = dataset['test_x']
#         self.theta_star = dataset['theta_star']
#
#         self.n_topics = self.train_x.shape[1]
#         self.n_items = self.train_x.shape[0]
#         ClickModel = CLICKMODEL_MAP[self.sim_args.ClickModel]
#         self.click_simulator = ClickModel(theta_star=self.theta_star, seed=sim_args.seed)
#         # find the best ranking based on the testing feature space.
#         self.best_ranking, self.best_delta = self.__greedy_search(self.test_x, self.k)
#
#         self.q_id = q_id
#
#     def __greedy_search(self, x, k):
#         """
#         search for the optimal ranking
#         :param x: input feature
#         :param k: number of postions
#         :return: optimal ranking
#         """
#         delta_t = []
#         coverage = np.zeros(self.n_topics)
#         ranking = []
#         ranking_set = set()
#         for i in range(k):
#             tie_breaker = self.prng.rand(len(x))
#             # Line 8 - 11 of Nips 11
#             delta = AbstractRanker.conditional_coverage(x=x, coverage=coverage)
#             score = np.dot(delta, self.theta_star)
#             tmp_rank = np.lexsort((tie_breaker, -score))
#             for tr in tmp_rank:
#                 if tr not in ranking_set:
#                     ranking.append(tr)
#                     ranking_set.add(tr)
#                     delta_t.append(delta[tr])
#                     break
#             coverage = AbstractRanker.ranking_coverage(x[ranking])
#         return ranking, np.asarray(delta_t)
#
#     def __convert_to_topic_coverage(self, x):
#         k, d = x.shape
#         delta_t = []
#         coverage = np.zeros(d)
#         for idx, topic in enumerate(x):
#             delta = AbstractRanker.conditional_coverage(x=topic, coverage=coverage)
#             delta_t.append((delta))
#             coverage = AbstractRanker.ranking_coverage(x[:idx+1])
#         return np.asarray(delta_t)
#
#     def run(self, rankers, save_results=False):
#         if type(rankers) is not list:
#             rankers = [rankers]
#
#         regret = {}
#         reward = {}
#         for ranker in rankers:
#             regret[ranker.name] = np.zeros(self.iteration)
#             reward[ranker.name] = np.zeros(self.iteration)
#
#         for i in range(self.iteration):
#             if self.sim_args.same_coins:
#                 self.click_simulator.set_coins(self.k)
#
#             best_clicks, best_reward = self.click_simulator.get_feedback(self.best_delta)
#             for ranker in rankers:
#                 ranking, delta = ranker.get_ranking(self.train_x, self.k, i)
#                 ranker.n_recommended[np.array(ranking)] = ranker.n_recommended[np.array(ranking)] + 1
#                 delta = self.__convert_to_topic_coverage(self.test_x[ranking])
#                 """
#                 The click is from the click simulator. So it is defined by the testing part. w_test and theta_test.
#                 Bug from the click log, the bias from train_x to test_x is large. Here, I still use train.
#                 """
#                 clicks, t_reward = self.click_simulator.get_feedback(delta)
#
#                 if (sum(clicks) > 0):
#                     save_history(i, self.q_id, ranking, np.array(ranking)[clicks])
#                 else:
#                     save_history(i, self.q_id, ranking, [])
#
#                 ranker.update(y=clicks)
#                 reward[ranker.name][i] = t_reward
#                 regret[ranker.name][i] = best_reward - t_reward
#
#             if self.sim_args.same_coins:
#                 self.click_simulator.del_coins()
#         # if save_results:
#         #     self.__save_results(rankers=rankers, reward=reward, regret=regret)
#
#         return reward, regret
#
#     def save_results(self, q_id, rankers, reward, regret):
#         """
#         save results to the self.sim_args.output director
#         the name is ranker.name+ranker parameters + random seed + save date
#         :param rankers: same as self.run()
#         :param reward: output of self.run()
#         :param regret: output of self.run()
#         :return: save results to json file.
#         """
#         # Saving directory
#         if self.sim_args.output[-1] == '/':
#             prefix = self.sim_args.output + \
#                      '/'.join([self.sim_args.data_name, self.sim_args.ClickModel, 'norm-'+str(self.sim_args.normalized),
#                                'rep'+str(self.sim_args.iteration),
#                                'pos'+str(self.sim_args.K), 'topic'+str(self.sim_args.n_topic)]) + '/' + str(q_id) + '/'
#         else:
#             prefix = self.sim_args.output + '/' + \
#                      '/'.join([self.sim_args.data_name, self.sim_args.ClickModel, 'norm-'+str(self.sim_args.normalized),
#                                'rep'+str(self.sim_args.iteration),
#                                'pos'+str(self.sim_args.K), 'topic'+str(self.sim_args.n_topic)]) + '/' + str(q_id) + '/'
#
#         if not os.path.exists(prefix):
#             os.makedirs(prefix)
#
#         suffix = 'seed-' + str(self.sim_args.seed) + \
#                  '-' + str(datetime.datetime.now().date()) + \
#                  '-' + str(datetime.datetime.now().time())[:8].replace(':', '-') \
#                  + '.js'
#
#         for ranker in rankers:
#             save_name = prefix + ranker.name + '-alpha%.2f-sigma%.2f-' % (ranker.alpha, ranker.sigma) + suffix
#             objs = {'reward': reward[ranker.name].tolist(),
#                     'regret': regret[ranker.name].tolist()
#                     }
#             with open(save_name, 'w') as f:
#                 json.dump(objs, f)
#
#
# if __name__ == '__main__':
#     args = SimulationArgumentParser()
#     sim_args = args.parse_args('-K 2 --output results/ --data synthetic --seed 2'.split())
#
#     SimulationArgumentParser.print(sim_args)
#
#     with open('../data/synthetic.pkl', 'rb') as f:
#         dataset = pk.load(f)
#
#     d = dataset['train_x'].shape[1]
#     rankers = [CascadeLSB(d=d, sigma=.1, alpha=.8, seed=sim_args.seed),
#                LSBGreedy(d=d, sigma=.1, alpha=.8, seed=sim_args.seed)
#               ]
#
#     sim = OnlineSimulator(dataset=dataset, sim_args=sim_args)
#     reward, regret = sim.run(rankers=rankers, save_results=True)
#
#     for key in reward:
#         print(key, (np.cumsum(reward[key])/np.arange(1, 1+sim_args.iteration))[-10:])
#
#     for key in regret:
#         print(key, np.cumsum(regret[key])[-10:])
#
