import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from bmcs_cross_section.mkappa.mkappa_ import MKappa, ModelData


def run_example_with_default_params():
    mc = MKappa(idx=25, n_m=100)
    mc.model_data.h = 600
    mc.model_data.b = 200
    mc.kappa_range = (-0.00002, 0.00002, 100)
    fig, ((ax1, ax2)) = plt.subplots(1, 2, figsize=(10, 5))
    mc.plot(ax1, ax2)
    plt.show()


def run_example_with_t_section_and_custom_params():
    mc = MKappa(idx=25, n_m=100)
    model_data = ModelData()

    # Material parameters [mm], [N/mm2]
    model_data.h = 666
    model_data.E_ct = 24000
    model_data.E_cc = 24000
    model_data.eps_cr = 0.000125
    model_data.eps_cy = 0.0010625  # 8.5 * eps_cr_
    model_data.eps_cu = 0.0035
    model_data.eps_tu = 0.02
    model_data.mu = 0.33

    # 2 layers reinforcement details
    model_data.A_j = np.array([250, 0])  # A_j[0] for tension steel / A_j[1] for compression steel
    model_data.z_j = np.array([0.1 * model_data.h, 0.9 * model_data.h])
    model_data.E_j = np.array([210000, 210000])
    model_data.eps_sy_j = np.array([0.002, 0.002])

    # Defining a variable width (T-section as an example)
    b_w = 50
    b_f = 500
    h_w = 0.85 * model_data.h
    # Beam width b as a function of the height z (the sympy z symbol in MomentCurvatureSymbolic is used)
    model_data.b = sp.Piecewise((b_w, mc.mcs.z < h_w), (b_f, mc.mcs.z >= h_w))

    mc.model_data = model_data

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