import numpy as np

from magnumapi.optimization.design_variable import DesignVariableFactory
from magnumapi.optimization.genetic.selection_operators import SelectionOperator
from tests.resource_files import create_resources_path
from magnumapi.optimization.design_variable.Individual import Individual

csv_global_file_path = create_resources_path(
    'resources/optimization/mock_programmable/design_variables_programmable_geometry.csv')
dv_gens = DesignVariableFactory.init_genetic_design_variables_with_csv(csv_global_file_path)


def test_select():
    np.random.seed(0)
    # arrange
    # # first individual
    individual1 = Individual(dv_gens)
    individual1.score = 20

    # # second individual
    individual2 = Individual(dv_gens)
    individual2.score = 10

    selection_operator = SelectionOperator(k_selection=2)

    # act
    individual_selected = selection_operator.select([individual1, individual2])

    # assert
    assert id(individual_selected) == id(individual2)
