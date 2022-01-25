import numpy as np
from streng.tools.rccola import rcmain, rcinput

sqcol_input = rcinput.RccolaInput

sqcol_input.first_row = rcinput.FirstRow(TYPEC=1,
                                         TYPES=1,
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

sqcol_input.second_row = rcinput.SecondRow(NLOAD=0,
                                           NLAYER=0,
                                           NDATA1=0,
                                           NDATA2=0,
                                           NSTRNI=4,
                                           NSTRNC=24,
                                           NITT=30)

sqcol_input.conc_sect_info = rcinput.ConcSectInfo(T=0.450,
                                                  B=0.450,
                                                  TC=0.402,
                                                  BC=0.402)

sqcol_input.reinf_place_info_TYPES12 = rcinput.ReinfPlaceInfoTYPES12(GT=.376,
                                                                     NB1=6,
                                                                     AS1=2.5447,
                                                                     NB2=2,
                                                                     AS2=2.5447,
                                                                     NBAR=1,
                                                                     AF=None)

sqcol_input.long_reinf_props = rcinput.LongReinfProps(FYS=440.,
                                                      YMS=200000.,
                                                      ESH=.010,
                                                      YSH=0.,
                                                      ESU=.120,
                                                      FSU=550.,
                                                      ESDYN=None)

sqcol_input.trans_reinf_info = rcinput.TransReinfInfo(FYSTRP=440.,
                                                      ASSTRP=1.005,
                                                      S=.150,
                                                      XL=3.00,
                                                      XSTRP=2.000,
                                                      ESUSTRP=.09)

sqcol_input.conc_props_ICSTR2348 = rcinput.ConcPropsICSTR2348(FCJ=28.0,
                                                              S=.150,
                                                              PPP=.003334)

sqcol_input.strains = np.array(
    [0.0, 0.001, 0.002, 0.003, 0.0035, 0.004, 0.005, 0.006, 0.007, 0.008, 0.009, 0.01, 0.011, 0.012,
     0.013, 0.014, 0.015, 0.016, 0.018, 0.02, 0.022, 0.024, 0.026, 0.028, 0.03])

sqcol_input.axials = None

rcc = rcmain.Rccola(input=sqcol_input,
                    outfilename='pyrcout_square.txt')

rcc.main()
# rcc.write_out()

print(rcc.outtxt)
