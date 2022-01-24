import numpy as np

from magnumapi.optimization.design_variable import DesignVariableFactory
from magnumapi.optimization.genetic.mutation_operators import MutationOperator
from tests.resource_files import create_resources_path
from magnumapi.optimization.design_variable.Individual import Individual

csv_global_file_path = create_resources_path(
    'resources/optimization/mock_programmable/design_variables_programmable_geometry.csv')
dv_gens = DesignVariableFactory.init_genetic_design_variables_with_csv(csv_global_file_path)


def test_mutate_without_change():
    np.random.seed(0)
    # arrange
    # # first individual
    individual = Individual(dv_gens)
    individual.generate_random_genes()

    mutation_operator = MutationOperator(r_mut=0)

    # act
    mutated_individual = mutation_operator.mutate(individual)

    # assert
    assert mutated_individual.assemble_chromosome() == individual.assemble_chromosome()


def test_mutate_with_change():
    np.random.seed(0)
    # arrange
    # # first individual
    individual = Individual(dv_gens)
    individual.generate_random_genes()

    mutation_operator = MutationOperator(r_mut=1)

    # act
    mutated_individual = mutation_operator.mutate(individual)

    # assert
    assert mutated_individual.assemble_chromosome() != individual.assemble_chromosome()
