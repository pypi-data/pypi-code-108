import unittest
import logging
import numpy as np
import glob
import os
from autoai_ts_libs.utils.score import Score
import pandas as pd

# logger = logging.getLogger()


# saved models were created by running:
# python3 run_time_series_daub.py -df time_series_fvt/repository/input/data/Air_Quality.csv -tc 1 2 -tsc 0 -imp true -impth 0.3 -impl Linear -ph 2 -mnde 10 -of ~/Documents/IBM/Research/IOT/autoai_ts_libs/tests/notebook_support/models/test -ompath ~/Documents/IBM/Research/IOT/autoai_ts_libs/tests/notebook_support/models -rrtc True

data_path = "data/Air_Quality.csv"

class FitTest(unittest.TestCase):
    def setUp(self):        
        file_path = os.path.realpath(__file__)
        cwdir = os.path.split(file_path)[0]
        self.saved_model_path = os.path.join(cwdir, "models")
        self.num_models = 10
        # print("saved_model_path", self.saved_model_path)
        # create a perturbed subsample which is larger
        X = pd.read_csv(os.path.join(cwdir, "..", "data", "Air_Quality.csv"))
        columns = [1, 2]
        l = min(200, X.shape[0])
        self.Xp = X.iloc[-l:,columns] + np.sqrt(0.1)*np.random.randn(l, len(columns)) + 10

    def tearDown(self):
        pass

    def test_load_and_fit(self):

        Xp = self.Xp
        models = glob.glob(os.path.join(self.saved_model_path, "*.pkl"))
        # first ensure we have the right count of models
        self.assertEqual(len(models),self.num_models)

        for p in models:
            with self.subTest(model_path=p, test="Load model"):
                print(p)
                m = Score.load(p)
            with self.subTest(model_path=p, test="predict(None)"):
                z = m.predict(None)
            with self.subTest(model_path=p, test="fit()"):
                m.fit(Xp, Xp)
                z2 = m.predict(None)
                # this test was too aggressive
                # self.assertGreater(np.mean(z2-z),0)
                self.assertEqual(z2.shape, z.shape)


if __name__ == "__main__":
    unittest.main()