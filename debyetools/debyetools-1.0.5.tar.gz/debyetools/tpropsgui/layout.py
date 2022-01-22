import debyetools.tpropsgui.elements as elmt

lo_fs_Cp = lambda i : [[elmt.T('C_P:','fs_Cp'+str(i),pad=(3,0),right_click_menu=['',['copy to clipboard::Cp_'+str(i)]])],
                       [elmt.Ipad('','fsCp_P0'+str(i),10, pad=(0,0)),elmt.T('*T^0','fs_Cp_P0'+str(i),pad = ((0,0),(0,0)))],
                       [elmt.Ipad('','fsCp_P1'+str(i),10, pad=(0,0)),elmt.T('*T^1','fs_Cp_P1'+str(i),pad = ((0,0),(0,0)))],
                       [elmt.Ipad('','fsCp_P2'+str(i),10, pad=(0,0)),elmt.T('*T^(-2)','fs_Cp_P2'+str(i),pad = ((0,0),(0,0)))],
                       [elmt.Ipad('','fsCp_P3'+str(i),10, pad=(0,0)),elmt.T('*T^2','fs_Cp_P3'+str(i),pad = ((0,0),(0,0)))],
                       [elmt.Ipad('','fsCp_P4'+str(i),10, pad=(0,0)),elmt.T('*T^(-0.5)','fs_Cp_P4'+str(i),pad = ((0,0),(0,0)))],
                       [elmt.Ipad('','fsCp_P5'+str(i),10, pad=(0,0)),elmt.T('*T^(-3)','fs_Cp_P5'+str(i),pad = ((0,0),(0,0)))]]
lo_fs_alpha = lambda i: [[elmt.T('alpha:','fs_alpha'+str(i),pad=(3,0))],
                         [elmt.Ipad('','fsa_P0'+str(i),10, pad=(0,0)),elmt.T('*T^0','fs_a_P0'+str(i),pad = ((0,0),(0,0)))],
                         [elmt.Ipad('','fsa_P1'+str(i),10, pad=(0,0)),elmt.T('*T^1','fs_a_P1'+str(i),pad = ((0,0),(0,0)))],
                         [elmt.Ipad('','fsa_P2'+str(i),10, pad=(0,0)),elmt.T('*T^(-1)','fs_a_P2'+str(i),pad = ((0,0),(0,0)))],
                         [elmt.Ipad('','fsa_P3'+str(i),10, pad=(0,0)),elmt.T('*T^(-2)','fs_a_P3'+str(i),pad = ((0,0),(0,0)))]]
lo_fs_K = lambda i:[[elmt.T('1/K:','fs_K'+str(i),pad=(3,0))],
                    [elmt.Ipad('','fsK_P0'+str(i),10, pad=(0,0)),elmt.T('*T^0','fs_K_P0'+str(i),pad = ((0,0),(0,0)))],
                    [elmt.Ipad('','fsK_P1'+str(i),10, pad=(0,0)),elmt.T('*T^1','fs_K_P1'+str(i),pad = ((0,0),(0,0)))],
                    [elmt.Ipad('','fsK_P2'+str(i),10, pad=(0,0)),elmt.T('*T^2','fs_K_P2'+str(i),pad = ((0,0),(0,0)))],
                    [elmt.Ipad('','fsK_P3'+str(i),10, pad=(0,0)),elmt.T('*T^3','fs_K_P3'+str(i),pad = ((0,0),(0,0)))]]
lo_fs_Kp = lambda i:[[elmt.T('dK/dP','fs_Kp'+str(i),pad=(3,0))],
                     [elmt.Ipad('','fsKp_P0'+str(i),10, pad=(0,0))],
                     [elmt.Ipad('','fsKp_P1'+str(i),10, pad=(0,0))]]
def lo_fsparams(i):
    return [[elmt.T('G+TS (T=298K) = ', 'H298'+str(i), pad=((5,0),0)),elmt.Ipad('','H298'+str(i),10, pad=((0,0),0)),elmt.T('S(T=298K) = ', 'S298'+str(i), pad=((5,0),0)),elmt.Ipad('','S298'+str(i),10, pad=((0,0),0))],
            [elmt.C(lo=lo_fs_Cp(i), key='fc_Cp'+str(i)),
               elmt.C(lo=lo_fs_alpha(i), key='fc_alpha'+str(i)),
               elmt.C(lo=lo_fs_K(i), key='fc_K'+str(i)),
               elmt.C(lo=lo_fs_Kp(i), key='fc_Kp'+str(i))],
              [elmt.T('select property to plot:','fsprop2plt'+str(i)),
               elmt.ICombo(['       ','Cp','alpha','1/K','dK/dP'],'fsprop2plt'+str(i),10,1),
               elmt.Bc('Open plotter','plotter_fsprop2plt'+str(i),('white',elmt.theme_background_color()))]]

def layout(EOS_str_lst):
    lo_options = {EOSStr:[[elmt.T(EOSStr+' params.:','params_'+EOSStr),elmt.dI('0, 0, 0, 0','params_'+EOSStr,25),elmt.dChk('fit','calc_params_'+EOSStr,True)]] for EOSStr in EOS_str_lst}
    lo_options['MP'] = [[elmt.T('Morse cutoff:','cutoff_MP'),elmt.I('5.0','cutoff_MP',3),elmt.T('# of neigh. lvls.:','ndists_MP'),elmt.I('3','ndists_MP',3)],
                     [elmt.T('Morse params.:','params_MP'),elmt.dI('0, 0, 0','params_MP',15),elmt.dChk('fit','calc_params_MP',True)]]
    lo_options['EAM'] = [[elmt.T('EAM cutoff:','cutoff_EAM'),elmt.I('5.0','cutoff_EAM',3),elmt.T('# of neigh. lvls.:','ndists_EAM'),elmt.I('3','ndists_EAM',3)],
                     [elmt.T('EAM params.:','params_EAM'),elmt.dI('0, 0, 0','params_EAM',15),elmt.dChk('fit','calc_params_EAM',True)]]

    lo_EOS = [[elmt.listbox(['Morse','EAM','Rose-Vinet','TB-SMA','Birch-Murnaghan (3)','Mie-Gruneisen','Murnaghan (1)','Poirier-Tarantola','Birch-Murnaghan (4)','Murnaghan (2)',
                             ],'EOS_listbox')],
              [elmt.Be('Add','add_EOS',('white', 'green'))]]

    lo_EOS_collapes = [
                [elmt.collapse(lo_options['MP'],'options_'+'MP')],
                [elmt.collapse(lo_options['EAM'],'options_'+'EAM')],
              [elmt.collapse(lo_options['RV'],'options_'+'RV')],
              [elmt.collapse(lo_options['TB'],'options_'+'TB')],
              [elmt.collapse(lo_options['BM'],'options_'+'BM')],
              [elmt.collapse(lo_options['MG'],'options_'+'MG')],
              [elmt.collapse(lo_options['MU'],'options_'+'MU')],
              [elmt.collapse(lo_options['PT'],'options_'+'PT')],
              [elmt.collapse(lo_options['BM4'],'options_'+'BM4')],
              [elmt.collapse(lo_options['MU2'],'options_'+'MU2')],

              ]
    lo_EOS = lo_EOS+lo_EOS_collapes
    lo_EOS = lo_EOS + [[elmt.Bc('fit EOS parameters','run_eos_fitting',('white', 'green'),right_click_menu=['',['plot fitting::PlotfittingEOS']])],]

    lo_poisson = [[elmt.T('nu:', 'nu'),elmt.dI('','nu',6), elmt.Bc('calculate','calc_nu',('white', 'green'),right_click_menu=['',['details...::nu']])]]

    lo_el = [[elmt.Chk('parameters:','el',disabled=True),elmt.dI('','p_el',20),elmt.Bc('calculate','calc_el',('gray','gray'))]]

    lo_def = [[elmt.Chk('','def',disabled=True),elmt.T('Evac:','p_evac'),elmt.dI('','p_evac',3),elmt.T('Svac:','p_svac'),elmt.dI('','p_svac',3)]]

    lo_anhxc = [[elmt.Chk('parameters:','anhxc',disabled=True),elmt.dI('','p_anhxc',10)]]

    lo_intanh = [[elmt.Chk('parameters:','intanh',disabled=True),elmt.dI('','p_intanh',10)]]

    lo_left = [[elmt.T('compound:','compound'),
                elmt.I('','compound',30),
                elmt.dI(txt='', key='FILEBROWSE_', w=0, disabled=False,enable_events=True,visible=False),
                elmt.Br('compound')],
               [elmt.T('formula:','formula'),elmt.dI('','formula',6),elmt.T('structure:','strkt'),elmt.dI('','strkt',4)],
               [elmt.T('mass: (Kg/mol-at)','mass'),elmt.dI('','mass',7),elmt.T('Tm:','Tm'),elmt.dI('','Tm',7),elmt.T('r:','r',visible=False),elmt.dI('1','r',5,visible=False)],
               [elmt.F('EOS parametrization',lo_EOS,'EOS', right_click_menu=['',['More Info...::EOS','Go to code...::GoToEOS',]])],
               [elmt.F("Poisson's ratio", lo_poisson,'poisson', right_click_menu=['',['More Info...::Poisson','Go to code...::GoToPoisson',]])],
               [elmt.F('Electronic contribution',lo_el,'el', right_click_menu=['',['More Info...::Electronic','Go to code...::GoToElectronic',]])],
               [elmt.F('Defects (mono-vacancies)',lo_def, 'def', right_click_menu=['',['More Info...::Defects','Go to code...::GoToDefects',]])],
               [elmt.F('Anharmonicity XC',lo_anhxc, 'anhxc', right_click_menu=['','Not Implemented...::Anh',])],
               [elmt.F('Intrinsic Anharmonicity',lo_intanh, 'intanh', right_click_menu=['','Not Implemented...::Intanh',])],
               ]

    lo_minF = [[elmt.T('P (Pa):','Pi'),elmt.dI('','Pi',4),elmt.T('initial T (K):','Ti'),elmt.dI('','Ti',4),elmt.T('final T (K):','Tf'),elmt.dI('','Tf',4),elmt.T('No. steps:','ntemps'),elmt.dI('','ntemps',4)],
               [elmt.Bc('run minimization','run_minF',('gray','gray'))],
               [elmt.sCol([[elmt.M('','minF_output',100,7)]], 'minF_output', 480, 80)],
               [elmt.Bc('Open plotter','plotter',('gray','gray'))],]

    lo_tabs_tprops = [[elmt.Tab(eos_str,[[elmt.sCol([[elmt.M('','tprop_'+eos_str,400,7)]], 'tprop_'+eos_str, 470, 80)]],eos_str,False) for eos_str in ['','MP','BM','RV','MG','TB','MU','PT','BM4','MU2','EAM','*MP','*BM','*RV','*MG','*TB','*MU','*PT','*BM4','*MU2','*EAM']]]

    lo_tprops = [[elmt.Bc('evaluate','eval_tprops',('gray','gray'))],
             [elmt.TG(lo_tabs_tprops,'tabs_tprops')],
             [elmt.T('select property to plot:','prop2plt'),elmt.ICombo(['       ','       ','       ','       '],'prop2plt',10,1),elmt.Bc('Open plotter','plotter_tprops',('white',elmt.theme_background_color()))]]

    lo_tabs_fsparams = [[elmt.Tab(k,lo_fsparams(k),'fs_'+k,False) for k in ['','MP','BM','RV','MG','TB','MU','PT','BM4','MU2','EAM','*MP','*BM','*RV','*MG','*TB','*MU','*PT','*BM4','*MU2','*EAM']]]

    lo_collaps_fsparams = [elmt.TG(lo_tabs_fsparams,'tabs_fsparas')]

    lo_right = [[elmt.F('Temperature dependence of equilibrium volume, V(T)',lo_minF,'minF')],
                [elmt.F('Thermodynamic Properties',lo_tprops,'tprops')],
                [elmt.F('FactSage Parameters',[[elmt.T('from T=','fs_Tfrom'),elmt.Ipad('','fs_Tfrom',4,pad=(0,0)),
                                                elmt.T('to T=','fs_Tto'),elmt.Ipad('','fs_Tto',4,pad=(0,0)),elmt.Bc('Run parametrization', 'run_fs_params',('gray','gray'))],
                                               lo_collaps_fsparams],'fsparams')],]
    layout = [[elmt.C(lo=lo_left,key='left'),
               elmt.VS(),
               elmt.C(lo=lo_right, key='right')],]

    return layout

def layout_bulk(initial_folder):
    lo_contr = [[elmt.Chk('electronic','el_blk'),elmt.Chk('defects','def_blk')],
                [elmt.Chk('anharmonic correction','anh_blk'),elmt.Chk('intrinsic anharmonicity','intanh_blk')],
                ]
    return [[elmt.T('folder:','folder_bulk'),
                elmt.I('','folder_bulk',10),
                elmt.dI(txt='', key='FILEBROWSE_bulk_', w=0, disabled=False,enable_events=True,visible=False),
                elmt.Br('folder_bulk',initial_folder)],
            [elmt.listbox(['BM','RV','MG','TB','MU','PT','BM4','MU2','EAM'],'bulk'),elmt.listbox([],'bulk_list')],
            [elmt.F('Contributions',lo_contr,'contr_bulk')],
            [elmt.Bc('Run','run_eos_fitting',('grey','grey'))],
            ]
