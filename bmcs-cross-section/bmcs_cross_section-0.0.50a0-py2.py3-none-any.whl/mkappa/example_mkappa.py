import matplotlib.pyplot as plt
from bmcs_cross_section.mkappa.mkappa import MKappa
from bmcs_cross_section.cs_design import TShape
from bmcs_cross_section.cs_design import CSDesign
import numpy as np


def run_example_with_default_params():
    mc = MKappa(idx=25, n_m=100)
    # mc.h = 600
    # mc.b = 200
    mc.kappa_range = (-0.00002, 0.00002, 100)
    fig, ((ax1, ax2)) = plt.subplots(1, 2, figsize=(10, 5))
    mc.plot(ax1, ax2)
    plt.show()


def run_example_with_t_section_and_custom_params():
    # TODO->Homam: debug MomentCurvature for t-section results

    H = 666
    # Defining a variable width (T-section as an example)
    b_w = 50
    b_f = 500
    h_w = 0.85 * H
    tshape = TShape(H=H, B_w=b_w, B_f=b_f, H_w=h_w)
    # Beam width b as a function of the height z (the sympy z symbol in MomentCurvatureSymbolic is used)

    if False:
        # Plotting
        fig, ((ax1)) = plt.subplots(1, 1, figsize=(10, 5))
        tshape.update_plot(ax1)
        plt.show()
        return

    bdesign = CSDesign(cross_section_shape=tshape,
                         L=1000)

    z_arr = np.linspace(0,H,10)
    mc = MKappa(beam_design=bdesign,
                H=H, idx=25, n_m=100)


    # Material parameters [mm], [N/mm2]
    mc.E_ct = 24000
    mc.E_cc = 24000
    mc.eps_cr = 0.000125
    mc.eps_cy = 0.0010625  # 8.5 * eps_cr_
    mc.eps_cu = 0.0035
    mc.eps_tu = 0.02
    mc.mu = 0.33

    # 2 layers reinforcement details
    mc.A_j = np.array([250, 0])  # A_j[0] for tension steel / A_j[1] for compression steel
    mc.z_j = np.array([0.1 * mc.H, 0.9 * mc.H])
    mc.E_j = np.array([210000, 210000])
    mc.eps_sy_j = np.array([0.002, 0.002])

    # If plot_norm is used, use the following:
    # mc.kappa_range = (0, mc.kappa_cr * 100, 100
    mc.kappa_range = (-0.00002, 0.00002, 100)

    # Plotting
    fig, ((ax1, ax2)) = plt.subplots(1, 2, figsize=(10, 5))
    mc.plot(ax1, ax2)
    plt.show()


if __name__ == '__main__':
    # run_example_with_default_params()
    run_example_with_t_section_and_custom_params()