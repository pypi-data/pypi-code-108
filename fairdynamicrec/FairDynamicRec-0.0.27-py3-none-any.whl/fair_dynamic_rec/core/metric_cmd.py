import numpy as np
import os
from pathlib import Path
import json
from fair_dynamic_rec.core.util.utils import get_legend_labels
from fair_dynamic_rec.core.util.utils import get_param_config_name
from scipy import stats

class MetricCmd:
    def __init__(self, config, dataObj, rankers):
        self.optimal_reward_filename = 'optimal-reward'
        self.ranker_reward_filename = 'ranker-reward'
        self.rankers = rankers
        config.get_metrics()
        self.load_rewards(config)

    def compute(self, config, dataObj, viz):
        for metric in config.metrics:
            if metric['name'] == 'n-step-regret':
                viz.draw(metric, self.n_step_regret(), {'x': 'rounds', 'y': metric, 'legend': get_legend_labels(self.rankers)}, 'line')
            if metric['name'] == 'cumulative-alpha-ia':
                viz.draw(metric, self.cumulative_alpha_ia(config, dataObj), {'x': 'rounds', 'y': metric, 'legend': get_legend_labels(self.rankers)}, 'line')
            if metric['name'] == 'item-exposure-per-round':
                viz.draw(metric, self.item_exposure_per_round(config, dataObj, metric), {'x': 'rounds', 'y': 'item rank', 'legend': get_legend_labels(self.rankers)}, 'scatter_colorbar')
            if metric['name'] == 'item-exposure-per-round-with-FPTP':
                viz.draw(metric, self.item_exposure_per_round_with_FPTP(config, dataObj, metric), {'x': 'rounds', 'y': 'item rank', 'legend': get_legend_labels(self.rankers)}, 'scatter_colorbar')
            if metric['name'] == 'ranking-popularity-correlation':
                viz.draw(metric, self.ranking_popularity_correlation(config, dataObj, metric), {'x': 'rounds', 'y': 'correlation', 'legend': get_legend_labels(self.rankers)}, 'scatter')
            if metric['name'] == 'pri':
                viz.draw(metric, self.PRI(config, dataObj, metric), {'x': 'rounds', 'y': 'correlation', 'legend': get_legend_labels(self.rankers)}, 'scatter')

    def n_step_regret(self):
        regret = {}
        for key, value in self.rewards.items():
            regret[key] = {'x':range(len(value['optimal'])), 'y': np.cumsum(np.array(value['optimal']) - np.array(value['ranker']))}
        return regret

    def cumulative_alpha_ia(self, config, dataObj):
        ia = self.compute_ia_per_round(config, dataObj)
        cumulative_ia = {}
        for key, value in ia.items():
            tmp = np.zeros(value.shape[0])
            for i in range(value.shape[0]):
                tmp[i] = np.count_nonzero(np.sum(value[:i+1, :], axis=0) >= 1) / dataObj.n_items
            cumulative_ia[key] = {'x': range(len(tmp)), 'y': tmp}
        return cumulative_ia

    def item_exposure_per_round(self, config, dataObj, metric):
        item_exposure = {}
        subdirs, dir_name = self.get_result_subdir(config)
        ranker_index = 0
        for subdir in subdirs:
            tmp = np.zeros((dataObj.n_items, config.rounds))
            for i in range(config.rounds):
                with open(str(subdir / str(i)), 'r') as f:
                    items_position = self.load_rankings_as_item_avg_ranking(config, dataObj, json.load(f))
                    tmp[:, i] = items_position
            item_exposure[dir_name[ranker_index]] = {'data': tmp}
                    # for item in range(items_position.shape[0]):
                    #     item_position = np.argwhere(items_position[item] > 0) + 1
                    #     item_exposure[dir_name[ranker_index]][item, i] = np.mean(item_position)
            if metric['orderby'] == 'ranking':
                item_exposure[dir_name[ranker_index]] = item_exposure[dir_name[ranker_index]][np.sum(item_exposure[dir_name[ranker_index]], axis=1).argsort()][::-1]
            elif metric['orderby'] == 'popularity':
                item_exposure[dir_name[ranker_index]] = item_exposure[dir_name[ranker_index]][self.compute_item_popularity(dataObj).argsort()][::-1]
            # item_exposure[dir_name[ranker_index]] = item_exposure[dir_name[ranker_index]][item_exposure[dir_name[ranker_index]][:,1].argsort()][::-1]
            ranker_index += 1
        return item_exposure

    def item_exposure_per_round_with_FPTP(self, config, dataObj, metric):
        item_exposure = {}
        subdirs, dir_name = self.get_result_subdir(config)
        ranker_index = 0
        for subdir in subdirs:
            tmp = np.zeros((dataObj.n_items, config.rounds))
            tmp_fp, tmp_tp = np.zeros((dataObj.n_items, config.rounds)), np.zeros((dataObj.n_items, config.rounds))
            for i in range(config.rounds):
                with open(str(subdir / str(i)), 'r') as f:
                    # items_position = self.load_ranking_as_item_position(config, dataObj, json.load(f))
                    items_position, positive_feedback, negative_feedback = self.load_ranking_pos_neg_feedback_as_matrix(config, dataObj, json.load(f))
                    tmp[:, i] = items_position
                    tmp_fp[:, i] = negative_feedback
                    tmp_tp[:, i] = positive_feedback
            item_exposure[dir_name[ranker_index]] = {'data': tmp, 'positive_feedback': tmp_tp, 'negative_feedback': tmp_fp}
            if metric['orderby'] == 'ranking':
                item_exposure[dir_name[ranker_index]]['data'] = item_exposure[dir_name[ranker_index]]['data'][np.sum(item_exposure[dir_name[ranker_index]], axis=1).argsort()][::-1]
                item_exposure[dir_name[ranker_index]]['positive_feedback'] = item_exposure[dir_name[ranker_index]]['positive_feedback'][np.sum(item_exposure[dir_name[ranker_index]], axis=1).argsort()][::-1]
                item_exposure[dir_name[ranker_index]]['negative_feedback'] = item_exposure[dir_name[ranker_index]]['negative_feedback'][np.sum(item_exposure[dir_name[ranker_index]], axis=1).argsort()][::-1]
            elif metric['orderby'] == 'popularity':
                item_exposure[dir_name[ranker_index]]['data'] = item_exposure[dir_name[ranker_index]]['data'][self.compute_item_popularity(dataObj).argsort()][::-1]
                item_exposure[dir_name[ranker_index]]['positive_feedback'] = item_exposure[dir_name[ranker_index]]['positive_feedback'][self.compute_item_popularity(dataObj).argsort()][::-1]
                item_exposure[dir_name[ranker_index]]['negative_feedback'] = item_exposure[dir_name[ranker_index]]['negative_feedback'][self.compute_item_popularity(dataObj).argsort()][::-1]
            ranker_index += 1
        return item_exposure

    def ranking_popularity_correlation(self, config, dataObj, metric):
        correlation = {}
        subdirs, dir_name = self.get_result_subdir(config)
        ranker_index = 0
        popularity = self.compute_item_popularity(dataObj)
        for subdir in subdirs:
            tmp = np.zeros(config.rounds)
            for i in range(config.rounds):
                with open(str(subdir / str(i)), 'r') as f:
                    items_position = self.load_rankings_as_item_avg_ranking(config, dataObj, json.load(f))
                    tmp[i] = -stats.spearmanr(items_position, popularity).correlation
            correlation[dir_name[ranker_index]] = {'x': range(len(tmp)), 'y': tmp}
            ranker_index += 1
        return correlation

    def PRI(self, config, dataObj, metric):
        correlation = {}
        subdirs, dir_name = self.get_result_subdir(config)
        ranker_index = 0
        popularity = self.compute_item_popularity(dataObj)
        for subdir in subdirs:
            tmp = np.zeros(config.rounds)
            for i in range(config.rounds):
                with open(str(subdir / str(i)), 'r') as f:
                    # test_data = dataObj.test_data[np.nonzero(np.any(dataObj.test_data != 0, axis=0))[0]]
                    items_position_matrix = self.load_rankings_as_item_ranking(config, dataObj, json.load(f))
                    avg_rank = np.multiply(dataObj.test_data, items_position_matrix).sum(axis=0) / np.count_nonzero(dataObj.test_data, axis=0)
                    tmp[i] = -stats.spearmanr(avg_rank[avg_rank.nonzero()[0]], popularity[avg_rank.nonzero()[0]]).correlation
            correlation[dir_name[ranker_index]] = {'x': range(len(tmp)), 'y': tmp}
            ranker_index += 1
        return correlation


    def compute_ia_per_round(self, config, dataObj):
        ia = {}
        subdirs, dir_name = self.get_result_subdir(config)
        ranker_index = 0
        for subdir in subdirs:
            ia[dir_name[ranker_index]] = np.zeros((config.rounds, dataObj.n_items))
            for i in range(config.rounds):
                with open(str(subdir / str(i)), 'r') as f:
                    ranking = self.load_ranking_as_matrix(dataObj, json.load(f))
                    ia[dir_name[ranker_index]][i, :] = np.sum(ranking, axis=0)
            ranker_index += 1
        return ia

    def load_rewards(self, config):
        self.rewards = {}
        subdirs, dir_name = self.get_result_subdir(config)
        i = 0
        for subdir in subdirs:
            with open(str(subdir / self.optimal_reward_filename), 'r') as f:
                optimal_reward = json.load(f)
            with open(str(subdir / self.ranker_reward_filename), 'r') as f:
                ranker_reward = json.load(f)
            self.rewards[dir_name[i]] = {'optimal': optimal_reward['reward'], 'ranker': ranker_reward['reward']}
            i += 1

    def get_result_subdir(self, config):
        subdirs, dir_name = [], []
        result_dir = config._target / Path('results')
        for i in range(len(self.rankers)):
            param_name = get_param_config_name(self.rankers[i]["config"])
            subdirs.append(result_dir / param_name)
            dir_name.append(param_name)

        # dirs = os.listdir(result_dir)
        # for dir in dirs:
        #     if os.path.isdir(result_dir / dir):
        #         subdirs.append(result_dir / dir)
        #         dir_name.append(dir)

        return subdirs, dir_name

    def compute_item_popularity(self, dataObj):
        return np.count_nonzero(dataObj.train_data, axis=0) / dataObj.train_data.shape[1]

    def load_ranking_as_matrix(self, dataObj, json_ranking):
        ranking = np.zeros((dataObj.n_users, dataObj.n_items))
        for key, value in json_ranking.items():
            ranking[dataObj.userid_mapped_data[key]][self.convert_itemids_to_internal_ids(dataObj, value['r'])] += 1
        return ranking
    def load_ranking_as_item_exposure_matrix(self, config, dataObj, json_ranking):
        items_position = np.zeros((dataObj.n_items, config.list_size))
        for key, value in json_ranking.items():
            ranked_items = self.convert_itemids_to_internal_ids(dataObj, value['r'])
            for i in range(len(ranked_items)):
                items_position[ranked_items[i]][i] += 1
        return items_position
    def load_rankings_as_item_ranking(self, config, dataObj, json_ranking):
        items_position = np.zeros((dataObj.n_users, dataObj.n_items))
        for key, value in json_ranking.items():
            ranked_items = self.convert_itemids_to_internal_ids(dataObj, value['r'])
            for i in range(len(ranked_items)):
                items_position[i][ranked_items[i]] += i + 1
        return items_position
    def load_rankings_as_item_avg_ranking(self, config, dataObj, json_ranking):
        items_position = np.zeros(dataObj.n_items)
        ranking_count = np.zeros(dataObj.n_items)
        for key, value in json_ranking.items():
            ranked_items = self.convert_itemids_to_internal_ids(dataObj, value['r'])
            for i in range(len(ranked_items)):
                items_position[ranked_items[i]] += i + 1
                ranking_count[ranked_items[i]] += 1
        np.seterr(invalid='ignore')
        avg_position = np.divide(items_position, ranking_count)
        avg_position[np.isnan(avg_position)] = 0
        return avg_position
    def load_ranking_pos_neg_feedback_as_matrix(self, config, dataObj, json_ranking):
        items_position = np.zeros(dataObj.n_items)
        ranking_count = np.zeros(dataObj.n_items)
        positive_feedback = np.zeros(dataObj.n_items)
        negative_feedback = np.zeros(dataObj.n_items)
        for key, value in json_ranking.items():
            ranked_items = self.convert_itemids_to_internal_ids(dataObj, value['r'])
            for i in range(len(ranked_items)):
                items_position[ranked_items[i]] += i + 1
                ranking_count[ranked_items[i]] += 1

            clicked_items = self.convert_itemids_to_internal_ids(dataObj, value['c'])
            previous_clicked_item_index = 0
            for clicked_item in clicked_items:
                positive_feedback[clicked_item] += 1
                current_clicked_item_index = ranked_items.index(clicked_item)
                negative_feedback[ranked_items[previous_clicked_item_index:current_clicked_item_index]] += 1
        np.seterr(invalid='ignore')
        avg_position = np.divide(items_position, ranking_count)
        avg_position[np.isnan(avg_position)] = 0
        return avg_position, positive_feedback, negative_feedback
    def load_pos_neg_feedback(self, config, dataObj, json_ranking):
        positive_feedback = np.zeros(dataObj.n_items)
        negative_feedback = np.zeros(dataObj.n_items)
        for key, value in json_ranking.items():
            ranked_items = self.convert_itemids_to_internal_ids(dataObj, value['r'])
            clicked_items = self.convert_itemids_to_internal_ids(dataObj, value['c'])
            previous_clicked_item_index = 0
            for clicked_item in clicked_items:
                positive_feedback[clicked_item] += 1
                current_clicked_item_index = ranked_items.index(clicked_item)
                negative_feedback[ranked_items[previous_clicked_item_index:current_clicked_item_index]] += 1
        return positive_feedback, negative_feedback

    def convert_itemids_to_internal_ids(self, dataObj, items):
        internal_list = []
        for item in items:
            internal_list.append(dataObj.itemid_mapped_data[item])
        return internal_list