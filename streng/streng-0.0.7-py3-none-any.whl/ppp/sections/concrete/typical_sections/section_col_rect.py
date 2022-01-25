from dataclasses import dataclass, field, InitVar
from streng.tools.rccola import rcmain, rcinput
from streng.ppp.sections.concrete.reinforcement.combos import LongReinforcementLayer as LongLayer
from streng.ppp.sections.concrete.reinforcement.areas import As
from streng.ppp.sections.concrete.reinforcement.ratios import ρw_vol
import numpy as np
import matplotlib.pyplot as plt
import datetime

PI = np.pi


@dataclass
class ColumnRectangular:
    b: float
    h: float
    cover: float
    length: float
    # corner bars
    bars_corn_n: int  # = field(default=4)
    bars_corn_dia: float
    # εσωτερικές ράβδοι παρειών
    long_layer_main_internal: LongLayer  # εσωτερικές ράβδοι (κάθε μίας) κύριας παρειάς
    long_layer_sec_internal: LongLayer  # εσωτερικές ράβδοι (κάθε μίας) δευτερεύουσας παρειάς
    # εγκάρσιος οπλισμός
    trans_pattern: int
    trans_dia: float
    trans_s: float

    rc_in: rcinput.RccolaInput

    conc_fc: float = 24.
    steel_fy: float = 440.
    steel_Es: float = 200000.
    steel_εsh: float = 0.01
    steel_Esh: float = 0.
    steel_εsu: float = 0.10
    steel_fu: float = 550.
    steel_fy_trans: float = 440.
    steel_εsu_trans: float = 0.10

    check_side: str = field(default='long')  # long or short

    rcc: rcmain.Rccola = field(init=False)

    def __post_init__(self):
        # Διαστάσεις του πυρήνα
        self.hc = self.h - 2 * self.cover - self.trans_dia
        self.bc = self.b - 2 * self.cover - self.trans_dia

        # Υπολογίζω ότι ο οπλισμός της κύριας παρειάς έχει τα γωνικά σίδερα (2) και επιπλέον τα ενδιάμεσα σίδερα
        _ns, _dias = self.long_layer_main_internal.ns.copy(
        ), self.long_layer_main_internal.dias.copy()
        _ns.append(self.bars_corn_n)
        _dias.append(self.bars_corn_dia)
        self.long_layer_main_full = LongLayer(ns=_ns, dias=_dias)

        # Βρίσκω τις θέσεις όλων των διαμήκων ράβδων. tuples(x, y, dia)
        self.all_bars = []
        self.__get_bars_locations()

        # Υπολογίζω το ογκομετρικό ποσοστό των συνδετήρων
        self.ρw_vol = self.__get_volumetric_ratio_trans()

    
    def __get_volumetric_ratio_trans(self):
        TC = self.hc
        BC = self.bc

        if self.trans_pattern == 1:
            hoops_length = 2 * TC + 2 * BC
        elif self.trans_pattern == 2:
            hoops_length = 2 * TC + 3 * BC
        elif self.trans_pattern == 3:
            hoops_length = 2 * TC + 4 * BC + 2 * (TC / 3)
        elif self.trans_pattern == 4:
            hoops_length = 2 * TC + 5 * BC + 2 * (TC / 2)
        elif self.trans_pattern == 5:
            hoops_length = 3 * TC + 2 * BC
        elif self.trans_pattern == 6:
            hoops_length = 3 * TC + 3 * BC
        elif self.trans_pattern == 7:
            hoops_length = 3 * TC + 4 * BC + 2 * (TC / 3)
        elif self.trans_pattern == 8:
            hoops_length = 3 * TC + 5 * BC + 2 * (TC / 2)

        return ρw_vol(hoops_length, self.trans_dia, self.bc, self.hc, self.trans_s)


    def __get_bars_locations(self):
        cnom = self.cover
        dia_main = self.long_layer_main_full.dia_equiv
        n_main = self.long_layer_main_full.ntot
        dia_sec = self.long_layer_sec_internal.dia_equiv
        n_sec = self.long_layer_sec_internal.ntot + 2  # προσθέτω τις γωνιακές
        spacing_main = (self.b - 2 * (cnom + self.trans_dia) -
                        dia_main) / (n_main - 1)
        spacing_sec = (self.h - 2 * (cnom + self.trans_dia) -
                       dia_main) / (n_sec - 1)

        first_bar_xy = cnom + self.trans_dia + 0.5 * dia_main
        for i in range(n_main):
            self.all_bars.append(
                (first_bar_xy + i*spacing_main, first_bar_xy, dia_main))
            self.all_bars.append(
                (first_bar_xy + i*spacing_main, self.h - first_bar_xy, dia_main))
        for i in range(n_sec-2):
            self.all_bars.append(
                (first_bar_xy, first_bar_xy + spacing_sec + i*spacing_sec, dia_sec))
            self.all_bars.append(
                (self.b - first_bar_xy, first_bar_xy + spacing_sec + i*spacing_sec, dia_sec))

    def plot_section(self):
        ax = plt.gca()

        for bar in self.all_bars:
            circle = plt.Circle(
                (bar[0], bar[1]), radius=bar[2], fc='r', linewidth=1)
            plt.gca().add_patch(circle)

        section_rectangle = plt.Rectangle(
            (0, 0), self.b, self.h, 0, fc='grey', linewidth=2, edgecolor='black', fill=True, alpha=0.5)
        plt.gca().add_patch(section_rectangle)

        plt.axis('scaled')

        return ax

    def prepare_AnySection(self, filename):
        textlines = []
        textlines.append('area')
        textlines.append('    label conc')
        textlines.append(
            f'    material concrete_confinedKappos {self.conc_fc} 0.002 {self.ρw_vol} {self.bc} {self.trans_s} {self.steel_fy_trans} 1')
        textlines.append(f'    section rectangular {self.b:.3f} {self.h:.3f}')
        textlines.append('end area')
        textlines.append('')
        textlines.append('fibergroup')
        textlines.append('    label reinf')
        textlines.append(
            f'    material steel_ParkSampson {self.steel_Es} {self.steel_fy} {self.steel_fu} {self.steel_εsh} {self.steel_εsu}')
        for bar in self.all_bars:
            textlines.append(
                f'    bar {bar[0]:.3f} {bar[1]:.3f} d{1000*bar[2]:.2f}')
        textlines.append('end fibergroup')

        with open(filename, 'w') as f:
            f.write('\n'.join(textlines))

    def run_rccola(self):
        T = self.h
        B = self.b
        TC = self.hc
        BC = self.bc
        GT = TC - self.trans_dia - self.bars_corn_dia
        NB1 = 2 * self.long_layer_main_full.ntot
        AS1 = 10000. * self.long_layer_main_full.As_equiv
        NB2 = 2 * self.long_layer_sec_internal.ntot
        AS2 = 10000. * self.long_layer_sec_internal.As_equiv

        if self.trans_pattern == 1:
            NBAR = 0
            XSTRP = 2
            PPP = (2 * TC + 2 * BC) * As(self.trans_dia) / \
                (TC * BC * self.trans_s)
        elif self.trans_pattern == 2:
            NBAR = 0
            XSTRP = 2
            PPP = (2 * TC + 3 * BC) * As(self.trans_dia) / \
                (TC * BC * self.trans_s)
        elif self.trans_pattern == 3:
            NBAR = 1
            XSTRP = 2
            PPP = (2 * TC + 4 * BC + 2 * (TC / 3)) * \
                As(self.trans_dia) / (TC * BC * self.trans_s)
        elif self.trans_pattern == 4:
            NBAR = 1
            XSTRP = 2
            PPP = (2 * TC + 5 * BC + 2 * (TC / 2)) * \
                As(self.trans_dia) / (TC * BC * self.trans_s)
        elif self.trans_pattern == 5:
            NBAR = 0
            XSTRP = 3
            PPP = (3 * TC + 2 * BC) * As(self.trans_dia) / \
                (TC * BC * self.trans_s)
        elif self.trans_pattern == 6:
            NBAR = 1
            XSTRP = 3
            PPP = (3 * TC + 3 * BC) * As(self.trans_dia) / \
                (TC * BC * self.trans_s)
        elif self.trans_pattern == 7:
            NBAR = 1
            XSTRP = 3
            PPP = (3 * TC + 4 * BC + 2 * (TC / 3)) * \
                As(self.trans_dia) / (TC * BC * self.trans_s)
        elif self.trans_pattern == 8:
            NBAR = 1
            XSTRP = 3
            PPP = (3 * TC + 5 * BC + 2 * (TC / 2)) * \
                As(self.trans_dia) / (TC * BC * self.trans_s)

        print('PPP = ', PPP)
        print('PPP2 = ', self.ρw_vol)

        col_input = rcinput.RccolaInput

        col_input.first_row = rcinput.FirstRow(TYPEC=1,
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

        col_input.second_row = rcinput.SecondRow(NLOAD=0,
                                                 NLAYER=0,
                                                 NDATA1=0,
                                                 NDATA2=0,
                                                 NSTRNI=24,
                                                 NSTRNC=24,
                                                 NITT=30)

        col_input.conc_sect_info = rcinput.ConcSectInfo(T, B, TC, BC)

        col_input.reinf_place_info_TYPES12 = rcinput.ReinfPlaceInfoTYPES12(GT=GT,
                                                                           NB1=NB1,
                                                                           AS1=AS1,
                                                                           NB2=NB2,
                                                                           AS2=AS2,
                                                                           NBAR=NBAR,
                                                                           AF=None)

        col_input.long_reinf_props = rcinput.LongReinfProps(FYS=self.steel_fy,
                                                            YMS=self.steel_Es,
                                                            ESH=self.steel_εsh,
                                                            YSH=self.steel_Esh,
                                                            ESU=self.steel_εsu,
                                                            FSU=self.steel_fu,
                                                            ESDYN=None)

        col_input.trans_reinf_info = rcinput.TransReinfInfo(FYSTRP=self.steel_fy_trans,
                                                            ASSTRP=XSTRP * 10000. * As(self.trans_dia),
                                                            S=self.trans_s,
                                                            XL=self.length,
                                                            XSTRP=2.000,
                                                            ESUSTRP=self.steel_εsu_trans)

        col_input.conc_props_ICSTR2348 = rcinput.ConcPropsICSTR2348(self.conc_fc,
                                                                    S=self.trans_s,
                                                                    PPP=PPP)

        # col_input.strains = np.array(
        #     [0.0, 0.001, 0.002, 0.003, 0.0035, 0.004, 0.005, 0.006, 0.007, 0.008, 0.009, 0.01, 0.011, 0.012,
        #      0.013, 0.014, 0.015, 0.016, 0.018, 0.02, 0.022, 0.024, 0.026, 0.028, 0.03])

        col_input.strains = np.array(
            [0.0, 0.0005, 0.0015, 0.002, 0.0025, 0.003, 0.0035, 0.004, 0.0045, 0.005, 0.006, 0.007, 0.008, 0.009, 0.01, 0.015, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045, 0.05, 0.06, 0.07])



            #     ActiveStrains = New Single() {0, 0.0005, 0.0015, 0.002, 0.0025, 0.003, 0.0035, _
            #                             0.004, 0.0045, 0.005, 0.006, 0.007, 0.008, 0.009, _
            #                             0.01, 0.015, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045, 0.05}
            #     ActiveStrNforXxpmax = 5
            # Case Is = 2
            #     ActiveStrains = New Single() {0, 0.00025, 0.0005, 0.00075, 0.001, 0.00125, 0.0015, 0.00175, 0.002, 0.00225, 0.0025, 0.00275, 0.003, 0.00325, 0.0035, 0.00375, _
            #                                      0.004, 0.00425, 0.0045, 0.00475, 0.005, 0.00525, 0.0055, 0.00575, 0.006, 0.00625, 0.0065, 0.00675, 0.007, 0.00725, 0.0075, 0.00775, _
            #                                      0.008, 0.00825, 0.0085, 0.00875, 0.009, 0.00925, 0.0095, 0.00975, 0.01, 0.01025, _
            #                                      0.0105, 0.01075, 0.011, 0.01125, 0.0115, 0.01175, 0.012, 0.01225, 0.0125, 0.01275, 0.013, 0.01325, 0.0135, 0.01375, 0.014, 0.01425, 0.0145, 0.01475, 0.015, _
            #                                      0.016, 0.017, 0.018, 0.019, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045, 0.05}
            #     ActiveStrNforXxpmax = 12
            # Case Else
        col_input.axials = None

        self.rcc = rcmain.Rccola(input=col_input,
                            outfilename='pyrcout_square.txt')

        self.rcc.calc()
        self.rcc.write_out()
        # print(rcc.outtxt)



        self.rc_in = col_input

        # self.rc_in = rcinput.RccolaInput(conc_sect_info = conc_sect_info)




# plt.axes()

# circle = plt.Circle((0, 0), radius=0.75, fc='y')
# plt.gca().add_patch(circle)

# plt.axis('scaled')
# plt.show()

# def multiple_custom_plots(x, y, ax=None, plt_kwargs={}, sct_kwargs={}):
#     if ax is None:
#         ax = plt.gca()
#     ax.plot(x, y, **plt_kwargs)
#     ax.scatter(x, y, **sct_kwargs)
#     return(ax)

# plot_params = {'linewidth': 2, 'c': 'g', 'linestyle':'--'}
# scatter_params = {'c':'red', 'marker':'+', 's':100}
# xdata = [1, 2]
# ydata = [10, 20]

# # plt.figure(figsize=(10, 5))
# axxx = multiple_custom_plots(xdata, ydata, plt_kwargs=plot_params, sct_kwargs=scatter_params)
# plt.savefig('plot')
# # plt.show()
