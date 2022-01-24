# ************* Begin Copyright - Do not add comments here **************
#   Licensed Materials - Property of IBM
#
#   (C) Copyright IBM Corp. 2019, All Rights Reserved
#
# The source code for this program is not published or other-
# wise divested of its trade secrets, irrespective of what has
# been deposited with the U.S. Copyright Office.
# **************************** End Copyright ***************************

"""
@author: Syed Yousaf Shah (syshah@us.ibm.com)
TS LIB client file
This is test file not to be executed in build time as it needs environment setup.
"""

# load watfore model from pickle file using ts_libs
# if tspy is not in environment error is returned.
# if tspy is in the environment you should see following output
import unittest

import numpy as np

'''
Pickle Done. Now loading...
{'ts_icol_loc': -1, 'target_column_indices': -1, '_timestamps': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 'prediction_horizon': 1, '_totalsamples': 10, 'lookback_win': 1, 'debug': False, 'model': [Forecasting Model
  Algorithm: HWSAdditive=5 (aLevel=0.608, bSlope=0.001, gSeas=0.9) level=2.527610267770796, slope=0.17112450086743108, seasonal(amp,per,avg)=(0.04231743463642318,5, 0,-0.07961105047447362), Forecasting Model
  Algorithm: HWSAdditive=5 (aLevel=0.106, bSlope=0.999, gSeas=0.001) level=4.470635748808377, slope=0.1710783236485742, seasonal(amp,per,avg)=(3.1363510287205857E-4,5, 0,-0.012625642525853626)], 'model_dumps': [b'\x80\x03ctspy.data_structures.forecasting.ForecastingModel\nForecastingModel\nq\x00)\x81q\......A=q\x04sb.'], 'model_update_predict': [Forecasting Model
  Algorithm: HWSAdditive=5 (aLevel=0.608, bSlope=0.001, gSeas=0.9) level=2.527610267770796, slope=0.17112450086743108, seasonal(amp,per,avg)=(0.04231743463642318,5, 0,-0.07961105047447362), Forecasting Model
  Algorithm: HWSAdditive=5 (aLevel=0.106, bSlope=0.999, gSeas=0.001) level=4.470635748808377, slope=0.1710783236485742, seasonal(amp,per,avg)=(3.1363510287205857E-4,5, 0,-0.012625642525853626)], 'log_transformed': True, 'compute_periodicity': True, 'model_description': "hw_additive_{'samples_per_season': 5, 'initial_training_seasons': 2, 'error_history_length': 2, 'algorithm_type': 'additive'}", 'model_family': 'statistical', 'model_name': 'hw_additive', 'model_id': 'st_', 'algorithm': 'hw_additive', 'all_args': {'samples_per_season': 0.6, 'algorithm': 'hw', 'error_history_length': 2, 'error_horizon_length': 2, 'initial_training_seasons': 2}, 'n_features_': 2, 'is_fitted_': True, 'wfts_context': None}
10
Predictions after loading [[ 11.09326624 100.41376817]]
'''


# TESTS will fail in Travis as there is no tspy in travis as of now
class TestWatForeForecasters(unittest.TestCase):

    def setUp(self):
        print('..................................Watfore TSLIB tests..................................')

    def watfore_pickle_write(self):
        print(
            '................................Watfore TSLIB Training and Pickle Write..................................')
        # for this make sure sys.modules['ai4ml_ts.estimators'] = watfore is removed from init otherwise package is confused
        try:
            import pickle
            import sys
            # sys.path.append('../../../autoai_ts/ai4ml_ts/estimators')
            # make sure you have latest version autoai_ts install
            # from watfore_forecasters import WatForeForecaster
            from ai4ml_ts.estimators.watfore_forecasters import WatForeForecaster
            # from watfore_forecasters import WatForeForecaster
            fr = WatForeForecaster(algorithm='hw', samples_per_season=0.6)  # , initial_training_seasons=3
            ts_val = [[0, 10.0], [1, 20.0], [2, 30.0], [3, 40.0], [4, 50.0], [5, 60.0], [6, 70.0], [7, 31.0], [8, 80.0],
                      [9, 90.0]]

            ml = fr.fit(ts_val, None)
            pr_before = fr.predict(None)
            fr2 = None
            print('Predictions before saving', pr_before)
            f_name = 'watfore_pipeline.pickle'  # ./tests/watfore/watfore_pipeline.pickle
            with open(f_name, 'wb') as pkl_dump:
                pickle.dump(ml, pkl_dump)
            pr2 = fr.predict(None)
            print('Predictions after pikcle dump', pr2)
            self.assertTrue((np.asarray(pr2).ravel() == np.asarray(pr_before).ravel()).all())
            print('Pickle Done. Now loading...')
            with open(f_name, 'rb') as pkl_dump:
                fr2 = pickle.load(pkl_dump)

            if fr2 is not None:
                print(fr2.__dict__)
                print(fr2._totalsamples)
                preds = fr2.predict(None)
                print('Predictions after loading', preds)
                self.assertTrue(len(preds) == 1)
                self.assertTrue((np.asarray(preds).ravel() == np.asarray(pr_before).ravel()).all())
            else:
                print('Failed to Load model(s) from location' + f_name)
                self.fail('Failed to Load model(s) from location' + f_name)
            print('................................Watfor TSLIB Pickle Write Done.........................')

        except Exception as e:
            print('Failed to Load model(s)')
            self.fail(e)

    def load_watfore_pipeline(self):

        print(
            '..................................Watfore TSLIB Pickle load and Predict.................................')
        import pickle
        # import sys
        # sys.path.append('../../autoai_ts_libs/watfore')
        # Import form autoai_ts_libs
        from autoai_ts_libs.watfore.watfore_forecasters import WatForeForecaster

        # f_name = './tests/watfore/watfore_pipeline.pickle'
        f_name = 'watfore_pipeline.pickle'
        print('Pickle Done. Now loading...')
        with open(f_name, 'rb') as pkl_dump:
            fr2 = pickle.load(pkl_dump)

        if fr2 is not None:
            print(fr2.__dict__)
            print(fr2._totalsamples)
            preds = fr2.predict(None)
            print('Predictions after loading', preds)
            self.assertTrue(len(preds) == 1)

            # self.assertTrue((np.asarray(preds).ravel() == np.asarray(pr_before).ravel()).all())
        else:
            print('Failed to Load model(s) from location' + f_name)
            self.fail('Failed to Load model(s) from location' + f_name)
        print('................................Watfore TSLIB Read and predict Done.........................')
# if __name__ == "__main__":
#     # If pickle file for pure watfore is not present and ai4ml is present
#     #test_watfore_pickle_write()
#     TestWatForeForecasters.watfore_pickle_write()
#     TestWatForeForecasters.load_watfore_pipeline()
