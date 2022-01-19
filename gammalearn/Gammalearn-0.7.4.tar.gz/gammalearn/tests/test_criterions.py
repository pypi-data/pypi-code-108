import unittest
import torch

from gammalearn.criterions import one_hot
import gammalearn.criterions as criterions
import gammalearn.constants as csts


class TestCriterions(unittest.TestCase):

    def setUp(self) -> None:
        self.labels = torch.tensor([0, 1, 1, 0, 1, 0, 0, 1], dtype=torch.long)
        self.onehot = torch.tensor([[1, 0],
                                    [0, 1],
                                    [0, 1],
                                    [1, 0],
                                    [0, 1],
                                    [1, 0],
                                    [1, 0],
                                    [0, 1]], dtype=torch.long)
        self.targets = {
            'energy': {
                'output_shape': 1,
                'loss': torch.nn.L1Loss(reduction='none'),
                'loss_weight': 1,
                'metrics': {
                    # 'functions': ,
                }
            },
            'impact': {
                'output_shape': 2,
                'loss': torch.nn.L1Loss(reduction='none'),
                'loss_weight': 1,
                'metrics': {}
            },
            'class': {
                'output_shape': 2,
                'label_shape': 1,
                'loss': criterions.nll_nn,
                'loss_weight': 1,
                'metrics': {}
            },
        }
        self.particle_dict = {0: 1, 1: 2, 101: 0}
        self.loss_options_masked = {
            'conditional': True,
            'gamma_class': self.particle_dict[csts.GAMMA_ID],
        }
        self.loss_options_masked_miss_gamma = {
            'conditional': True,
        }
        self.loss_options_not_masked = {
            'conditional': False,
            'gamma_class': self.particle_dict[csts.GAMMA_ID],
        }
        self.loss_options_masked_gradnorm = {
            'conditional': True,
            'gamma_class': self.particle_dict[csts.GAMMA_ID],
            'last_common_layer': 'cv_layer5',
            # 'alpha': 0.5,  # for gradnorm
        }
        self.loss_options_masked_miss_gamma_gradnorm = {
            'conditional': True,
            'last_common_layer': 'cv_layer5',
            # 'alpha': 0.5,  # for gradnorm
        }
        self.loss_options_not_masked_gradnorm = {
            'conditional': False,
            'gamma_class': self.particle_dict[csts.GAMMA_ID],
            'last_common_layer': 'cv_layer5',
            # 'alpha': 0.5,  # for gradnorm
        }
        self.outputs_loss = {
            'energy': torch.tensor([0.1, 0.2, 0.1, 0.3, 0.6]).unsqueeze(1),
            'impact': torch.tensor([[1.1, 1.5, 1.9, 0.7, 0.8],
                                    [0.3, 0.6, 2.1, 2.2, 0.1]]).transpose(0, 1),
            'class': torch.log(torch.tensor([[0.7, 0.6, 0.3, 0.8, .2],
                                             [0.3, 0.4, 0.7, 0.2, 0.8]])).transpose(0, 1)
        }
        self.labels_loss = {
            'energy': torch.tensor([0.2, 0.1, 0.05, 0.5, 0.1]).unsqueeze(1),
            'impact': torch.tensor([[1.3, 0.5, 0.9, 1.7, 0.9],
                                    [0.2, 0.9, 2.0, 2.1, 0.3]]).transpose(0, 1),
            'class': torch.tensor([1, 0, 0, 1, 1])
        }
        self.true_losses_masked = [torch.tensor(0.8/3), torch.tensor(1.7/6),
                                   - (torch.log(torch.tensor(0.3)) +
                                      torch.log(torch.tensor(0.6)) +
                                      torch.log(torch.tensor(0.3)) +
                                      torch.log(torch.tensor(0.2)) +
                                      torch.log(torch.tensor(0.8))).squeeze() / 5
                                   ]

        self.true_losses_not_masked = [torch.tensor(0.95/5), torch.tensor(5.1/10),
                                       - (torch.log(torch.tensor(0.3)) +
                                          torch.log(torch.tensor(0.6)) +
                                          torch.log(torch.tensor(0.3)) +
                                          torch.log(torch.tensor(0.2)) +
                                          torch.log(torch.tensor(0.8))).squeeze() / 5
                                       ]

    def test_onehot(self):
        torch.allclose(self.onehot.float(),
                       one_hot(self.labels, num_classes=2).float())

    def test_compute_loss_masked(self):
        loss_func = criterions.compute_mt_loss(self.targets, **self.loss_options_masked)
        loss, _ = loss_func(self.outputs_loss, self.labels_loss)
        torch.allclose(torch.tensor(loss), torch.tensor(self.true_losses_masked))

    def test_compute_loss_not_masked(self):
        loss_func = criterions.compute_mt_loss(self.targets, **self.loss_options_not_masked)
        loss, _ = loss_func(self.outputs_loss, self.labels_loss)
        torch.allclose(torch.tensor(loss), torch.tensor(self.true_losses_not_masked))

    def test_compute_loss_masked_miss_gamma(self):
        loss_func = criterions.compute_mt_loss(self.targets, **self.loss_options_masked_miss_gamma)
        self.assertRaises(AssertionError, loss_func, self.outputs_loss, self.labels_loss)

    def test_uncertainty_loss_masked(self):
        loss_func = criterions.MultilossBalancing(self.targets, **self.loss_options_masked)
        loss, _ = loss_func(self.outputs_loss, self.labels_loss)
        torch.allclose(torch.tensor(loss), torch.tensor(self.true_losses_masked))

    def test_uncertainty_loss_not_masked(self):
        loss_func = criterions.MultilossBalancing(self.targets, **self.loss_options_not_masked)
        loss, _ = loss_func(self.outputs_loss, self.labels_loss)
        torch.allclose(torch.tensor(loss), torch.tensor(self.true_losses_not_masked))

    def test_uncertainty_loss_masked_miss_gamma(self):
        self.assertRaises(AssertionError, criterions.MultilossBalancing,
                          self.targets, **self.loss_options_masked_miss_gamma)

    def test_gradnorm_loss_masked(self):
        loss_func = criterions.GradNormBalancing(self.targets, **self.loss_options_masked_gradnorm)
        loss, _ = loss_func(self.outputs_loss, self.labels_loss)
        torch.allclose(torch.tensor(loss), torch.tensor(self.true_losses_masked))

    def test_gradnorm_loss_not_masked(self):
        loss_func = criterions.GradNormBalancing(self.targets, **self.loss_options_not_masked_gradnorm)
        loss, _ = loss_func(self.outputs_loss, self.labels_loss)
        torch.allclose(torch.tensor(loss), torch.tensor(self.true_losses_not_masked))

    def test_gradnorm_loss_masked_miss_gamma(self):
        self.assertRaises(AssertionError, criterions.GradNormBalancing,
                          self.targets, **self.loss_options_masked_miss_gamma_gradnorm)


if __name__ == '__main__':
    unittest.main()
