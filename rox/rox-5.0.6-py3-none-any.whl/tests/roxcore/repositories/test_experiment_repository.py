import unittest

from rox.core.configuration.models.experiment_model import ExperimentModel
from rox.core.repositories.experiment_repository import ExperimentRepository


class ExperimentRepositoryTests(unittest.TestCase):
    def test_will_return_null_when_not_found(self):
        exp = [ExperimentModel('1', '1', '1', False, ['a'], set(), 'stam')]
        exp_repo = ExperimentRepository()
        exp_repo.set_experiments(exp)

        self.assertIsNone(exp_repo.get_experiment_by_flag('b'))

    def test_will_return_when_found(self):
        exp = [ExperimentModel('1', '1', '1', False, ['a'], set(), 'stam')]
        exp_repo = ExperimentRepository()
        exp_repo.set_experiments(exp)

        self.assertEqual('1', exp_repo.get_experiment_by_flag('a').id)
