# -*- coding: utf-8 -*-
# @Author: Antoine Tavant
# @Date:   2022-01-24 15:49:41
# @Last Modified by:   Antoine Tavant
# @Last Modified time: 2022-01-25 09:39:52
import pytest

import pythermica
from pythermica.analyse_nwk import (extract_nodes, get_useful_files,
                                    generate_correlation_matrixes,
                                    read_gb_file,
                                    get_all_dict_of_gb_lines,
                                    analyse_GR_nwk_data,
                                    analyse_GL_nwk_data,
                                    get_nth_max_coupling)


def test_get_useful_files():
    root = pythermica.__path__[0]+"/../exemples/model_test/"

    filename_gb, filename_nod, filename_gr, filename_gl = get_useful_files(
        root)

    assert filename_gb.name == "ionsat_deployed_4.WINTER.HC.1.gb.txt"
    assert filename_nod.name == "ionsat_deployed_4.WINTER.HC.1.nod.nwk"
    assert filename_gr.name == "ionsat_deployed_4.WINTER.HC.1.gr.nwk"
    assert filename_gl.name == "ionsat_deployed_4.WINTER.HC.1.gl.nwk"

  
def test_extract_nodes():
    
    root = pythermica.__path__[0]+"/../exemples/model_test/"

    filename_gb, filename_nod, filename_gr, filename_gl = get_useful_files(
        root)

    list_of_nodes_numbers, list_of_nodes_names = extract_nodes(filename_nod)
    
    assert len(list_of_nodes_names) == len(list_of_nodes_numbers)
    
    
def test_analyse_GR_nwk_data():

    root = pythermica.__path__[0]+"/../exemples/model_test/"

    filename_gb, filename_nod, filename_gr, filename_gl = get_useful_files(
        root)

    list_of_nodes_numbers, list_of_nodes_names = extract_nodes(filename_nod)

    mat_GR = analyse_GR_nwk_data(filename_gr,
                        list_of_nodes_numbers,
                        list_of_nodes_names)
    
    assert mat_GR.shape == (len(list_of_nodes_names), len(list_of_nodes_names))
    
    
def test_analyse_GL_nwk_data():

    root = pythermica.__path__[0]+"/../exemples/model_test/"

    filename_gb, filename_nod, filename_gr, filename_gl = get_useful_files(
        root)

    list_of_nodes_numbers, list_of_nodes_names = extract_nodes(filename_nod)

    mat_GL = analyse_GL_nwk_data(filename_gl,
                                 list_of_nodes_numbers,
                                 list_of_nodes_names)

    assert mat_GL.shape == (len(list_of_nodes_names), len(list_of_nodes_names))


def test_generate_correlation_matrixes():

    root = pythermica.__path__[0]+"/../exemples/model_test/"

    filename_gb, filename_nod, filename_gr, filename_gl = get_useful_files(
        root)

    list_of_nodes_numbers, list_of_nodes_names = extract_nodes(filename_nod)

    mat_GR = analyse_GR_nwk_data(filename_gr,
                                 list_of_nodes_numbers,
                                 list_of_nodes_names)

    fig, axarr = generate_correlation_matrixes([mat_GR],
                                            list_of_nodes_names,
                                            "mat_GR",
                                            )
    assert len(axarr) == 1


def test_read_gb_file():
    root = pythermica.__path__[0]+"/../exemples/model_test/"

    filename_gb, filename_nod, filename_gr, filename_gl = get_useful_files(
        root)

    list_nodes_numbers_bg, index_lines_with_new_node, lines_with_new_node = read_gb_file(filename_gb)
    

def test_get_nth_max_coupling():
    
    root = pythermica.__path__[0]+"/../exemples/model_test/"

    filename_gb, filename_nod, filename_gr, filename_gl = get_useful_files(
        root)
    
    list_of_nodes_numbers, list_of_nodes_names = extract_nodes(filename_nod)

    mat_GR = analyse_GR_nwk_data(filename_gr,
                                 list_of_nodes_numbers,
                                 list_of_nodes_names)
    
    get_nth_max_coupling(mat_GR, list_of_nodes_names, 5)


def test_get_all_dict_of_gb_lines():
    root = pythermica.__path__[0]+"/../exemples/model_test/"

    filename_gb, filename_nod, filename_gr, filename_gl = get_useful_files(
        root)

    list_of_nodes_numbers, list_of_nodes_names = extract_nodes(filename_nod)

    list_nodes_numbers_bg, index_lines_with_new_node, lines_with_new_node = read_gb_file(
        filename_gb)

    mat_gb_vf, mat_gb_ir = get_all_dict_of_gb_lines(
        filename_gb,
        list_of_nodes_numbers,
        index_lines_with_new_node,
        lines_with_new_node)
