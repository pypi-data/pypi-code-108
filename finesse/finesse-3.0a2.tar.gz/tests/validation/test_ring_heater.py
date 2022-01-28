import numpy as np
from finesse.thermal.ring_heater import substrate_temperature, thermal_lens
from finesse.materials import FusedSilica

from os import path


def test_fea(request):
    FEA = np.load(path.join(path.dirname(request.fspath), "test_ring_heater_fea.npz"))
    r = FEA["r"]
    a = 0.17
    b = 50e-3
    c = 70e-3
    h = 0.2
    z = np.linspace(-h / 2, h / 2, 1000)
    dz = z[1] - z[0]
    material = FusedSilica

    W = thermal_lens(r, a, b, c, h, material)
    W -= W.min()
    abs(W - FEA["substrate"]).max() < 1e-8

    # rough approximation for surface deformation
    Z = W / FusedSilica.dndT * FusedSilica.alpha
    abs(Z - FEA["surface"]).max() < 1e-9

    # integrate sub temp for total thermal lens
    T_rh_per_W = substrate_temperature(r, z, a, b, c, h, material)
    W = T_rh_per_W.sum(0) * dz * material.dndT
    abs(W - FEA["substrate"]).max() < 1e-8
