
from pathlib import Path
from configuration import DATASETS, DATASETS_CONFIGS
import sys, os
sys.path.append(os.getcwd() + '/dpcopula/')
from dpcgeneration import DPCopula
import pandas as pd



def run_generation(dataset, model, dp_epsilon=1, output='./out/',privbayes_degree_max=3,extendoutput=None):


    dataset_config = DATASETS_CONFIGS[dataset]
    #Create output repository if not exists
    output =  output.strip()
    if output[-1] != '/':
        output += '/'
    Path(output).mkdir(parents=True, exist_ok=True)


    print('Start dpc generation ')
    try:
        df = pd.read_csv(DATASETS[dataset])
    except FileNotFoundError:
        print('Error File does not exist')

    dataset_attributes = dataset_config['attributes']

    copula = DPCopula()

    withNoise = True
    if dp_epsilon == 0 :
        withNoise = False

    if model == 'dpc':
        df_res = copula.rundpc( data=df[dataset_attributes], withNoise=withNoise, epslimit=dp_epsilon,  path_fnl=output,
                                                     labels = ['dpc'], epssize=None,  extendoutput=extendoutput, verbose=True)
    elif model == 'dpc-cond':
        df_res = copula.rundpc_cond(data=df[dataset_attributes], withNoise=True,
                                                        epslimit=dp_epsilon, path_fnl=output,epssize=None,
                                                        privbayes =True,
                                                        privbayes_degree_max=3, extendoutput=extendoutput, verbose=True)
    elif model == 'dpc-cond2':
        copula_attribute_list = dataset_config['cop_attributes']
        df_res = copula.rundpc_cond2(data=df[dataset_attributes], withNoise=True,
                                    epslimit=dp_epsilon, path_fnl=output, epssize=None,
                                    privbayes=True,
                                    copula_attribute_list=copula_attribute_list, extendoutput=extendoutput, verbose=True)

    else:
        print('Error Model does not exist')


''
if __name__ == '__main__':

    #get input parameters
    run_generation(dataset='adult', model='dpc-cond')