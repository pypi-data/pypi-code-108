# -*- coding: utf-8 -*-
# @Author: Antoine Tavant
# @Date:   2022-01-26 14:31:18
# @Last Modified by:   Antoine Tavant
# @Last Modified time: 2022-01-26 15:01:48

import pythermica
from pythermica import Thermica
from pythermica.analyse_nwk import *
from pythermica.plot_variables import *

def process_nwk_and_temperature( path_results,
                                output_dir=None,
                                nodes_names_to_discard=[]):
    
    """analyse everythin needed for one simulation"""
    
    
    if output_dir is None:
        output_dir = path_results
    
    """First the NWK data"""
    filename_gb, filename_nod, filename_gr, filename_gl = get_useful_files(
        path_results)

    list_of_nodes_numbers, list_of_nodes_names = extract_nodes(filename_nod)
    
    """Analysing the Gebhart Factor"""
    list_nodes_numbers_bg, index_lines_with_new_node, lines_with_new_node = read_gb_file(
        filename_gb,)

    """Is ther any missing factor ?"""
    
    print("missing Gebhart Factor entry for nodes : ")

    for idx, n in enumerate(list_of_nodes_numbers):
        if n not in list_nodes_numbers_bg:
            print(n, ":", list_of_nodes_names[idx])
    
    print("")
    """ generating the GB matrix figure"""
    
    mat_gb_vf, mat_gb_ir = get_all_dict_of_gb_lines(
        filename_gb, list_of_nodes_numbers, index_lines_with_new_node, lines_with_new_node)

    print("Generating Correlation Matrix for BG factors")
    # fig, axarr = generate_correlation_matrixes(list_mats=[mat_gb_ir, mat_gb_vf],
    #                                            list_node_names=list_of_nodes_names,
    #                                            list_titles=[
    #     "Gebhart factor IR", "Gebhart factor VF"],
    #     use_log=False,
    #     save_fig=True,
    #     filename=output_dir+"/matrices_Gebhart_factors_values",
    #     cmap="Blues")
    
    """ generating the GR matrix figure"""
    mat_GR = analyse_GR_nwk_data(
        filename_gr, list_of_nodes_numbers, list_of_nodes_names)
    
    print("Generating Correlation Matrix for GR coefs")

    fig, axarr = generate_correlation_matrixes(list_mats=[mat_GR],
                                               list_node_names=list_of_nodes_names,
                                               list_titles=[
                                                   "Radiative couplings (IR) computed by Thermica"],
                                               use_log=True,
                                               save_fig=True,
                                               filename=output_dir+"/matrices_IR_GR_factors_values"
                                               )
    
    mat_GL = analyse_GL_nwk_data(
        filename_gl, list_of_nodes_numbers, list_of_nodes_names)

    fig, axarr = generate_correlation_matrixes([mat_GL],
                                               list_of_nodes_names,
                                               ["conductives couplings computed by Thermica"],
                                               use_log=True,
                                               save_fig=True,
                                               filename=output_dir+"/matrices_GL_factors_values"
                                               )
    
    """Second, the thermal data"""
    
    thermal_result = Thermica(path_results)
    
    time_temperature = thermal_result.return_time_temperature()
    temperatures = thermal_result.get_temperature()

    fig, axarr = plt.subplots(4, 6, figsize=(8, 3))

    for ax, node_label, nodes_list_for_label in zip(axarr.flatten(),
                                                    thermal_result.names_unique,
                                                    thermal_result.nodes_per_names):
        if node_label == "Space Node":
            pass
        else:
            index_nodes_chassis = []
            for i, node in enumerate(thermal_result.nodes_value):
                if node in nodes_list_for_label:
                    index_nodes_chassis.append(i)

            index_nodes_chassis = np.array(index_nodes_chassis)

            ax.plot(time_temperature, temperatures.T[:, index_nodes_chassis])
            ax.set_title(node_label)
            ax.grid(c="grey")

    plt.savefig(output_dir +"/all_node_temp.png", dpi=300)
    
    figure_over_nodes(therm_results=[thermal_result],
                      temperatures=[temperatures],
                      times=[time_temperature],
                      n_orbits=8,
                      path_list=[path_results],
                      case_names=[""],
                      nodes_to_process=list_of_nodes_names,
                      path_root=output_dir,
                      name_yaxis="Temperature",
                      filename_prefix="")
    
    internal_dissipations = thermal_result.get_internal_dissipation()
    
    figure_over_nodes(therm_results=[thermal_result],
                      temperatures=[internal_dissipations],
                        times=[time_temperature],
                        n_orbits=8,
                        path_list=[path_results],
                        case_names=[""],
                        nodes_to_process=["/Powercard P60", "/Printed Circuits",
                                          "/Transponder (1)", "/Batteries",
                                          "/Propeller side front",
                                          "/Propeller side left",
                                          "/Propeller side right",
                                          "/Propeller side top",
                                          "/Propeller side back",
                                          "/Propeller side bottom", ],
                        path_root=output_dir,
                        name_yaxis="Internal Dissipation [W]",
                        filename_prefix="")
    
    totalInternalDissipation(thermal_result,
                             internal_dissipations,
                             time_temperature,
                             n_orbits = 8,
                             path_list = [path_results],
                             nodes_to_process=None,
                             path_root=output_dir,
                             filename_prefix="Total_IQ")



    


