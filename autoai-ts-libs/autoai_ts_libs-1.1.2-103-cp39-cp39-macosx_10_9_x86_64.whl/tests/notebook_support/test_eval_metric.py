import unittest
import glob
import os
import sys
from autoai_ts_libs.utils.score import Score
import pandas as pd
from autoai_ts_libs.utils.metrics import get_scorer

# saved models were created by running:
# python3 run_time_series_daub.py -df time_series_fvt/repository/input/data/Air_Quality.csv -tc 1 2 -tsc 0 -imp true -impth 0.3 -impl Linear -ph 2 -mnde 10 -of ~/Documents/IBM/Research/IOT/autoai_ts_libs/tests/notebook_support/models/test -ompath ~/Documents/IBM/Research/IOT/autoai_ts_libs/tests/notebook_support/models -rrtc True

data_path = "data/Air_Quality.csv"

class FitTest(unittest.TestCase):
    def setUp(self):        
        file_path = os.path.realpath(__file__)
        cwdir = os.path.split(file_path)[0]
        if (sys.version_info >= (3, 8)) and (sys.version_info < (3, 9)):
            print("Python version: 3.8")
            models_location = "models/python38"
        elif sys.version_info >= (3, 9) and (sys.version_info < (3, 10)):
            print("Python version: 3.9")
            models_location = "models/python39"
        self.saved_model_path = os.path.join(cwdir, models_location)
        self.num_models = 10
        # print("saved_model_path", self.saved_model_path)
        # create a perturbed subsample which is larger
        self.X = pd.read_csv(os.path.join(cwdir, "..", "data", "Air_Quality.csv"))
        self.columns = [1, 2]
        self.X_test = self.X.iloc[-20:, self.columns].to_numpy()
        self.y_test = self.X.iloc[-20:, self.columns].to_numpy()


    def tearDown(self):
        pass

    def test_evaluation_metric(self):
        models = glob.glob(os.path.join(self.saved_model_path, "*.pkl"))

        scorer = get_scorer("neg_avg_symmetric_mean_absolute_percentage_error")
        # scorer = get_scorer("avg_r2")
        # scorer = get_scorer("neg_avg_root_mean_squared_error")
        # scorer = get_scorer("neg_avg_mean_absolute_error")

        for p in models:
            with self.subTest(model_path=p, test="Load model"):
                print(p)
                m = Score.load(p)

            with self.subTest(model_path=p, test="scorer"):
                lookback_win = Score.get_lookback_win(m)
                print(lookback_win)
                if (lookback_win == 'auto'):
                    lookback_win = 20
                self.X_test = self.X.iloc[-(20 + lookback_win):, self.columns].to_numpy()
                score_value = scorer(m, self.X_test, self.y_test)
                print(score_value)


if __name__ == "__main__":
    unittest.main()