r"""
Module for visualizing the tree for a whole sps-calculation
"""
from spinterface.sps_results.stage_visualizer.ivisstage import IVisStage
from pathlib import Path
from typing import Union
from treelib import Node, Tree
import ete3 as et
import pandas as pd
from decimal import Decimal
import math as mt


class CVisTree(IVisStage):
    r"""
    Visualizes all the stages of a sps-calculation in a tree.
    """

    def __init__(self, strategy: int, info_file_disp: Union[Path, str], info_file_esc: Union[Path, str],
                 info_file_conv: Union[Path, str]) -> None:
        r"""
        Initialize the visualization stage
        Args:
            strategy(int): for each stage a certain strategy was applied. The visualization also depends on these strategies.
            info_file_conv(Path,str): information about the convergence stage
            info_file_disp(Path,str): information about the dipslace stage
            info_file_esc(Path,str): infomration about the escape stage
        """
        self.strategy = strategy
        self.info_file_disp = info_file_disp
        self.info_file_esc = info_file_esc
        self.info_file_conv = info_file_conv
        self.parent_directory = self.info_file_conv.parent
        self.image_scale_initial = 500
        self.image_scale_disp = 500
        self.image_scale_esc = 500
        self.image_scale_conv = 500
        self.branchlength = 0.5

    def set_image_scales(self, initial: float = 500, disp: float = 500, esc: float = 500, conv: float = 500):
        r"""
        Sets the sizes of the images for the different stages
        """
        self.image_scale_conv = conv
        self.image_scale_disp = disp
        self.image_scale_initial = initial
        self.image_scale_esc = esc

    @property
    def stage(self) -> str:
        r"""
        Returns:
            the name of the stage
        """
        return 'Visualize Tree'

    def _stagestrategytext(self) -> str:
        r"""
        Returns:
            the strategy of the stage
        """
        if self.strategy in [1]:
            return 'Simple Visualization with treelib'
        elif self.strategy in [2]:
            return 'Advanced Visualization with ete3'
        else:
            raise ValueError('Visualization strategy for tree not yet coded.')

    def __call__(self) -> None:
        r"""
        Calls the certain visualization.
        """
        if self.strategy in [1]:
            self._create_tree_treelib()
        if self.strategy in [2]:
            self._create_tree_ete()

    def _create_newick_string(self) -> str:
        r"""
        Creates a newick string describing the topology and the nodes of the tree. Also included are basic information
        as the branch distances.
        """
        df_disp = pd.read_csv(self.info_file_disp, sep=r'\s+')
        df_esc = pd.read_csv(self.info_file_esc, sep=r'\s+')
        df_conv = pd.read_csv(self.info_file_conv, sep=r'\s+')
        str = ''
        for index, key in enumerate(df_disp['DISPKEY']):
            str = str + '('
            current_esc_keys = df_esc[df_esc['DISPKEY'] == key]['ESCKEY'].to_numpy()
            current_esc_folders = df_esc[df_esc['DISPKEY'] == key]['folder'].to_numpy()
            esckeys_reescape = []
            for index2, esckey in enumerate(current_esc_keys):
                splitted = esckey.split('DIR')
                if len(splitted[1]) > 1:
                    esckeys_reescape.append(esckey)
            for index2, esckey in enumerate(current_esc_keys):
                if esckey in esckeys_reescape:
                    continue
                path_to_esc_folder = current_esc_folders[index2]
                df_mf_calc = pd.read_csv(self.parent_directory / Path(path_to_esc_folder) / 'info_mf.dat', r'\s+')
                eig1 = abs(df_mf_calc['eig001'].to_numpy()[-1] * 1000)  # display in meV
                df_conv_filtered = df_conv[df_conv['DISPKEY'] == key]
                try:
                    sp_or_convex = df_conv_filtered[df_conv_filtered['ESCKEY'] == esckey]['sp_or_convex'].to_numpy()[0]
                    folder_search = df_conv_filtered[df_conv_filtered['ESCKEY'] == esckey]['folder'].to_numpy()[0]
                    df_mmf = pd.read_csv(self.parent_directory / Path(folder_search) / 'info_mmf.dat', sep=r'\s+')
                    eig1_conv = abs(df_mmf['eig001'].to_numpy()[-1] * 1000)  # in meV
                    if sp_or_convex == 'sp':
                        #str = str + f'({sp_or_convex}:{eig1_conv}){esckey}:{abs(eig1)},'
                        str = str + f'({sp_or_convex}:{self.branchlength}){esckey}:{self.branchlength},'
                    else:
                        # look for re-escapes
                        current_reesc_keys = []
                        current_reesc_keys_attempts = []
                        for reesc_key in esckeys_reescape:
                            if reesc_key.startswith(esckey):
                                current_reesc_keys.append(reesc_key)
                                current_reesc_keys_attempts.append(int(reesc_key[-2:]))
                        if not current_reesc_keys:
                            # list is empty no successful re-escape attempt for this key
                            str = str + f'({sp_or_convex}:{eig1_conv}){esckey}:{abs(eig1)},'
                        else:
                            # check ordering of keys
                            current_reesc_keys = [reesc_key for _, reesc_key in
                                                  sorted(zip(current_reesc_keys_attempts, current_reesc_keys))]
                            # go through re-escape keys
                            reesc_str = '(' * (2 * (len(current_reesc_keys) - 1) + 1)
                            for reesc_key in reversed(current_reesc_keys):
                                folder = self.parent_directory / Path(
                                    df_esc[df_esc['ESCKEY'] == reesc_key]['folder'].to_numpy()[0])
                                df_esca = pd.read_csv(folder / 'info_esca.dat', sep=r'\s+')
                                eig_esca1 = abs(df_esca['eig001'].to_numpy()[-1] * 1000)
                                # look for corresponding search calculation
                                sp_or_convex = \
                                    df_conv_filtered[df_conv_filtered['ESCKEY'] == reesc_key][
                                        'sp_or_convex'].to_numpy()[0]
                                reesc_str = reesc_str + f'{sp_or_convex}){reesc_key}:{1.0})'
                            reesc_str = reesc_str[:-1]  # remove last bracket
                            #str = str + f'(({reesc_str}){sp_or_convex}:{eig1_conv}){esckey}:{abs(eig1)},'
                            str = str + f'(({reesc_str}){sp_or_convex}:{self.branchlength}){esckey}:{self.branchlength},'
                except IndexError:
                    #str = str + f'(NC:{0.0}){esckey}:{abs(eig1)},'
                    str = str + f'(NC:{0.0}){esckey}:{self.branchlength},'
            # remove last comma
            str = str[:-1]
            str = str + ')'
            str = str + f'{key},'
        return str[:-1]

    def _design_node_initial_state(self, tree: et.Tree) -> None:
        r"""
        Add faces to root node (initial state)
        """
        # maximum number of eigenvalues created by spinaker
        max_eval = 9
        root_node = tree.search_nodes(name='initial')[0]
        img_face = et.ImgFace("SpinSTMi.png", width=self.image_scale_initial, height=self.image_scale_initial)
        root_node.add_face(img_face, column=0, position='branch-right')
        rootnodestyle = et.NodeStyle()
        rootnodestyle['bgcolor'] = "Moccasin"
        root_node.set_style(rootnodestyle)
        if (self.parent_directory / 'info_sps_eigenvalues.dat').is_file():
            df_sps_eval = pd.read_csv(self.parent_directory / 'info_sps_eigenvalues.dat', sep=r'\s+')
            if 'initialstate' in df_sps_eval['Stage'].values:
                for i in range(1, max_eval + 1):
                    eval = float(
                        str(df_sps_eval[df_sps_eval['Stage'] == 'initialstate'][f'eig{i}'].to_numpy()[0]).replace('d',
                                                                                                                  'e'))
                    str_scientific = '{:.2e}'.format(eval)
                    tf = et.TextFace(f'eig{i}=' + str_scientific, fsize=20)
                    root_node.add_face(tf, column=0, position='branch-bottom')

    def _design_node_displaced_state(self, node: et.Tree, df_disp: pd.DataFrame, index: int, key: str) -> None:
        r"""
        Add faces to displace node
        """
        max_eval = 9
        disp_spinfile = self.parent_directory / df_disp['spin_file'].to_numpy()[index]
        disp_spinfile = disp_spinfile.as_posix().replace('.dat', '.png')
        img_face = et.ImgFace(disp_spinfile, width=self.image_scale_disp, height=self.image_scale_disp)
        node.add_face(img_face, column=0)
        dispnodestyle = et.NodeStyle()
        dispnodestyle['bgcolor'] = "LightSteelBlue"
        node.set_style(dispnodestyle)
        if (self.parent_directory / 'info_sps_eigenvalues.dat').is_file():
            df_sps_eval = pd.read_csv(self.parent_directory / 'info_sps_eigenvalues.dat', sep=r'\s+')
            if key in df_sps_eval['Stage'].values:
                for i in range(1, max_eval + 1):
                    eval = float(
                        str(df_sps_eval[df_sps_eval['Stage'] == key][f'eig{i}'].to_numpy()[0]).replace('d', 'e'))
                    str_scientific = '{:.2e}'.format(eval)
                    tf = et.TextFace(f'eig{i}=' + str_scientific, fsize=20)
                    node.add_face(tf, column=0, position='branch-bottom')

    def _design_node_escaped_state(self, node: et.Tree, df_esc: pd.DataFrame) -> None:
        r"""
        Designs and add faces to nodes of the escape stage
        """
        current_esc_folder = df_esc[df_esc['ESCKEY'] == node.name]['folder'].to_numpy()[0]
        current_esc_spinfile = df_esc[df_esc['ESCKEY'] == node.name]['spin_file'].to_numpy()[0]
        path_to_spin_file = self.parent_directory / Path(current_esc_spinfile)
        esc_spinfile = path_to_spin_file.as_posix().replace('.dat', '.png')
        img_face = et.ImgFace(esc_spinfile, width=self.image_scale_esc, height=self.image_scale_esc)
        tf = et.TextFace('Escaped config.', fsize=25)
        tf.inner_border.width = 1
        tf.inner_border.type = 0
        img_face.inner_border.width = 1
        img_face.inner_border.type = 0
        node.add_face(tf, column=1, position='branch-top')
        node.add_face(img_face, column=1, position='branch-top')
        escnodestyle=et.NodeStyle()
        escnodestyle['bgcolor']="Khaki"
        node.set_style(escnodestyle)
        # Test if an eigenvector file for the beginning of mmf exists
        esc_evec0file = esc_spinfile.replace('spin_mf_end', 'evec_mmf_0')
        if Path(esc_evec0file).is_file():
            tf = et.TextFace('Lowest eigenmode', fsize=25)
            tf.inner_border.width = 1
            tf.inner_border.type = 0
            node.add_face(tf, column=1, position='branch-bottom')
            img_face = et.ImgFace(esc_evec0file, width=self.image_scale_esc, height=self.image_scale_esc)
            img_face.inner_border.width = 1
            img_face.inner_border.type = 0
            node.add_face(img_face, column=1, position='branch-bottom')

        path_to_mf_file = self.parent_directory / Path(current_esc_folder) / 'info_mf.dat'
        df_mf = pd.read_csv(path_to_mf_file, sep=r'\s+')
        eig1 = df_mf['eig001'].to_numpy()[-1]
        eig2 = df_mf['eig002'].to_numpy()[-1]
        node.add_feature('eig2', eig2)
        node.add_feature('eig1', eig1)
        scientific_str = '{:.2e}'.format(eig1)
        tf1 = et.faces.TextFace(f"eig1:{scientific_str}", fsize=20)
        scientific_str = '{:.2e}'.format(eig1)
        tf2 = et.faces.TextFace(f"eig2:{scientific_str}", fsize=20)
        node.add_face(tf1, column=0, position='branch-bottom')
        node.add_face(tf2, column=0, position='branch-bottom')

    def _design_node_converged_state(self, node: et.Tree, df_conv: pd.DataFrame) -> None:
        r"""
        Designs and add faces to convergence stage
        """
        if not (df_conv['folder'].to_numpy().size == 0):
            folder_search = df_conv['folder'].to_numpy()[0]
            df_mmf = pd.read_csv(self.parent_directory / Path(folder_search) / 'info_mmf.dat', sep=r'\s+')
            eig1 = df_mmf['eig001'].to_numpy()[-1]
            eig2 = df_mmf['eig002'].to_numpy()[-1]
            scientific_str = '{:.2e}'.format(eig1)
            tf1 = et.faces.TextFace(f"eig1:{scientific_str}", fsize=20)
            scientific_str = '{:.2e}'.format(eig2)
            tf2 = et.faces.TextFace(f"eig2:{scientific_str}", fsize=20)
            node.add_face(tf1, column=0, position='branch-top')
            node.add_face(tf2, column=0, position='branch-top')
            energy_sp = df_mmf['energy'].to_numpy()[-1]
            steps_sp = df_mmf['steps'].to_numpy()[-1]
            scientific_str = '{:.2e}'.format(energy_sp)
            tf1 = et.faces.TextFace(f"energy={scientific_str} eV", fsize=20)
            tf2 = et.faces.TextFace(f"steps={steps_sp}", fsize=20)
            node.add_face(tf1, column=0, position='branch-bottom')
            node.add_face(tf2, column=0, position='branch-bottom')
            if not (df_conv['spin_file'].to_numpy().size == 0):
                spinfile_search = df_conv['spin_file'].to_numpy()[0]
                path_to_spin_file = self.parent_directory / Path(spinfile_search)
                conv_spinfile = path_to_spin_file.as_posix().replace('.dat', '.png')
                img_face = et.ImgFace(conv_spinfile, width=self.image_scale_conv, height=self.image_scale_conv)
                node.add_face(img_face, column=1, position='branch-bottom')
                convnodestyle = et.NodeStyle()
                if df_conv['sp_or_convex'].to_numpy()[0] == 'sp':
                    node.add_face(et.faces.TextFace('Unstable Mode', fsize=25), column=1, position='branch-top')
                    convnodestyle['bgcolor']="DarkSeaGreen"
                else:
                    node.add_face(et.faces.TextFace('Lowest Mode', fsize=25), column=1, position='branch-top')
                    convnodestyle['bgcolor'] ="LightSalmon"
                node.set_style(convnodestyle)
                conv_evecfile = conv_spinfile.replace('spin', 'evec')
                img_face = et.ImgFace(conv_evecfile, width=self.image_scale_conv, height=self.image_scale_conv)
                node.add_face(img_face, column=1, position='branch-top')

    def _design_node_reescape_esc_state(self, node: et.Tree, df_esc: pd.DataFrame) -> None:
        r"""
            Designs and add faces to nodes of the escape stage
        """
        current_esc_folder = df_esc[df_esc['ESCKEY'] == node.name]['folder'].to_numpy()[0]
        current_esc_spinfile = df_esc[df_esc['ESCKEY'] == node.name]['spin_file'].to_numpy()[0]
        path_to_spin_file = self.parent_directory / Path(current_esc_spinfile)
        esc_spinfile = path_to_spin_file.as_posix().replace('.dat', '.png')
        reescape_escnodestyle = et.NodeStyle()
        reescape_escnodestyle['bgcolor']="Khaki"
        node.set_style(reescape_escnodestyle)
        if Path(esc_spinfile).is_file():
            img_face = et.ImgFace(esc_spinfile, width=self.image_scale_esc, height=self.image_scale_esc)
            tf = et.TextFace('Escaped config.', fsize=25)
            tf.inner_border.width = 1
            tf.inner_border.type = 0
            img_face.inner_border.width = 1
            img_face.inner_border.type = 0
            node.add_face(tf, column=1, position='branch-top')
            node.add_face(img_face, column=1, position='branch-top')
        # Test if an eigenvector file for the beginning of mmf exists
        path_to_evec_file = self.parent_directory / Path(current_esc_spinfile).parent / 'evec_mmf_0.png'
        esc_evec0file = path_to_evec_file.as_posix()
        if Path(esc_evec0file).is_file():
            tf = et.TextFace('Lowest eigenmode', fsize=25)
            tf.inner_border.width = 1
            tf.inner_border.type = 0
            node.add_face(tf, column=1, position='branch-bottom')
            img_face = et.ImgFace(esc_evec0file, width=self.image_scale_esc, height=self.image_scale_esc)
            img_face.inner_border.width = 1
            img_face.inner_border.type = 0
            node.add_face(img_face, column=1, position='branch-bottom')

        path_to_esca_file = self.parent_directory / Path(current_esc_folder) / 'info_esca.dat'
        df_mf = pd.read_csv(path_to_esca_file, sep=r'\s+')
        eig1 = df_mf['eig001'].to_numpy()[-1]
        eig2 = df_mf['eig002'].to_numpy()[-1]
        node.add_feature('eig2', eig2)
        node.add_feature('eig1', eig1)
        scientific_str = '{:.2e}'.format(eig1)
        tf1 = et.faces.TextFace(f"eig1:{scientific_str}", fsize=20)
        scientific_str = '{:.2e}'.format(eig1)
        tf2 = et.faces.TextFace(f"eig2:{scientific_str}", fsize=20)
        node.add_face(tf1, column=0, position='branch-bottom')
        node.add_face(tf2, column=0, position='branch-bottom')

    def _design_node_reescape_conv_state(self, node: et.Tree, df_conv: pd.DataFrame) -> None:
        r"""
        Designs and adds faces to nodes of the re-escape stage in the convergence phases
        """
        if not (df_conv['folder'].to_numpy().size == 0):
            folder_search = df_conv['folder'].to_numpy()[0]
            df_mmf = pd.read_csv(self.parent_directory / Path(folder_search) / 'info_mmf.dat', sep=r'\s+')
            eig1 = df_mmf['eig001'].to_numpy()[-1]
            eig2 = df_mmf['eig002'].to_numpy()[-1]
            scientific_str = '{:.2e}'.format(eig1)
            tf1 = et.faces.TextFace(f"eig1:{scientific_str}", fsize=20)
            scientific_str = '{:.2e}'.format(eig2)
            tf2 = et.faces.TextFace(f"eig2:{scientific_str}", fsize=20)
            node.add_face(tf1, column=0, position='branch-top')
            node.add_face(tf2, column=0, position='branch-top')
            energy_sp = df_mmf['energy'].to_numpy()[-1]
            steps_sp = df_mmf['steps'].to_numpy()[-1]
            scientific_str = '{:.2e}'.format(energy_sp)
            tf1 = et.faces.TextFace(f"energy={scientific_str} eV", fsize=20)
            tf2 = et.faces.TextFace(f"steps={steps_sp}", fsize=20)
            node.add_face(tf1, column=0, position='branch-bottom')
            node.add_face(tf2, column=0, position='branch-bottom')
            if not (df_conv['spin_file'].to_numpy().size == 0):
                spinfile_search = df_conv['spin_file'].to_numpy()[0]
                path_to_spin_file = self.parent_directory / Path(spinfile_search)
                conv_spinfile = path_to_spin_file.as_posix().replace('.dat', '.png')
                reescape_convnodestyle = et.NodeStyle()
                if df_conv['sp_or_convex'].to_numpy()[0] == 'sp':
                    reescape_convnodestyle['bgcolor'] = "DarkSeaGreen"
                else:
                    reescape_convnodestyle['bgcolor'] = "LightSalmon"
                node.set_style(reescape_convnodestyle)
                if Path(conv_spinfile).is_file():
                    img_face = et.ImgFace(conv_spinfile, width=self.image_scale_conv, height=self.image_scale_conv)
                    node.add_face(img_face, column=1, position='branch-bottom')
                conv_evecfile = conv_spinfile.replace('spin', 'evec')
                if Path(conv_evecfile).is_file():
                    if df_conv['sp_or_convex'].to_numpy()[0] == 'sp':
                        node.add_face(et.faces.TextFace('Unstable Mode', fsize=25), column=1, position='branch-top')
                    else:
                        node.add_face(et.faces.TextFace('Lowest Mode', fsize=25), column=1, position='branch-top')
                    img_face = et.ImgFace(conv_evecfile, width=self.image_scale_conv, height=self.image_scale_conv)
                    node.add_face(img_face, column=1, position='branch-top')

    def _create_tree_ete(self):
        r"""
        Create a more advanced version of a tree using ETE
        """

        def my_layout(node):
            # if node.is_root():
            #    img_face = et.ImgFace("SpinSTMi.png", width=250, height=250)
            #    et.faces.add_face_to_node(img_face, node, column=0, position="branch-top")
            if node.is_leaf():
                # If terminal node, draws its name
                name_face = et.AttrFace("name", fsize=30)
                et.faces.add_face_to_node(name_face, node, column=0, position="branch-right")
            else:
                # If internal node, draws label with smaller font size
                name_face = et.AttrFace("name", fsize=20)
                et.faces.add_face_to_node(name_face, node, column=0, position="branch-right")
            # Adds the name face to the image at the preferred position

        df_disp = pd.read_csv(self.info_file_disp, sep=r'\s+')
        df_esc = pd.read_csv(self.info_file_esc, sep=r'\s+')
        df_conv = pd.read_csv(self.info_file_conv, sep=r'\s+')
        t = et.Tree(f'({self._create_newick_string()})initial:0.0;', format=1)
        self._design_node_initial_state(tree=t)
        # Add features/ faces to tree
        for index, key in enumerate(df_disp['DISPKEY']):
            # This should be unique get the escape nodes
            key_node = t.search_nodes(name=key)[0]
            self._design_node_displaced_state(node=key_node, df_disp=df_disp, index=index, key=key)
            escape_nodes = key_node.get_children()
            # get sub data frame
            df_esc_filtered = df_esc[df_esc['DISPKEY'] == key]
            # iterate through escape nodes
            for escape_node in escape_nodes:
                # Get folder for these escape nodes
                self._design_node_escaped_state(node=escape_node, df_esc=df_esc_filtered)
                # go through converge stage
                conv_nodes = escape_node.get_children()
                df_conv_filtered = df_conv[df_conv['DISPKEY'] == key]
                df_conv_filtered = df_conv_filtered[df_conv_filtered['ESCKEY'] == escape_node.name]
                for conv_node in conv_nodes:
                    self._design_node_converged_state(node=conv_node, df_conv=df_conv_filtered)
                    nodes_at_current_depth = True
                    curr_node = conv_node
                    while nodes_at_current_depth:
                        try:
                            curr_node = curr_node.get_children()[0]
                            if curr_node.name in ['convex', 'sp']:
                                escapemodename = curr_node.up.name
                                df_conv_filtered = df_conv[df_conv['DISPKEY'] == key]
                                df_conv_filtered = df_conv_filtered[df_conv_filtered['ESCKEY'] == escapemodename]
                                self._design_node_reescape_conv_state(node=curr_node, df_conv=df_conv_filtered)
                            else:
                                df_esc_filtered = df_esc[df_esc['DISPKEY'] == key]
                                self._design_node_reescape_esc_state(node=curr_node, df_esc=df_esc_filtered)

                        except IndexError:
                            nodes_at_current_depth = False
                            print('reached leaf')
        ts = et.TreeStyle()
        # Do not add leaf names automatically
        ts.show_leaf_name = False
        ts.mode = 'c'
        ts.show_scale = False
        ts.show_branch_length = False
        ts.root_opening_factor = 0.0
        ts.arc_span = 360
        # Use my custom layout
        ts.layout_fn = my_layout
        t.show(tree_style=ts)

    def _create_tree_treelib(self):
        r"""
        Simple treelib representation of tree
        """
        l_tree = Tree()
        df_disp = pd.read_csv(self.info_file_disp, sep=r'\s+')
        df_esc = pd.read_csv(self.info_file_esc, sep=r'\s+')
        df_conv = pd.read_csv(self.info_file_conv, sep=r'\s+')
        # root node
        l_tree.create_node('initial configuration', 'root')
        for index, key in enumerate(df_disp['DISPKEY']):
            l_tree.create_node(df_disp['spin_file'][index], key, parent='root')
        for index, key in enumerate(df_esc['DISPKEY']):
            l_tree.create_node(df_esc['spin_file'][index], key + df_esc['ESCKEY'][index], parent=key)
        for index, key in enumerate(df_conv['DISPKEY']):
            l_tree.create_node(df_conv['spin_file'][index],
                               key + df_conv['ESCKEY'][index] + df_conv['spin_file'][index],
                               parent=key + df_conv['ESCKEY'][index])
            l_tree.create_node(df_conv['sp_or_convex'][index],
                               key + df_conv['ESCKEY'][index] + df_conv['sp_or_convex'][index],
                               parent=key + df_conv['ESCKEY'][index] + df_conv['spin_file'][index])
        l_tree.save2file(filename=self.parent_directory / 'sps_tree.txt')
