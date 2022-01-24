'''
Created on 30.08.2016

@author: Yingxiong
'''
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider


E = 100.
eps_cu = -0.2  # the minimum matrix strain
# material law - matrix
Sig = lambda eps: E * eps * (eps >= eps_cu) * (eps <= 0.0)
# material law - reinforcement
eps_u_r = 0.2
Sig_reinf = lambda eps: 500. * eps * \
    (eps >= -eps_u_r * 1.05) * (eps <= eps_u_r * 1.05)

reinf_y_coord = np.array([6., 7., 4., 2., 1, 9])
reinf_area = np.array([0.1, 0.1, 0.1, 0.1, 0.1, 0.1])


height = 10.
gravity_center = height / 2.
width = 2.

n_ip = 10000
# discretization of the matrix
y_coord = np.linspace(0, height, n_ip)

# upper strain
eps_upper = -0.1
# lower strain
eps_lower = 0.05


def get_NM(eps_lower, eps_upper):
    # matrix strain array
    strain_y = np.interp(y_coord, [0, height], [eps_lower, eps_upper])

    # matirx stress array
    stress_y = Sig(strain_y)

    # reinf strain
    strain_r = np.interp(reinf_y_coord, [0, height], [eps_lower, eps_upper])

    # reinf stress
    stress_r = Sig_reinf(strain_r)

    # normal force - matrix
    N_m = np.trapz(stress_y * width, y_coord)
    # normal force - reinforcement
    N_r = np.sum(stress_r * reinf_area)
    N = N_m + N_r

    # moment - matrix
    M_m = np.trapz(stress_y * width * (y_coord - gravity_center), y_coord)
    # moment - reinforcement
    M_r = np.sum(stress_r * reinf_area * (reinf_y_coord - gravity_center))
    M = M_m + M_r

    return N, M, strain_y, stress_y, strain_r, stress_r

# get the mxn diagram

# Convert the strain in the lowest reinforcement layer at failure
# to the strain at the bottom of the cross section


def convert_eps_u_2_lo(eps_up, eps_u_r, y_coord_r):
    # eps_u_r -- the maximum strain of the corresponding reinforcement
    h = height
    eps_lo = eps_up + (eps_u_r - eps_up) / (h - y_coord_r) * h
    return eps_lo

eps_lo_arr = convert_eps_u_2_lo(-0.1, eps_u_r, reinf_y_coord)
env_reinf_idx = np.argmin(eps_lo_arr)

eps_ccu = 0.8 * eps_cu


n_eps = 20
reinforced = True
if reinforced:
    eps_t_lo = convert_eps_u_2_lo(
        eps_cu, eps_u_r, reinf_y_coord[env_reinf_idx])
    eps_t_lo_0 = convert_eps_u_2_lo(0., eps_u_r, reinf_y_coord[env_reinf_idx])
    eps_t_u = eps_u_r

    # Strain arrays for the lower rim
    eps_cc_0 = np.linspace(eps_ccu, 0., n_eps)
    eps_0_tlo = np.linspace(0., eps_t_lo, n_eps)
    eps_tlo_tlo0 = np.linspace(eps_t_lo, eps_t_lo_0, n_eps)
    eps_tlo0_tu = np.linspace(eps_t_lo_0, eps_t_u, n_eps)

    # Strain arrays for the upper rim
    eps_cc_c = np.linspace(eps_ccu, eps_cu, n_eps)
    eps_c_const = eps_cu * np.ones_like(eps_cc_0)
    eps_c_0 = np.linspace(eps_cu, 0., n_eps)
    eps_0_tu = np.linspace(0., eps_t_u, n_eps)

    eps1 = np.vstack([eps_cc_0, eps_cc_c])
    eps2 = np.vstack([eps_0_tlo, eps_c_const])
    eps3 = np.vstack([eps_tlo_tlo0, eps_c_0])
    eps4 = np.vstack([eps_tlo0_tu, eps_0_tu])

    eps_arr = np.hstack([eps1, eps2, eps3, eps4])
else:
    # Strain arrays for the lower rim
    eps_cc_0 = np.linspace(eps_ccu, 0., n_eps)
    eps_00 = np.zeros_like(eps_cc_0)

    # Strain arrays for the upper rim
    eps_cc_c = np.linspace(eps_ccu, eps_cu, n_eps)
    eps_c_0 = np.linspace(eps_cu, 0., n_eps)

    eps1 = np.vstack([eps_cc_0, eps_cc_c])
    eps2 = np.vstack([eps_00, eps_c_0])

    eps_arr = np.hstack([eps1, eps2])

# get the m-n envelop
M_arr = np.zeros_like(eps_arr[0])
N_arr = np.zeros_like(eps_arr[0])
for i in np.arange(len(eps_arr[0])):

    result = get_NM(eps_arr[0][i], eps_arr[1][i])

    N_arr[i] = result[0]
    M_arr[i] = result[1]
#     print result[1]

# print np.where(np.abs(M_arr + 78.94480586) < 1.)

N, M, strain_y, stress_y, strain_r, stress_r = get_NM(
    eps_arr[0][0], eps_arr[1][0])

ax1 = plt.subplot(221)
ax1.plot(strain_y, y_coord)
ax1.plot((0, 0), (0, height))
for i, strain in enumerate(strain_r):
    ax1.plot((strain, 0), (reinf_y_coord[i], reinf_y_coord[i]), '--')

ax2 = plt.subplot(222)
ax2.plot(stress_y, y_coord)
ax2.plot((0, 0), (0, height))
for i, stress in enumerate(stress_r):
    ax2.plot((stress, 0), (reinf_y_coord[i], reinf_y_coord[i]), '--')

ax3 = plt.subplot(223)
ax3.plot(-eps_arr, [0, height], 'k-')
l, = ax3.plot(-eps_arr.T[0], [0, height], 'r')

ax4 = plt.subplot(224)
ax4.plot(-M_arr, -N_arr, lw=2)
p, = ax4.plot(-M_arr[0], -N_arr[0], 'ro')
ax4.axhline(0, color='k')
ax4.axvline(0, color='k')

ax = plt.axes([0.10, 0.015, 0.80, 0.02])

step_slider = Slider(
    ax, 'step', 0.0, len(eps_arr[0]) - 1, valinit=0, valfmt='%1.0f')


def update(val):
    step = step_slider.val
    step = int(round(step))
    l.set_xdata(-eps_arr.T[step])
    p.set_data(-M_arr[step], -N_arr[step])
    N, M, strain_y, stress_y, strain_r, stress_r = get_NM(
        eps_arr[0][step], eps_arr[1][step])
    ax1.cla()
    ax1.plot(strain_y, y_coord)
    ax1.plot((0, 0), (0, height))
    for i, strain in enumerate(strain_r):
        ax1.plot((strain, 0), (reinf_y_coord[i], reinf_y_coord[i]), '--')
    ax2.cla()
    ax2.plot(stress_y, y_coord)
    ax2.plot((0, 0), (0, height))
    for i, stress in enumerate(stress_r):
        ax2.plot((stress, 0), (reinf_y_coord[i], reinf_y_coord[i]), '--')


step_slider.on_changed(update)

plt.show()
