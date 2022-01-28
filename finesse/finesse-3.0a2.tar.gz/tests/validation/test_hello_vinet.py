import pytest
import numpy as np
from finesse.thermal.hello_vinet import (
    zeros_of_xjn_1_chi_jn,
    thermal_lenses_HG00,
    substrate_temperatures_HG00,
    surface_deformation_coating_heating_HG00,
    surface_deformation_substrate_heating_HG00,
    get_p_n_s_numerical,
    eval_p_n_s_numerical,
)
from scipy.special import jv, eval_hermite
from finesse.materials import FusedSilica
from os import path


@pytest.mark.parametrize("chi", (1e-4, 1, 100))
@pytest.mark.parametrize("n_max", (10,))
@pytest.mark.parametrize("s_max", (10, 50))
def test_zeros(chi, n_max, s_max):
    ns = np.arange(n_max + 1)
    eta = zeros_of_xjn_1_chi_jn(chi, n_max, s_max, 1e-6)
    x = eta
    zeros = x * jv(ns[:, np.newaxis] + 1, x) - chi * jv(ns[:, np.newaxis], x)
    assert abs(zeros).max() < 1e-5


@pytest.mark.parametrize("a", (0.1, 1))
@pytest.mark.parametrize("h", (0.1, 1))
@pytest.mark.parametrize("w", (0.01, 0.05))
@pytest.mark.parametrize("s_max", (10,))
def test_integrate_sub_T_vs_direct(a, h, w, s_max):
    r = np.linspace(0, a, 100)
    z = np.linspace(-h / 2, h / 2, 1000)
    dz = z[1] - z[0]
    material = FusedSilica

    Z_coat_per_W, Z_bulk_per_W = thermal_lenses_HG00(r, a, h, w, material, s_max=s_max)

    T_coat_per_W, T_bulk_per_W = substrate_temperatures_HG00(
        r, z, a, h, w, material, s_max=s_max
    )

    int_coat = dz * material.dndT * (T_coat_per_W).sum(0)
    int_bulk = dz * material.dndT * (T_bulk_per_W).sum(0)

    # loose requirements that the numerical integral is about the same as the direct calculation
    assert (abs(int_coat - Z_coat_per_W) / abs(Z_coat_per_W)).max() < 0.03
    assert (abs(int_bulk - Z_bulk_per_W) / abs(Z_bulk_per_W)).max() < 0.03


def test_coating_heating_thermo_refractive_and_elastic_vs_fea(request):
    """Tests HV gives similar result to FEA."""
    FEA = np.load(
        path.join(
            path.dirname(request.fspath),
            "test_hello_vinet_fea_data_coating_heating.npz",
        )
    )
    R_ap = 0.17
    h = 0.2
    w = 53e-3
    material = FusedSilica
    r = FEA["surface"][:, 0]

    W_z_coat_per_W = thermal_lenses_HG00(
        r, R_ap, h, w, material, s_max=7, root_accuracy=1e-3
    )[0]
    W_z_coat_per_W -= abs(W_z_coat_per_W).max()

    assert abs(W_z_coat_per_W - FEA["substrate"][:, 1]).max() < 15e-9

    Z = -surface_deformation_coating_heating_HG00(
        FEA["surface"][:, 0], R_ap, h, w, material, s_max=7, root_accuracy=1e-3
    )
    Z -= abs(Z).min()

    assert abs(Z - FEA["surface"][:, 1]).max() < 2e-9


def test_substrate_heating_thermo_refractive_and_elastic_vs_fea(request):
    FEA = np.load(
        path.join(
            path.dirname(request.fspath),
            "test_hello_vinet_fea_data_bulk_heating.npz",
        )
    )
    R_ap = 0.17
    h = 0.2
    w = 53e-3
    material = FusedSilica
    r = FEA["r"]

    W_z_bulk_per_W = thermal_lenses_HG00(
        r, R_ap, h, w, material, s_max=7, root_accuracy=1e-3
    )[1]

    assert abs(W_z_bulk_per_W - FEA["substrate"]).max() < 15e-9

    Z = surface_deformation_substrate_heating_HG00(
        r, R_ap, h, w, material, s_max=7, root_accuracy=1e-3
    )

    assert abs(Z - FEA["surface"]).max() < 2e-9


def test_numerical_p_n_s_fit():
    """Tests fourier-bessel decomposition fit."""
    a = 0.17
    w = 53e-3
    r = np.linspace(0, a, 101)
    # 5th order hermite radial distribution
    E = eval_hermite(5, np.sqrt(2) * r / w) * np.exp(-((r / w) ** 2))
    I = E * E
    fit = get_p_n_s_numerical(I, a, 20, FusedSilica)
    assert abs(I - eval_p_n_s_numerical(fit)).max() < 1
