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

'''
# Adapted from pickletest.py
def test_data_gen_2000_multivariates(buildmodel, est, exclude, y_lookback):
    df_name = '../../../autoai_ts/time_series_fvt/repository/input/data/data_gen_train_2000.csv'
    tc = '3 10'
    lbw = str(12)
    ph = str(2)
    output_f: str = 'model_data_gen_2000_' + est
    pickle_name: str = output_f + '.pickle'
    # Build model and save best pipeline
    if buildmodel:
        case = 'python3 ../../../autoai_ts/run_time_series_daub.py -df ' + df_name + ' -pl watfore -tc ' + tc \
               + ' -sbm ' + pickle_name + ' -ee ' + exclude + ' -lbw ' + lbw + ' -ph ' + ph + ' -of ' + output_f
        print(case)
        res = subprocess.run(case, shell=True)
        print(res.returncode)
    # Load model to predict with y_lookback data.
    y_pred = None
    model = pickle.load(gzip.open(pickle_name, 'rb')) #Score.load(pickle_name, False)
    if model is None:
        print('Cannot load model')
    else:
        print("****************************")
        y_pred = model.predict(y_lookback)
        # print(y_pred)
    return y_pred

def test_model_loader(y_lookback):
    pkls = ['model_data_gen_2000_BATS.pickle','model_data_gen_2000_ARIMA.pickle','model_data_gen_2000_HoltWinters.pickle']
    for pickle_name in pkls:
        model = pickle.load(gzip.open(pickle_name, 'rb'))
        if model is None:
            print('Cannot load model')
        else:
            print("****************************")
            y_pred = model.predict(y_lookback)
            print ('Forecasted Values', y_pred)


'''


def watfore_pickle_write():
    print('Pickle and Load Test')
    try:
        import pickle
        import sys
        # print(glob.glob("../../../autoai_ts/ai4ml_ts/*"))
        sys.path.append('../../../autoai_ts/')
        # make sure you have latest version autoai_ts install
        # print(sys.path)
        import ai4ml_ts
        # sys.modules['ai4ml_ts'] = ai4ml_ts
        from ai4ml_ts.estimators.watfore_forecasters import WatForeForecaster
        # from watfore_forecasters import WatForeForecaster
        fr = WatForeForecaster(algorithm='hw', samples_per_season=0.6)  # , initial_training_seasons=3
        ts_val = [[0, 10.0], [1, 20.0], [2, 30.0], [3, 40.0], [4, 50.0], [5, 60.0], [6, 70.0], [7, 31.0], [8, 80.0],
                  [9, 90.0]]

        ml = fr.fit(ts_val, None)
        pr_before = fr.predict(None)
        fr2 = None
        print('Predictions before saving', pr_before)
        f_name = 'watfore_pipeline.pickle'
        with open(f_name, 'wb') as pkl_dump:
            pickle.dump(fr, pkl_dump)
        pr2 = fr.predict(None)
        print('Predictions after pikcle dump', pr2)
        # self.assertTrue((np.asarray(pr2).ravel() == np.asarray(pr_before).ravel()).all())
        print('Pickle Done. Now loading...')
        with open(f_name, 'rb') as pkl_dump:
            fr2 = pickle.load(pkl_dump)

        if fr2 is not None:
            print(fr2.__dict__)
            print(fr2._totalsamples)
            preds = fr2.predict(None)
            print('Predictions after loading', preds)
            # self.assertTrue(len(preds) == 1)

            # self.assertTrue((np.asarray(preds).ravel() == np.asarray(pr_before).ravel()).all())
        else:
            print('Failed to Load model(s) from location' + f_name)

    except Exception as e:
        print('Failed to Load model(s)')
        print(e)
        # self.fail(e)


def load_watfore_pipeline():
    import pickle
    # import sys
    # sys.path.append('../../autoai_ts_libs/watfore')
    # Import form autoai_ts_libs
    from autoai_ts_libs.watfore.watfore_forecasters import WatForeForecaster

    f_name = 'watfore_pipeline.pickle'
    print('Pickle Done. Now loading...')
    with open(f_name, 'rb') as pkl_dump:
        fr2 = pickle.load(pkl_dump)

    if fr2 is not None:
        print(fr2.__dict__)
        print(fr2._totalsamples)
        preds = fr2.predict(None)
        print('Predictions after loading', preds)
        # self.assertTrue(len(preds) == 1)

        # self.assertTrue((np.asarray(preds).ravel() == np.asarray(pr_before).ravel()).all())
    else:
        print('Failed to Load model(s) from location' + f_name)


def load_refit_watfore_pipeline():
    import pickle
    # import sys
    # sys.path.append('../../autoai_ts_libs/watfore')
    # Import form autoai_ts_libs
    from autoai_ts_libs.watfore.watfore_forecasters import WatForeForecaster

    f_name = 'watfore_pipeline.pickle'
    print('Pickle Done. Now loading and refitting...')
    with open(f_name, 'rb') as pkl_dump:
        fr2 = pickle.load(pkl_dump)

    if fr2 is not None:
        # print(fr2.__dict__)

        # ts_val = [[0, 110.0], [1, 120.0], [2, 130.0], [3, 140.0], [4, 150.0], [5, 160.0], [6, 170.0], [7, 180.0], [8, 190.0]]
        ts_val = [[9, 100.0], [10, 110.0], [11, 120.0]]
        fr2.fit(ts_val, None)
        # print(fr2.get_last_updated())
        # import inspect
        # print(inspect.getfile(fr2.__class__))
        preds = fr2.predict(None)
        print('Predictions after loading and refit', preds)
        # self.assertTrue(len(preds) == 1)

        # self.assertTrue((np.asarray(preds).ravel() == np.asarray(pr_before).ravel()).all())
    else:
        print('Failed to Load model(s) from location' + f_name)


if __name__ == "__main__":
    # If pickle file for pure watfore is not present and ai4ml is present

    # import sys
    # from autoai_ts_libs import watfore
    # sys.modules['ai4ml_ts'] = watfore
    # sys.modules['ai4ml_ts.estimators'] = watfore

    # watfore_pickle_write()

    load_watfore_pipeline()
    print('===========================================================***********************************')
    load_refit_watfore_pipeline()

    # TESTS from pickletest
    # data used for prediction for case 1 - airPassenger
    # y_lbw_uni = [417, 391, 419, 461, 472, 535, 622, 606, 508, 461, 390, 432]
    # # data used for prediction for case 2 - data_gen_2000
    # y_lbw_multi1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    # y_lbw_multi2 = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    # segdata = np.mat([y_lbw_multi1, y_lbw_multi2]).T
    # test_model_loader(segdata)

    # IF pickle files are not there and path to run_time_seriesdaub exists uncomment & run below
    # estimators_list = ["BATS", "ARIMA", "HoltWinters"]
    # y_forcast = dict.fromkeys(estimators_list)
    # estimator: str
    # for estimator in estimators_list:
    #     estimators_exclude = [x for x in estimators_list if x is not estimator]
    #     estimators_exclude = " ".join(estimators_exclude)
    #     y_forcast[estimator] = test_data_gen_2000_multivariates(buildmodel=True, est=estimator,
    #                                                             exclude=estimators_exclude, y_lookback=segdata)
    # print(y_forcast)
