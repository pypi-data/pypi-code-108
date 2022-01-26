from unittest import TestCase

from tests import apiv1

class TestGetUser(TestCase):
    def test_deserialize(self):
        r = apiv1.get_user("tybug2")

        self.assertEqual(r.username, "tybug2")
        self.assertEqual(apiv1.get_user(12092800).username, "tybug2")

class TestGetBeatmaps(TestCase):
    def test_deserialize(self):
        apiv1.get_beatmaps(beatmapset_id=1051305)
        apiv1.get_beatmaps(beatmap_id=221777)

class TestGetUserBest(TestCase):
    def test_deserialize(self):
        apiv1.get_user_best(12092800)

class TestGetReplay(TestCase):
    def test_deserialize(self):
        r1 = apiv1.get_replay(beatmap_id=221777, user=2757689)
        r2 = apiv1.get_replay(score_id=2828620518)

        self.assertEqual(len(r1), 155328)
        self.assertEqual(len(r2), 141068)

class TestGetScores(TestCase):
    def test_deserialize(self):
        apiv1.get_scores(221777)
        apiv1.get_scores(221777, user="tybug2")

class TestGetUserRecent(TestCase):
    def test_deserialize(self):
        apiv1.get_user_recent(12092800)

class TestGetMatch(TestCase):
    def test_deserialize(self):
        apiv1.get_match(69063884)
