import unittest, time, os
import pandas as pd
from dpcgeneration import DPCopula
from configuration import DATASETS, DATASETS_CONFIGS
from dpcgeneration import calculate_oneWay, calculate_print, calculate_twoWay

class MyTestCase(unittest.TestCase):




    def test_rundpcbin(self):

        copula = DPCopula()

        try:
            df = pd.read_csv('../' + DATASETS['adult'])
        except FileNotFoundError:
            print('Error File does not exist')
        timestr = time.strftime("%Y%m%d-%H%M%S")
        out_file =  '../out/data_test_dpc_bin_epsilon=None_' + timestr + '.csv'
        df_res = copula.rundpc_onehot(data=df[['sex','race']],
                               withNoise=False,
                               epslimit=1,
                               path_fnl='../out/',
                               labels=['dpc-bin'],
                               out_file=out_file,
                               epssize=None,
                               extendoutput=None, verbose=True, save =False)


        self.assertEqual(len(df_res), len(df))
        os.remove(out_file)


    def test_rundpconehot_small(self):

        copula = DPCopula()

        try:
            df = pd.read_csv('../' + DATASETS['mnist_0'])
        except FileNotFoundError:
            print('Error File does not exist')
        timestr = time.strftime("%Y%m%d-%H%M%S")
        out_file =  '../out/data_test_dpc_bin_epsilon=None_' + timestr + '.csv'
        df_res = copula.rundpc_onehot(data=df[df.columns.tolist()[5:10]],
                               withNoise=False,
                               epslimit=1,
                               path_fnl='../out/',
                               labels=['dpc-bin'],
                               out_file=out_file,
                                convert_bin=False,
                               epssize=None,
                               extendoutput=None, verbose=True, save =False)

        df.columns = df.columns.astype(str)
        df_res = df_res.astype(int)
        df_oneway_orig = calculate_oneWay(df,df.columns.tolist()[5:10])
        df_oneway_gen= calculate_oneWay(df_res, df_res.columns.tolist())

        calculate_print([df_oneway_orig], [df_oneway_gen], 'CDF of One Way', labels=['5 onehot encoding attributes'],
                                                             figname='../out/'+'mnist0-oneway', printgraph=False, savedata='../out/'+'mnist0-oneway_gen')

        df_twoway_orig = calculate_twoWay(df, df.columns.tolist()[5:10])
        df_twoway_gen = calculate_twoWay(df_res, df_res.columns.tolist())
        calculate_print([df_twoway_orig], [df_twoway_gen], 'CDF of Two Way', labels=['5 onehot encoding attributes'],
                                                            figname='../out/'+'mnist0-twoway', printgraph=False, savedata='../out/'+'mnist0-twoway_gen')


        self.assertEqual(len(df_res), len(df))
        #os.remove(out_file)

    def test_rundpconehot_big(self):

        copula = DPCopula()

        try:
            df = pd.read_csv('../' + DATASETS['adult'])
        except FileNotFoundError:
            print('Error File does not exist')
        timestr = time.strftime("%Y%m%d-%H%M%S")
        out_file =  '../out/data_test_dpc_bin_epsilon=None_' + timestr + '.csv'
        df_res = copula.rundpc_onehot(data=df[['sex','age']],
                               withNoise=False,
                               epslimit=1,
                               path_fnl='../out/',
                               labels=['dpc-bin'],
                               out_file=out_file,
                               epssize=None,
                               extendoutput=None, verbose=True, save =False)


        self.assertEqual(len(df_res), len(df))
        os.remove(out_file)



    def test_rundpc(self):
        copula = DPCopula()

        try:
            df = pd.read_csv('../'+DATASETS['adult'])
        except FileNotFoundError:
            print('Error File does not exist')
        timestr = time.strftime("%Y%m%d-%H%M%S")
        out_file = '../out/data_test_dpc_epsilon=None_' + timestr + '.csv'
        df_res = copula.rundpc(data=df[['sex','race']],
                               withNoise=False,
                               epslimit=1,
                               path_fnl='../out/',
                               labels=['dpc'],
                               out_file=out_file,
                               epssize=None,
                               extendoutput=None, verbose=True, save =False)


        self.assertEqual(len(df_res), len(df))
        os.remove(out_file)

    def test_rundpccond(self):
        copula = DPCopula()

        try:
            df = pd.read_csv('../'+DATASETS['adult'])
        except FileNotFoundError:
            print('Error File does not exist')
        timestr = time.strftime("%Y%m%d-%H%M%S")
        out_file = '../out/data_test_dpc_cond_epsilon=None_' + timestr + '.csv'


        df_res = copula.rundpc_cond( data= df[['sex','race','marital-status','workclass']],
                                     withNoise=True,
                                     epslimit=1,
                                     epsilon_cond=1,
                                     path_fnl='../out/',
                                     cop_att_list=['sex','race'],

                                     out_file=out_file,
                                    privbayes_degree_max =2, extendoutput=None, verbose=True, save=False)


        self.assertEqual(len(df_res), len(df))
        os.remove(out_file)

    def test_rundpccond_bayse(self):
        copula = DPCopula()

        try:
            df = pd.read_csv('../'+DATASETS['adult'])
        except FileNotFoundError:
            print('Error File does not exist')
        timestr = time.strftime("%Y%m%d-%H%M%S")
        out_file = '../out/data_test_dpc_cond_epsilon=None_' + timestr + '.csv'


        df_res = copula.rundpc_cond( data= df[['sex','race','marital-status','workclass']],
                                     withNoise=True,
                                     epslimit=1,
                                     epsilon_cond=1,
                                     path_fnl='../out/',
                                     cop_att_list=[],

                                     out_file=out_file,
                                    privbayes_degree_max =2, extendoutput=None, verbose=True, save=False)


        self.assertEqual(len(df_res), len(df))
        os.remove(out_file)

    def test_rundpccond_bin(self):
        copula = DPCopula()

        try:
            df = pd.read_csv('../'+DATASETS['adult'])
        except FileNotFoundError:
            print('Error File does not exist')
        timestr = time.strftime("%Y%m%d-%H%M%S")
        out_file = '../out/data_test_dpc_cond_epsilon=None_' + timestr + '.csv'


        df_res = copula.rundpc_cond( data= df[['sex','race','marital-status','workclass']],
                                     withNoise=True,
                                     epslimit=1,
                                     epsilon_cond=1,
                                     path_fnl='../out/',
                                     cop_att_list=['sex','race'],
                                     run_binnary=True,
                                     out_file=out_file,
                                    privbayes_degree_max =2, extendoutput=None, verbose=True, save=False)


        self.assertEqual(len(df_res), len(df))
        #os.remove(out_file)


if __name__ == '__main__':
    unittest.main()
