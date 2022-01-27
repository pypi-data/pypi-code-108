

from pandas import DataFrame
import numpy as np
from scipy.stats import norm
from scipy import  linalg
import pandas as pd
from tqdm import tqdm
import multiprocessing as mp
import time, os
from scipy import stats
import random
from sklearn.metrics import mutual_info_score

import warnings
from dpcgeneration.copula import Copulafuncs
from dpcgeneration.baysennetwork import greedy_bayes
from dpcgeneration.laplacenoise import Laplacenoise
from dpcgeneration.utils import *


warnings.filterwarnings("ignore", category=RuntimeWarning)


class DPCopula(object):






    def rundpc(self, data: DataFrame, withNoise: bool, epslimit: int, path_fnl: str, labels = ['dpc'], out_file = '', epssize=None,  extendoutput=None, verbose=False, save=False):


        if out_file =='':
            timestr = time.strftime("%Y%m%d-%H%M%S")
            out_file = path_fnl + 'data_out_' + labels[0] + '_epsilon='+str(epslimit)+ '_' + timestr + '.csv'
        self.dataset = data
        self.copula = Copulafuncs()
        self.verbose = verbose
        self.withNoise = withNoise
        # Read Initial and  binned file

        df_oneway_orig, df_oneway_gen = [], []
        df_twoway_orig, df_twoway_gen = [], []
        df_copulas = []


        for orig_dt in [self.dataset]:

            self.record_num, self.attribute_num = self.copula.get_mat_len(orig_dt)
            nb_marginal = self.attribute_num


            # Calculate epsilon
            epsilon = Laplacenoise(nb_marginal, epslimit).getEpsilon()

            self.scale = float(2 / epsilon)
            if verbose == True:
                print('epsilon', epsilon, 'scale', self.scale)



            #Convert Dataset to integer
            if verbose == True:
                print('step 0 : Convert Dataset to numerical Dataset ')
            self.orig_dataset, attr_dictionary = self.transform_dataset_numerical(orig_dt)
            # Save attribute names
            att_name_list_old = list(self.orig_dataset.columns)

            self.threshold_arrays, threshold_arrays_init = {}, {}
            dictlist_init, dictlist_with_noise = {}, {}

            # Step 1 : For each attribute att in the list
            # Calculate 1-way with noise
            if verbose == True:
                print('step 1 : Calculals ou te 1-way with noise ')

            dropped_attr = {}
            self.att_name_list = []
            # display(self.orig_dataset.head())
            for att in att_name_list_old:

                # Calculate counts for each value and save it into a dictionary
                unique, counts = np.unique(self.orig_dataset[att].fillna(-1), return_counts=True)
                # display(att, unique, counts)
                if len(unique) == 1:
                    dropped_attr[att] = dict(zip(unique, counts))

                else:
                    self.att_name_list.append(att)

            for att in self.att_name_list:
                unique, counts = np.unique(self.orig_dataset[att].fillna(-1), return_counts=True)

                dictlist_init[att] = dict(zip(unique, counts))
                if self.withNoise == True:
                    dictlist_with_noise[att] = self.copula.addNoiseAndRescale(att, dictlist_init[att], self.scale, self.record_num)
                else:
                    dictlist_with_noise[att] = dictlist_init[att]
                # Calculet cdf and thereshold for initial and noisy counts
                cumul = np.cumsum(list(dictlist_with_noise[att].values()))
                summ = sum(list(dictlist_with_noise[att].values()))
                self.threshold_arrays[self.att_name_list.index(att)] = cumul / summ

                cumul = np.cumsum(list(dictlist_init[att].values()))
                summ = sum(dictlist_init[att].values())
                threshold_arrays_init[self.att_name_list.index(att)] = cumul / summ

            if save == True:
                convert_dico_dataframe(dropped_attr, path_fnl + labels[0] + '-dropped_attr.csv')
                convert_dico_dataframe(self.threshold_arrays, path_fnl + labels[0] + '-threshold_arrays.csv')
                convert_dico_dataframe(threshold_arrays_init, path_fnl + labels[0] + '-threshold_arrays_init.csv')
                convert_dico_dataframe(dictlist_init, path_fnl + labels[0] + '-dictlist_init.csv')
                convert_dico_dataframe(dictlist_with_noise, path_fnl + labels[0] + '-dictlist_with_noise.csv')

            if verbose == True:
                print('step 2 : Calculate the Gaussian threshold  ')


            # Get all values
            self.Value_arrays = {self.att_name_list.index(x): list(dictlist_with_noise[x].keys()) for x in self.att_name_list}

            if save == True:
                convert_dico_dataframe(self.Value_arrays, path_fnl + labels[0] + '-Value_arrays.csv')

            if verbose == True:

                print('step 3 : Calculate 2-way noisy marginals, Pearson R, target_cov')
            # Step2 : Pearson R
            # Calculate 2-way noisy marginals, Pearson R, target_cov

            shape = (self.attribute_num, self.attribute_num)
            R = {}
            twoway_diff = {}
            twoway_init = {}
            target_cov_value_matrix = {}


            params0 = []
            for att in range(len(self.att_name_list)):
                for j in range(att+1, len(self.att_name_list)):
                    params0.append([att,j])





            results = []

            pbar = tqdm(total=len(params0))
            with mp.Pool(processes=10) as pool:
                def callback(*args):
                    # callback
                    pbar.update(1)
                    return
                results = [pool.apply_async(self.runtwoways, args=(i,), callback=callback) for i in params0]
                results = [r.get() for r in results]





            for res in results:#.get():
                att = res[0]
                j = res[1]

                R[(self.att_name_list[att], self.att_name_list[j])] = res[2]
                target_cov_value_matrix[(self.att_name_list[att], self.att_name_list[j])] = res[3]
                twoway_diff.update(res[4])
                twoway_init.update(res[5])

            pbar.close()


            for j in range(len(self.att_name_list)):
                for att in range(att, len(self.att_name_list)):

                    if att == j:
                        if att == j:
                            # The diadonale is 1
                            R[(self.att_name_list[att], self.att_name_list[att])] = 1

                            target_cov_value_matrix[(self.att_name_list[att], self.att_name_list[att])] = np.mean(
                                self.orig_dataset[self.att_name_list[att]].fillna(-1) * self.orig_dataset[
                                    self.att_name_list[j]].fillna(-1))

                    else:

                        # The matrix are symetrical --> no need to recalculate
                        target_cov_value_matrix[(self.att_name_list[att], self.att_name_list[j])] = target_cov_value_matrix[
                            (self.att_name_list[j], self.att_name_list[att])]

                        R[(self.att_name_list[att], self.att_name_list[j])] = R[(self.att_name_list[j], self.att_name_list[att])]

            if save == True:
                convert_dico_dataframe(twoway_init, path_fnl + labels[0] + '-twoway_init.csv')
                convert_dico_dataframe(twoway_diff, path_fnl + labels[0] + '-twoway_diff.csv')
                convert_dico_dataframe(R, path_fnl + labels[0] + '-R.csv')
                convert_dico_dataframe(target_cov_value_matrix, path_fnl + labels[0] + '-target_cov_value_matrix.csv')

            if verbose == True:
                print('\nstep 4 : Calculate the estimation of Pearson R using the bisectionalSearch')

            # Step3 : Calculate the estimation of Pearson R using the bisectionalSearch
            shape = (self.attribute_num, self.attribute_num)
            estimation = np.zeros((self.attribute_num, self.attribute_num))

            params = []
            for attribute_i in range(len(self.att_name_list)):
                #if verbose == True:
                #    print(str(attribute_i) + '/' + str(len(att_name_list)))
                for nj in range(attribute_i + 1, len(self.att_name_list)):
                    params.append( [target_cov_value_matrix[
                                                        self.att_name_list[attribute_i], self.att_name_list[nj]],attribute_i, nj] )

            pbar = tqdm(total=len(params))

            with mp.Pool(processes=10) as pool:
                # results = tqdm(pool.map_async(self.runtwoways, params0, chunksize=1 // 10))
                def callback(*args):
                    # callback
                    pbar.update()
                    return

                results = [pool.apply_async(self.runbisectionalSearch, args=(i,), callback=callback) for i in params]
                results = [r.get() for r in results]
            pbar.close()

            for res in results:#.get():
                estimation[res[0], res[1]] = res[2]

            if save == True:
                convert_numpy_dataframe(estimation, path_fnl+labels[0]+'-estimation.csv')

            if verbose == True:

                print('step 5 : Calculate the Pearson_Q ')
            # Step4 : Calculate the Pearson_Q
            Pearson_Q = estimation + estimation.T + np.diag(np.ones(self.attribute_num))

            if save == True:
                convert_numpy_dataframe(Pearson_Q, path_fnl + labels[0] + '-Pearson_Q.csv')

            if verbose == True:
                print('step 6 : Calculate the Nearest Pearson_Q ')
            # Step5 :Calculate the Nearest Pearson_Q : remove the semi-negative matrix
            Pearson_Q_NSPD = self.copula.nearestSPD(Pearson_Q)

            if save == True:
                convert_numpy_dataframe(Pearson_Q_NSPD, path_fnl+labels[0]+'-Pearson_Q_NSPD.csv')

            if verbose == True:
                print('step 7 : Calculate the cholesky Pearson matrix until the nearestSPD work ')
            # try to calculate the cholesky Pearson matrix until the nearestSPD work
            for att in range(10):
                try:
                    chol_decomp_matrix = linalg.cholesky(Pearson_Q_NSPD)
                    break;
                except  np.linalg.linalg.LinAlgError:
                    Pearson_Q_NSPD = self.copula.nearestSPD(Pearson_Q_NSPD)

            if verbose == True:
                print('step 8 : Calculate cholesky Pearson matrix ')
            # Step6 : Calculate the cholesky Pearson matrix
            Pearson_Q_NSPD_Ncorr = self.copula.getPearson_Q_NSPD_Ncorr(Pearson_Q_NSPD, self.attribute_num)


            if save == True:
                convert_numpy_dataframe(Pearson_Q_NSPD_Ncorr, path_fnl + labels[0] + '-Pearson_Q_NSPD_Ncorr.csv')
            if verbose == True:
                # convert_numpy_dataframe(Pearson_Q_NSPD, path_fnl+'Pearson_Q_NSPD.csv')
                print('step 9 : Generate data using Copula ')
            # Step7 : Generate data using Copula

            if extendoutput == None:
                    nb =0
            else:
                    nb = extendoutput
            if epssize == None:
                surplus_record_num = self.record_num + nb
            else:
                lap = np.random.laplace(0, 1 / epssize, 1)
                surplus_record_num = int(self.record_num+ nb + lap)

            Y = np.random.multivariate_normal(np.zeros(self.attribute_num), Pearson_Q_NSPD_Ncorr, surplus_record_num)

            X_prime = np.zeros([surplus_record_num, self.attribute_num])
            Y_final = np.zeros([surplus_record_num, self.attribute_num])
            for att in range(self.attribute_num):
                Y_final[:, att] = (
                    self.copula.getFminux(norm.cdf(Y[:, att]), self.threshold_arrays[att], self.Value_arrays[att])).astype(int)

            if verbose == True:
                # convert_numpy_dataframe(Pearson_Q_NSPD, path_fnl+'Pearson_Q_NSPD.csv')
                print('step 10 : Save the data into th final file ')
            # Save the data into th final file


            out_file_binary = path_fnl+'data_out_'+labels[0]+'_bin.csv'

            with open(out_file_binary, 'w') as f:
                f.write(','.join(self.att_name_list) + '\n')
                for att in range(surplus_record_num):
                    ll = ''
                    for j in range(self.attribute_num):
                        ll += str(Y_final[att, j]) + ','
                    f.write(ll[:-1] + '\n')

            df_copulas_all_d = pd.DataFrame()
            df_copulas_all = pd.read_csv(out_file_binary)
            df_copulas.append(df_copulas_all)

            for x in attr_dictionary:
                df_copulas_all_d[x] = [attr_dictionary[x][int(a)] for a in df_copulas_all[x]]
            df_copulas_all_d.to_csv(out_file, index=False)
            os.remove(out_file_binary)

            # return orig_dataset, Y_final

            #df_oneway_orig.append(calculate_oneWay(orig_dt, self.att_name_list))
            #df_oneway_gen.append(calculate_oneWay(df_copulas_all_d, self.att_name_list))


            #df_twoway_orig.append(calculate_twoWay(orig_dt, self.att_name_list))
            #df_twoway_gen.append(calculate_twoWay(df_copulas_all_d, self.att_name_list))

        #df_oneway_compares = calculate_print(df_oneway_orig, df_oneway_gen, 'CDF of One Way', labels=labels,
        #                                     figname=path_fnl+labels[0]+'-oneway', printgraph=False, savedata=path_fnl+labels[0]+'-oneway_gen')
        #df_twoway_compares = calculate_print(df_twoway_orig, df_twoway_gen, 'CDF of Two Way', labels=labels,
        #                                     figname=path_fnl+labels[0]+'-twoway', printgraph=False, savedata=path_fnl+labels[0]+'-twoway_gen')

        return df_copulas[0]

    def genProbability(self, df, scale):
        summ0 = max(sum(df['occurence'].tolist()), 1)
        summ = 0

        while summ == 0:
            df['summ'] = summ0
            df['noisy'] = [int(max(0, x + np.random.laplace(0, scale, 1)[0])) for x in df['occurence'].tolist()]
            df['noisy_cumul'] = df.sort_values(by=['noisy'], ascending=False)['noisy'].cumsum()

            df['noisy_cumul2'] = [min(val, summ0) for val in df['noisy_cumul'].tolist()]
            df['noisy2'] = df.sort_values(by=['noisy'], ascending=False)['noisy_cumul2'].diff().fillna(
                df['noisy_cumul2'].iloc[0])
            df['noisy3'] = np.where(df['noisy2'] > 0, df['noisy'], 0)

            summ = sum(df['noisy3'].tolist())

        if summ > 0:
            df['probability'] = [x / summ for x in df['noisy3'].tolist()]
        return summ, df



    def transform_dataset_numerical(self, df_data):
        # Transform original dataset to numerical values
        df_data_num = pd.DataFrame()

        attr_dictionary = {}
        for col in df_data.columns:
            attr_dictionary[col] = list(set(df_data[col].tolist()))

        for x in attr_dictionary:
            df_data_num[x] = [attr_dictionary[x].index(a) for a in df_data[x]]

        return df_data_num, attr_dictionary

    # Get the k less correlate attributes
    def get_indices_of_k_smallest(self, x, k=20):
            indices = []
            for a in sorted(set(x.ravel())):
                # display(a, np.where(np.isin(x, a)))
                indices.append(np.where(np.isin(x, a))[0])
                k -= 1
                if k == 0:
                    break

            return indices


    def conditional_algo(self, df_orig: DataFrame, df_copula: DataFrame, dico_predictioned:dict, scale:int, out_file:str):

        df = df_orig.copy()


        for i in (dico_predictioned.keys()):

            attribute_name = dico_predictioned[i]
            # if i == 'StartStn':
            #    attribute_name = [i, attribute_name,'EntTime' ]
            # else:
            attribute_name = [i, attribute_name]
            print('attribute_name:', i, 'predictor ', attribute_name)

            if len(attribute_name) == 3:
                poss_att = [[] for x in range(3)]
                for i in range(3):
                    poss_att[i] = sorted(np.unique(df[attribute_name[i]].tolist()))

                # Calculate Conditional count attribute1 vs attribute2 and attribute3
                count_serie = df.groupby([attribute_name[0], attribute_name[1], attribute_name[2]]).size()
                new_df = count_serie.to_frame(name='occurence').reset_index()

                for att1 in poss_att[1]:
                    for att2 in poss_att[2]:

                        # For each count add laplace noise
                        # For each count add laplace noise
                        new_df2 = new_df[(new_df[attribute_name[1]] == att1) & (new_df[attribute_name[2]] == att2)].copy()

                        if len(new_df2) > 0:
                            summ, new_df2 = self.genProbability(new_df2, scale)

                            if summ > 0:
                                # Now Calculate conditional probabilities
                                # new_df2['probability']=[x/summ for x in new_df2['noisy3'].tolist()]

                                df_copula2 = df_copula[
                                    (df_copula[attribute_name[1]] == att1) & (df_copula[attribute_name[2]] == att2)]
                                # Generate data usiing these conditional probabilities
                                b = np.random.choice(new_df2[attribute_name[0]].tolist(), len(df_copula2),
                                                     p=new_df2['probability'].tolist())
                                random.shuffle(b)
                                df_copula.loc[
                                    (df_copula[attribute_name[1]] == att1) & (df_copula[attribute_name[2]] == att2),
                                    attribute_name[0]] = b
                            else:

                                aa = df_copula[
                                    (df_copula[attribute_name[1]] == att1) & (df_copula[attribute_name[2]] == att2)]
                                print('len(aa)', len(aa))
                                print(attribute_name[0], attribute_name[1], attribute_name[2], att1, att2, 'errrrrrror')
                                exit()

            else:
                poss_att = [[] for x in range(2)]

                #display(
                #    'Start Calculate Conditional count attribute1 vs attribute2 ' + str(datetime.now() - start))
                # Calculate Conditional count attribute1 vs attribute2 and attribute3
                for i in range(2):
                    poss_att[i] = sorted(np.unique(df[attribute_name[i]].tolist()))

                count_serie = df.groupby([attribute_name[0], attribute_name[1]]).size()
                new_df = count_serie.to_frame(name='occurence').reset_index()
                #display('This is number of occurance by value1/value2')
                #display(new_df.head())
                # Pour l instant je vire cette partie parce qu'elle prend trop de temps

                #display(
                #    'Start This is number of occurance by value1/value2 with noise ' + str(datetime.now() - start))

                for att1 in poss_att[1]:

                    # For each count add laplace noise
                    # For each count add laplace noise
                    #print ('df_copula', df_copula[0].head())

                    #print (' test', df_copula[attribute_name[1]] )
                    new_df2 = new_df[(new_df[attribute_name[1]] == att1)].copy()

                    if len(new_df2) > 0:
                        summ, new_df2 = self.genProbability(new_df2, scale)

                        if summ > 0:
                            # Now Calculate conditional probabilities
                            # new_df2['probability']=[x/summ for x in new_df2['noisy3'].tolist()]

                            df_copula2 = df_copula[(df_copula[attribute_name[1]] == att1)]
                            # Generate data usiing these conditional probabilities
                            b = np.random.choice(new_df2[attribute_name[0]].tolist(), len(df_copula2),
                                                 p=new_df2['probability'].tolist())
                            random.shuffle(b)
                            df_copula.loc[(df_copula[attribute_name[1]] == att1), attribute_name[0]] = b
                        else:
                            print ('summ est egal a zero je sors')
                            print(new_df2)
                            aa = df_copula[(df_copula[attribute_name[1]] == att1)]
                            exit()
        df_copula_cond = df_copula

        return df_copula_cond


    def getbaysennetwork(self, df_data_num, nb_copula_atts):
            data_attributes_list = list(df_data_num.columns)
            bayesian_network = greedy_bayes(df_data_num[data_attributes_list], 3, 1 / 2, verbose=1)
            bayesnetwork_attribute_list = bayesian_network[0][1]

            for i in range(nb_copula_atts-1):
                bayesnetwork_attribute_list.append(bayesian_network[i][0])

            return bayesnetwork_attribute_list

    def lesscorrelatedattributes(self, df_data_num, nb_copula_atts):

            data_attributes_list = list(df_data_num.columns)
            corrMatrix = df_data_num.corr()

            corrMatrix = np.absolute(corrMatrix)
            indices = self.get_indices_of_k_smallest(corrMatrix.to_numpy())
            copula_attribute_list = []

            for ind in indices:
                att1 = data_attributes_list[ind[0]]
                att2 = data_attributes_list[ind[1]]
                # print( att1, att2)
                if not att1 in copula_attribute_list:
                    copula_attribute_list.append(att1)

                if not att2 in copula_attribute_list:
                    copula_attribute_list.append(att2)

                if len(copula_attribute_list) >= nb_copula_atts:
                    return copula_attribute_list

    def predict_conditional_attributes_list(self, df_data_num, data_attributes_list, copula_attribute_list):
            # Use Mutual Information Score to find wich attribute I'll use to predict conditional_attributes_list
            original_df = df_data_num[data_attributes_list].copy()

            conditional_attributes_list = list(set(data_attributes_list) - set(copula_attribute_list))

            # initialize the normalized mutual information matrix
            normalized_mutual_info_matrix = \
                np.zeros((len(conditional_attributes_list), len(copula_attribute_list)))

            mutual_info_matrix = \
                np.zeros((len(conditional_attributes_list), len(copula_attribute_list)))

            for attribute_topredict in conditional_attributes_list:
                for col_idx1 in range(len(copula_attribute_list)):
                    name1 = copula_attribute_list[col_idx1]

                    original_df[name1] = original_df[name1].map(str)

                    mutual_dico = mutual_info_score(original_df[name1].tolist(),
                                                         original_df[attribute_topredict].tolist())

                    mutual_info_matrix[0, col_idx1] = mutual_dico
                    l = stats.entropy(pd.Series(np.array(original_df[attribute_topredict].dropna())).value_counts())
                    normalized_mutual_dico = mutual_dico / l
                    normalized_mutual_info_matrix[
                        conditional_attributes_list.index(attribute_topredict), col_idx1] = normalized_mutual_dico

            normalized_mutual_info_matrix_dico = {}
            # show the values on the figure
            for col_idx1 in range(len(conditional_attributes_list)):
                for col_idx2 in range(len(copula_attribute_list)):
                    normalized_mutual_info_matrix_dico[
                        (conditional_attributes_list[col_idx1], copula_attribute_list[col_idx2])] = \
                        normalized_mutual_info_matrix[col_idx1, col_idx2]
                    this_value = normalized_mutual_info_matrix[col_idx1, col_idx2]

            normalized_mutual_info_matrix_dico_sorted = {k: v for k, v in
                                                         sorted(normalized_mutual_info_matrix_dico.items(),
                                                                key=lambda item: item[1], reverse=True)}
            avepredictioned = {}
            for attribute_topredict in conditional_attributes_list:
                for key, value in normalized_mutual_info_matrix_dico_sorted.items():
                    if attribute_topredict in key:
                        avepredictioned[attribute_topredict] = key[1]
                        break
            return avepredictioned

    def runbisectionalSearch(self, param):

        ress = self.copula.bisectionalSearch(threshold_arrays=self.threshold_arrays,
                                                        target_cov_value_matrix=param[0],
                                                        colM=param[1], colS=param[2], dic_col=self.Value_arrays)
                        # print('estim', ress)

        return ress

    
    def runtwoways(self, params):
        att = params[0]
        j = params[1]


        res = self.copula.getPearson_R(att, j, self.orig_dataset[self.att_name_list[att]].fillna(-1),
                                           self.orig_dataset[self.att_name_list[j]].fillna(-1), self.withNoise, self.scale,
                                           self.record_num, self.attribute_num, self.att_name_list)

        return   res


    def rundpc_onehot(self, data: DataFrame, withNoise: bool, epslimit: float, path_fnl: str, labels = ['dpc-bin'],
                      convert_bin =True, out_file = '', epssize=0, extendoutput=None, verbose=False, save=False):


        if out_file =='':
            timestr = time.strftime("%Y%m%d-%H%M%S")

            out_file = path_fnl + 'data_out_' + labels[0] + '_epsilon='+str(epslimit)+ '_' + timestr + '.csv'

        bins_col = []
        if convert_bin == True:
            for col in data.columns:
                values = dict(data[col].value_counts())
                bins_col += [col+'_'+ str(x) for x in values.keys()]
        else:
            bins_col = data.columns.tolist()


        if len(bins_col) > 160 :
            print ('Can t run dpc-bin. Number of attributes is too big (>= 150) '+ str(len(bins_col))  )
            return ''

        databin = pd.DataFrame(0, index=np.arange(len(data)), columns=bins_col)
        if convert_bin == True:
            if verbose == True:
                print ('Start convert data to binnary data')

            for id, row in tqdm(data.iterrows()):

                for col in data.columns:
                    val = col + '_'+ str(row[col])
                    databin.at[id, val] =1
        else:
            databin = data


        return self.rundpc(databin, withNoise, epslimit, path_fnl, ['dpc'], out_file, epssize , extendoutput , verbose, save)

    def rundpc_cond(self, data: DataFrame,  withNoise: bool, epslimit: int, epsilon_cond:int,
                    path_fnl: str, cop_att_list=[],  out_file=str,run_binnary=False,
                    privbayes_degree_max =3, extendoutput=None, verbose=False, save=False):

        self.dataset0 = data

        if out_file =='':
            timestr = time.strftime("%Y%m%d-%H%M%S")

            out_file = path_fnl + 'data_out_dpc_cond_epsilon='+str(epslimit)+ '_' + timestr + '.csv'

        self.copula = Copulafuncs()
        self.verbose = verbose
        self.withNoise = withNoise
        # Read Initial and  binned file

        df_oneway_orig, df_oneway_gen = [], []
        df_twoway_orig, df_twoway_gen = [], []
        df_copulas = []
        labels = ['dpc+cond']

        # Convert Dataset to integer
        if verbose == True:
            print('step 0 : Convert Dataset to numerical Dataset ')
        dataset_num, attr_dictionary = self.transform_dataset_numerical(self.dataset0)
        data_attributes_list = list(dataset_num.columns)




        # Before Running Copula, Check which attributes are less correlate
        #if verbose == True:
        #    print('step 1 : Get less correlation  attributes')
        #copula_attribute_list = self.lesscorrelatedattributes(dataset_num, privbayes_degree_max)


        if len(cop_att_list) ==0:
            if verbose == True:
                print('step 2 : Get greedy_bayes network')
            copula_attribute_list = self.getbaysennetwork(dataset_num, privbayes_degree_max)

        else:
            copula_attribute_list = cop_att_list

        if verbose == True:
            print('Run Copula with these attributes')



        df_final_f =  pd.DataFrame()



        df_oneway_orig, df_oneway_gen = [], []
        df_twoway_orig, df_twoway_gen =  [], []


        if run_binnary==True:
            if verbose == True:
                print('Start convert data to binnary data')
            databin = pd.DataFrame(0, index=np.arange(len(dataset_num[copula_attribute_list])), columns=copula_attribute_list)
            for id, row in tqdm(dataset_num[copula_attribute_list].iterrows()):

                for col in dataset_num[copula_attribute_list].columns:
                    val = col + '_' + str(row[col])
                    databin.at[id, val] = 1

            orig_dts = [dataset_num[copula_attribute_list].copy()]
        else:
            orig_dts = [dataset_num[copula_attribute_list].copy()]


        scale = 1 / epsilon_cond
        for orig_dt in orig_dts:
            df_copula = self.rundpc(data = orig_dt,withNoise=True, epslimit=epslimit, path_fnl=path_fnl,
                                         labels = ['dpc'], out_file=path_fnl+'skeleton.csv', epssize=None, extendoutput=extendoutput, verbose=verbose, save=save)

            if save ==False:
                os.remove(path_fnl+'skeleton.csv')
            # Now Time to run conditionnal algo with the other  attributes
            if verbose == True:
                ('#### Now Time to run conditionnal algo with the other  attributes')



            avepredictioned = self.predict_conditional_attributes_list(dataset_num, data_attributes_list,
                                                                      copula_attribute_list)

            df_final = self.conditional_algo(dataset_num, df_copula, dico_predictioned=avepredictioned,
                                            scale=scale,out_file=out_file )

            for key in df_final.columns:
                df_final_f[key] = [attr_dictionary[key][(int(x))] for x in df_final[key]]





            df_final_f.to_csv( out_file, index=False)

            '''df_oneway_orig.append(calculate_oneWay(self.dataset0, self.att_name_list))
            df_oneway_gen.append(calculate_oneWay(df_final_f[label], self.att_name_list))

            df_twoway_orig.append(calculate_twoWay(self.dataset0, self.att_name_list))
            df_twoway_gen.append(calculate_twoWay(df_final_f[label], self.att_name_list))

            df_oneway_compares = calculate_print(df_oneway_orig, df_oneway_gen, 'CDF of One Way', labels=labels,
                                                 figname=path_fnl + 'final_'+label + '-oneway', printgraph=False,
                                                 savedata=path_fnl +'final_'+ label + '-oneway_gen')
            df_twoway_compares = calculate_print(df_twoway_orig, df_twoway_gen, 'CDF of Two Way', labels=labels,
                                             figname=path_fnl + 'final_'+label + '-twoway', printgraph=False,
                                             savedata=path_fnl + 'final_'+label + '-twoway_gen')
            '''

        return df_final_f


    def rundpc_cond2(self, data: DataFrame,  withNoise: bool, epslimit: int,
                    path_fnl: str, epssize=None,  privbayes = False,
                    copula_attribute_list = [], extendoutput=None, verbose=False):
        self.dataset0 = data
        self.copula = Copulafuncs()
        self.verbose = verbose
        self.withNoise = withNoise
        # Read Initial and  binned file

        df_oneway_orig, df_oneway_gen = [], []
        df_twoway_orig, df_twoway_gen = [], []
        df_copulas = []
        labels = ['dpc+cond']

        # Convert Dataset to integer
        if verbose == True:
            print('step 0 : Convert Dataset to numerical Dataset ')
        dataset_num, attr_dictionary = self.transform_dataset_numerical(self.dataset0)
        data_attributes_list = list(dataset_num.columns)






        df_final_f = {'skeleton': pd.DataFrame(),
                      }

        cop_att_list = {'skeleton':copula_attribute_list}

        df_oneway_orig, df_oneway_gen = [], []
        df_twoway_orig, df_twoway_gen =  [], []



        if privbayes == True:

            orig_dts = {'skeleton': dataset_num[copula_attribute_list].copy(),

                        }
        else:

            orig_dts = {'skeleton': dataset_num[copula_attribute_list].copy()}

        scale = 1 / epslimit
        for label in orig_dts.keys():




            orig_dt =  orig_dts[label]



            df_copulas = self.rundpc(data = orig_dt,withNoise=True, epslimit=epslimit, path_fnl=path_fnl,
                                                    labels = [label], epssize=None, extendoutput=extendoutput, verbose=verbose)

            # Now Time to run conditionnal algo with the other  attributes
            print('#### Now Time to run conditionnal algo with the other  attributes')



            avepredictioned = self.predict_conditional_attributes_list(dataset_num, data_attributes_list,
                                                                      cop_att_list[label])
            df_final = self.conditional_algo(dataset_num, df_copulas[0], dico_predictioned=avepredictioned,
                                            scale=scale)

            for key in df_final.columns:
                df_final_f[label][key] = [attr_dictionary[key][(int(x))] for x in df_final[key]]




            output_filename = path_fnl + 'out'

            df_final_f[label].to_csv( output_filename + '_dpcopula_with' + label + '.csv', index=False)

            df_oneway_orig.append(calculate_oneWay(self.dataset0, self.att_name_list))
            df_oneway_gen.append(calculate_oneWay(df_final_f[label], self.att_name_list))

            df_twoway_orig.append(calculate_twoWay(self.dataset0, self.att_name_list))
            df_twoway_gen.append(calculate_twoWay(df_final_f[label], self.att_name_list))

            df_oneway_compares = calculate_print(df_oneway_orig, df_oneway_gen, 'CDF of One Way', labels=labels,
                                                 figname=path_fnl + 'final_'+label + '-oneway', printgraph=False,
                                                 savedata=path_fnl +'final_'+ label + '-oneway_gen')
            df_twoway_compares = calculate_print(df_twoway_orig, df_twoway_gen, 'CDF of Two Way', labels=labels,
                                             figname=path_fnl + 'final_'+label + '-twoway', printgraph=False,
                                             savedata=path_fnl + 'final_'+label + '-twoway_gen')

        return df_final_f


