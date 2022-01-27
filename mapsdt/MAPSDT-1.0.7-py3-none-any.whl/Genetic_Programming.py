import numpy as np
from data_load import Chromosome
import data_load as data_load
import copy
import Training
import MAPSC45 as mc
from data_load import DT
import pickle


def GPFE(continuousAttr, attribute, config):
    train_data, test_data = config['train_data'], config['test_data']
    def init_population(_init_size, _continuousAttr):
        _chromosome_list, gene, operation = [], [], ['+', '-', '*', '/']
        num_of_gene_in_chromosome = 10
        selectOP = np.random.choice(operation, _init_size * num_of_gene_in_chromosome)
        m = len(selectOP) * 2
        operation.append(' ')
        for i in range(m):
            op = np.random.choice(operation, 1)
            if op in ('+', '-', '*', '/'):
                if op == '-':
                    random_choice = np.random.choice(_continuousAttr, 2, replace=False)
                elif op == '/':
                    random_choice = np.random.choice(_continuousAttr, 2, replace=False)
                    if len(list(filter(lambda x:x.__getattribute__(random_choice[1].name) == 0, train_data))) + len(list(filter(lambda x:x.__getattribute__(random_choice[1].name) == 0, test_data))) > 0:
                        op = np.random.choice(['+', '-', '*'], 1)
                else:
                    random_choice = np.random.choice(_continuousAttr, 2, replace=True)
                attr1, attr2 = random_choice[0].name, random_choice[1].name
                gene.append(str('(obj.' + attr1 + op[0] + 'obj.' + attr2 + ')'))
            else:
                attr1 = np.random.choice(_continuousAttr, 1)[0].name
                gene.append('obj.' + attr1)

        for _chromosome, _index in enumerate(range(int(len(selectOP)/num_of_gene_in_chromosome))):
            temp_list = []
            for i in range(num_of_gene_in_chromosome):
                _chromosome = Chromosome()
                if selectOP[_index] == '/':
                    if len(list(filter(lambda obj:eval(gene[1]) == 0, train_data))) + len(list(filter(lambda obj:eval(gene[1]) == 0, test_data))) > 0:
                        selectOP[_index] = np.random.choice(['+', '-', '*'], 1)[0]
                _chromosome.gene1, _chromosome.gene2, _chromosome.operation, _chromosome.generation = gene[0], gene[1], selectOP[_index], 1
                _chromosome.combine()
                temp_list.append(_chromosome)
                gene.remove(gene[0])
                gene.remove(gene[0])
            _chromosome_list.append(temp_list)
        forest = []
        return _chromosome_list, forest

    def fitness(_chromosome_list, forest, _data, _attribute, test_data, config):
        for _chromosome in _chromosome_list:
            new_attribute_list = copy.deepcopy(_attribute)
            data = copy.deepcopy(_data)
            for i in _chromosome:
                new_attribute = data_load.Attribute()
                new_attribute.name = i.chromosome
                new_attribute.type = 'Continuous'
                new_attribute.new = True
                new_attribute_list.append(new_attribute)
                for obj in data:
                    setattr(obj, new_attribute.name, eval(new_attribute.name))
            config_new = copy.deepcopy(config)
            config_new['train_data'] = data
            config_new['attribute'] = new_attribute_list
            config_new['Genetic Programming'] = False
            config_new['save'] = False

            # ==========================================

            rule_decision, leaf_list, root = Training.buildDecisionTree(config_new)
            tree = DT()
            tree.leaf = leaf_list
            tree.root = root
            tree.rule_decision = rule_decision
            tree.test_data = test_data
            tree.fit()
            accuracy, precision, recall, f1_score = mc.evaluate(tree.test_data)
            tree.accuracy = accuracy
            tree.chromosome = _chromosome
            forest.append(tree)
        return _chromosome_list, forest

    def crossover_mutate(_chromosome_list, _max_generation, forest, _data, test_data, config):
        generation, operation = 2, ['+', '-', '*', ' ', '/']
        num_of_gene_in_chromosome = 10
        def tournament_selection(population):
            parents = np.random.choice(population, num_of_gene_in_chromosome)
            parents = sorted(parents, key=lambda x: x.accuracy, reverse=True)
            return parents[0].chromosome

        while generation <= _max_generation:
            parent = [tournament_selection(forest) for i in range(int(config['init_size'] * 0.25))]
            parent.extend(list(map(lambda x: x.chromosome, np.random.choice(forest, config['init_size'] - int(config['init_size'] * 0.25)))))
            new_parent = []
            for i in range(int(len(parent)/2)):
                np.random.shuffle(parent)
                child1 = parent[i*2][:int(num_of_gene_in_chromosome/2)] + parent[i*2+1][int(num_of_gene_in_chromosome/2):]
                child2 = parent[i*2+1][:int(num_of_gene_in_chromosome/2)] + parent[i*2][int(num_of_gene_in_chromosome/2):]

                mutate_probability = np.random.rand(1)[0]
                if mutate_probability > 0.95:
                    _operation = ['+', '-', '*', '/']
                    selectOP = np.random.choice(_operation, 1)
                    gene = []
                    for i in range(2):
                        op = np.random.choice(operation, 1)
                        if op in ('+', '-', '*', '/'):
                            if op == '-':
                                random_choice = np.random.choice(continuousAttr, 2, replace=False)
                            elif op == '/':
                                random_choice = np.random.choice(continuousAttr, 2, replace=False)
                                if len(list(filter(lambda x: x.__getattribute__(random_choice[1].name) == 0,
                                                   train_data))) + len(list(
                                        filter(lambda x: x.__getattribute__(random_choice[1].name) == 0,
                                               test_data))) > 0:
                                    op = np.random.choice(['+', '-', '*'], 1)
                            else:
                                random_choice = np.random.choice(continuousAttr, 2, replace=True)
                            attr1, attr2 = random_choice[0].name, random_choice[1].name
                            gene.append(str('(obj.' + attr1 + op[0] + 'obj.' + attr2 + ')'))
                        else:
                            attr1 = np.random.choice(continuousAttr, 1)[0].name
                            gene.append('obj.' + attr1)

                    _chromosome = Chromosome()
                    if selectOP[0] == '/':
                        if len(list(filter(lambda obj: eval(gene[1]) == 0, train_data))) + len(
                                list(filter(lambda obj: eval(gene[1]) == 0, test_data))) > 0:
                            selectOP[0] = np.random.choice(['+', '-', '*'], 1)[0]
                    _chromosome.gene1, _chromosome.gene2, _chromosome.operation, _chromosome.generation = gene[0], gene[1], selectOP[0], 1
                    _chromosome.combine()
                    child2[-1] = _chromosome

                new_parent.append(child1)
                new_parent.append(child2)
            new_forest = []
            _chromosome_list, forest = fitness(new_parent, new_forest, _data, attribute, test_data, config)
            print(generation, ' Generation completed...')
            best_tree = sorted(forest, key=lambda x: x.accuracy, reverse=True)[0]
            print(best_tree.accuracy * 100)
            if config['save']:
                with open('tree/' + 'Depth' + str(config['max_depth']) + '_' + str(generation) + 'generation' + '.p',
                          'wb') as file:  # james.p 파일을 바이너리 쓰기 모드(wb)로 열기
                    pickle.dump(best_tree, file)
                f = open('test-output/' + 'Depth' + str(config['max_depth']) + '_' + str(generation) + 'generation' + '.txt',
                         'w')
                for i in best_tree.rule_decision:
                    rule = i[0] + '=' + str(config['target_names'][int(i[1])] + '\n')
                    f.write(rule)
            generation += 1

        return _chromosome_list, forest

    init_size = config['init_size']
    chromosome_list, forest = init_population(init_size, continuousAttr)
    chromosome_list, forest = fitness(chromosome_list, forest, train_data, attribute, test_data, config)
    print('\nInitial population completed...')
    best_tree = sorted(forest, key=lambda x: x.accuracy, reverse=True)[0]
    print(best_tree.accuracy * 100)
    if config['save']:
        with open('tree/' + 'Depth' + str(config['max_depth']) + '_' + str(1) + 'generation' + '.p', 'wb') as file:
            pickle.dump(best_tree, file)
        f = open('test-output/' + 'Depth' + str(config['max_depth']) + '_' + str(1) + 'generation' + '.txt', 'w')
        for i in best_tree.rule_decision:
            rule = i[0] + '=' + str(config['target_names'][int(i[1])] + '\n')
            f.write(rule)
    max_generation = config['max_generations']
    chromosome_list, forest = crossover_mutate(chromosome_list, max_generation, forest, train_data, test_data, config)
    return chromosome_list, forest
