import pytest

import numpy as np

from magnumapi.optimization.design_variable.GeneticDesignVariable import GeneticDesignVariable
from magnumapi.optimization.design_variable.GeneticDesignVariable import GeneticLayerDesignVariable

global_dv = GeneticDesignVariable(variable='R_EE', xl=0, xu=10, variable_type='int', bits=6)
layer_dv = GeneticLayerDesignVariable(variable='current', xl=100.10, xu=130, variable_type='float', layer=1, bits=6)


@pytest.mark.parametrize('design_variable,expected_output', zip([global_dv, layer_dv],
                                                                [[0, 0, 0, 0, 1, 1], [0, 1, 1, 0, 1, 1]]))
def test_generate_random_gene(design_variable, expected_output):
    np.random.seed(0)
    design_variable.generate_random_gene()
    assert design_variable.gene == expected_output


# use int for both as it is a private method
@pytest.mark.parametrize('design_variable,gene,expected_output', zip([global_dv, global_dv],
                                                                     [[1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 1, 1]],
                                                                     [[0, 0, 1, 0, 1, 0], [0, 0, 0, 0, 1, 1]]))
def test__correct_int_gene_overflow(design_variable, gene, expected_output):
    assert design_variable._correct_int_gene_overflow(gene) == expected_output


@pytest.mark.parametrize('design_variable,expected_output', zip([global_dv, layer_dv], [3, 112.7140625]))
def test_value_getter(design_variable, expected_output):
    np.random.seed(0)
    design_variable.generate_random_gene()
    assert design_variable.value == expected_output


@pytest.mark.parametrize('design_variable,gene,expected_output', zip([global_dv, layer_dv],
                                                                     [[1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 1, 1]],
                                                                     [[0, 0, 1, 0, 1, 0], [0, 0, 0, 0, 1, 1]]))
def test_gene_setter(design_variable, gene, expected_output):
    design_variable.gene = gene
    assert design_variable.gene == expected_output


def test_convert_gene_to_int():
    # arrange
    gene = [1, 0, 1, 0]

    # act
    int_value = GeneticDesignVariable.convert_gene_to_int(gene)

    # assert
    assert int_value == 10


def test_convert_int_to_gene():
    # arrange
    int_value = 10

    # act
    gene = GeneticDesignVariable.convert_int_to_gene(int_value, 4)

    # assert
    assert gene == [1, 0, 1, 0]


def test_convert_int_to_gene_five_bits():
    # arrange
    int_value = 10

    # act
    gene = GeneticDesignVariable.convert_int_to_gene(int_value, 5)

    # assert
    assert [0, 1, 0, 1, 0] == gene
