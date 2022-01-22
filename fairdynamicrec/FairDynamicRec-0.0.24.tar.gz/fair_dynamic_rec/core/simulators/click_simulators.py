import numpy as np


class AbstractSimulator(object):
    name = 'Abstract'

    def __init__(self, seed=42):
        self.prng = np.random.RandomState(seed=seed)

    def get_feedback(self, rank):
        raise NotImplementedError


class CascadeSimulator(AbstractSimulator):
    name = 'CM'

    def __init__(self, theta_star, *args, **kwargs):
        super(CascadeSimulator, self).__init__(*args, **kwargs)
        assert np.linalg.norm(theta_star) <= 1.00001
        self.theta = theta_star
        self.coins = None
        self.coins_ready = False

    def set_coins(self, k):
        """
        -- call this, if you want to use the same coins for each positions each round
        -- set coins for each round.
        -- this should be called before get_feedback
        """
        self.coins = self.prng.rand(k)
        self.coins_ready = True

    def get_feedback(self, delta):
        if type(delta) is list:
            delta = np.asarray(delta)
        delta = np.tile(delta, (1, 1))
        assert delta.shape[1] == self.theta.shape[0]

        if not self.coins_ready:
            self.set_coins(len(delta))
            self.del_coins()
        score = np.dot(delta, self.theta)
        score[score > 1] = 1.
        coins = score >= self.coins
        click = np.where(coins)[0]
        if len(click) > 0:
            coins[click[0]+1:] = False
        return coins, sum(coins)

    def del_coins(self):
        """
        This should be called by simulator at the end of each round.
        :return:
        """
        self.coins_ready = False

    def ave_feedback(self, delta):
        score = np.dot(delta, self.theta)
        score[score > 1] = 1.
        return 1 - np.prod(1-score)


class DCMSimulator(CascadeSimulator):
    name = 'DCM'

    def __init__(self, theta_star, stop_prob=None, *args, **kwargs):
        super(DCMSimulator, self).__init__(theta_star, *args, **kwargs)
        assert np.linalg.norm(theta_star) <= 1
        self.theta = theta_star
        self.coins = None
        self.stop_coins = None
        self.coins_ready = False
        if not stop_prob:
            self.stop_prob = [0.6555304, 0.4868164, 0.46051615, 0.46315161,
                              0.45642676, 0.47130397, 0.50317268, 0.54764235,
                              0.65359742, 0.0]
            # self.stop_prob = 1. / np.arange(1, 11)
        else:
            self.stop_prob = stop_prob

    def set_coins(self, k):
        """
        -- call this, if you want to use the same coins for each positions each round
        -- set coins for each round.
        -- this should be called before get_feedback
        """
        self.coins = self.prng.rand(k)
        self.stop_coins = self.prng.rand(k)
        self.coins_ready = True

    def get_feedback(self, delta):
        if type(delta) is list:
            delta = np.asarray(delta)
        delta = np.tile(delta, (1, 1))
        assert delta.shape[1] == self.theta.shape[0]
        k = len(delta)
        assert k <= len(self.stop_prob)

        if not self.coins_ready:
            self.set_coins(k)
            self.del_coins()
        score = np.dot(delta, self.theta)
        score[score > 1] = 1.
        coins = score >= self.coins
        stops = self.stop_prob[:k] >= self.stop_coins
        stop_click = stops * coins
        if sum(stop_click) == 0:
            stop_pos = len(score)
        else:
            stop_pos = np.flatnonzero(stop_click)[0] + 1

        coins[stop_pos:] = False
        stop_click[stop_pos:] = False
        return coins, sum(stop_click)


class PBMSimulator(AbstractSimulator):
    """
    Position based model
    """
    name = 'PBM'

    def __init__(self, theta_star, examination_prob=None, *args, **kwargs):
        """
        :param theta_star:
        :param examination_prob: examination probability
        :param args:
        :param kwargs:
        """
        super(PBMSimulator, self).__init__(*args, **kwargs)
        assert np.linalg.norm(theta_star) <= 1
        self.theta = theta_star
        if not examination_prob:
            self.exam_prob = 1 / np.arange(1, 11)
            self.exam_prob = np.asarray([0.99999257, 0.96679847, 0.7973465, 0.63112651,
                                         0.50237947, 0.41921298, 0.35512778, 0.30566137,
                                         0.28128806, 0.2852233])
            self.K = 10
        else:
            self.K = len(examination_prob)
            self.exam_prob = examination_prob
        self.coin_pos = None
        self.coin_att = None
        self.coins_ready = False

    def set_coins(self, k):
        """
        -- call this, if you want to use the same coins for each positions each round
        -- set coins for each round.
        -- this should be called before get_feedback
        """
        self.coin_pos = self.prng.rand(self.K)
        self.coin_att = self.prng.rand(k)
        self.coins_ready = True

    def get_feedback(self, delta):
        if type(delta) is list:
            delta = np.asarray(delta)
        delta = np.tile(delta, (1, 1))
        assert delta.shape[1] == self.theta.shape[0]
        assert len(delta) <= self.K

        if not self.coins_ready:
            self.set_coins(len(delta))
            self.del_coins()

        k = len(delta)
        score = np.dot(delta, self.theta)
        score[score > 1] = 1.
        att_coins = score >= self.coin_att
        pos_coins = self.exam_prob >= self.coin_pos
        click = att_coins * pos_coins[:k]

        return click, sum(click)

    def del_coins(self):
        """
        This should be called by simulator at the end of each round.
        :return:
        """
        self.coins_ready = False


class DBMSimulator(CascadeSimulator):
    name = 'Document based model'

    def __init__(self, theta_star, *args, **kwargs):
        super(DBMSimulator, self).__init__(theta_star, *args, **kwargs)

    def get_feedback(self, delta):
        if type(delta) is list:
            delta = np.asarray(delta)
        delta = np.tile(delta, (1, 1))
        assert delta.shape[1] == self.theta.shape[0]

        if not self.coins_ready:
            self.set_coins(len(delta))
            self.del_coins()
        score = np.dot(delta, self.theta)
        score[score > 1] = 1.
        coins = score >= self.coins
        return coins, sum(coins)

class NaiveCascadeSimulator(AbstractSimulator):
    name = 'NCM'

    def __init__(self, *args, **kwargs):
        super(NaiveCascadeSimulator, self).__init__(*args, **kwargs)
        # assert np.linalg.norm(theta_star) <= 1.00001
        # self.theta = theta_star
        self.coins = None
        self.coins_ready = False

    def set_coins(self, k):
        """
        -- call this, if you want to use the same coins for each positions each round
        -- set coins for each round.
        -- this should be called before get_feedback
        """
        self.coins = self.prng.rand(k)
        self.coins_ready = True

    def get_feedback(self, weights):
        # if type(delta) is list:
        #     delta = np.asarray(delta)
        # delta = np.tile(delta, (1, 1))
        # assert delta.shape[1] == self.theta.shape[0]

        if not self.coins_ready:
            self.set_coins(len(weights))
            self.del_coins()
        # score = np.dot(delta, self.theta)
        weights[weights > 1] = 1.
        coins = weights >= self.coins
        click = np.where(coins)[0]
        if len(click) > 0:
            coins[click[0]+1:] = False
        return coins, sum(coins)

    def del_coins(self):
        """
        This should be called by simulator at the end of each round.
        :return:
        """
        self.coins_ready = False

    def ave_feedback(self, delta):
        score = np.dot(delta, self.theta)
        score[score > 1] = 1.
        return 1 - np.prod(1-score)
