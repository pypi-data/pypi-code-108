import numpy as np
from streng.tools.rccola import rcmain, rcinput

tbeampos_input = rcinput.RccolaInput

tbeampos_input.first_row = rcinput.FirstRow(TYPEC=3,
                                TYPES=3,
                                ISPALL=0,
                                ICSTR=8,
                                ICSTRS=0,
                                NPTS=0,
                                NPTSS=0,
                                ITCONF=1,
                                ISSTL=0,
                                IECU=1,
                                ISSTR=0,
                                IGRAPH=3)

tbeampos_input.second_row = rcinput.SecondRow(NLOAD=1,
                                  NLAYER=60,
                                  NDATA1=2,
                                  NDATA2=1,
                                  NSTRNI=4,
                                  NSTRNC=24,
                                  NITT=30)

tbeampos_input.conc_sect_info = rcinput.ConcSectInfo(T=0.600,
                                         B=0.250,
                                         TC=0.532,
                                         BC=0.182)

tbeampos_input.reinf_place_info_TYPES3 = rcinput.ReinfPlaceInfoTYPES3(NL=2,
                                                          NBAR=0,
                                                          YS=[0.255, -0.255],
                                                          AS=[1.54, 1.54],
                                                          NBS=[3, 3],
                                                          IBUC=[0, 0],
                                                          YSS=[],
                                                          ASS=[],
                                                          NBSS=[])

tbeampos_input.long_reinf_props = rcinput.LongReinfProps(FYS=440.,
                                             YMS=200000.,
                                             ESH=.010,
                                             YSH=0.,
                                             ESU=.100,
                                             FSU=550.,
                                             ESDYN=None)

tbeampos_input.trans_reinf_info = rcinput.TransReinfInfo(FYSTRP=440.,
                                             ASSTRP=1.00,
                                             S=.20,
                                             XL=4.00,
                                             XSTRP=2.000,
                                             ESUSTRP=0.10)

tbeampos_input.conc_props_ICSTR2348 = rcinput.ConcPropsICSTR2348(FCJ=24.0,
                                                     S=.20,
                                                     PPP=.0037)

tbeampos_input.geometry_conc_crossec_info = rcinput.GeometryConcCrossSectionInfo(
    AA=[1.700, 0.250],
    N1=[15, 45],
    A1=None,
    AAc=[0.182],
    N1c=[60])

tbeampos_input.strains = np.array([0.0, 0.001, 0.002, 0.003, 0.0035, 0.004, 0.005, 0.006, 0.007, 0.008, 0.009, 0.01, 0.011, 0.012,
                       0.013, 0.014, 0.015, 0.016, 0.018, 0.02, 0.022, 0.024, 0.026, 0.028, 0.03])

tbeampos_input.axials = np.array([0.0])

rcc = rcmain.Rccola(input=tbeampos_input,
                    outfilename='pyrcout_tbeampos.txt')

rcc.main()
rcc.write_out()

print(rcc.outtxt)
