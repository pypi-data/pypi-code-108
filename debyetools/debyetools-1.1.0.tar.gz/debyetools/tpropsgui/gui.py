#### imports
def gui():
    import PySimpleGUI as sg
    from debyetools.tpropsgui.layout import layout
    import debyetools.tpropsgui.events as events
    import debyetools.tpropsgui.toolbox as tbox
    from debyetools.aux_functions import load_doscar, load_V_E, load_EM, load_cell
    import debyetools.potentials as potentials
    import traceback
    from debyetools.poisson import poisson_ratio
    from debyetools.electronic import fit_electronic
    from debyetools.ndeb import nDeb
    from debyetools.aux_functions import gen_Ts
    from debyetools.fs_compound_db import fit_FS
    import numpy as np
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


    sg.set_options(element_padding=(0, 0))

    from matplotlib import pyplot as plt
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["mathtext.fontset"] = "dejavuserif"


    EOS_long_lst = {'Morse':'MP','Birch-Murnaghan (3)':'BM','Rose-Vinet':'RV','Mie-Gruneisen':'MG','TB-SMA':'TB','Murnaghan (1)':'MU','Poirier-Tarantola':'PT','Birch-Murnaghan (4)':'BM4','Murnaghan (2)':'MU2','EAM':'EAM',
                    }#'*Morse':'MP','*Birch-Murnaghan (3)':'*BM','*Rose-Vinet':'*RV','*Mie-Gruneisen':'*MG','*TB-SMA':'*TB','*Murnaghan (1)':'*MU','*Poirier-Tarantola':'*PT','*Birch-Murnaghan (4)':'*BM4','*Murnaghan (2)':'*MU2','*EAM':'*EAM'}
    EOS_str_lst = ['MP','BM','RV','MG','TB','MU','PT','BM4','MU2','EAM']#,'*MP','*BM','*RV','*MG','*TB','*MU','*PT','*BM4','*MU2','*EAM']

    loc = '..'
    contcar_str = '/CONTCAR.5'
    opened_EOS_dict = {str_i:False for str_i in EOS_str_lst}#{'MP':False,'BM':False,'RV':False,'MG':False,'TB':False,'MU':False,'BM3':False}
    checked_EOS_dict = {str_i:True for str_i in EOS_str_lst}
    EOS2plot_dict = {str_i:'' for str_i in EOS_str_lst}
    mws_dict = {'Al3Ca_D022': 0.030255624999999998, 'H': 0.0010079, 'He': 0.0040026, 'Li': 0.006941, 'Be': 0.0090122, 'B': 0.010811, 'C': 0.0120107, 'N': 0.0140067, 'O': 0.0159994, 'F': 0.0189984, 'Ne': 0.020179700000000002, 'Na': 0.0229897, 'Mg': 0.024305, 'Al': 0.026981500000000002, 'Si': 0.0280855, 'P': 0.0309738, 'S': 0.032064999999999996, 'Cl': 0.035453000000000005, 'K': 0.0390983, 'Ar': 0.039948, 'Ca': 0.040078, 'Sc': 0.0449559, 'Ti': 0.047867, 'V': 0.0509415, 'Cr': 0.051996099999999996, 'Mn': 0.054938, 'Fe': 0.055845, 'Ni': 0.0586934, 'Co': 0.0589332, 'Cu': 0.063546, 'Zn': 0.06539, 'Ga': 0.069723, 'Ge': 0.07264, 'As': 0.0749216, 'Se': 0.07895999999999999, 'Br': 0.079904, 'Kr': 0.0838, 'Rb': 0.0854678, 'Sr': 0.08762, 'Y': 0.0889059, 'Zr': 0.091224, 'Nb': 0.0929064, 'Mo': 0.09594, 'Tc': 0.098, 'Ru': 0.10107, 'Rh': 0.1029055, 'Pd': 0.10642, 'Ag': 0.1078682, 'Cd': 0.112411, 'In': 0.114818, 'Sn': 0.11871, 'Sb': 0.12176000000000001, 'I': 0.1269045, 'Te': 0.1276, 'Xe': 0.131293, 'Cs': 0.13290549999999998, 'Ba': 0.137327, 'La': 0.1389055, 'Ce': 0.14011600000000002, 'Pr': 0.1409077, 'Nd': 0.14424, 'Pm': 0.145, 'Sm': 0.15036000000000002, 'Eu': 0.151964, 'Gd': 0.15725, 'Tb': 0.1589253, 'Dy': 0.1625, 'Ho': 0.1649303, 'Er': 0.167259, 'Tm': 0.1689342, 'Yb': 0.17304, 'Lu': 0.174967, 'Hf': 0.17849, 'Ta': 0.1809479, 'W': 0.18384, 'Re': 0.18620699999999998, 'Os': 0.19022999999999998, 'Ir': 0.19221700000000003, 'Pt': 0.195078, 'Au': 0.1969665, 'Hg': 0.20059, 'Tl': 0.2043833, 'Pb': 0.2072, 'Bi': 0.2089804, 'Po': 0.209, 'At': 0.21, 'Rn': 0.222, 'Fr': 0.223, 'Ra': 0.226, 'Ac': 0.227, 'Pa': 0.2310359, 'Th': 0.2320381, 'Np': 0.237, 'U': 0.2380289, 'Am': 0.243, 'Pu': 0.244, 'Cm': 0.247, 'Bk': 0.247, 'Cf': 0.251, 'Es': 0.252, 'Fm': 0.257, 'Md': 0.258, 'No': 0.259, 'Rf': 0.261, 'Lr': 0.262, 'Db': 0.262, 'Bh': 0.264, 'Sg': 0.266, 'Mt': 0.268, 'Rg': 0.272, 'Hs': 0.277}

    #


    #### Window layout
    layout = layout(EOS_str_lst)

    #### Window creation
    window = sg.Window('ThermoProps V1.1', layout=layout)

    #### loop to wait for user action
    all_props={}
    tprops_dict_all = {}
    p_el_inittial = [3.8027342892e-01, -1.8875015171e-02,
                    5.3071034596e-04, -7.0100707467e-06]
    FS_db_params = {}


    while True:
        event, values = window.read()
        # print(event)

        # #close window
        if event in (sg.WIN_CLOSED, '--B_close'):
            break
        #
        # #file browser
        if event == '--I_FILEBROWSE_':
            try:
                # opened_EOS_dict = events.fbrowser_resets(window, opened_EOS_dict)
                str_folderbrowser = events.fbrowser_fill_browser(window, event)
                events.fbrowser_update_fields(window, contcar_str, mws_dict, str_folderbrowser)
            except Exception as e:
                sg.popup_ok(traceback.format_exc())
        if event == '||B_add_EOS':
            try:
                for k in opened_EOS_dict.keys():
                    opened_EOS_dict[k]=False
                for k in window['--LBx_EOS_listbox'].get():
                    opened_EOS_dict[EOS_long_lst[k]]=True
                # print(opened_EOS_dict)

                events.chk_eos(window,opened_EOS_dict)
            except Exception as e:
                sg.popup_ok(traceback.format_exc())
#
        #EOS calculation Checkbox
        if '--Chk_calc_params_' in event:
            try:
                events.chk_calc_params(window,event)
            except Exception as e:
                sg.popup_ok(traceback.format_exc())

        #
        #EOS fitting button
        if event == '||B_run_eos_fitting':
            try:
                V_DFT, E_DFT = load_V_E(str_folderbrowser, str_folderbrowser+'/CONTCAR.5', units='J/mol')
                for k in opened_EOS_dict:
                    if opened_EOS_dict[k]:
                        if k in ['MP','EAM']:
                            cutoff, number_of_neighbor_levels = float(window['--I_cutoff_MP'].get()), int(window['--I_ndists_MP'].get())
                            formula, primitive_cell, basis_vectors = load_cell(str_folderbrowser+'/CONTCAR.5')
                            args = formula, primitive_cell, basis_vectors, cutoff, number_of_neighbor_levels

                        else:
                            args = ''
                        EOS2params = getattr(potentials,k)(*args)
                        if k == 'MP':
                            initial_parameters =  [0.35, 1, 3.2]*len(EOS2params.comb_types)
                        elif k =='EAM':
                            initial_parameters = [1,1,1,1,1,1]*len(EOS2params.comb_types)+[1,1,1,1]*EOS2params.ntypes
                        else:
                            E0 = min(E_DFT)
                            V0 = V_DFT[np.where(E_DFT==E0)]
                            initial_parameters = [float(pi) for pi in window['--I_params_BM'].get().split(', ')]+[0]
                            if np.sum(initial_parameters)==0:
                                initial_parameters =  [E0, V0, 7.618619745e+10, 4.591924487e+00,1e-10]+[0]
                            else:
                                pass

                        if checked_EOS_dict[k]:
                            print(k, 'fitted')
                            EOS2params.fitEOS(V_DFT, E_DFT, initial_parameters=initial_parameters)
                        else:
                            print(k, 'not fitted')
                            EOS2params.pEOS = [float(pi) for pi in window['--I_params_'+k].get().split(', ')]
                            EOS2params.V0=1e-5

                        # print(EOS2params.pEOS)
                        events.eos_write_params(window,k,EOS2params.pEOS)

                        EOS2plot_dict[k] = EOS2params
                EOS2plot_dict['V_DFT']=V_DFT
                EOS2plot_dict['E_DFT']=E_DFT
            except Exception as e:
                sg.popup_ok(traceback.format_exc())
        # Plot the fitting
        if event == 'plot fitting::PlotfittingEOS':
            try:
                events.plot_EvV(window, EOS2plot_dict, opened_EOS_dict)
            except Exception as e:
                sg.popup_ok(traceback.format_exc())

        if event == '||B_calc_nu':
            try:
                EM = EM = load_EM(str_folderbrowser+'/OUTCAR.eps')
                nu = poisson_ratio(EM)
                # print(nu)
                window['--I_nu'].update('%.3f' % (nu))
            except Exception as e:
                sg.popup_ok(traceback.format_exc())
        if event == '||B_calc_el':
            try:
                E, N, Ef = load_doscar(str_folderbrowser+'/DOSCAR.EvV.')
                p_electronic = fit_electronic(V_DFT, p_el_inittial,E,N,Ef)

                window['--I_p_el'].update(', '.join(['%.5e' for _ in p_electronic]) % tuple(p_electronic))
            except Exception as e:
                sg.popup_ok(traceback.format_exc())

        if event == '||B_run_minF':
            try:
                nu = float(window['--I_nu'].get())
                m =float(window['--I_mass'].get())
                p_electronic = [float(stri) for stri in window['--I_p_el'].get().replace(' ','').split(',')]
                p_intanh = [float(stri) for stri in window['--I_p_intanh'].get().replace(' ','').split(',')]
                p_anh = [float(stri) for stri in window['--I_p_anhxc'].get().replace(' ','').split(',')]

                if window['--Chk_def'].get():
                    p_defects = float(window['--I_p_evac'].get()),float(window['--I_p_svac'].get()), float(window['--I_Tm'].get()), 0.1
                else:
                    p_defects = 1e10, 0, float(window['--I_Tm'].get()), 0.1
                # print('p_defects',p_defects)
                nDebs_dict = {}
                for k in opened_EOS_dict.keys():
                    if opened_EOS_dict[k]:
                        nDebs_dict[k] = {'ndeb':'','T':'','V':'','tprops':''}
                Pressure, T_initial, T_final, number_Temps = float(window['--I_Pi'].get()), float(window['--I_Ti'].get()), float(window['--I_Tf'].get()), float(window['--I_ntemps'].get())
                T = gen_Ts(T_initial, T_final, number_Temps)

                for k in opened_EOS_dict.keys():
                    if opened_EOS_dict[k]:
                        nDebs_dict[k]['ndeb'] = nDeb(nu, m, p_intanh, EOS2plot_dict[k], p_electronic,
                                             p_defects, p_anh)
                        Tmin, Vmin = nDebs_dict[k]['ndeb'].min_G(T,nDebs_dict[k]['ndeb'].EOS.V0,P=Pressure)
                        nDebs_dict[k]['T'] = np.array(Tmin)
                        nDebs_dict[k]['V'] = Vmin
                txt2VT = '#T'

                mtxs = np.array(T)

                for o in opened_EOS_dict:
                    if opened_EOS_dict[o]:
                        txt2VT = txt2VT + '             '+ o
                        mtxs=np.c_[mtxs,nDebs_dict[o]['V']]

                txt2VT = txt2VT+'\n'
                for line in mtxs:
                    txt2VT = txt2VT + ' '.join(['%.9e' for _ in line]) % tuple(line) + '\n'
                window['--M_minF_output'].update(txt2VT)

                events.minF_enable_nexts(window)
            except Exception as e:
                sg.popup_ok(traceback.format_exc())

        if event == '||B_plotter':
            try:
                events.plot_VvT(window)
            except Exception as e:
                sg.popup_ok(traceback.format_exc())


        if event == '||B_eval_tprops':
            try:
                for o in opened_EOS_dict:
                    if opened_EOS_dict[o]:
                        print('Results for:',o)
                        tprops_dict_all[o] = nDebs_dict[o]['ndeb'].eval_props(nDebs_dict[o]['T'],nDebs_dict[o]['V'],P=Pressure)

                        window['--Tab_'+o].update(visible=True)
                        #window['--Tab_'+o].select()
                        keys_TPs = tprops_dict_all[o].keys()
                        tprops_str = '#T          '+' '.join([(j+'            ') for j in list(keys_TPs)[1:]])+'\n'
                        TPs_arr = np.c_[tuple([tprops_dict_all[o][j] for j in keys_TPs])]
                        for rowi in TPs_arr:
                            tprops_str = tprops_str + ' '.join(['%.11e' for i in rowi])%tuple(rowi)+'\n'
                        window['--M_tprop_'+o].update(tprops_str)
                        window['--IC_prop2plt'].update(values=list(keys_TPs)[1:])
                window['--Tab_'].update(visible=False)
                events.tprops_enable_nexts(window)
            except Exception as e:
                sg.popup_ok(traceback.format_exc())

        if event == '||B_plotter_tprops':
            try:
                keys_EOS = []
                for o in opened_EOS_dict:
                    if opened_EOS_dict[o]:
                        keys_EOS.append(o)
                events.plot_tprops(window,keys_EOS)
            except Exception as e:
                sg.popup_ok(traceback.format_exc())

        #electronic Checkbox
        if event == '--Chk_el':
            try:
                events.chk_el(window,event)
            except Exception as e:
                sg.popup_ok(traceback.format_exc())
        #intrinsic anharmonicity Checkbox
        if event == '--Chk_def':
            try:
                events.chk_def(window,event)
            except Exception as e:
                sg.popup_ok(traceback.format_exc())
        #intrinsic anharmonicity Checkbox
        if event == '--Chk_intanh':
            try:
                events.chk_intanh(window,event)
            except Exception as e:
                sg.popup_ok(traceback.format_exc())

        if event == '--Chk_anhxc':
            try:
                events.chk_anhxc(window,event)
            except Exception as e:
                sg.popup_ok(traceback.format_exc())
        #
        # #parametrization of FS parameters button
        if event == '||B_run_fs_params':
            try:
                for o in opened_EOS_dict:
                    if opened_EOS_dict[o]:
                        FS_db_params[o] = fit_FS(tprops_dict_all[o],float(window['--I_fs_Tfrom'].get()), float(window['--I_fs_Tto'].get()))

                        ix_T0 = np.where(np.round(tprops_dict_all[o]['T'],2) == np.round(298.15,2))[0][0]
                        H298 = tprops_dict_all[o]['G'][ix_T0]+tprops_dict_all[o]['T'][ix_T0]*tprops_dict_all[o]['S'][ix_T0]
                        S298 = tprops_dict_all[o]['S'][ix_T0]

                        window['--Tab_fs_'+o].update(visible=True)
                        window['--Tab_fs_'+o].select()

                        window['--I_H298'+o].update(disabled=False)
                        window['--I_H298'+o].update(H298)
                        window['--I_S298'+o].update(disabled=False)
                        window['--I_S298'+o].update(S298)
                        for i in range(len(FS_db_params[o]['Cp'])):
                            window['--I_fsCp_P'+str(i)+o].update(disabled=False)
                            window['--I_fsCp_P'+str(i)+o].update('%.4e'%(FS_db_params[o]['Cp'][i]))
                        for i in range(len(FS_db_params[o]['a'])):
                            window['--I_fsa_P'+str(i)+o].update(disabled=False)
                            window['--I_fsa_P'+str(i)+o].update('%.4e'%(FS_db_params[o]['a'][i]))
                        for i in range(len(FS_db_params[o]['1/Ks'])):
                            window['--I_fsK_P'+str(i)+o].update(disabled=False)
                            window['--I_fsK_P'+str(i)+o].update('%.4e'%(FS_db_params[o]['1/Ks'][i]))
                        for i in range(len(FS_db_params[o]['Ksp'])):
                            window['--I_fsKp_P'+str(i)+o].update(disabled=False)
                            window['--I_fsKp_P'+str(i)+o].update('%.4e'%(FS_db_params[o]['Ksp'][i]))


                window['--Tab_fs_'].update(visible=False)
            except Exception as e:
                sg.popup_ok(traceback.format_exc())

        if '||B_plotter_fsprop2plt' in event:
            try:
                events.plot_fsprops(window,event,FS_db_params, float(window['--I_fs_Tfrom'].get()),float(window['--I_fs_Tto'].get()), tprops_dict_all)
            except Exception as e:
                sg.popup_ok(traceback.format_exc())


        checked_EOS_dict = events.update_diabled(window,opened_EOS_dict,EOS_str_lst,checked_EOS_dict)
