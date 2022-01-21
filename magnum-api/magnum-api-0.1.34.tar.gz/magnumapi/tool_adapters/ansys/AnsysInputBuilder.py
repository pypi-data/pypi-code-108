from typing import List
import os

from magnumapi.geometry.Geometry import HomogenizedCosThetaGeometry
from magnumapi.geometry.SlottedGeometry import SlottedHomogenizedCosThetaGeometry
import magnumapi.commons.text_file as text_file


class AnsysInputBuilder:
    """ An AnsysInputBuilder class with methods used to create an ANSYS coil geometry input

    """

    @classmethod
    def update_input_template(cls, template_path: str, index: int, input_dir: str, input_file: str):
        # read template file
        template_content = text_file.read(template_path)

        # update template file with index
        template_content = template_content.format(index)

        # write updated template file to output directory with index
        output_path = os.path.join(input_dir, input_file % index)
        text_file.write(output_path, template_content)

    @classmethod
    def write_geometry_input_file(cls, homo_geometry: HomogenizedCosThetaGeometry, model_path: str) -> None:
        """ Class method writing a geometry parameters for ANSYS input file from a homogenized cos-theta geometry

        :param homo_geometry: a homogenized cos-theta geometry
        :param model_path: a path to model input
        """
        output_text = cls.generate_ansys_input_text(homo_geometry)
        text_file.writelines(model_path, output_text)

    @classmethod
    def write_geometry_input_file_sm_ct(cls, homo_geometry, model_path):
        output_text = cls.generate_ansys_input_text_sm_ct(homo_geometry)
        text_file.writelines(model_path, output_text)

    @staticmethod
    def generate_ansys_input_text(homo_geometry: HomogenizedCosThetaGeometry) -> List[str]:
        """ Method generating an ANSYS coil geometry input text from a homogenized cos-theta geometry

        :param homo_geometry: homogenized cos-theta geometry
        :param n_layers: number of layers
        :param blocks_per_layer: number of blocks per layer
        :return: a list of model inputs
        """
        n_layers = homo_geometry.get_number_of_layers()
        blocks_per_layer = homo_geometry.get_number_of_blocks_per_layer()
        model_inputs = []
        model_inputs.append('! Example Input File\n')
        model_inputs.append('! -------------------\n')
        model_inputs.append('! - Standard\n')
        model_inputs.append('/UNITS,SI\n')
        model_inputs.append('pi = acos(-1)\n')
        model_inputs.append('*afun,deg		 ! Specifies the units for angular functions in parameter expressions\n')
        model_inputs.append('tref,293\n')
        model_inputs.append('! -------------------\n')
        model_inputs.append('! Set-up arrays\n')
        model_inputs.append('! *dim,V_Field,array,1,1\n')
        model_inputs.append('! *dim,V_Nlay,array,1,1\n')
        model_inputs.append('! *dim,V_blocks,array,1,1\n')
        model_inputs.append('! *dim,V_current,array,1,1\n')
        model_inputs.append('! *dim,V_rad,array,1,2\n')
        model_inputs.append('! *dim,V_turns,array,1,1\n')
        model_inputs.append('! *dim,V_corners,array,2,4\n')
        model_inputs.append('\n')
        model_inputs.append('! General\n')

        model_inputs.append('Nlay = %d\n' % n_layers)
        model_inputs.append('\n')

        radius_inner_prev = None
        index_layer = -1
        index_block = 0
        for block in homo_geometry.blocks:
            if radius_inner_prev != block.block_def.radius_inner:
                index_block = 0
                index_layer += 1
                model_inputs.append('! Layer\n')
                model_inputs.append('Nb%d = %d\n' % (index_layer + 1, blocks_per_layer[index_layer]))
                model_inputs.append('current%d = %f\n' % (index_layer + 1, block.block_def.current))
                model_inputs.append('r%d1 = %fe-3\n' % (index_layer + 1, block.block_def.radius_inner))
                model_inputs.append('r%d2 = %fe-3\n' % (index_layer + 1, block.block_def.radius_outer))

            model_inputs.append('! Block\n')
            model_inputs.append('Nc%d%d = %d\n' % (index_layer + 1, index_block + 1, block.block_def.nco))
            model_inputs.append('\n')
            model_inputs.append('! Save angles\n')
            model_inputs.append('t%d%d_1 = %.4f\n' % (index_layer + 1, index_block + 1, block.block_def.phi_0))
            model_inputs.append('t%d%d_2 = %.4f\n' % (index_layer + 1, index_block + 1, block.block_def.phi_1))
            model_inputs.append('t%d%d_3 = %.4f\n' % (index_layer + 1, index_block + 1, block.block_def.phi_2))
            model_inputs.append('t%d%d_4 = %.4f\n' % (index_layer + 1, index_block + 1, block.block_def.phi_3))

            if index_block + 1 == blocks_per_layer[index_layer]:
                # Fixes the first 2 angles of the 1st block to be 0 / assumes mid-plane shim thickness = 0
                model_inputs.append('\n')
                model_inputs.append('t%d1_1 = 0\n' % (index_layer + 1))
                model_inputs.append('t%d1_2 = 0\n' % (index_layer + 1))
                model_inputs.append('\n')

            index_block += 1
            radius_inner_prev = block.block_def.radius_inner

        model_inputs.append('! Names\n')
        model_inputs.append('r1 = r11\n')
        model_inputs.append('r%d = r%d2\n' % (n_layers + 1, n_layers))
        model_inputs.append('rout = r%d\n' % (n_layers + 1))
        model_inputs.append('Nlayers = Nlay\n')

        model_inputs.append('\n')
        model_inputs.append('! -------------------------------------\n')
        model_inputs.append('! - Geometry parameters\n')
        model_inputs.append('! ---- Filler\n')
        model_inputs.append('*set, fillerth, 5e-3\n')

        model_inputs.append('\n')
        model_inputs.append('! ---- Yoke\n')
        model_inputs.append('*set,yoketh,260e-3\n')

        model_inputs.append('\n')
        model_inputs.append('! Update geometry\n')
        model_inputs.append('*set, rin_yoke, rout + fillerth\n')
        model_inputs.append('*set, rout_yoke, rin_yoke + yoketh\n')

        model_inputs.append('\n')
        model_inputs.append('! -------------------------------------\n')
        model_inputs.append('! Interlay Contact - Filler is Nlayers+1\n')
        model_inputs.append('! Glue = 5 , Sliding = 0\n')
        model_inputs.append('ilay_12 = 5\n')
        model_inputs.append('ilay_23 = 0\n')
        model_inputs.append('ilay_34 = 5\n')
        model_inputs.append('ilay_45 = 0\n')
        model_inputs.append('! -------------------------------------\n')
        model_inputs.append('! Mesh Parameters\n')
        model_inputs.append('mpar = 1\n')
        model_inputs.append('\n')
        model_inputs.append('mesh_azim_size = mpar*2e-3    ! Coil Azimuthal\n')
        model_inputs.append('mesh_radial_size = mpar*2e-3    ! Coil Radial\n')
        model_inputs.append('\n')
        model_inputs.append('msize_aperture = mpar*1e-3\n')
        model_inputs.append('msize_filler = mpar*3e-3\n')
        model_inputs.append('msize_yoke = mpar*10e-3\n')
        model_inputs.append('\n')
        model_inputs.append('!!!!!!!!!!!!!!!!!!!!!!!\n')
        model_inputs.append('! Friction Parameters !\n')
        model_inputs.append('!!!!!!!!!!!!!!!!!!!!!!!\n')
        model_inputs.append('mu_single = 0.0\n')
        model_inputs.append('mu_g10_coil = mu_single\n')
        model_inputs.append('mu_ti_coil = mu_single\n')
        model_inputs.append('mu_ti_g10 = mu_single\n')
        model_inputs.append('mu_g10_ss = mu_single\n')
        model_inputs.append('mu_alu_iron = mu_single\n')
        model_inputs.append('mu_ss_ss = mu_single\n')
        model_inputs.append('mu_ss_ti = mu_single\n')
        model_inputs.append('mu_ss_iron = mu_single\n')

        return model_inputs

    @staticmethod
    def generate_ansys_input_text_sm_ct(geometry: SlottedHomogenizedCosThetaGeometry):
        output_text = []
        output_text.append('! Number of layers')
        n_layers = geometry.get_number_of_layers()
        output_text.append('*set,n_lay,%d' % n_layers)

        output_text.append('! vector with r-coo of layers inner and outer (columns)')
        output_text.append('*dim,n_lay_r_vec,array,%d,2' % n_layers)

        radius_outer_prev = None
        for index_layer, layer_def in enumerate(geometry.layer_defs):
            index_in_blocks = geometry.get_index_in_blocks_for_layer_block_index(layer_def.blocks[0])
            block = geometry.blocks[index_in_blocks]
            if index_layer == 0:
                inner_rad = geometry.r_aperture
            else:
                inner_rad = radius_outer_prev

            output_text.append('*set,n_lay_r_vec(%d,1),%.2fe-3' % (index_layer + 1, inner_rad))
            output_text.append('*set,n_lay_r_vec(%d,2),%.2fe-3' % (index_layer + 1, block.block_def.radius_outer))

            radius_outer_prev = block.block_def.radius_outer

        output_text.append('! vector with number of blocks per layer')
        output_text.append('*dim,n_lay_block_vec,array,%d,1' % n_layers)
        for index_layer, layer_def in enumerate(geometry.layer_defs):
            output_text.append('*set,n_lay_block_vec(%d,1),%d'% (index_layer + 1, len(layer_def.blocks)))

        output_text.append('! total number of blocks')
        output_text.append('*set,n_tot_block,%d' % len(geometry.blocks))

        output_text.append('! vector with current (columns) of blocks')
        output_text.append('*dim,n_block_curr_vec,array,%d,1' % len(geometry.blocks))
        output_text.append('*dim,n_block_nco_vec,array,%d,1' % len(geometry.blocks))
        for index_block, block in enumerate(geometry.blocks):
            output_text.append('*set,n_block_curr_vec(%d,1),%.2f' % (index_block + 1, block.block_def.current))

        output_text.append('! vector with r-coo of four corners (columns) of blocks (cyl coo)')
        output_text.append('*dim,n_block_r_vec,array,%d,4' % len(geometry.blocks))
        for index_block, block in enumerate(geometry.blocks):
            output_text.append('*set,n_block_r_vec(%d,1),%.2fe-3' % (index_block + 1, block.block_def.radius_inner))
            output_text.append('*set,n_block_r_vec(%d,2),%.2fe-3' % (index_block + 1, block.block_def.radius_inner))
            output_text.append('*set,n_block_r_vec(%d,3),%.2fe-3' % (index_block + 1, block.block_def.radius_outer))
            output_text.append('*set,n_block_r_vec(%d,4),%.2fe-3' % (index_block + 1, block.block_def.radius_outer))

        output_text.append('! vector with a-coo of four corners (columns) of blocks (cyl coo)')
        output_text.append('*dim,n_block_a_vec,array,%d,4' % len(geometry.blocks))
        for index_block, block in enumerate(geometry.blocks):
            output_text.append('*set,n_block_a_vec(%d,1),%.2f' % (index_block + 1, block.block_def.phi_3))
            output_text.append('*set,n_block_a_vec(%d,2),%.2f' % (index_block + 1, block.block_def.phi_0))
            output_text.append('*set,n_block_a_vec(%d,3),%.2f' % (index_block + 1, block.block_def.phi_1))
            output_text.append('*set,n_block_a_vec(%d,4),%.2f' % (index_block + 1, block.block_def.phi_2))

        output_text.append('! vector with number of conductors (columns) of blocks')
        output_text.append('*dim,n_block_cond_vec,array,%d,1' % len(geometry.blocks))
        for index_block, block in enumerate(geometry.blocks):
            output_text.append('*set,n_block_cond_vec(%d,1),%d' % (index_block + 1, block.block_def.nco))

        output_text.append('! vector with spar thickness (column) of layers')
        output_text.append('*dim,n_lay_spar_th_vec,array,%d,1' % n_layers)

        for layer_index, layer_def in enumerate(geometry.layer_defs):
            output_text.append('*set,n_lay_spar_th_vec(%d,1),%.2fe-3' % (layer_index + 1, layer_def.spar_thickness))

        output_text.append('*set,inter_lay_ins,0.5e-3')
        output_text.append('*set,backbone_x,12.0e-3')
        output_text.append('*set,backbone_y,6.0e-3')
        output_text.append('*set,backbone_r,4.0e-3')
        output_text.append('*set,backbone_r2,4.5e-3')

        return output_text
