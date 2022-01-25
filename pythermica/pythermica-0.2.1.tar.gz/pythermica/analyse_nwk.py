# -*- coding: utf-8 -*-
# @Author: Antoine Tavant
# @Date:   2021-12-17 15:36:12
# @Last Modified by:   Antoine Tavant
# @Last Modified time: 2022-01-25 09:24:33

import numpy as np
import parse as prs
import matplotlib.pyplot as plt
from pathlib import Path

def get_useful_files(root):
    """Look for the useful fils in a folder

    Args:
        root (str): relative or absolute name of the folder
    """

    p_root = Path(root)

    filename_gb = list(p_root.glob("*gb.txt"))[0]
    filename_gl = list(p_root.glob("*gl.nwk"))[0]
    filename_gr = list(p_root.glob("*gr.nwk"))[0]
    filename_nod = list(p_root.glob("*.nod.nwk"))[0]
    
    return filename_gb, filename_nod, filename_gr, filename_gl

def extract_nodes(filename_nod):
    """Read the *.od.nwk file and generate the list of all nodes and their names

    Args:
        filename_nod (str): file name of the results in *.nod.nwk

    Returns:
        list_of_nodes_numbers [list]: list of all the node numbers, ordered

        list_of_nodes_names [list]: list of the name of each node,
                                    with the same order as list_of_nodes_numbers

    """

    useful_lines = []

    with open(filename_nod, 'r') as f_nod:

        lines = f_nod.readlines()
        
        for i, line in enumerate(lines):

            if line == "$NODES\n":
                for j, line2 in enumerate(lines[i:]):

                    if line2 != "$INITIAL\n":
                        useful_lines.append(line2) 
                    else:
                        break

    useful_lines = useful_lines[3:-4]

    list_of_nodes_numbers = []
    list_of_nodes_names = []

    detect_str = " = '/"

    for line in useful_lines:

        try :
            index = line.index(detect_str)

            list_of_nodes_numbers.append( eval( line[index-6:index]))
            list_of_nodes_names.append(  line[index+5:index+40].strip()  )

        except ValueError:
            pass

    return list_of_nodes_numbers, list_of_nodes_names

def analyse_GR_nwk_data(filename_gr: str,
                        list_of_nodes_numbers: list,
                        list_of_nodes_names: list ):
    """read the gr.nwk file and generate the relation matrix,
     with the same order as the list_of_nodes_numbers

    Args:
        filename_gr (str): filename of the *gr.nwk to process
        list_of_nodes_numbers (list): list of all the node numbers
        list_of_nodes_names (list): ist of the name of each node,
                                    with the same order as list_of_nodes_numbers

    Returns:
        mat_GR (np.array): the coefficient matrice with GL links between each nodes
    """
    

    mat_GR = np.zeros( (len(list_of_nodes_names), len(list_of_nodes_names)))

    with open(filename_gr, 'r') as f_gr:
        lines = f_gr.readlines()
        
    for line in lines:

        if "GR( " in line:

            
            format_string = "      GR( {n_org} , {n_dest} )	=	{data};\n"
            parsed = prs.parse(format_string, line)
            
            if parsed is None:
                format_string = "     #GR( {n_org} , {n_dest} )	=	{data};\n"
                parsed = prs.parse(format_string, line)

            if parsed is None:
                format_string = "     #GR( {n_org} , {n_dest} )	=	{data};	# {otherdata} %\n"
                parsed = prs.parse(format_string, line)

            
            try:
                gr_value = eval( parsed["data"])
                
                if parsed["n_dest"]  not in ['99999999', "SCREEN", "FILTER"]:
                    ind_dest = list_of_nodes_numbers.index(eval(parsed["n_dest"]))
                    ind_org = list_of_nodes_numbers.index(eval(parsed["n_org"]))

                    mat_GR[ind_dest, ind_org] = gr_value
                    mat_GR[ind_org, ind_dest] = gr_value
            except TypeError:
                print(line)

    return mat_GR

def analyse_GL_nwk_data(filename_gl, list_of_nodes_numbers, list_of_nodes_names):
    """read the gl.nwk file and generate the relation matrix,
     with the same order as the list_of_nodes_numbers

    Args:
        filename_gl (str): filename of the *gl.nwk to process
        list_of_nodes_numbers (list): list of all the node numbers
        list_of_nodes_names (list): ist of the name of each node,
                                    with the same order as list_of_nodes_numbers

    Returns:
        mat_GL (np.array): the coefficient matrice with GL links between each nodes
    """

    mat_GL = np.zeros( (len(list_of_nodes_names), len(list_of_nodes_names)))

    with open(filename_gl, 'r') as f_gr:
        lines = f_gr.readlines()
        
    COND_Aluminium_2024 = 120
    COND_Aluminium_6061 = 120
    COND_Aluminium_7075 = 120
    COND_MLI = 0


    for line in lines:

        if "GL(" in line:

            
            format_string = "   GL({n_org}, {n_dest}) =   {data};\n"
            parsed = prs.parse(format_string, line)

            if parsed is None:
                format_string = "   GL({n_org}, {n_dest}) = {data};\n"
                parsed = prs.parse(format_string, line)


            gl_value = eval( parsed["data"])

            ind_dest = list_of_nodes_numbers.index(eval(parsed["n_dest"]))
            ind_org = list_of_nodes_numbers.index(eval(parsed["n_org"]))

            mat_GL[ind_dest, ind_org] = gl_value
            mat_GL[ind_org, ind_dest] = gl_value
    
    return mat_GL

def generate_correlation_matrixes(list_mats,
                                  list_node_names,
                                  list_titles,
                                  use_log=True,
                                  save_fig=False,
                                  filename="",
                                  cmap="afmhot_r"):
    """creat a Matrice figure of the node coefficients

    Args:
        list_mats (list of np.array): list of the coefficient matrices
        list_node_names (list): list of the node names, needs one for each node
        list_titles (list): list of the subplot titles, coerrespondes to list_mats
        use_log (bool, optional): if `True`, then compute the log10 of the matrice before ploting . Defaults to True.
        save_fig (bool, optional): if `True`, then save the figure on a PNG file. Defaults to False.
        filename (str, optional): name of the figure file, used if `save_fig`. Defaults to "".

    Returns:
        fig, axarr [matplotlib.Figure and Axies]: the matplotlig objects
    """


    n_plots = len(list_mats)

    fig, axarr = plt.subplots(n_plots, 1, figsize=(15, 15*n_plots)) 

    if n_plots == 1:
        axarr = [axarr]


    for i, mat_values in enumerate(list_mats):

        """ preprocessing the matrices data"""
        #mat_GL[mat_GL < 1e-10] = 0
        mat_values /= mat_values.max()

        if use_log:
            mat_values_toplot = np.log10(mat_values+1e-5)
        else:
            mat_values_toplot = mat_values*10
        
        axarr[i].grid(False)
        neg = axarr[i].imshow( mat_values_toplot, cmap=cmap )
        fig.colorbar(neg, ax=axarr[i],
                     location='right',
                     anchor=(0.5, 1.5),
                     shrink=0.3,
                     label="Coef Value", )

        text_title = list_titles[i]
        if use_log:
            text_title += " \nLog Scale"

        axarr[i].set_title(text_title)


    for ax in axarr:
        """Set up the figures nicely"""
        #ax.set_xlabel("node Numbers")
        #ax.set_ylabel("node Numbers")
        ax.set_xticks(range(len(list_node_names)))
        ax.set_yticks(range(len(list_node_names)))

        ax.set_xticklabels(list_node_names)
        ax.tick_params(labeltop=True, labelright=True)

        for label in ax.get_xticklabels():
            pos = label.get_position()
            if pos[1] == 0:
                label.set_ha("right")
                label.set_rotation(80)
            elif pos[1] == 1:
                label.set_ha("left")
                label.set_rotation(80)

        ax.set_yticklabels(list_node_names)

        ax.grid(alpha=0.2)


    fig.tight_layout()

    if save_fig:
        if use_log:
            filename += "_log"

        plt.savefig(filename+".png", dpi=200)
    
    return fig, axarr

def parse_one_node_lines(lines_selected):
    node_numbers = []
    gb_vfs = []
    gb_irs = []

    for line in lines_selected:

        node_number = eval(line[26:31])
        gb_vf = eval(line[36:46])
        gb_ir = eval(line[48:])

        node_numbers.append(node_number)
        gb_irs.append(gb_ir)
        gb_vfs.append(gb_vf)

    return node_numbers, gb_vfs, gb_irs

    
def read_gb_file(filename_gb):
    """Read a first time the BG fiel to have a big picture

    Args:
        filename_gb ([type]): [description]

    Returns:
        [type]: [description]
    """
    with open(filename_gb, 'r') as f_gb:

        lines = f_gb.readlines()

    lines_with_new_node = []
    index_lines_with_new_node = []

    for i, line in enumerate(lines):
        
        if "Factors from node:" in line:
            lines_with_new_node.append(line)
            index_lines_with_new_node.append(i)

    list_nodes_numbers_bg = [ eval( l[19:24] ) for l in lines_with_new_node]
    
    return list_nodes_numbers_bg, index_lines_with_new_node, lines_with_new_node


def trans_dict_of_list_to_mat(dol, list_of_nodes_numbers):
    """transform the dist of list to a np.array

    Args:
        dol (dict of list): the dict of list generated earlier

    Returns:
        mat_gb: the np.array matrix
    """
    mat_gb = np.zeros( (len(list_of_nodes_numbers), len(list_of_nodes_numbers)) )

    for i, id in enumerate(list_of_nodes_numbers):
        for j, jd in enumerate(list_of_nodes_numbers):
            try:
                mat_gb[i, j]= dol[id][j]
            except KeyError:
                print(i, j, id, jd)


    return mat_gb


def get_all_dict_of_gb_lines(filename_gb, list_of_nodes_numbers, index_lines_with_new_node, lines_with_new_node):
    """open the file and read all the coefficients"""

    with open(filename_gb, 'r') as f_gb:

        lines = f_gb.readlines()


    dict_of_list_gb_vf = {}
    dict_of_list_gb_ir = {}

    for linenumber, linetitle in zip(index_lines_with_new_node, lines_with_new_node):

        node_number = eval(linetitle[19:24])
        line_start = linenumber+3

        for index, line in enumerate(lines[line_start:]):
            if "------------------" in line:
                line_stop = line_start+index
                break 



        lines_selected = lines[line_start:line_stop]

        nodes, gb_vfs, gb_irs = parse_one_node_lines(lines_selected)

        dict_gbvfs = { n: gb for n,gb in zip(nodes, gb_vfs )}
        dict_gbirs = { n: gb for n,gb in zip(nodes, gb_irs )}

        
        gbvf_every_nodes = []
        gbir_every_nodes = []
        for n in list_of_nodes_numbers:
            gbvf_every_nodes.append( dict_gbvfs.get(n, 0) )
            gbir_every_nodes.append( dict_gbirs.get(n, 0) )


        
        dict_of_list_gb_vf[node_number] = gbvf_every_nodes
        dict_of_list_gb_ir[node_number] = gbir_every_nodes

    #added empty nodes
    for n in list_of_nodes_numbers:
        if n not in dict_of_list_gb_vf.keys():
            dict_of_list_gb_vf[n] = [ 0 for n in list_of_nodes_numbers]

        if n not in dict_of_list_gb_ir.keys():
            dict_of_list_gb_ir[n] = [ 0 for n in list_of_nodes_numbers]
            
    mat_gb_vf = trans_dict_of_list_to_mat(dict_of_list_gb_vf, list_of_nodes_numbers)
    mat_gb_ir = trans_dict_of_list_to_mat(dict_of_list_gb_ir, list_of_nodes_numbers)

    return mat_gb_vf, mat_gb_ir


def get_nth_max_coupling(mat, list_of_nodes_names, n=10):
    """Read the matrice and print the biggest elements

    Args:
        mat (numpy.array): the coefficients matrix
        list_of_nodes_names (list): the list of names
        n (int, optional): number of maximum element to print. Defaults to 10.
    """
    ind = np.argsort(mat, None,)[-2*n:][::-1]
    ind_2d = np.unravel_index(ind, mat.shape)

    oposit_couples = []
    for ind_i, ind_j in zip(*ind_2d):
        if [ind_i, ind_j] not in oposit_couples:

            oposit_couples.append([ind_j, ind_i])

            print( f" {mat[ind_i, ind_j]:2.4f} between {list_of_nodes_names[ind_i]} and {list_of_nodes_names[ind_j]}")
