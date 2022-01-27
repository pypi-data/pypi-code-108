import click
from pathlib import Path
from configuration import DATASETS, DATASETS_CONFIGS
import sys, os
sys.path.append(os.getcwd() + '/dpcopula/')
from dpcgeneration import DPCopula
import pandas as pd



@click.command()
@click.option('--dataset', type=str, default='adult', prompt='input data',
              help='Input dataset: adult, mnist, eudm, transport')
@click.option('--model', type=str, default='dpc-cond', prompt='dpc or dpc-cond',
              help='dpc or dpc-onehot or dpc-cond.')
@click.option('--epsilon', type=float, default=1.0, prompt='epsilon',
              help='epsilon')
@click.option('--output', type=str, default='out/' , #prompt='output',
              help='output repository', required=False)
@click.option('--privbayes-degree-max', type=int, default=3, #prompt='privbayes degree max',
              help='privbayes degree max', required=False)
@click.option('--extendoutput', type=int, default=None, #prompt='extend output',
              help='extend output', required=False)
def run_generation(dataset, model, epsilon=1, output='./out/',privbayes_degree_max=3,extendoutput=None):


    dataset_config = DATASETS_CONFIGS[dataset]
    #Create output repository if not exists
    output =  output.strip()
    if output[-1] != '/':
        output += '/'
    Path(output).mkdir(parents=True, exist_ok=True)


    click.echo('Start dpc generation ')
    try:
        df = pd.read_csv(DATASETS[dataset])
    except FileNotFoundError:
        print('Error File does not exist')

    dataset_attributes = dataset_config['attributes']

    copula = DPCopula()

    withNoise = True
    if epsilon == 0 :
        withNoise = False

    if model == 'dpc':
        df_res = copula.rundpc( data=df[dataset_attributes], withNoise=withNoise, epslimit=epsilon,  path_fnl=output,
                                                     labels = ['dpc'], epssize=None,  extendoutput=extendoutput, verbose=True)
    elif model == 'dpc-cond':
        df_res = copula.rundpc_cond(data=df[dataset_attributes], withNoise=True,
                                                        epslimit=epsilon, path_fnl=output,epssize=None,
                                                        privbayes =True,
                                                        privbayes_degree_max=3, extendoutput=extendoutput, verbose=True)
    elif model == 'dpc-cond2':
        copula_attribute_list = dataset_config['cop_attributes']
        df_res = copula.rundpc_cond2(data=df[dataset_attributes], withNoise=True,
                                    epslimit=epsilon, path_fnl=output, epssize=None,
                                    privbayes=True,
                                    copula_attribute_list=copula_attribute_list, extendoutput=extendoutput, verbose=True)
    elif model == 'dpc-onehot':

        # convert dataset to onehot encoding dataset

        df_res = copula.rundpc_onehot(data=df[dataset_attributes], withNoise=True,
                                                        epslimit=epsilon, path_fnl=output,epssize=None,convert_bin=False,
                                                         extendoutput=extendoutput, verbose=True)

    else:
        print('Error Model does not exist')


''
if __name__ == '__main__':

    #get input parameters
    run_generation()