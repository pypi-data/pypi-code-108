from abc import abstractmethod, ABC
from copy import deepcopy

import numpy as np

from magnumapi.geometry.Geometry import Geometry
from magnumapi.geometry.GeometryChange import GeometryChange
from magnumapi.optimization.design_variable.Individual import Individual


class ModelTranslatorFactory:
    # ToDo: Rename to ModelCreator after removing old classes
    @classmethod
    def build(cls, model_creation_type, geometry):
        if model_creation_type == 'default':
            return DefaultModelTranslator(geometry)
        elif model_creation_type == 'targeted':
            return TargetedModelTranslator(geometry)
        elif model_creation_type == 'programmable':
            return ProgrammableModelTranslator(geometry)
        else:
            raise AttributeError('Model creation type %s not supported!' % model_creation_type)


class ModelTranslator(ABC):
    def __init__(self, geometry):
        self._geometry = geometry

    @property
    def geometry(self):
        return deepcopy(self._geometry)

    @abstractmethod
    def generate_random_individual(self, individual: Individual) -> Individual:
        raise NotImplementedError()

    @abstractmethod
    def update_geometry(self, individual: Individual) -> Geometry:
        raise NotImplementedError()


class DefaultModelTranslator(ModelTranslator):

    def generate_random_individual(self, individual: Individual) -> Individual:
        individual.generate_random_genes()

        return individual

    def update_geometry(self, individual: Individual) -> Geometry:
        """ Method updating model parameters given as ROXIE block definitions. Typically, it is a relative block
        definition.

        :param individual: a dictionary with keys containing a parameter name and block separated with a colon
        :return: an updated list of block definitions
        """
        geometry = self.geometry
        # update global variables
        geometry = GeometryChange.update_global_variables(geometry, individual)

        # update layer variables
        geometry = GeometryChange.update_layer_variables(geometry, individual)

        # update block variables
        geometry = GeometryChange.update_block_variables(geometry, individual)

        # update multiblock variables
        geometry = GeometryChange.update_multiblock_variables(geometry, individual)

        # Remove empty blocks
        return GeometryChange.update_layer_indexing(geometry)


class TargetedModelTranslator(DefaultModelTranslator):

    def update_geometry(self, individual: Individual) -> Geometry:
        geometry_rel = self.geometry

        # update phi_r
        geometry_rel = GeometryChange.update_phi_r(geometry_rel, individual)

        # update nco_r
        geometry_rel = GeometryChange.update_nco_r(geometry_rel, individual)

        # extract absolute geometry to correct radiality
        geometry_abs = geometry_rel.to_abs_geometry()

        # correct block radiality
        geometry_abs = GeometryChange.calculate_radial_alpha(geometry_abs)

        # extract relative geometry
        geometry_rel = geometry_abs.to_rel_geometry()

        # update alpha_rad_r
        return GeometryChange.update_alpha_radial(geometry_rel, individual)


class ProgrammableModelTranslator(ModelTranslator):
    def generate_random_individual(self, individual: Individual) -> Individual:

        # initialize global variables
        for dv in individual.get_global_dvs():
            dv.generate_random_gene()

        # initialize layer variables
        layer_dvs = individual.get_layer_dvs()
        for st_dv in [layer_dv for layer_dv in layer_dvs if layer_dv.variable == 'spar_thickness']:
            st_dv.generate_random_gene()

        # initialize number of conductors turn variables
        n_layers = max([layer_dv.layer for layer_dv in layer_dvs if layer_dv.variable == 'nbl_layer'])
        for layer_index in range(1, n_layers + 1):
            # randomly select spar thickness
            st_dv = [layer_dv for layer_dv in layer_dvs
                     if layer_dv.variable == 'spar_thickness' and layer_dv.layer == layer_index][0]
            st_dv.generate_random_gene()

            # randomly select nco
            nco_layer_dv = [layer_dv for layer_dv in layer_dvs
                            if layer_dv.variable == 'nco_layer' and layer_dv.layer == layer_index][0]
            nbl_layer_dv = [layer_dv for layer_dv in layer_dvs
                            if layer_dv.variable == 'nbl_layer' and layer_dv.layer == layer_index][0]
            nco_layer_dv.generate_random_gene()
            nbl_layer_dv.generate_random_gene()
            partitioned_blocks = ProgrammableModelTranslator._generate_number_random_partition(nco_layer_dv.value,
                                                                                               nbl_layer_dv.value)
            partitioned_blocks_sorted = sorted(partitioned_blocks, reverse=True)
            # convert partition blocks into bits
            nco_layer_dvs = [block_dv for block_dv in individual.get_block_dvs()
                             if block_dv.variable == 'nco' and block_dv.layer == layer_index]
            for block_index, partitioned_block in enumerate(partitioned_blocks_sorted, start=1):
                nco_layer_dv = [layer_dv for layer_dv in nco_layer_dvs if layer_dv.block == block_index][0]
                nco_layer_dv.gene = nco_layer_dv.convert_int_to_gene(partitioned_block, nco_layer_dv.bits)

        # initiate remaining block and multiblock variables except nco
        for block_dv in [block_dv for block_dv in individual.get_block_dvs() if block_dv.variable != 'nco']:
            block_dv.generate_random_gene()

        for mblock_dv in [mblock_dv for mblock_dv in individual.get_multiblock_dvs() if mblock_dv.variable != 'nco']:
            mblock_dv.generate_random_gene()

        return individual

    @staticmethod
    def _generate_number_random_partition(number, n_slices):
        random_in_range = [np.random.randint(1, number) for _ in range(n_slices - 1)]
        random_in_range = [0] + sorted(random_in_range) + [number]
        partition = [t - s for s, t in zip(random_in_range, random_in_range[1:])]
        return sorted(partition, reverse=True)

    def update_geometry(self, individual: Individual) -> Geometry:
        geometry = self.geometry
        # update global variables
        geometry = GeometryChange.update_global_variables(geometry, individual)

        # update layer variables
        geometry = GeometryChange.update_layer_variables(geometry, individual)

        # update nco varying blocks
        geometry_rel = GeometryChange.update_nco_varying_blocks(geometry, individual)

        # update phi_r
        geometry_rel = GeometryChange.update_phi_r(geometry_rel, individual)

        # limit minimum phi_r
        geometry_rel = GeometryChange.limit_minimum_phi_r(geometry_rel, min_length=1)

        # calculate radiality
        try:
            geometry_abs = geometry_rel.to_abs_geometry()
        except AttributeError as attrib_error:
            print('Inconsistent geometry - there is a block with radial side not intercepting a layer radius')
            raise attrib_error

        geometry_abs = GeometryChange.calculate_radial_alpha(geometry_abs)

        # update alpha_phi_rad
        geometry_rel = geometry_abs.to_rel_geometry()
        geometry_rel = GeometryChange.update_alpha_radial(geometry_rel, individual)

        return geometry_rel
