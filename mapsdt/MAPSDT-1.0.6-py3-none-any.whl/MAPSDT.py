import os
import pickle
import time
from viztree import viztree
from preProcessing import preprocessingData
import MAPSC45 as mc


def MAPSDT(df, target_names:list, tree=None, split_portion=0.3, max_depth=5, Genetic_Progrmmaing=False, init_size=50, max_generations=50,
           save=True,
           visualizing=True):
    config = {'data': df,
              'target_names': target_names,
              'split_portion': split_portion,
              'max_depth': max_depth,
              'Genetic Programming': Genetic_Progrmmaing,
              'init_size': init_size,
              'max_generations': max_generations,
              'save': save, 'Visualizing': visualizing,
              'tree': tree
              }
    total_time = time.time()
    start_time = time.time()
    df = config['data']
    split_portion = config['split_portion']
    target_names = config['target_names']
    config['train_data'], config['test_data'], config['attribute'] = preprocessingData(config)

    if not os.path.exists('tree'):
        os.makedirs('tree')
    if not os.path.exists('test-output'):
        os.makedirs('test-output')

    if config['tree'] is None:
        tree = mc.createTree(config)

    else:
        with open(config['tree'], 'rb') as file:
            tree = pickle.load(file)
        print("=================================")
        print('Creating time : ', time.time() - start_time)
    tree.test_data = config['test_data']

    # ===========================================================

    tree.fit()
    visualizing = config['Visualizing']
    if visualizing:
        viztree(tree.leaf, tree.root, config)

    accuracy, precision, recall, f1_score = mc.evaluate(tree.test_data)
    print('\nAccuracy : ', accuracy * 100, '%')
    print('Precision : ', precision * 100, '%')
    print('Recall : ', recall * 100, '%')
    print('F1 Score : ', f1_score * 100, '%')
    print('\n\nTotal time : ', time.time() - total_time)
