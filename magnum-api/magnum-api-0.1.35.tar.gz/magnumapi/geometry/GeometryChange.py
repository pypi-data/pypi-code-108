import math
from copy import deepcopy

from magnumapi.geometry.Geometry import Geometry
from magnumapi.geometry.SlottedGeometry import SlottedRelativeCosThetaGeometry
from magnumapi.geometry.blocks.Block import Block
from magnumapi.geometry.blocks.CosThetaBlock import AbsoluteCosThetaBlock
from magnumapi.geometry.primitives.Line import Line
from magnumapi.optimization.design_variable.Individual import Individual


class GeometryChange:

    @staticmethod
    def update_global_variables(geometry, individual: Individual) -> Geometry:
        geometry = deepcopy(geometry)
        for global_dv in individual.get_global_dvs():
            if hasattr(geometry, global_dv.variable):
                setattr(geometry, global_dv.variable, global_dv.value)

        return geometry

    @classmethod
    def update_layer_variables(cls, geometry, individual: Individual) -> Geometry:
        geometry = deepcopy(geometry)
        for layer_dv in individual.get_layer_dvs():
            layer_def = geometry.layer_defs[layer_dv.layer - 1]
            if hasattr(layer_def, layer_dv.variable):
                setattr(layer_def, layer_dv.variable, layer_dv.value)
        return geometry

    @classmethod
    def update_block_variables(cls, geometry, individual: Individual) -> Geometry:
        geometry = deepcopy(geometry)
        for block_dv in individual.get_block_dvs():
            cls.update_block_variable(geometry, block_dv, block_dv.block)
        return geometry

    @classmethod
    def update_block_variable(cls, geometry, dv, block):
        block_index = geometry.layer_defs[dv.layer - 1].blocks[block - 1]
        index_in_blocks = geometry.get_index_in_blocks_for_layer_block_index(block_index)
        block_def = geometry.blocks[index_in_blocks].block_def
        if hasattr(block_def, dv.variable):
            setattr(block_def, dv.variable, dv.value)

    @classmethod
    def update_multiblock_variables(cls, geometry, individual: Individual) -> Geometry:
        geometry = deepcopy(geometry)
        for multiblock_dv in individual.get_multiblock_dvs():
            for index in range(multiblock_dv.block_start, multiblock_dv.block_end):
                cls.update_block_variable(geometry, multiblock_dv, index)
        return geometry

    @classmethod
    def limit_minimum_phi_r(cls, geometry, min_length=1) -> Geometry:
        geometry = deepcopy(geometry)
        for layer_def in geometry.layer_defs:
            for blocks_index, block_index in enumerate(layer_def.blocks):
                if blocks_index > 0:
                    index_in_blocks = geometry.get_index_in_blocks_for_layer_block_index(block_index)
                    radius = geometry.blocks[index_in_blocks].block_def.radius
                    phi_r = geometry.blocks[index_in_blocks].block_def.phi_r
                    if radius > 0:
                        geometry.blocks[index_in_blocks].block_def.phi_r = max(phi_r, math.degrees(min_length / radius))

        return geometry

    @classmethod
    def update_nco_varying_blocks(cls,
                                  geometry,
                                  individual: Individual) -> SlottedRelativeCosThetaGeometry:
        geometry = deepcopy(geometry)

        nco_dvs = [dv for dv in individual.get_block_dvs() if dv.variable == 'nco']
        block_index = 1
        blocks = []
        # for each layer
        for layer_index, layer_def in enumerate(geometry.layer_defs, start=1):
            # find a reference block - first block in layer_def
            block_layer_index_ref = layer_def.blocks[0]
            block_index_ref = geometry.get_index_in_blocks_for_layer_block_index(block_layer_index_ref)
            block_def_ref = geometry.blocks[block_index_ref]

            # find all ncos that belong to that layer and are non-zero
            # update a copy of the reference block as long as there are non-zero blocks - todo: sort the keys
            layer_blocks = []

            nco_layer_dvs = [dv for dv in nco_dvs if (dv.value > 0) and (dv.layer == layer_index)]
            for nco_layer_dv in nco_layer_dvs:
                block_def_ref = deepcopy(block_def_ref)
                block_def_ref.block_def.nco = nco_layer_dv.value
                block_def_ref.block_def.no = block_index
                layer_blocks.append(block_index)
                block_index += 1
                blocks.append(block_def_ref)

            layer_def.blocks = layer_blocks

        return SlottedRelativeCosThetaGeometry(r_aperture=geometry.r_aperture,
                                               blocks=blocks,
                                               layer_defs=geometry.layer_defs)

    @classmethod
    def update_alpha_radial(cls, geometry, individual: Individual):
        geometry = deepcopy(geometry)
        alpha_r_dvs = [block_dv for block_dv in individual.get_block_dvs() if block_dv.variable == 'alpha_rad_r']
        for alpha_r_dv in alpha_r_dvs:

            # block index
            if alpha_r_dv.block <= len(geometry.layer_defs[alpha_r_dv.layer - 1].blocks):
                no_block = geometry.layer_defs[alpha_r_dv.layer - 1].blocks[alpha_r_dv.block - 1]
                block_index = geometry.get_index_in_blocks_for_layer_block_index(no_block)
                geometry.blocks[block_index].block_def.phi_r += alpha_r_dv.value

        return geometry

    @classmethod
    def update_phi_r(cls, geometry: Geometry, individual: Individual) -> Geometry:
        geometry = deepcopy(geometry)
        phi_r_dvs = [block_dv for block_dv in individual.get_block_dvs() if block_dv.variable == 'phi_r']
        for phi_r_dv in phi_r_dvs:

            # block index
            if phi_r_dv.block <= len(geometry.layer_defs[phi_r_dv.layer - 1].blocks):
                no_block = geometry.layer_defs[phi_r_dv.layer - 1].blocks[phi_r_dv.block - 1]
                block_index = geometry.get_index_in_blocks_for_layer_block_index(no_block)
                geometry.blocks[block_index].block_def.phi_r = phi_r_dv.value

        return geometry

    @classmethod
    def calculate_radial_alpha(cls, geometry: Geometry) -> Geometry:
        """ Method correcting radiality of cos-theta blocks in a geometry.

        """
        # check whether areas were initialize before performing radiality correction
        is_any_area_initialized = any([area for block in geometry.blocks for area in block.areas])

        # Set alpha equal to phi for all blocks except the mid-plane
        geometry = cls._set_alpha_equal_to_phi(geometry)

        # Build blocks and calculate turn positions
        geometry.build_blocks()

        # Calculate alpha corrections
        alpha_corrections = cls._calculate_alpha_corrections(geometry)

        # Correct alpha
        geometry = cls._apply_alpha_correction(geometry, alpha_corrections)

        # Return to the external context of the geometry before entering
        if is_any_area_initialized:
            geometry.build_blocks()
        else:
            geometry.empty_block_areas()

        return geometry

    @staticmethod
    def _set_alpha_equal_to_phi(geometry):
        for layer_def in geometry.layer_defs:
            for block_index in layer_def.blocks[1:]:
                index_in_blocks = geometry.get_index_in_blocks_for_layer_block_index(block_index)
                block = geometry.blocks[index_in_blocks]
                if isinstance(block, AbsoluteCosThetaBlock):
                    block.block_def.alpha = block.block_def.phi
        return geometry

    @classmethod
    def _calculate_alpha_corrections(cls, geometry):
        alpha_corrections = []
        for layer_def in geometry.layer_defs:
            for index, block_index in enumerate(layer_def.blocks):
                index_in_blocks = geometry.get_index_in_blocks_for_layer_block_index(block_index)
                block = geometry.blocks[index_in_blocks]
                # Calculate correction for all blocks except the mid-plane one
                if index and isinstance(block, AbsoluteCosThetaBlock):
                    alpha_correction = cls.compute_radial_alpha(block)
                else:
                    alpha_correction = 0.0
                alpha_corrections.append(alpha_correction)

        return alpha_corrections

    @staticmethod
    def compute_radial_alpha(block: Block) -> float:
        """ Static method calculating a radiality correction angle for a cos-theta block. It is based on an assumption
        that block alpha angle (inclination angle) is equal to phi angle (positioning angle).

        :param block: a block instance with initialized areas
        :return: an alpha angle correction factor
        """
        if not block.areas:
            raise IndexError('The list of areas is empty, please build block first with build_block() method.')

        l_down = block.areas[0].get_line(0)
        p_down = l_down.p1
        l_up = block.areas[-1].get_line(2)
        p_up = l_up.p2

        angle_ref = (p_up.get_phi() + p_down.get_phi()) / 2

        alpha_down = angle_ref - Line.calculate_relative_alpha_angle(l_down)
        alpha_up = Line.calculate_relative_alpha_angle(l_up) - angle_ref

        return (alpha_down - alpha_up) / 2

    @staticmethod
    def _apply_alpha_correction(geometry, alpha_corrections):
        for index, block in enumerate(geometry.blocks):
            if isinstance(block, AbsoluteCosThetaBlock):
                block.block_def.alpha += alpha_corrections[index]

        return geometry

    @classmethod
    def update_layer_indexing(cls, geometry) -> Geometry:
        """ Method updating block and layer indexing in case a block has no turns.
        The algorithm works as follows:
        1. Take old block indices and map them to None
        2. Keep blocks with at least one conductor
        3. Update the numbering of blocks; update mapping from old to new indices from point 1
        4. Update block indices in each layer definition with map; if a new index is None, then it means that a block
        was removed

        :return: method returns a dictionary from old to new block indices
        """
        # # initialize map
        geometry = deepcopy(geometry)
        old_to_new_index = {block.block_def.no: None for block in geometry.blocks}

        # # remove the missing blocks
        # # keep only block indices that are not missing
        blocks = []
        for index, block in enumerate(geometry.blocks):
            if block.block_def.nco > 0:
                blocks.append(block)
                old_to_new_index[block.block_def.no] = block.block_def.no

        geometry.blocks = blocks

        # # update layers definition
        for layer_def in geometry.layer_defs:
            layer_def.blocks = [old_to_new_index[block] for block in layer_def.blocks]
            layer_def.blocks = [block for block in layer_def.blocks if block is not None]

        return geometry

    @classmethod
    def update_nco_r(cls, geometry, individual: Individual):
        block_dvs = individual.get_block_dvs()
        nco_r_dvs = [block_dv for block_dv in block_dvs if block_dv.variable == 'nco_r']
        geometry = deepcopy(geometry)

        for nco_r_dv in nco_r_dvs:
            no_block = geometry.layer_defs[nco_r_dv.layer - 1].blocks[nco_r_dv.block - 1]
            block_index = geometry.get_index_in_blocks_for_layer_block_index(no_block)
            block_def_curr = geometry.blocks[block_index].block_def
            block_def_next = geometry.blocks[block_index + 1].block_def
            if nco_r_dv.value >= 0:
                block_def_curr.nco += min(nco_r_dv.value, block_def_next.nco)
                block_def_next.nco -= min(nco_r_dv.value, block_def_next.nco)
            else:
                block_def_curr.nco -= min(abs(nco_r_dv.value), block_def_curr.nco)
                block_def_next.nco += min(abs(nco_r_dv.value), block_def_next.nco)

        geometry = GeometryChange.update_layer_indexing(geometry)
        return geometry
