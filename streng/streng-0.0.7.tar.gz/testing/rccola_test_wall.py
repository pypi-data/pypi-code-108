import numpy as np
from streng.tools.rccola import rcmain, rcinput

wall_input = rcinput.RccolaInput

wall_input.first_row = rcinput.FirstRow(TYPEC=3,
                                TYPES=3,
                                ISPALL=1,
                                ICSTR=8,
                                ICSTRS=2,
                                NPTS=0,
                                NPTSS=0,
                                ITCONF=0,
                                ISSTL=0,
                                IECU=1,
                                ISSTR=0,
                                IGRAPH=3)

wall_input.second_row = rcinput.SecondRow(NLOAD=0,
                                  NLAYER=200,
                                  NDATA1=5,
                                  NDATA2=0,
                                  NSTRNI=24,
                                  NSTRNC=0,
                                  NITT=30)

wall_input.conc_sect_info = rcinput.ConcSectInfo(T=4.000,
                                         B=0.250,
                                         TC=3.952,
                                         BC=0.202)

wall_input.reinf_place_info_TYPES3 = rcinput.ReinfPlaceInfoTYPES3(
      NL=29,
      NBAR=1,
      YS=[1.962, 1.826, 1.690, 1.554, 1.418, 1.350, 1.200, 1.050, 0.900, 0.750, 0.600, 0.450, 0.300, 0.150, 0.000,
          -0.150, -0.300, -0.450, -0.600, -0.750, -0.900, -1.050, -1.200, -1.350, -1.418, -1.554, -1.690, -1.826, -1.962],
      AS=[3.14, 3.14, 3.14, 3.14, 3.14, 0.79, 0.79, 0.79, 0.79, 0.79, 0.79, 0.79, 0.79, 0.79, 0.79, 0.79, 0.79, 0.79,
          0.79, 0.79, 0.79, 0.79, 0.79, 0.79, 3.14, 3.14, 3.14, 3.14, 3.14],
      NBS=[2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
      IBUC=[0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
      YSS=[],
      ASS=[],
      NBSS=[])

wall_input.long_reinf_props = rcinput.LongReinfProps(FYS=440.,
                                             YMS=200000.,
                                             ESH=.010,
                                             YSH=0.,
                                             ESU=.100,
                                             FSU=550.,
                                             ESDYN=None)

wall_input.trans_reinf_info = rcinput.TransReinfInfo(FYSTRP=440.,
                                             ASSTRP=1.00,
                                             S=.20,
                                             XL=4.00,
                                             XSTRP=2.000,
                                             ESUSTRP=0.10)

wall_input.conc_props_ICSTR2348 = rcinput.ConcPropsICSTR2348(FCJ=24.0,
                                                     S=.20,
                                                     PPP=.0047)

wall_input.conc_unconfined_props_ICSTRS2 = rcinput.ConcUnconfinedPropsICSTRS2(FCJS=24.0,
                                                                      SS=0.20,
                                                                      PPX=0.0001,
                                                                      NSP=1)

wall_input.geometry_conc_crossec_info = rcinput.GeometryConcCrossSectionInfo(
    AA=[0.0002, 0.2020, 0.0002, 0.2020, 0.0002],
    N1=[1, 29, 140, 29, 1],
    A1=[0.2498, 0.048, 0.2498, 0.048, 0.2498],
    AAc=[0.182],
    N1c=[60])

wall_input.strains = np.array([0.0, 0.001, 0.002, 0.003, 0.0035, 0.004, 0.005, 0.006, 0.007, 0.008, 0.009, 0.01, 0.011, 0.012,
                       0.013, 0.014, 0.015, 0.016, 0.018, 0.02, 0.022, 0.024, 0.026, 0.028, 0.03])

wall_input.axials = None

rcc = rcmain.Rccola(input=wall_input,
                    outfilename='pyrcout_wall.txt')

rcc.main()
rcc.write_out()

print(rcc.outtxt)
