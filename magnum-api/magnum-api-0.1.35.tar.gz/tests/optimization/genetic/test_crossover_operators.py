import numpy as np

from magnumapi.optimization.design_variable import DesignVariableFactory
from magnumapi.optimization.genetic.crossover_operators import CrossOverOperator
from tests.resource_files import create_resources_path
from magnumapi.optimization.design_variable.Individual import Individual

csv_global_file_path = create_resources_path(
    'resources/optimization/mock_programmable/design_variables_programmable_geometry.csv')
dv_gens = DesignVariableFactory.init_genetic_design_variables_with_csv(csv_global_file_path)


def test_crossover_without_change():
    np.random.seed(0)
    # arrange
    # # first individual
    individual1 = Individual(dv_gens)
    individual1.generate_random_genes()

    # # second individual
    individual2 = Individual(dv_gens)
    individual2.generate_random_genes()

    crossover_operator = CrossOverOperator(r_cross=0)

    # act
    child1, child2 = crossover_operator.crossover(individual1, individual2)

    # assert
    assert child1.assemble_chromosome() == individual1.assemble_chromosome()
    assert child2.assemble_chromosome() == individual2.assemble_chromosome()


def test_crossover_with_change():
    # arrange
    # # first individual
    individual1 = Individual(dv_gens)
    individual1.generate_random_genes()

    # # second individual
    individual2 = Individual(dv_gens)
    individual2.generate_random_genes()

    crossover_operator = CrossOverOperator(r_cross=1)

    # act
    child1, child2 = crossover_operator.crossover(individual1, individual2)

    # assert
    assert child1.assemble_chromosome() != individual1.assemble_chromosome()
    assert child2.assemble_chromosome() != individual2.assemble_chromosome()

