from unittest import TestCase

from dkist_processing_pac import generic

#TODO: Make this whole module not stupid. It has become stupid since the switch to ini_params.asdf implementation
class TestFitRecipes(TestCase):

    def setUp(self):
        self.exclude = ['x34','t34','x56','t56','switches','I_sys']

    def param_in_range(self, mode_opts, parameter):
        assert mode_opts[parameter]['value'] >= mode_opts[parameter][ 'min']
        assert mode_opts[parameter]['value'] <= mode_opts[parameter][ 'max']

    def test_baseline(self):
        mode_opts = generic.init_fit_mode('baseline', 666, True)
        for par in mode_opts.keys():
            if par in self.exclude:
                continue
            with self.subTest(parameter=par):
                self.param_in_range(mode_opts, par)
